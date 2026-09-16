import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")

OUT_PATH = Path("reference/sheet_registry_skeleton.csv")

files = sorted(RAW_DIR.glob("*.xlsx"))

print(f"Found {len(files)} workbooks")

for f in files:
    print("  ", f.name)

# Matches a year label like "2020-21" anywhere in the filename.
YEAR_PATTERN = re.compile(r"(\d{4}-\d{2})")


def report_year(path):
    """Extract the report year from a workbook filename.

    'AISHE_Final_Report_2020-21.xlsx' -> '2020-21'
    """
    match = YEAR_PATTERN.search(path.name)
    if match is None:
        raise ValueError(f"No year found in filename: {path.name}")
    return match.group(1)

# Matches digits at the START of a sheet name, allowing leading whitespace.
TABLE_PATTERN = re.compile(r"^\s*(\d+)")


def guess_table_number(sheet_name):
    """Guess the AISHE table number from a sheet name.

    '43ENRLT 6'   -> '43'
    '1a.InsResponse' -> '1'
    'Cover'       -> '' (no leading number)

    This is only a hint. The authoritative table_id is assigned by hand
    in the registry.
    """
    match = TABLE_PATTERN.match(sheet_name)
    return match.group(1) if match else ""

# Collect one dictionary per sheet. We build a list first and convert to a
# DataFrame at the end -- appending to a DataFrame row by row is slow and
# awkward, whereas building a list is neither.
rows = []

for path in files:
    year = report_year(path)

    # ExcelFile reads only the workbook structure, not the cell data, so
    # this is fast even though the files are large.
    xl = pd.ExcelFile(path)

    for sheet in xl.sheet_names:
        rows.append({
            "report": year,
            "sheet_name": sheet,          # exactly as stored, spaces included
            "table_no_guess": guess_table_number(sheet),
            "table_id": "",               # to be filled in by hand
            "description": "",            # to be filled in by hand
            "include": "",                # yes / no, filled in by hand
            "notes": "",                  # filled in by hand
        })

    print(f"  {year}: {len(xl.sheet_names)} sheets")


registry = pd.DataFrame(rows)

# Make sure the output folder exists. parents=True creates intermediate
# folders; exist_ok=True stops it erroring if it's already there.
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# index=False because pandas' row numbers aren't data and would just be
# a stray unnamed column in the CSV.
registry.to_csv(OUT_PATH, index=False)

print(f"\nWrote {len(registry)} rows to {OUT_PATH}")