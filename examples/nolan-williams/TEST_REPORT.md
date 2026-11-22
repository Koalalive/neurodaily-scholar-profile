# Case study: Nolan Williams (Stanford University)

A public-metadata example for psychiatry and neuromodulation. No private data,
credentials, unpublished work or patient information is included.

| Field | Value |
|---|---|
| Name | Nolan Williams |
| Affiliation | Stanford University / Stanford Medicine |
| ORCID | `0000-0003-4368-3203` |
| OpenAlex | `A5074022923` |
| OpenAlex works count | 249 |
| Works collected | 200 (collector limit) |
| Detected domain | `psychiatry` |
| Disciplines | Transcranial Magnetic Stimulation; Deep Brain Stimulation and Movement Disorders; Major Depression; Electroconvulsive Therapy |
| Keywords | 12 |
| Journals | 20 (field leaders + author venues) |

## Commands

```bash
python scripts/collect_scholar.py \
  --name "Nolan Williams" \
  --orcid 0000-0003-4368-3203 \
  --affiliation "Stanford University" \
  --author-id A5074022923 \
  --limit 200 \
  --out examples/nolan-williams/evidence.json

python scripts/build_profile.py \
  examples/nolan-williams/evidence.json \
  --name "Nolan Williams" \
  --profile-id nolan-williams-stanford \
  --journals-limit 20 \
  --out examples/nolan-williams/profile.json

python scripts/validate_profile.py examples/nolan-williams/profile.json
```

## Result

```text
nolan-williams-stanford: 4 disciplines, 12 keywords, 20 journals
domain: psychiatry | query: depression OR PTSD OR "transcranial magnetic stimulation" OR neuromodulation OR "deep brain stimulation"
OK: nolan-williams-stanford
```

The profile also passes NeuroDaily's native validator:

```text
[neurodaily] profile OK: nolan-williams-stanford
```

## Journals

Field leaders:

- Nature, Science, PNAS, Nature Communications, Science Advances
- JAMA Psychiatry, The Lancet Psychiatry, Molecular Psychiatry,
  Biological Psychiatry, World Psychiatry, American Journal of Psychiatry,
  Nature Mental Health
- Brain Stimulation, NeuroImage, Translational Psychiatry

Author venues retained (reserved slots):

- Transcranial Magnetic Stimulation
- Journal of Clinical Psychiatry
- Journal of Affective Disorders
- npj Mental Health Research

Preprint servers and case-duplicate journal names are filtered. The field catalog
is editorial, not an official JCR/CAS ranking; see
[`references/top-journals.md`](../../references/top-journals.md).

## Notes

- The evidence contains 200 of 249 OpenAlex works, selected by the collector limit.
- Domain detection now uses word-boundary scoring, so forestry's `plant` token does
  not match `implant` in neuromodulation titles.
- Always review inferred interests and journals before importing a profile.
