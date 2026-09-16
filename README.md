# Higher Education in India: Evidence from AISHE, 2015-16 to 2023-24

A research compendium analysing India's All India Survey on Higher Education
(AISHE). Contains the full pipeline from raw published spreadsheets through
cleaned data and analysis to written outputs.

**Status:** in development.

## Contents

| Path | Contents |
|---|---|
| `data/` | Raw AISHE workbooks and cleaned derivatives |
| `src/aishe/` | Extraction and cleaning package |
| `tests/` | Verification against published totals |
| `analysis/` | Scripts producing every cited result |
| `outputs/` | Generated tables and figures |
| `writing/` | Policy memo, article, conference paper |
| `docs/` | Methodology, data dictionary, known data issues |

## Reproducing

Every figure and table is generated from the raw files in `data/raw/`.
Nothing in `outputs/` is edited by hand.

## Source

All India Survey on Higher Education, Department of Higher Education,
Ministry of Education, Government of India. https://aishe.gov.in

AISHE is a voluntary survey with self-reported institutional data. Response
rates vary considerably by state and year, and published totals are grossed
up to account for non-response. See `docs/caveats.md`.

## Licence

Code: MIT. Derived data: CC-BY-4.0. Underlying AISHE data is Government of
India material.

## Author

Sahil Mittal, Heinz College, Carnegie Mellon University.
