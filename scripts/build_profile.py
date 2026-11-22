#!/usr/bin/env python3
"""Turn scholar evidence JSON into a portable NeuroDaily profile."""
from __future__ import annotations

import argparse
from collections import Counter
import json

from field_journals import merge as merge_field_journals
import re
import sys

GENERIC = {
    "medicine", "biology", "internal medicine", "science", "research",
    "computer science", "chemistry", "physics", "pathology", "surgery",
    "public health", "engineering", "mathematics", "materials science",
    "environmental science", "ecology", "geology", "geography",
    "hydrology", "soil science", "agronomy", "forestry", "economics",
    "psychology", "neuroscience", "psychiatry", "stimulation",
}

PREPRINT_JOURNALS = {
    "osf preprints", "arxiv", "biorxiv", "medrxiv", "research square",
    "ssrn", "preprints.org", "psyarxiv", "techrxiv", "chemrxiv",
}

JOURNAL_CANONICAL = {
    "brain stimulation": "Brain Stimulation",
    "transcranial magnetic stimulation": "Transcranial Magnetic Stimulation",
    "journal of clinical psychiatry": "Journal of Clinical Psychiatry",
    "the journal of clinical psychiatry": "Journal of Clinical Psychiatry",
    "american journal of psychiatry": "American Journal of Psychiatry",
    "the american journal of psychiatry": "American Journal of Psychiatry",
    "biological psychiatry": "Biological Psychiatry",
    "molecular psychiatry": "Molecular Psychiatry",
    "world psychiatry": "World Psychiatry",
    "nature mental health": "Nature Mental Health",
    "translational psychiatry": "Translational Psychiatry",
    "journal of affective disorders": "Journal of Affective Disorders",
    "npj mental health research": "npj Mental Health Research",
}

DOMAINS = {
    "forestry": {
        "needles": ("forest", "soil", "erosion", "hydrology", "vegetation",
                    "loess", "afforestation", "watershed", "grassland",
                    "sediment", "land degradation", "arid", "plant"),
        "sources": {
            "journal": {"enabled": True, "max_results": 300, "lookback_days": 7},
            "pubmed": {"enabled": True, "max_results": 300, "lookback_days": 7},
            "arxiv": {"enabled": False, "max_results": 100, "lookback_days": 2},
            "biorxiv": {"enabled": False, "max_results": 100, "lookback_days": 2},
            "trials": {"enabled": False, "max_results": 100, "lookback_days": 2},
            "policy": {"enabled": False, "max_results": 100, "lookback_days": 7},
            "fda_drugs": {"enabled": False, "max_results": 50, "lookback_days": 2},
            "fda_devices": {"enabled": False, "max_results": 50, "lookback_days": 2},
        },
    },
    "neuroscience": {
        "needles": ("neuroscience", "neural", "brain", "neuro", "cognitive",
                    "cognition", "hippocampus", "cortex"),
        "sources": {
            "journal": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "pubmed": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "arxiv": {"enabled": True, "max_results": 200, "lookback_days": 2},
            "biorxiv": {"enabled": True, "max_results": 200, "lookback_days": 2},
            "trials": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "policy": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "fda_drugs": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "fda_devices": {"enabled": True, "max_results": 100, "lookback_days": 2},
        },
    },
    "oncology": {
        "needles": ("oncology", "cancer", "tumor", "tumour", "carcinoma",
                    "leukemia", "lymphoma", "chemotherapy"),
        "sources": {
            "journal": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "pubmed": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "biorxiv": {"enabled": True, "max_results": 200, "lookback_days": 2},
            "arxiv": {"enabled": False, "max_results": 100, "lookback_days": 2},
            "trials": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "policy": {"enabled": True, "max_results": 100, "lookback_days": 2},
        },
    },
    "psychiatry": {
        "needles": ("psychiatry", "psychiatric", "mental", "depression",
                    "schizophrenia", "anxiety", "addiction", "neuromodulation",
                    "transcranial", "deep brain stimulation", "ptsd",
                    "traumatic brain injury", "bipolar", "suicide",
                    "obsessive-compulsive", "electroconvulsive"),
        "sources": {
            "journal": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "pubmed": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "biorxiv": {"enabled": True, "max_results": 200, "lookback_days": 2},
            "arxiv": {"enabled": False, "max_results": 100, "lookback_days": 2},
            "trials": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "policy": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "fda_drugs": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "fda_devices": {"enabled": True, "max_results": 100, "lookback_days": 2},
        },
    },
    "general": {
        "needles": (),
        "sources": {
            "journal": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "pubmed": {"enabled": True, "max_results": 300, "lookback_days": 2},
            "arxiv": {"enabled": True, "max_results": 200, "lookback_days": 2},
            "biorxiv": {"enabled": True, "max_results": 200, "lookback_days": 2},
            "trials": {"enabled": True, "max_results": 100, "lookback_days": 2},
            "policy": {"enabled": True, "max_results": 100, "lookback_days": 2},
        },
    },
}

