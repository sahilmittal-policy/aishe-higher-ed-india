# To do

Move items to Done when finished. Delete nothing -- the Done list is the
record of what got built.

## Next
- [ ] Decide: extract shared parser code to src/aishe/, or copy per table
- [ ] Parse enrol_social_series (Table 45, caste back-series)
- [ ] Parse response_rate (Table 1a) -- needed to test the male-decline finding
- [ ] Add is_total column to the parser output

## Later
- [ ] Email AISHE cell about the Ph.D. jump
- [ ] Parse remaining back-series tables (46, 47, 48, 49)
- [ ] Parse single-year status tables for the 2023-24 chapter
- [ ] Decide whether to extract Table 1a from the 2018-19 PDF
- [ ] Write docs/caveats.md

## Done
- [x] Create repository structure
- [x] Add raw AISHE workbooks with manifest and checksums
- [x] Build sheet registry: 306 sheets mapped to 66 table_ids
- [x] Fix four table_id collisions causing silent overwrites
- [x] Dump all included sheets to interim CSVs
- [x] Parse enrol_level_series, all five checks passing
