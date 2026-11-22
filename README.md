# NeuroDaily Scholar Profile v1.2.0

A reusable Agent Skill that turns a scholar's **public publication record** into a
validated, portable [NeuroDaily](https://github.com/Koalalive/neurodaily) research
profile.

It collects evidence from ORCID, OpenAlex and PubMed, infers disciplines,
keywords and journals, writes a single `neurodaily.profile` JSON, and validates it
before a human imports it.

## Install as a skill

Copy this repository into your Agent Skills directory:

```bash
git clone https://github.com/Koalalive/neurodaily-scholar-profile.git \
  ~/.claude/skills/neurodaily-scholar-profile
```

Or install with a skills CLI if your environment supports GitHub skill sources.

The skill is defined by [`SKILL.md`](SKILL.md); scripts are dependency-free
Python 3.10+.

## Use

Ask the agent:

> Create a NeuroDaily profile for Jane Doe, ORCID 0000-0002-1825-0097.

The skill runs:

```bash
python scripts/collect_scholar.py \
  --name "Jane Doe" \
  --orcid 0000-0002-1825-0097 \
  --out evidence.json

python scripts/build_profile.py evidence.json \
  --name "Jane Doe" \
  --domain forestry \
  --mode interests \
  --exclude pediatric --exclude anticancer \
  --out neurodaily-profile.json

python scripts/validate_profile.py neurodaily-profile.json
```

Then import it into NeuroDaily:

```bash
neurodaily profile validate neurodaily-profile.json
neurodaily profile import neurodaily-profile.json --name jane-doe
neurodaily profile doctor jane-doe
```

## Supported domains and options

`--domain` auto-detects or accepts `forestry`, `neuroscience`, `oncology`,
`psychiatry`, or `general`. Forestry profiles use PubMed + forestry journal RSS
and disable arXiv/bioRxiv/trials/policy by default; neuroscience profiles enable
the full stack.

`--mode author` creates an author-tracking query instead of an interest query.
`--exclude` adds an `AND NOT (...)` cleanup clause. `--query` supplies an explicit
query. `--no-field-journals` disables the field catalog; `--journals-limit`
defaults to 20. Use repeated `--author-id` to merge split OpenAlex records after identity
confirmation.

## What the profile contains

- `disciplines[]` inferred from repeated concepts (max 4)
- `global_keywords`
- top journals from the scholar's works **plus** a curated field-leading catalog
  (author journals get reserved slots)
- a conservative `search` block
- default sources and retrieval windows
- no SMTP/API keys or local delivery settings

See [`examples/`](examples/) for evidence and generated profile samples.

## Case study

[`examples/nolan-williams/`](examples/nolan-williams/) contains a tested profile for
Nolan Williams (Stanford University), built from ORCID
`0000-0003-4368-3203` and OpenAlex `A5074022923`. It validates and imports into
NeuroDaily; see [`TEST_REPORT.md`](examples/nolan-williams/TEST_REPORT.md) for
commands and the psychiatry/neuromodulation domain fit.

## Field-leading journals

The field catalog is editorial, not an official JCR/CAS ranking. It prevents a
profile from being limited to the scholar's own venues while still reserving slots
for those venues. See [`references/top-journals.md`](references/top-journals.md).

## Evidence and disambiguation

- ORCID is the strongest identity anchor. Use `--author-id` only when records are
  confirmed to be the same person.
- Without ORCID, OpenAlex author candidates are recorded; pass an affiliation
  when names are ambiguous.
- PubMed is only a fallback when ORCID/OpenAlex return no works.
- The output is a **draft**. A researcher should review inferred interests and
  journals before relying on it.

## Rules

- No fabricated publications, journals, metrics or MeSH terms.
- No private or sensitive personal data.
- No JCR/CAS metrics unless the user supplies an official source.
- Validation must pass before presenting the profile.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_profile.py examples/neurodaily-profile.example.json
```

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