FIELD_HINTS = (
    (("neuroscience", "neural", "brain", "neuro", "cognitive", "cognition"),
     {"arxiv": ["q-bio.NC"], "bio": ["neuroscience"]}),
    (("psychiatry", "psychiatric", "mental", "depression", "schizophrenia",
      "anxiety", "addiction"),
     {"bio": ["psychiatry"], "mesh": ["Psychiatry"]}),
    (("oncology", "cancer", "tumor", "tumour", "carcinoma", "leukemia"),
     {"bio": ["cancer biology"], "mesh": ["Neoplasms"]}),
    (("cardiology", "cardiovascular", "heart"), {"mesh": ["Cardiovascular Diseases"]}),
    (("immunology", "immune", "inflammation"), {"mesh": ["Immunology"]}),
    (("genetics", "genomics", "genome"), {"bio": ["genomics"]}),
    (("machine learning", "artificial intelligence", "deep learning"),
     {"arxiv": ["cs.LG", "cs.AI"]}),
    (("epidemiology", "public health"), {"mesh": ["Epidemiology"]}),
)

DOMAIN_QUERIES = {
    "forestry": 'Loess OR "soil erosion" OR "vegetation restoration" OR afforestation OR "forest hydrology" OR "soil water"',
    "psychiatry": 'depression OR PTSD OR "transcranial magnetic stimulation" OR neuromodulation OR "deep brain stimulation"',
}

# Policy/news RSS is explicit: enabling the policy source without feeds yields
# no policy/news section. These are official or publisher feeds, not scraped
# private pages. Review them before importing a profile.
DOMAIN_POLICY_FEEDS = {
    "psychiatry": [
        "https://www.nimh.nih.gov/news/index.rss",
        "https://nida.nih.gov/rss.xml",
        "https://www.ninds.nih.gov/news-events/news-releases/rss.xml",
        "https://www.sfn.org/news",
        "https://www.nature.com/subjects/neuroscience.rss",
        "https://www.nature.com/subjects/psychiatric-disorders.rss",
        "https://www.nature.com/mp.rss",
        "https://www.nature.com/nm.rss",
        "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml",
    ],
    "neuroscience": [
        "https://www.nimh.nih.gov/news/index.rss",
        "https://www.ninds.nih.gov/news-events/news-releases/rss.xml",
        "https://www.sfn.org/news",
        "https://www.nature.com/subjects/neuroscience.rss",
        "https://www.nature.com/nn.rss",
    ],
}


JOURNAL_RSS = {
    "Journal of Environmental Management": "https://rss.sciencedirect.com/publication/science/03014797",
    "Applied Soil Ecology": "https://rss.sciencedirect.com/publication/science/09291393",
    "Water Resources Research": "https://agupubs.onlinelibrary.wiley.com/feed/19447973/most-recent",
    "Land Degradation and Development": "https://onlinelibrary.wiley.com/feed/1099145X/most-recent",
    "Ecological Engineering": "https://rss.sciencedirect.com/publication/science/09258574",
    "Water": "https://www.mdpi.com/rss/journal/water",
    "Agronomy": "https://www.mdpi.com/rss/journal/agronomy",
    "Journal of Arid Land": "https://link.springer.com/search.rss?facet-journal-id=40333",
    "CATENA": "https://rss.sciencedirect.com/publication/science/03418162",
}


