"""
Dump every included sheet from the AISHE workbooks to CSV.

This reads reference/sheet_registry.csv, and for every row marked
include = yes, writes that sheet out as a CSV named by its stable table_id.

The output is NOT tidy data. It is the raw cell grid exactly as it sits in
Excel, headers and merged-cell blanks included. The point is to get out of
Excel once and for all, so that every later step is a plain pandas problem.

Run from the repository root:

    python analysis/01_dump_sheets.py

Output: data/interim/{table_id}__{report}.csv
"""

from pathlib import Path

import pandas as pd

# --- Paths -----------------------------------------------------------------
# Defined once at the top so there is a single place to change them.

REGISTRY_PATH = Path("reference/sheet_registry.csv")
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/interim")


# --- Load the registry -----------------------------------------------------

registry = pd.read_csv(REGISTRY_PATH)

# Blank cells arrive from CSV as NaN. Converting to empty strings lets us
# compare with == "" instead of having to use pd.isna() everywhere.
registry = registry.fillna("")

# Keep only the sheets we decided are real data.
registry = registry[registry["include"] == "yes"]

print(f"Registry: {len(registry)} sheets marked for inclusion")

# Make sure the output folder exists. parents=True creates any missing
# parent folders; exist_ok=True means it won't complain if it already exists.
OUT_DIR.mkdir(parents=True, exist_ok=True)


# --- Dump each sheet -------------------------------------------------------

written = 0
failed = []

# Group by report so we open each workbook once rather than once per sheet.
# Opening a 60-sheet Excel file 60 separate times is slow; this is much faster.
for report, rows in registry.groupby("report"):

    workbook_path = RAW_DIR / f"AISHE_Final_Report_{report}.xlsx"

    if not workbook_path.exists():
        print(f"  MISSING WORKBOOK: {workbook_path}")
        continue

    # ExcelFile holds the opened workbook so repeated reads reuse it.
    excel_file = pd.ExcelFile(workbook_path)

    print(f"\n{report}: {len(rows)} sheets")

    for _, row in rows.iterrows():

        sheet_name = row["sheet_name"]
        table_id = row["table_id"]

        # A row marked include = yes with no table_id is a registry error.
        # Skip it and report at the end rather than writing a file called
        # "__2023-24.csv".
        if table_id == "":
            failed.append((report, sheet_name, "no table_id"))
            continue

        try:
            # header=None is essential. AISHE header blocks are 3-4 rows deep
            # and inconsistent, so we take every cell as data and deal with
            # the headers later, in code, where it is visible and testable.
            #
            # sheet_name is passed EXACTLY as the registry stores it, including
            # any trailing spaces. pandas matches sheet names exactly, so
            # stripping it here would cause a lookup failure.
            sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

        except Exception as error:
            failed.append((report, sheet_name, str(error)))
            continue

        # Two underscores separate table_id from report, because table_id
        # already contains single underscores. This keeps the filename
        # splittable back into its two parts later.
        out_path = OUT_DIR / f"{table_id}__{report}.csv"

        # index=False so pandas' row numbers don't become a stray unnamed
        # column. utf-8 so the file opens correctly on any operating system.
        sheet.to_csv(out_path, index=False, header=False, encoding="utf-8")

        written += 1
        print(f"  {table_id:38s} {sheet.shape[0]:>4} x {sheet.shape[1]:>3}")


# --- Report ----------------------------------------------------------------

print(f"\n{'='*60}")
print(f"Wrote {written} files to {OUT_DIR}")

if failed:
    print(f"\n{len(failed)} sheets failed:")
    for report, sheet_name, reason in failed:
        print(f"  {report}  {sheet_name!r}  -- {reason}")
else:
    print("No failures.")