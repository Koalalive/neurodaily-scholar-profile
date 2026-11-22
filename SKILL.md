---
version: 1.3.2
name: neurodaily-scholar-profile
description: Build a validated NeuroDaily research profile from a scholar's published work and stated interests. Use when asked to create or update a NeuroDaily configuration for a named researcher, PI, author, ORCID, PubMed author, or Google Scholar identity; collects ORCID/OpenAlex/PubMed evidence, infers disciplines, keywords, journals, and search rules, then exports one portable neurodaily.profile JSON.
---

# NeuroDaily Scholar Profile

Create a portable NeuroDaily profile from a scholar's **published record**, not from guesswork.

## When to use

Use this skill when the user asks to:

- create a NeuroDaily profile/config for a researcher or lab PI
- turn someone's publication list into a research-interest profile
- import a scholar into NeuroDaily
- refresh an existing profile after new publications

Do **not** use it to infer sensitive personal facts, private grants, or unpublished work.

## Inputs

Minimum: a scholar name. Prefer one of:

- ORCID iD (best disambiguation)
- affiliation
- OpenAlex author ID (or several IDs when a scholar has split records)
- PubMed author name
- Google Scholar profile URL (fetch manually; this skill does not scrape Scholar)

If the name is ambiguous and no ORCID/affiliation is supplied, ask one short clarifying question before generating a profile.

## Source discovery map

Look beyond one database. Use the identity layer first, then works, then field
context:

| Direction | Examples | Why |
|---|---|---|
| Identity | ORCID, OpenAlex, Crossref, Semantic Scholar author IDs | disambiguation |
| Biomedical papers | PubMed, Europe PMC, publisher pages | DOI/PMID, MeSH, affiliations |
| Preprints | bioRxiv, medRxiv, arXiv, SSRN, Research Square | current work |
| Clinical / regulatory | ClinicalTrials.gov, WHO ICTRP, FDA, EMA | trials and approvals |
| Funding | NIH RePORTER, CORDIS, UKRI, NSFC, institutional pages | grants and lab focus |
| IP / translation | USPTO, EPO/Espacenet, Google Patents | patents and technology transfer |
| Data / software | Zenodo, Figshare, Dryad, GEO, OpenNeuro, GitHub | data/software outputs |
| Human context | institutional profile, lab site, CV, Google Scholar | current role and missed papers |

Full query examples and fallback rules:
[`references/source-discovery.md`](references/source-discovery.md).

Never merge author records on name alone. Anchor with ORCID, DOI/PMID,
affiliation and coauthors; record every source URL and identifier.

## Workflow

### 1. Collect public evidence

```bash
python scripts/collect_scholar.py \
  --name "Scholar Name" \
  --orcid 0000-0000-0000-0000 \
  --affiliation "University" \
  --author-id A1234567890 \
  --author-id A0987654321 \
  --out evidence.json
```

The script queries ORCID public API, OpenAlex, and falls back to PubMed. Repeat
`--author-id` to merge split OpenAlex records **only after confirming they are the
same person**. It writes works, journals, concepts, and source URLs. Never invent a
publication.

Review the evidence:

- top 10 works and journals
- top concepts/keywords
- any `warnings` or ambiguous author candidates

### 2. Generate the profile

```bash
python scripts/build_profile.py evidence.json \
  --name "Scholar Name" \
  --domain psychiatry \
  --mode interests \
  --exclude pediatric --exclude anticancer \
  --out neurodaily-profile.json
```

- `--mode interests` (default) builds a topic query from inferred interests.
- `--mode author` builds an author-tracking query (`AU="Name"`).
- `--domain` overrides auto-detection: `forestry`, `neuroscience`,
  `oncology`, `psychiatry`, `general`.
- `--exclude` adds an `AND NOT (...)` cleanup clause.
- `--query` supplies an explicit query and overrides generated queries.
- `--no-field-journals` disables the curated field-leading catalog (author-only view).
- `--journals-limit` defaults to 20.

This emits the NeuroDaily single-JSON format:

```json
{"format": "neurodaily.profile", "version": 1, "config": { ... }}
```

The profile includes:

- `disciplines[]` inferred from repeated concepts
- `global_keywords`
- top journals from **both** the scholar's record and a curated field-leading
  catalog (with RSS for known environment/forestry journals); at least 25% of
  slots are reserved for the scholar's own journals
