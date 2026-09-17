"""
Fix table_id collisions in the sheet registry.

A table_id must be unique within a report. Where two sheets in the same
workbook were given the same table_id, the dump script silently overwrote
one with the other -- so some interim CSVs were missing.

Four collisions found and resolved here:

1. 11dProgrammeOnline (2022-23) was labelled as the distance-mode table.
   It is the ONLINE mode table. Relabelled.

2. WomenCollege is Table 1 (universities by specialisation). The sheet named
   2University-Specialisation is Table 2 -- a different cut of similar data.
   Both are real, so WomenCollege gets its own id.

3. '4CollegeIndicator (2)' is a shorter duplicate of '4CollegeIndicator'.
   Excluded.

4. 'ManagementCollegeNo (2)' is a shorter duplicate of '5ManagementCollegeNo'.
   Excluded.

Run from the repository root:

    python analysis/00b_fix_registry_collisions.py
"""

from pathlib import Path

import pandas as pd

REGISTRY_PATH = Path("reference/sheet_registry.csv")

registry = pd.read_csv(REGISTRY_PATH).fillna("")

# Work on the stripped sheet name for matching, but never write the stripped
# version back -- the registry must record the sheet name exactly as stored.
sheet = registry["sheet_name"].str.strip()


# --- Fix 1: online mode mislabelled as distance ----------------------------

mask = sheet == "11dProgrammeOnline"
registry.loc[mask, "table_id"] = "enrol_programme_social_online"
registry.loc[mask, "description"] = "Programme x social group enrolment, online mode"
registry.loc[mask, "notes"] = "Was mislabelled as distance mode; corrected"
print(f"Fix 1: relabelled {mask.sum()} row(s) to enrol_programme_social_online")


# --- Fix 2: WomenCollege is Table 1, not Table 2 ---------------------------

mask = sheet == "WomenCollege"
registry.loc[mask, "table_id"] = "university_specialisation_t1"
registry.loc[mask, "notes"] = (
    "SHEET NAME MISLEADING: contains Table 1, universities by specialisation. "
    "Distinct from Table 2 in 2University-Specialisation"
)
print(f"Fix 2: relabelled {mask.sum()} row(s) to university_specialisation_t1")


# --- Fix 3 and 4: exclude the duplicate '(2)' sheets -----------------------

mask = sheet.isin(["4CollegeIndicator (2)", "ManagementCollegeNo (2)"])
registry.loc[mask, "include"] = "no"
registry.loc[mask, "table_id"] = ""
registry.loc[mask, "description"] = ""
registry.loc[mask, "notes"] = "Shorter duplicate of the main sheet; excluded"
print(f"Fix 3/4: excluded {mask.sum()} duplicate sheet(s)")


# --- Verify no collisions remain -------------------------------------------

included = registry[registry["include"] == "yes"]
collisions = included[included.duplicated(["table_id", "report"], keep=False)]

if len(collisions):
    print("\nREMAINING COLLISIONS -- do not proceed:")
    print(collisions[["report", "sheet_name", "table_id"]].to_string(index=False))
    raise SystemExit(1)

print(f"\nNo collisions remain.")
print(f"Included sheets: {len(included)}")
print(f"Distinct table_ids: {included['table_id'].nunique()}")

registry.to_csv(REGISTRY_PATH, index=False, encoding="utf-8")
print(f"Registry updated: {REGISTRY_PATH}")