# Source discovery playbook

Use **multiple public indexes**, not one search box. A profile is only as good as
the identity and works it is built from.

## Identity first

| Source | Best use | Anchor |
|---|---|---|
| ORCID | canonical identity, employment, works | `https://pub.orcid.org/v3.0/{id}/works` |
| OpenAlex | works, concepts, citations, split author records | `api.openalex.org/authors?search=` |
| Crossref | DOI metadata, publisher records, ORCID links | `api.crossref.org/works?query.author=` |
| Semantic Scholar | citation graph, related papers, author IDs | `api.semanticscholar.org/graph/v1/author/search` |
| PubMed / Europe PMC | biomedical papers, MeSH, affiliations | E-utilities / `europepmc.org` |
| Google Scholar | broad coverage and citation counts | manual browser check; do not scrape |
| ORCID + institutional profile | current affiliation, lab, CV | university profile / lab page |

Prefer ORCID. If the name is ambiguous, use affiliation + coauthors + DOI/PMID
anchors; never merge OpenAlex records on name alone.

## Work sources

- Publisher pages and journal RSS (Nature, Elsevier, Wiley, Springer, Cell)
- PubMed, Europe PMC, Crossref
- bioRxiv, medRxiv, arXiv, SSRN, Research Square
- ClinicalTrials.gov and WHO ICTRP
- NIH RePORTER, CORDIS, UKRI, NSFC and institutional grant pages
- USPTO, EPO/Espacenet, Google Patents
- Zenodo, Figshare, Dryad, GEO, ArrayExpress, OpenNeuro
- GitHub and software releases when software is part of the research output
- Conference proceedings and society abstracts

Record the **source URL and identifier** for every work. A DOI/PMID is stronger
than a title match.

## Search order

1. ORCID works and employment.
2. OpenAlex author record(s), including split records.
3. Crossref/PubMed/Europe PMC fill gaps and resolve DOI/PMID.
4. Semantic Scholar for citation neighbors and missed papers.
5. Manual check of institutional profile, lab site, CV and Google Scholar.
6. Use preprints/trials/patents/datasets only when they are part of the record.

## What to tell the user

- which identity anchors were used;
- which sources were unavailable or rate-limited;
- which records are uncertain and why;
- that the result is an evidence-derived draft, not an official CV.

## Safety

Use public metadata only. Do not collect private grants, unpublished manuscripts,
patient data, personal addresses, or credentials. Do not automate Google Scholar
in violation of its terms; use it for a manual cross-check.
