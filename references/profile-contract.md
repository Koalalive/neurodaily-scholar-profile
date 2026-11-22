# NeuroDaily profile contract

The generated file is a **single portable JSON document**:

```json
{
  "format": "neurodaily.profile",
  "version": 1,
  "config": {
    "profile": "scholar-slug",
    "disciplines": [],
    "global_keywords": [],
    "search": {},
    "sources": {},
    "windows": {},
    "policy_feeds": [],
    "journals": []
  }
}
```

## Required shape

| Field | Rule |
|---|---|
| `format` | Exactly `neurodaily.profile` |
| `version` | Exactly `1` |
| `config.profile` | Stable slug used as the profile filename |
| `config.disciplines` | At least one; each enabled row needs keywords/mesh/arxiv/bio |
| `config.sources` | Optional; generic RSS requires `type` + `url` |
| `config.journals` | Optional; each row needs a `name` |
| `config.search` | Optional; `journal_mode` = `any`/`only`/`prefer`; `sort` = `default`/`latest`/`relevance`/`journal` |

## Field details

### `config.disciplines[]`

```json
{"name": "Soil erosion and sediment transport", "keywords": ["..."],
 "arxiv_cats": [], "mesh_terms": [], "bio_cats": [], "enabled": true}
```

An enabled discipline must have at least one of `keywords`, `mesh_terms`,
`arxiv_cats`, `bio_cats`.

### `config.search`

```json
{"query": "(Loess OR \"soil erosion\") AND NOT (pediatric)",
 "sets": {}, "rules": {},
 "journal_mode": "prefer", "journals": ["CATENA"], "sort": "relevance"}
```

- `query`: NeuroDaily's Boolean expression. Multi-word phrases must be quoted.
- `sets`: named, reusable expressions (`"1": "TI=..."`).
- `rules`: optional scoped expressions for `news`, `policy`, `trial`.
- `journal_mode`: `any`, `only`, or `prefer`.
- `sort`: `default`, `latest`, `relevance`, or `journal`.

### `config.sources`

```json
{"pubmed": {"enabled": true, "max_results": 300, "lookback_days": 7},
 "arxiv": {"enabled": false},
 "my_feed": {"type": "rss", "url": "https://example.org/feed.xml", "kind": "news"}}
```

Built-in names: `journal`, `pubmed`, `arxiv`, `biorxiv`, `fda_drugs`,
`fda_devices`, `trials`, `policy`. A custom source needs `type` + `url`.

### `config.windows`

```json
{"daily_paper_hours": 36, "manual_paper_hours": 240,
 "trials_hours": 36, "funding_hours": 36, "news_hours": 36,
 "other_lookback_days": 7}
```

### `config.journals[]`

```json
{"name": "CATENA", "url": "https://www.sciencedirect.com/journal/catena",
 "rss": "https://rss.sciencedirect.com/publication/science/03418162",
 "category": "forestry", "impact_factor": null, "jcr": "", "cas": ""}
```

`impact_factor`, `jcr`, `cas`, `year`, `aliases`, and `issns` are optional.

## Private fields are excluded

Never put SMTP settings, API keys, recipient addresses, webhook URLs, local output
paths, or scheduler settings in a shared profile. NeuroDaily's import/export code
keeps those local; this skill also rejects obvious secret fields.

## Journal metrics

Journal rows may include user-supplied `impact_factor`, `jcr`, `cas`, and `year`.
This skill intentionally leaves them empty unless the user provides an official
source. Do not fabricate JCR/CAS values.

## Import into NeuroDaily

```bash
python scripts/validate.py neurodaily-profile.json
neurodaily profile validate neurodaily-profile.json
neurodaily profile import neurodaily-profile.json --name scholar-slug
neurodaily profile doctor scholar-slug
```

`validate.py` reports JSON syntax errors with line/column and schema errors with
field paths (for example `config.sources.policy.feed_kinds[...]`) before import.
