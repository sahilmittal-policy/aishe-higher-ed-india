# Verification ledger

Every extracted table gets a row. A table is not usable in analysis or
writing until its row reads PASS.

Checks applied:
- **Totals**: does the parsed All India total match the published figure?
- **Internal**: do components sum to their stated totals?
- **Cross-report**: where two reports cover the same year, do they agree?
- **Coverage**: are all 36 states/UTs plus All India present, and is the
  distinct-state count across the whole panel exactly 37?

| Table | Description | Totals | Internal | Cross-report | Coverage | Status |
|---|---|---|---|---|---|---|
| enrol_level_series | Enrolment by level and sex, 2015-16 to 2023-24 | PASS | PASS | PASS | PASS | **PASS** |
| enrol_social_series | SC/ST/OBC enrolment back-series | — | — | — | — | not started |
| enrol_minority_series | Muslim, minority, PwBD, EWS back-series | — | — | — | — | not started |
| response_rate | Institutional response rates by state | — | — | — | — | not started |
| ger_series | Gross enrolment ratio back-series | — | — | — | — | not started |
| gpi_series | Gender parity index back-series | — | — | — | — | not started |
| population_projection | Population 18-23, GER denominator | — | — | — | — | not started |
| outturn_social_state | Graduates by social group | — | — | — | — | not started |
| teacher_social_state | Teachers by social group | — | — | — | — | not started |

## enrol_level_series detail

- 24,260 rows, 37 states, 9 reference years, 5 report vintages.
- All India grand totals reproduce published figures for all five years.
- Male + Female = Both across 8,074 cells, zero mismatches.
- Eight levels sum to Grand Total across 915 state-years, zero off by >0.5%.
- 256 state-years appear in two or more reports, zero disagreement.
- The 36 states sum exactly to the All India row.