- a domain-aware `search` block
- source presets: forestry disables arXiv/bioRxiv/trials/policy; neuroscience
  enables the full stack. Psychiatry enables FDA drug/device sources for the
  industry bucket.
- `policy_feeds` for psychiatry/neuroscience; enabling policy without feeds
  produces no policy/news section
- default windows

## Supported domains

| Domain | Source preset | Query style |
|---|---|---|
| `forestry` | journal + PubMed; arXiv/bioRxiv/trials/policy off | Loess / soil erosion / vegetation restoration / afforestation / forest hydrology |
| `neuroscience` | journal + PubMed + arXiv + bioRxiv + trials + policy | inferred concepts |
| `oncology` | journal + PubMed + bioRxiv + trials + policy | inferred concepts |
| `psychiatry` | journal + PubMed + bioRxiv + trials + policy + FDA drug/device | depression / PTSD / TMS / neuromodulation |
| `general` | journal + PubMed + arXiv + bioRxiv | inferred concepts |

Domain detection scores word-boundary concept hits (so `plant` does not match
`implant`, and `neuro` does not match `neuromodulation`) and falls back to
`general`; verify the chosen domain before import. The field catalog is an editorial starting point, **not** an official
JCR/CAS ranking. See [`references/top-journals.md`](references/top-journals.md).

## Case study

[`examples/nolan-williams/`](examples/nolan-williams/) is a real public-metadata
case study: Nolan Williams (Stanford University, ORCID `0000-0003-4368-3203`).
The generated psychiatry/neuromodulation profile validates in NeuroDaily.

## Profile data structure

The output is a wrapper:

```json
{"format": "neurodaily.profile", "version": 1, "config": { ... }}
```

`config` contains `profile`, `disciplines`, `global_keywords`, `search`,
`sources`, `windows`, `policy_feeds`, and `journals`. See
[`references/profile-contract.md`](references/profile-contract.md) for every
field. No SMTP/API keys or recipient addresses are included.

Do not hand-edit in invented journals or metrics. If the evidence is thin, say so and keep fewer disciplines.

### 3. Validate

Use the strict config validator, not a bare JSON parser:

```bash
python scripts/validate.py neurodaily-profile.json
```

It reports exact JSON syntax errors and schema/type/enum/URL problems such as
`sources.policy.feed_kinds[...]` or `journals[2].url` instead of a generic
"invalid config". The older `validate_profile.py` remains available for
compatibility.

If NeuroDaily is installed, also run:

```bash
neurodaily profile validate neurodaily-profile.json
neurodaily profile doctor neurodaily-profile.json
```

Fix every error before presenting the profile.

### 4. Present for human review

Show:

- scholar identity and source URLs
- 3–6 inferred research interests
- top journals and why they were chosen
- uncertainty/warnings
- the output path
- import command:

```bash
neurodaily profile import neurodaily-profile.json --name scholar-slug
```

Never claim the profile is "the scholar's official interests". It is an **evidence-derived draft** that the researcher must review.

## Rules

- Use only public metadata.
- Cite the source of every inferred interest in the evidence summary.
- Do not fabricate publications, journal names, metrics, or MeSH terms.
- Keep the output free of API keys, email passwords, SMTP settings, and private notes.
- Prefer fewer, stronger interests over a long noisy list.
- If ORCID/OpenAlex disagree, keep both and flag the conflict.
- Merge multiple OpenAlex IDs only after an explicit identity check.
- Run the actual NeuroDaily `profile validate` and `profile doctor` when available.
- A profile with no evidence must fail validation rather than silently producing generic keywords.
- Do not present the field-journal catalog as a formal JCR/CAS ranking.
- Always keep the scholar's own journals in the profile when slots allow.

## Files

- `scripts/collect_scholar.py` — ORCID/OpenAlex/PubMed evidence collector
- `scripts/build_profile.py` — evidence → NeuroDaily profile
- `scripts/field_journals.py` — curated field-leading journals
- `scripts/validate.py` — strict JSON/schema/config validation with field paths
- `scripts/validate_profile.py` — legacy structural validation
- `references/profile-contract.md` — NeuroDaily profile format and mapping rules
- `references/interest-inference.md` — how to infer disciplines/keywords
- `references/top-journals.md` — field-journal catalog and its limits
- `references/source-discovery.md` — broader public source discovery playbook
- `examples/` — sample evidence and output

## Suggested supporting skills

- `academic-search` for extra paper/citation lookup
- `orcid` / `pubmed` MCP tools when available
- `verification-before-completion` before declaring a profile ready