def _clean(value) -> str:
    return " ".join(str(value or "").split())


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", _clean(value).casefold()).strip("-")
    return slug[:40] or "scholar"


def _category(concept: str) -> dict:
    low = concept.casefold()
    for needles, values in FIELD_HINTS:
        if any(needle in low for needle in needles):
            return values
    return {}


def _normalize_concept(value: str) -> str:
    name = _clean(value)
    name = re.sub(r"\s+Studies$", "", name, flags=re.I)
    name = re.sub(r"^Treatment of\s+", "", name, flags=re.I)
    return name


def _keywords(evidence: dict, limit: int = 12) -> list[str]:
    words = []
    for item in evidence.get("top_concepts") or []:
        name = _normalize_concept(item.get("name"))
        if (len(name) < 3 or name.casefold() in GENERIC
                or "economic" in name.casefold()
                or "(" in name or ")" in name):
            continue
        words.append(name)
    if not words:
        counter = Counter()
        for work in evidence.get("works") or []:
            for word in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", work.get("title", "")):
                if word.casefold() not in {"the", "and", "with", "from", "study", "using"}:
                    counter[word] += 1
        words = [word for word, _ in counter.most_common(limit)]
    unique, seen = [], set()
    for word in words:
        key = word.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(word)
    return unique[:limit]


def _detect_domain(evidence: dict, override: str | None = None) -> str:
    if override:
        return override
    text = " ".join([_clean(item.get("name")) for item in evidence.get("top_concepts") or []] +
                    [_clean(work.get("title")) for work in evidence.get("works") or []])
    scores = {}
    for name, config in DOMAINS.items():
        if name == "general":
            continue
        score = 0
        for needle in config["needles"]:
            # Word boundaries prevent "plant" matching "implant" and
            # "neuro" matching "neuromodulation" indiscriminately.
            score += len(re.findall(r"(?<![a-z0-9])" + re.escape(needle) +
                                    r"(?![a-z0-9])", text, re.I))
        scores[name] = score
    best = max(scores, key=lambda name: (scores[name], name == "psychiatry"))
    return best if scores[best] > 0 else "general"


def _quote(term: str) -> str:
    term = _clean(term).replace('"', "")
    return f'"{term}"' if " " in term else term


def _query(keywords: list[str], exclude: list[str], mode: str, name: str) -> str:
    if mode == "author":
        query = f'AU="{_clean(name)}"'
    else:
        query = " OR ".join(_quote(word) for word in keywords[:6])
    if exclude:
        query += " AND NOT (" + " OR ".join(_quote(word) for word in exclude) + ")"
    return query


def _disciplines(keywords: list[str]) -> list[dict]:
    rows = []
    for name in keywords[:4]:
        hints = _category(name)
        rows.append({
            "name": name,
            "arxiv_cats": hints.get("arxiv", []),
            "mesh_terms": hints.get("mesh", []),
            "bio_cats": hints.get("bio", []),
            "keywords": [name],
            "enabled": True,
        })
    return rows


def _normalize_journal(value: str) -> str:
    name = _clean(value).rstrip(" .")
    name = re.sub(r"^the\s+", "", name, flags=re.I)
    return JOURNAL_CANONICAL.get(name.casefold(), name)


def _is_preprint(name: str) -> bool:
    low = name.casefold()
    return any(token in low for token in PREPRINT_JOURNALS)


def _journals(evidence: dict, limit: int) -> list[dict]:
    result = []
    seen = set()
    for item in evidence.get("top_journals") or []:
        name = _normalize_journal(item.get("name"))
        key = name.casefold()
        if not name or key in seen or _is_preprint(name):
            continue
        seen.add(key)
        result.append({"name": name, "url": "", "rss": JOURNAL_RSS.get(name, ""),
                       "category": "forestry" if name in JOURNAL_RSS else "general",
                       "impact_factor": None, "jcr": "", "cas": "", "metric_year": None,
                       "year": None, "aliases": [], "issns": []})
        if len(result) >= limit:
            break
    return result


