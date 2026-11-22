# Field-leading journal catalog

A scholar's own publication list is evidence of **where they published**, not a
complete map of where their field's strongest work appears. The profile builder
therefore merges two sources:

1. journals observed in the scholar's works;
2. a curated field-leading catalog in `scripts/field_journals.py`.

The catalog is an **editorial starting point**, not an official JCR or CAS
ranking. Do not quote its order as a formal metric. Verify current scope and
metrics against JCR, Scopus/Scimago, or institutional lists before evaluation.

## Forestry / soil / water / ecology selection

The forestry preset draws from general flagships and field journals including:

- Nature, Science, PNAS, Nature Communications, Science Advances
- Current Forestry Reports, Nature Ecology & Evolution, Nature Climate Change,
  Nature Sustainability, Nature Water, Nature Geoscience
- Global Change Biology, Ecology Letters, Trends in Ecology & Evolution,
  Journal of Ecology
- Forest Ecology and Management, Agricultural and Forest Meteorology,
  Forest Ecosystems, Urban Forestry & Urban Greening
- Soil Biology and Biochemistry, Geoderma, CATENA, Soil and Tillage Research,
  Plant and Soil, Applied Soil Ecology
- Water Research, Water Resources Research, Journal of Hydrology,
  Hydrology and Earth System Sciences, Agricultural Water Management,
  Land Degradation & Development

## Psychiatry / neuromodulation selection

The psychiatry preset combines general flagships with clinical and translational
journals including:

- JAMA Psychiatry, The Lancet Psychiatry, Molecular Psychiatry,
  Biological Psychiatry, World Psychiatry, American Journal of Psychiatry,
  Nature Mental Health
- Author-venue examples include Brain Stimulation, Journal of Clinical Psychiatry,
  NeuroImage, Journal of Affective Disorders, Translational Psychiatry

This preset is used by the Nolan Williams case study (Stanford University,
ORCID `0000-0003-4368-3203`), whose work spans transcranial magnetic stimulation,
deep brain stimulation, depression, PTSD and electroconvulsive therapy.

## Selection logic

- Prefer journals that represent the **field's readership**, not only the
  scholar's publication history.
- Keep general flagships only when the field work can plausibly reach them.
- Reserve at least 25% of the journal slots for the scholar's own journals
  (when they are not already in the field catalog), so the profile still reflects
  their actual venue network.
- No JCR/CAS/IF values are invented. Journal metrics remain empty unless the user
  supplies an official source.
- Disable the catalog with `--no-field-journals` when a strict author-only view is
  required.

## Sources consulted

- OOIR journal rankings (Forestry, Soil Science, Water Resources, Ecology,
  Psychiatry)
- SCImago Journal & Country Rank subject categories
- Google Scholar Metrics (Soil Sciences, Hydrology, Ecology, Psychiatry)
- Research.com ecology/hydrology/psychiatry journal rankings
- Publisher journal scopes and RSS endpoints (Elsevier, Wiley, Nature, Springer,
  Copernicus)

These are complementary signals; they do not always agree. Re-check before using a
journal in a formal review or promotion packet.
