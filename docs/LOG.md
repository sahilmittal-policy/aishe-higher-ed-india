# Project log

Append a dated entry each working session. Newest at the top.

Record: what was done, what was verified, what is still open, and anything
surprising found in the data. The "open" items are what you read first when
you come back.

---

## 2026-09-16

**Done**
- Created repository with full research-compendium structure.
- Confirmed all four uploaded AISHE workbooks (2019-20, 2021-22, 2022-23,
  2023-24) parse and reconcile on Table 43.

**Verified**
- Table 43 All India grand totals match published figures for all five
  reference years in the 2023-24 report.
- 220 state-years appear in two or more reports; all agree exactly.

**Open**
- 2020-21 workbook downloaded locally but not yet added to `data/raw/`.
- 2018-19 exists only as PDF. Back-series in the 2019-20 report covers
  2015-16 to 2019-20, so the workbook is not required for the panel.
- Ph.D. enrolment rises 47% between 2022-23 and 2023-24. Cause unknown.
  Query to AISHE cell not yet sent.

**Notes**
- Panel runs 2015-16 to 2023-24 (nine years) using only the 2019-20 and
  2023-24 back-series, with 2021-22 and 2022-23 as validators.

---

## 2026-09-16 (session 2)

**Done**
- Built sheet registry covering all 306 included sheets across 5 workbooks,
  mapped to 66 stable table_ids.
- Dumped every included sheet to data/interim/ as raw CSV.
- Parsed enrol_level_series (Table 43) into a verified tidy panel:
  24,260 rows, 37 states, 2015-16 to 2023-24.

**Verified**
- All India grand totals reproduce published figures for all five years.
- Male + Female = Both across 8,074 cells, no mismatches.
- Eight levels sum to Grand Total across 915 state-years.
- 256 state-years appear in 2+ reports, zero disagreement.
- 36 states sum exactly to the All India row.

**Bugs found and fixed**
- Four table_id collisions caused silent file overwrites in the dump. The
  script reported 312 writes but only 306 files existed. Caught by comparing
  reported writes against files on disk.
- 11dProgrammeOnline was labelled as the distance-mode table. Corrected.
- WomenCollege contains Table 1, not women's colleges. Relabelled.
- 2020-21 writes the merged UT as "The Dadra and Nagar Haveli and Daman and
  Diu" with a leading "The". Every report showed 37 states while the panel
  had 38. Added a distinct-state check so this fails loudly in future.

**Findings (UNVERIFIED -- do not publish yet)**
- Male enrolment falls 229,197 in 2023-24; female rises 598,058. First male
  decline in the series. Male growth: +8.1%, +6.3%, +1.3%, -1.0%.
- Ph.D. enrolment up 47% in one year (233,422 to 343,559) against 0.83%
  overall growth. Unexplained.
- M.Phil. down 91% over five years. Consistent with NEP 2020 discontinuation.
- Certificate enrolment swings 160k / 156k / 77k / 150k / 209k. Too unstable
  to be real. Treat as unreliable.
- UG enrolment fell ~93,000 in 2023-24; UG is ~77% of total.

**Open**
- Male decline is NOT publishable yet. Must parse response_rate first and
  test whether declines track falling institutional response.
- Query to AISHE cell about the Ph.D. jump still not sent.
- Decide whether to refactor shared parser code before table 45.

**Notes**
- Total rows (Both / Grand Total / All India) are mostly redundant but not
  entirely: DNH&DD Ph.D. 2023-24 has Both=2, Female=2, Male missing. Do not
  delete total rows from processed files; filter at analysis time instead.
- Close Excel before running scripts that write to reference/. A
  PermissionError cost a full re-run today.
