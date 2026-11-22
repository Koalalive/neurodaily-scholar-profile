#!/usr/bin/env python3
"""Curated field-leading journals for profile construction.

This is an editorial starting point, not an official JCR/CAS ranking. It exists so
a scholar profile is not limited to the journals that scholar happened to publish
in. Verify the current scope and metrics with JCR/Scopus/Scimago before relying on
a journal for formal evaluation.
"""
from __future__ import annotations

import argparse
import json
import re

GENERAL = [
    {"name": "Nature", "url": "https://www.nature.com/",
     "rss": "https://www.nature.com/nature.rss", "category": "general"},
    {"name": "Science", "url": "https://www.science.org/", "rss": "", "category": "general"},
    {"name": "PNAS", "url": "https://www.pnas.org/",
     "rss": "https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=pnas",
     "category": "general"},
    {"name": "Nature Communications", "url": "https://www.nature.com/ncomms",
     "rss": "https://www.nature.com/ncomms.rss", "category": "general"},
    {"name": "Science Advances", "url": "https://www.science.org/journal/sciadv",
     "rss": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv",
     "category": "general"},
]

FORESTRY = [
    {"name": "Current Forestry Reports", "url": "https://link.springer.com/journal/40725",
     "rss": "", "category": "forestry"},
    {"name": "Nature Ecology & Evolution", "url": "https://www.nature.com/natecolevol",
     "rss": "https://www.nature.com/natecolevol.rss", "category": "ecology"},
    {"name": "Nature Climate Change", "url": "https://www.nature.com/nclimate",
     "rss": "https://www.nature.com/nclimate.rss", "category": "climate"},
    {"name": "Nature Sustainability", "url": "https://www.nature.com/natsustain",
     "rss": "https://www.nature.com/natsustain.rss", "category": "sustainability"},
    {"name": "Nature Water", "url": "https://www.nature.com/natwater",
     "rss": "https://www.nature.com/natwater.rss", "category": "water"},
    {"name": "Nature Geoscience", "url": "https://www.nature.com/ngeo",
     "rss": "https://www.nature.com/ngeo.rss", "category": "earth"},
    {"name": "Global Change Biology", "url": "https://onlinelibrary.wiley.com/journal/13652486",
     "rss": "https://onlinelibrary.wiley.com/feed/13652486/most-recent", "category": "ecology"},
    {"name": "Ecology Letters", "url": "https://onlinelibrary.wiley.com/journal/14610248",
     "rss": "https://onlinelibrary.wiley.com/feed/14610248/most-recent", "category": "ecology"},
    {"name": "Trends in Ecology & Evolution", "url": "https://www.cell.com/trends/ecology-evolution",
     "rss": "https://www.cell.com/action/showFeed?type=etoc&feed=rss&jc=tree", "category": "ecology"},
    {"name": "Journal of Ecology", "url": "https://besjournals.onlinelibrary.wiley.com/journal/13652745",
     "rss": "https://besjournals.onlinelibrary.wiley.com/feed/13652745/most-recent", "category": "ecology"},
    {"name": "Forest Ecology and Management", "url": "https://www.sciencedirect.com/journal/forest-ecology-and-management",
     "rss": "https://rss.sciencedirect.com/publication/science/03781127", "category": "forestry"},
    {"name": "Agricultural and Forest Meteorology", "url": "https://www.sciencedirect.com/journal/agricultural-and-forest-meteorology",
     "rss": "https://rss.sciencedirect.com/publication/science/01681923", "category": "forestry"},
    {"name": "Forest Ecosystems", "url": "https://www.sciencedirect.com/journal/forest-ecosystems",
     "rss": "https://rss.sciencedirect.com/publication/science/21975620", "category": "forestry"},
    {"name": "Urban Forestry & Urban Greening", "url": "https://www.sciencedirect.com/journal/urban-forestry-and-urban-greening",
     "rss": "https://rss.sciencedirect.com/publication/science/16188667", "category": "forestry"},
    {"name": "Soil Biology and Biochemistry", "url": "https://www.sciencedirect.com/journal/soil-biology-and-biochemistry",
     "rss": "https://rss.sciencedirect.com/publication/science/00380717", "category": "soil"},
    {"name": "Geoderma", "url": "https://www.sciencedirect.com/journal/geoderma",
     "rss": "https://rss.sciencedirect.com/publication/science/00167061", "category": "soil"},
    {"name": "CATENA", "url": "https://www.sciencedirect.com/journal/catena",
     "rss": "https://rss.sciencedirect.com/publication/science/03418162", "category": "soil"},
    {"name": "Soil and Tillage Research", "url": "https://www.sciencedirect.com/journal/soil-and-tillage-research",
     "rss": "https://rss.sciencedirect.com/publication/science/01671987", "category": "soil"},
    {"name": "Plant and Soil", "url": "https://link.springer.com/journal/11104",
     "rss": "", "category": "soil"},
    {"name": "Applied Soil Ecology", "url": "https://www.sciencedirect.com/journal/applied-soil-ecology",
     "rss": "https://rss.sciencedirect.com/publication/science/09291393", "category": "soil"},
    {"name": "Water Research", "url": "https://www.sciencedirect.com/journal/water-research",
     "rss": "https://rss.sciencedirect.com/publication/science/00431354", "category": "water"},
    {"name": "Water Resources Research", "url": "https://agupubs.onlinelibrary.wiley.com/journal/19447973",
     "rss": "https://agupubs.onlinelibrary.wiley.com/feed/19447973/most-recent", "category": "water"},
    {"name": "Journal of Hydrology", "url": "https://www.sciencedirect.com/journal/journal-of-hydrology",
     "rss": "https://rss.sciencedirect.com/publication/science/00221694", "category": "water"},
    {"name": "Hydrology and Earth System Sciences", "url": "https://hess.copernicus.org/",
     "rss": "https://hess.copernicus.org/xml/rss2_0.xml", "category": "water"},
    {"name": "Agricultural Water Management", "url": "https://www.sciencedirect.com/journal/agricultural-water-management",
     "rss": "https://rss.sciencedirect.com/publication/science/03783774", "category": "water"},
    {"name": "Land Degradation & Development", "url": "https://onlinelibrary.wiley.com/journal/1099145X",
     "rss": "https://onlinelibrary.wiley.com/feed/1099145X/most-recent", "category": "land"},
]