def build(evidence: dict, name: str | None = None, profile_id: str | None = None,
          journals_limit: int = 20, *, mode: str = "interests", domain: str | None = None,
          exclude: list[str] | None = None, query_override: str | None = None,
          include_field_journals: bool = True) -> dict:
    works = evidence.get("works") or []
    if not works:
        raise ValueError("evidence contains no works; refusing to invent a profile")
    scholar = evidence.get("scholar") or {}
    display = _clean(name or scholar.get("name") or profile_id or "Scholar")
    pid = profile_id or _slug(display)
    keywords = _keywords(evidence)
    if not keywords:
        raise ValueError("could not infer keywords from evidence")
    selected_domain = _detect_domain(evidence, domain)
    author_journals = _journals(evidence, journals_limit)
    journals = merge_field_journals(author_journals, selected_domain,
                                    include_field=include_field_journals,
                                    limit=journals_limit)
    top_journals = [row["name"] for row in journals[:12]]
    if query_override:
        query = query_override
    elif mode == "interests" and selected_domain in DOMAIN_QUERIES:
        query = DOMAIN_QUERIES[selected_domain]
    else:
        query = _query(keywords, exclude or [], mode, display)
    if exclude and "AND NOT (" not in query:
        query = f"({query}) AND NOT (" + " OR ".join(_quote(word) for word in exclude) + ")"
    config = {
        "profile": pid,
        "disciplines": _disciplines(keywords),
        "global_keywords": keywords,
        "search": {
            "query": query,
            "sets": {},
            "journal_mode": "prefer",
            "journals": top_journals,
            "sort": "relevance" if mode == "interests" else "latest",
        },
        "sources": DOMAINS[selected_domain]["sources"],
        "windows": {
            "daily_paper_hours": 36,
            "manual_paper_hours": 240,
            "trials_hours": 36,
            "funding_hours": 36,
            "news_hours": 36,
            "other_lookback_days": 7,
        },
        "policy_feeds": DOMAIN_POLICY_FEEDS.get(selected_domain, []),
        "journals": journals,
    }
    return {"format": "neurodaily.profile", "version": 1, "config": config}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", help="JSON from collect_scholar.py")
    parser.add_argument("--name", default=None, help="display name override")
    parser.add_argument("--profile-id", default=None, help="NeuroDaily profile id")
    parser.add_argument("--journals-limit", type=int, default=20)
    parser.add_argument("--mode", choices=("interests", "author"), default="interests")
    parser.add_argument("--domain", choices=tuple(DOMAINS), default=None,
                        help="domain preset override")
    parser.add_argument("--exclude", action="append", default=[],
                        help="term to append as AND NOT (repeatable)")
    parser.add_argument("--query", default=None, help="explicit search query override")
    parser.add_argument("--no-field-journals", action="store_true",
                        help="do not add the curated field-leading journal catalog")
    parser.add_argument("--out", default="neurodaily-profile.json")
    args = parser.parse_args()
    with open(args.evidence, encoding="utf-8") as stream:
        evidence = json.load(stream)
    try:
        profile = build(evidence, args.name, args.profile_id, args.journals_limit,
                        mode=args.mode, domain=args.domain, exclude=args.exclude,
                        query_override=args.query,
                        include_field_journals=not args.no_field_journals)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as stream:
        json.dump(profile, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    config = profile["config"]
    print(f"{config['profile']}: {len(config['disciplines'])} disciplines, "
          f"{len(config['global_keywords'])} keywords, {len(config['journals'])} journals -> {args.out}")
    print("disciplines:", ", ".join(row["name"] for row in config["disciplines"]))
    print("domain:", _detect_domain(evidence, args.domain), "| query:", config["search"]["query"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
