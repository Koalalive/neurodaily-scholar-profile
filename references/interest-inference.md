# Interest inference rules

The goal is a **defensible draft**, not a personality profile.

## Evidence hierarchy

1. ORCID works (identity anchor)
2. OpenAlex works (journal and concept metadata)
3. PubMed fallback (only when the first two return no works)

Use repeated concepts across independent works. A single paper is not a research
program. Prefer concepts that appear in at least two works; if the record is
small, label the output as low-confidence.

## What becomes what

| Profile field | Evidence |
|---|---|
| `disciplines[].name` | Top distinct concepts, at most 4 |
| `disciplines[].keywords` | The concept plus close variants |
| `disciplines[].arxiv_cats` | Known field map (e.g. neuroscience → `q-bio.NC`) |
| `disciplines[].mesh_terms` | Known field map; leave empty rather than invent |
| `global_keywords` | Up to 12 repeated concepts |
| `journals` | Journals with the most works |
| `search.query` | The strongest single concept |
| `search.journals` | Top journals, used as a preference list |

## Never infer

- JCR/CAS metrics without an official import
- Unpublished grants, private funding, or personal facts
- MeSH terms solely because they sound related
- A different scholar with the same name without disambiguation

## Handling ambiguity

If OpenAlex returns multiple plausible authors:

1. Prefer ORCID.
2. Otherwise prefer an exact name + affiliation match.
3. If still ambiguous, stop and ask the user for ORCID/affiliation.
4. Record candidates and warnings in evidence JSON.

## Quality gates

- Profile has works, at least one discipline, and keywords.
- Every journal name appears in the evidence.
- No secret fields.
- Validation and, when available, `neurodaily profile doctor` pass.
