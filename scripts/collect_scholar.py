#!/usr/bin/env python3
"""Collect public publication evidence for a scholar.

Sources: ORCID public API, OpenAlex, PubMed E-utilities fallback.
No API key is required. Output is evidence JSON consumed by build_profile.py.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

UA = "NeuroDaily-Scholar-Profile/1.0 (+https://github.com/Koalalive/neurodaily)"
TIMEOUT = 30


def _get(url: str, accept: str = "application/json") -> dict:
    request = Request(url, headers={"Accept": accept, "User-Agent": UA})
    with urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _clean(value) -> str:
    return " ".join(str(value or "").split())


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _clean(value).casefold()).strip()


def _orcid(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"\d{4}-\d{4}-\d{4}-\d{3}[\dXx]", value)
    return match.group(0).upper().replace("X", "X") if match else None


def _doi(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"10\.\d{4,9}/[^\s\"<>]+", value)
    return match.group(0).rstrip(".,;)").lower() if match else None


def _year(value) -> int | None:
    match = re.search(r"(19|20)\d{2}", str(value or ""))
    return int(match.group(0)) if match else None


def _orcid_works(orcid: str | None) -> list[dict]:
    if not orcid:
        return []
    try:
        payload = _get(f"https://pub.orcid.org/v3.0/{quote(orcid)}/works")
    except (HTTPError, URLError, ValueError, TimeoutError, OSError):
        return []
    works = []
    for group in payload.get("group", []):
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        row = summaries[0]
        title = _clean((row.get("title") or {}).get("title", {}).get("value"))
        journal = _clean((row.get("journal-title") or {}).get("value"))
        year = _year((row.get("publication-date") or {}).get("year", {}).get("value"))
        doi = None
        for ext in (row.get("external-ids") or {}).get("external-id", []):
            if (ext.get("external-id-type") or "").lower() == "doi":
                doi = _doi(ext.get("external-id-value"))
                break
        if title:
            works.append({"title": title, "year": year, "journal": journal,
                          "doi": doi, "source": "ORCID", "concepts": []})
    return works


def _openalex_author(name: str, orcid: str | None, affiliation: str | None,
                     mailto: str | None) -> tuple[dict | None, list[dict], list[str]]:
    warnings: list[str] = []
    candidates: list[dict] = []
    author = None
    try:
        if orcid:
            author = _get(f"https://api.openalex.org/authors/{quote('https://orcid.org/' + orcid, safe='')}")
        else:
            params = {"search": name, "per-page": 10}
            if mailto:
                params["mailto"] = mailto
            payload = _get("https://api.openalex.org/authors?" + urlencode(params))
            for row in payload.get("results", []):
                inst = ((row.get("last_known_institutions") or [{}])[0].get("display_name")
                        if row.get("last_known_institutions") else "")
                candidates.append({"id": row.get("id"), "name": row.get("display_name"),
                                   "orcid": row.get("orcid"), "works": row.get("works_count"),
                                   "affiliation": inst})
            exact = [row for row in candidates if _norm(row.get("name")) == _norm(name)]
            if affiliation:
                exact = [row for row in exact
                         if _norm(affiliation) in _norm(row.get("affiliation"))] or exact
            author = exact[0] if exact else (candidates[0] if candidates else None)
            if not author:
                warnings.append("No OpenAlex author match.")
            elif len(exact) != 1 and not affiliation:
                warnings.append("Author match is ambiguous; pass --orcid or --affiliation.")
    except (HTTPError, URLError, ValueError, TimeoutError, OSError) as exc:
        warnings.append(f"OpenAlex author lookup failed: {type(exc).__name__}")
    return author, candidates, warnings


def _openalex_works(author: dict | None, limit: int, mailto: str | None) -> list[dict]:
    if not author or not author.get("id"):
        return []
    return _openalex_works_by_id(author["id"].rsplit("/", 1)[-1], limit, mailto)


def _openalex_works_by_id(author_id: str, limit: int, mailto: str | None) -> list[dict]:
    params = {"filter": f"author.id:{author_id}", "per-page": min(200, max(1, limit)),
              "sort": "publication_year:desc"}
    if mailto:
        params["mailto"] = mailto
    try:
        payload = _get("https://api.openalex.org/works?" + urlencode(params))
    except (HTTPError, URLError, ValueError, TimeoutError, OSError):
        return []
    works = []
    for row in payload.get("results", [])[:limit]:
        source = ((row.get("primary_location") or {}).get("source") or {})
        concepts = [_clean((item or {}).get("display_name"))
                    for item in (row.get("concepts") or []) if item]
        topics = [_clean((item or {}).get("display_name"))
                  for item in (row.get("topics") or []) if item]
        doi = _doi(row.get("doi"))
        works.append({
            "title": _clean(row.get("title")),
            "year": _year(row.get("publication_year")),
            "journal": _clean(source.get("display_name")),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else _clean(row.get("id")),
            "source": "OpenAlex",
            "concepts": concepts + topics,
        })
    return works


def _pubmed_works(name: str, limit: int) -> list[dict]:
    if not name:
        return []
    try:
        search = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urlencode({
            "db": "pubmed", "term": f"{name}[Author]", "retmode": "json",
            "retmax": min(200, limit), "tool": "neurodaily-scholar-profile",
        }))
        ids = (search.get("esearchresult") or {}).get("idlist") or []
        if not ids:
            return []
        summary = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urlencode({
            "db": "pubmed", "id": ",".join(ids), "retmode": "json",
            "tool": "neurodaily-scholar-profile",
        }))
    except (HTTPError, URLError, ValueError, TimeoutError, OSError):
        return []
    result = summary.get("result") or {}
    works = []
    for pmid in ids:
        row = result.get(pmid) or {}
        doi = next((_doi(item.get("value")) for item in row.get("articleids", [])
                    if (item.get("idtype") or "").lower() == "doi"), None)
        works.append({
            "title": _clean(row.get("title")),
            "year": _year(row.get("pubdate")),
            "journal": _clean(row.get("fulljournalname") or row.get("source")),
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "source": "PubMed",
            "concepts": [],
        })
    return works


def _merge(works: list[dict], limit: int) -> list[dict]:
    merged: dict[str, dict] = {}
    for work in works:
        if not work.get("title"):
            continue
        key = (work.get("doi") or _norm(work["title"]))[:400]
        current = merged.get(key)
        if not current:
            merged[key] = work
            continue
        for field in ("year", "journal", "doi", "url"):
            if not current.get(field) and work.get(field):
                current[field] = work[field]
        current["concepts"] = list(dict.fromkeys(
            [c for c in current.get("concepts", []) if c] +
            [c for c in work.get("concepts", []) if c]
        ))
    return list(merged.values())[:limit]


def collect(name: str, orcid: str | None, affiliation: str | None,
            limit: int, mailto: str | None,
            author_ids: list[str] | None = None) -> dict:
    orcid = _orcid(orcid)
    warnings: list[str] = []
    works = _orcid_works(orcid)
    author, candidates, author_warnings = _openalex_author(name or "", orcid, affiliation, mailto)
    warnings.extend(author_warnings)
    if author_ids:
        for author_id in author_ids:
            works.extend(_openalex_works_by_id(author_id.rsplit("/", 1)[-1], limit, mailto))
    else:
        works.extend(_openalex_works(author, limit, mailto))
    if not works:
        warnings.append("No ORCID/OpenAlex works; trying PubMed author fallback.")
        works.extend(_pubmed_works(name or "", limit))
    works = _merge(works, limit)
    if not works:
        warnings.append("No publications found. Do not generate a profile from guesswork.")

    concepts = Counter()
    journals = Counter()
    for work in works:
        for concept in work.get("concepts", []):
            if len(concept) >= 3:
                concepts[concept] += 1
        if work.get("journal"):
            journals[work["journal"]] += 1

    return {
        "format": "neurodaily.scholar-evidence",
        "version": 1,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "scholar": {
            "name": _clean(name),
            "orcid": orcid,
            "affiliation": _clean(affiliation),
            "openalex_author": author,
            "openalex_authors": author_ids or ([author] if author else []),
        },
        "works": works,
        "top_concepts": [{"name": k, "count": v} for k, v in concepts.most_common(30)],
        "top_journals": [{"name": k, "count": v} for k, v in journals.most_common(20)],
        "author_candidates": candidates,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="", help="scholar name")
    parser.add_argument("--orcid", default=None, help="ORCID iD (recommended)")
    parser.add_argument("--affiliation", default=None, help="institution for disambiguation")
    parser.add_argument("--limit", type=int, default=100, help="max works")
    parser.add_argument("--mailto", default=None, help="contact email for OpenAlex polite pool")
    parser.add_argument("--author-id", action="append", default=[],
                        help="OpenAlex author ID to include (repeatable; merges split records)")
    parser.add_argument("--out", default="evidence.json")
    args = parser.parse_args()
    if not args.name and not args.orcid:
        parser.error("pass --name and/or --orcid")
    evidence = collect(args.name, args.orcid, args.affiliation, args.limit, args.mailto,
                       args.author_id)
    with open(args.out, "w", encoding="utf-8") as stream:
        json.dump(evidence, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"{len(evidence['works'])} works -> {args.out}")
    for item in evidence["top_concepts"][:8]:
        print(f"  {item['name']} ({item['count']})")
    for warning in evidence["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    return 0 if evidence["works"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