NEUROSCIENCE = [
    {"name": "Nature Neuroscience", "url": "https://www.nature.com/nn", "rss": "https://www.nature.com/nn.rss",
     "category": "neuroscience"},
    {"name": "Neuron", "url": "https://www.cell.com/neuron",
     "rss": "https://www.cell.com/action/showFeed?type=etoc&feed=rss&jc=neuron", "category": "neuroscience"},
    {"name": "Nature Reviews Neuroscience", "url": "https://www.nature.com/nrn",
     "rss": "https://www.nature.com/nrn.rss", "category": "neuroscience"},
    {"name": "Brain", "url": "https://academic.oup.com/brain", "rss": "", "category": "neurology"},
    {"name": "Nature Medicine", "url": "https://www.nature.com/nm", "rss": "https://www.nature.com/nm.rss",
     "category": "medicine"},
    {"name": "The Lancet Neurology", "url": "https://www.thelancet.com/journals/laneur", "rss": "",
     "category": "neurology"},
    {"name": "Journal of Neuroscience", "url": "https://www.jneurosci.org/", "rss": "",
     "category": "neuroscience"},
    {"name": "eLife", "url": "https://elifesciences.org/",
     "rss": "https://observer.elifesciences.org/report/latest-articles.rss", "category": "life science"},
    {"name": "Trends in Neurosciences", "url": "https://www.cell.com/trends/neurosciences",
     "rss": "https://www.cell.com/action/showFeed?type=etoc&feed=rss&jc=tins", "category": "neuroscience"},
]

