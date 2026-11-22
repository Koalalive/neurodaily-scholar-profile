#!/usr/bin/env python3
"""Validate the portable structure of a NeuroDaily scholar profile."""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import parse_qsl, urlsplit

SECRETS = {"key", "apikey", "token", "accesstoken", "authtoken", "secret",
           "password", "signature", "sig", "credential", "jwt"}


def _clean(value) -> str:
    return " ".join(str(value or "").split())


def _url(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return "URL must be http(s) with a host"
    for key, _ in parse_qsl(parts.query, keep_blank_values=True):
        if re.sub(r"[^a-z]", "", key.casefold()) in SECRETS:
            return f"URL query contains secret-like parameter {key!r}"
    return ""


def validate(document: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(document, dict):
        return ["profile must be a JSON object"], warnings
    if document.get("format") != "neurodaily.profile":
        errors.append("format must be 'neurodaily.profile'")
    if document.get("version") != 1:
        errors.append("version must be 1")
    config = document.get("config")
    if not isinstance(config, dict):
        return errors + ["config must be an object"], warnings
    disciplines = config.get("disciplines")
    if not isinstance(disciplines, list) or not disciplines:
        errors.append("config.disciplines must contain at least one entry")
    else:
        for index, row in enumerate(disciplines):
            if not isinstance(row, dict) or not _clean(row.get("name")):
                errors.append(f"disciplines[{index}].name is required")
                continue
            enabled = row.get("enabled", True)
            if enabled and not any(row.get(key) for key in
                                   ("keywords", "mesh_terms", "arxiv_cats", "bio_cats")):
                errors.append(f"disciplines[{index}] needs keywords/mesh/arxiv/bio")
    journals = config.get("journals") or []
    if not journals:
        warnings.append("no journals inferred; profile will rely on keyword search")
    seen = set()
    for index, row in enumerate(journals):
        name = _clean((row or {}).get("name"))
        if not name:
            errors.append(f"journals[{index}].name is required")
        elif name.casefold() in seen:
            warnings.append(f"duplicate journal: {name}")
        seen.add(name.casefold())
        for field in ("url", "rss"):
            value = _clean((row or {}).get(field))
            if value:
                problem = _url(value)
                if problem:
                    errors.append(f"journals[{index}].{field}: {problem}")
    for name, opts in (config.get("sources") or {}).items():
        if not isinstance(opts, dict):
            errors.append(f"sources.{name} must be an object")
            continue
        if opts.get("type") in {"rss", "json_api", "json"} and not _clean(opts.get("url")):
            errors.append(f"sources.{name} requires url")
    search = config.get("search")
    if search is not None:
        if not isinstance(search, dict):
            errors.append("search must be an object")
        elif search.get("journal_mode") not in (None, "any", "only", "prefer"):
            errors.append("search.journal_mode must be any/only/prefer")
        elif search.get("sort") not in (None, "default", "latest", "relevance", "journal"):
            errors.append("search.sort is invalid")
    for name in ("email", "smtp", "password", "api_key"):
        if name in config:
            errors.append(f"private delivery field {name!r} must not be in a profile")
    if not any(url for url in (config.get("policy_feeds") or [])):
        warnings.append("no policy feeds; add them in NeuroDaily if needed")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.profile, encoding="utf-8") as stream:
            document = json.load(stream)
    except OSError as exc:
        print(f"error: cannot read {args.profile}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}",
              file=sys.stderr)
        return 1
    errors, warnings = validate(document)
    result = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        if not errors:
            print(f"OK: {document['config'].get('profile', 'profile')}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