ONCOLOGY = [
    {"name": "Nature Medicine", "url": "https://www.nature.com/nm", "rss": "https://www.nature.com/nm.rss",
     "category": "medicine"},
    {"name": "Cancer Cell", "url": "https://www.cell.com/cancer-cell",
     "rss": "https://www.cell.com/action/showFeed?type=etoc&feed=rss&jc=cancell", "category": "oncology"},
    {"name": "Nature Cancer", "url": "https://www.nature.com/natcancer",
     "rss": "https://www.nature.com/natcancer.rss", "category": "oncology"},
    {"name": "The Lancet Oncology", "url": "https://www.thelancet.com/journals/lanonc", "rss": "",
     "category": "oncology"},
    {"name": "Journal of Clinical Oncology", "url": "https://ascopubs.org/journal/jco", "rss": "",
     "category": "oncology"},
    {"name": "Cancer Discovery", "url": "https://aacrjournals.org/cancerdiscovery", "rss": "",
     "category": "oncology"},
    {"name": "Annals of Oncology", "url": "https://www.annalsofoncology.org/", "rss": "",
     "category": "oncology"},
    {"name": "JAMA Oncology", "url": "https://jamanetwork.com/journals/jamaoncology", "rss": "",
     "category": "oncology"},
    {"name": "Nature Reviews Cancer", "url": "https://www.nature.com/nrc", "rss": "https://www.nature.com/nrc.rss",
     "category": "oncology"},
]

PSYCHIATRY = [
    {"name": "JAMA Psychiatry", "url": "https://jamanetwork.com/journals/jamapsychiatry", "rss": "",
     "category": "psychiatry"},
    {"name": "The Lancet Psychiatry", "url": "https://www.thelancet.com/journals/lanpsy", "rss": "",
     "category": "psychiatry"},
    {"name": "Molecular Psychiatry", "url": "https://www.nature.com/mp", "rss": "https://www.nature.com/mp.rss",
     "category": "psychiatry"},
    {"name": "Biological Psychiatry", "url": "https://www.biologicalpsychiatryjournal.com/",
     "rss": "https://rss.sciencedirect.com/publication/science/00063223", "category": "psychiatry"},
    {"name": "World Psychiatry", "url": "https://onlinelibrary.wiley.com/journal/20515545", "rss": "",
     "category": "psychiatry"},
    {"name": "American Journal of Psychiatry", "url": "https://ajp.psychiatryonline.org/", "rss": "",
     "category": "psychiatry"},
    {"name": "Nature Mental Health", "url": "https://www.nature.com/natmentalhealth",
     "rss": "https://www.nature.com/natmentalhealth.rss", "category": "psychiatry"},
]

DOMAIN_JOURNALS = {
    "forestry": GENERAL + FORESTRY,
    "neuroscience": GENERAL + NEUROSCIENCE,
    "oncology": GENERAL + ONCOLOGY,
    "psychiatry": GENERAL + PSYCHIATRY,
    "general": GENERAL,
}


def _key(name: str) -> str:
    normalized = re.sub(r"^the\s+", "", (name or "").strip(), flags=re.I)
    return re.sub(r"[^a-z0-9]+", "", normalized.casefold())


def for_domain(domain: str) -> list[dict]:
    return [dict(row) for row in DOMAIN_JOURNALS.get(domain, GENERAL)]


def merge(author_rows: list[dict], domain: str, *, include_field: bool = True,
          limit: int = 20) -> list[dict]:
    """Field leaders first, but reserve slots for journals the scholar published in."""
    field_rows = []
    if include_field:
        for row in for_domain(domain):
            field_rows.append({**row, "impact_factor": None, "jcr": "", "cas": "",
                               "metric_year": None, "year": None, "aliases": [], "issns": []})
    field_keys = {_key(row["name"]) for row in field_rows}
    author_unique = [row for row in author_rows
                     if row.get("name") and _key(row["name"]) not in field_keys]
    reserve = min(len(author_unique), max(4, limit // 4)) if include_field else 0
    field_take = max(0, limit - reserve) if include_field else 0
    ordered = field_rows[:field_take] + author_rows + field_rows[field_take:]
    rows, seen = [], set()
    for row in ordered:
        key = _key(row.get("name"))
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append(row)
        if len(rows) >= limit:
            break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain", nargs="?", default="forestry",
                        choices=tuple(DOMAIN_JOURNALS))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = for_domain(args.domain)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for index, row in enumerate(rows, 1):
            print(f"{index:>2}. {row['name']} [{row['category']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
