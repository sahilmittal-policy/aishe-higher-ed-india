"""
Parse enrol_level_series (AISHE Table 43) into tidy long format.

Table 43 is a back-series table: each report restates the previous five
years. Combining all five reports gives a 2015-16 to 2023-24 panel, with
overlapping years acting as a cross-check on the parser.

SOURCE LAYOUT
-------------
The sheet is not one row per state. It is a block per state:

    row:  All India        <- state header, data cells blank
    row:  2023-24          <- data
    row:  2022-23          <- data
    ...five year rows...
    row:  A & N Islands    <- next state header
    row:  2023-24          <- data

One column carries both state names and year labels, so the state name has
to be carried downward as we walk the rows.

The 2019-20 workbook has no "Sl. No." column, so it is 28 columns wide while
every later report is 29. We handle that by anchoring on the RIGHT edge:
there are always 27 data columns (9 levels x 3 sexes), so data begins at
column (n_columns - 27) regardless of what sits to the left.

OUTPUT
------
data/processed/enrol_level_series.csv, one row per observation:

    report | state | state_raw | ref_year | level | sex | value | is_estimated

Run from the repository root:

    python analysis/02_parse_enrol_level_series.py
"""

import re
from pathlib import Path

import pandas as pd

# --- Paths -----------------------------------------------------------------

INTERIM_DIR = Path("data/interim")
OUT_PATH = Path("data/processed/enrol_level_series.csv")

TABLE_ID = "enrol_level_series"


# --- Table shape -----------------------------------------------------------
# The 27 data columns are always in this order: for each level, Male, Female,
# Both. This ordering is what lets us unpack position i into level i // 3 and
# sex i % 3.

LEVELS = [
    "Ph.D.",
    "M.Phil.",
    "PG",
    "UG",
    "PG Diploma",
    "Diploma",
    "Certificate",
    "Integrated",
    "Grand Total",
]
SEXES = ["Male", "Female", "Both"]

N_DATA_COLS = len(LEVELS) * len(SEXES)   # 27


# --- Patterns --------------------------------------------------------------

# A reference year label such as "2019-20". Anchored at both ends so that a
# stray string merely containing a year does not match.
YEAR_RE = re.compile(r"^\s*(\d{4}-\d{2})\s*$")

# Rows whose label is one of these are header furniture, not states.
HEADER_LABELS = {
    "state/uts",
    "states/uts",
    "state/ut",
    "sl. no.",
    "sl.\nno.",
    "sl no",
    "state",
}


# --- State canonicalisation ------------------------------------------------
# AISHE spells several states differently between reports, and not
# consistently in one direction -- "A & N Islands" appears in some reports
# and "Andaman and Nicobar Islands" in others, flipping back and forth.
#
# Dadra & Nagar Haveli and Daman & Diu were separate UTs until the January
# 2020 merger. Both old names map to the merged entity, and the rows are
# summed later, so the series has no artificial discontinuity.

STATE_CANON = {
    "a & n islands": "Andaman & Nicobar Islands",
    "a&n islands": "Andaman & Nicobar Islands",
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar": "Andaman & Nicobar Islands",
    "d & n haveli and daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "d & n haveli & daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    # The 2020-21 report writes the merged UT with a leading "The".
    "the dadra and nagar haveli and daman and diu":
        "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu":
        "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "india": "All India",
    "all india": "All India",
    "chhatisgarh": "Chhattisgarh",
    "jammu and kashmir": "Jammu & Kashmir",
    "jammu & kashmir": "Jammu & Kashmir",
    "delhi": "Delhi",
    "nct of delhi": "Delhi",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "odisha": "Odisha",
    "orissa": "Odisha",
}


def canonical_state(raw):
    """Map a raw spreadsheet state label to a canonical name."""
    key = str(raw).strip().lower()
    key = re.sub(r"\s+", " ", key)          # collapse runs of whitespace
    key = key.replace("\n", " ").strip()
    return STATE_CANON.get(key, str(raw).strip())


# --- Locating the label column ---------------------------------------------

def find_label_column(frame):
    """Return the index of the column holding state names and year labels.

    We do not assume a position, because the 2019-20 workbook lacks the
    "Sl. No." column that later reports have. Instead we look for the column
    containing many year labels -- that is necessarily the label column,
    since the stacked layout puts years and state names in the same column.
    """
    best_column = None
    best_count = 0

    # Only the leftmost few columns are plausible candidates.
    for column in range(min(4, frame.shape[1])):
        values = frame[column].dropna().astype(str)
        count = values.apply(lambda v: bool(YEAR_RE.match(v))).sum()
        if count > best_count:
            best_count = count
            best_column = column

    if best_column is None or best_count < 5:
        raise ValueError("Could not locate the label column: too few year labels")

    return best_column


# --- Parsing one report ----------------------------------------------------

def parse_report(path, report):
    """Parse one interim CSV into tidy rows."""
    frame = pd.read_csv(path, header=None)

    label_column = find_label_column(frame)

    # Right-anchor the data block. There are always 27 data columns, so
    # whatever sits to the left -- with or without a serial number column --
    # does not matter.
    first_data_column = frame.shape[1] - N_DATA_COLS
    if first_data_column < 0:
        raise ValueError(
            f"{report}: only {frame.shape[1]} columns, need at least {N_DATA_COLS}"
        )

    rows = []
    current_state = None
    n_data_rows = 0

    for position in range(len(frame)):
        label = frame.iloc[position, label_column]

        if pd.isna(label):
            continue

        label = str(label).strip()
        if not label:
            continue

        year_match = YEAR_RE.match(label)

        if year_match:
            # A data row, belonging to whichever state header we last saw.
            if current_state is None:
                continue

            ref_year = year_match.group(1)
            block = frame.iloc[position, first_data_column:].tolist()
            n_data_rows += 1

            for index, raw_value in enumerate(block):
                value = pd.to_numeric(raw_value, errors="coerce")

                # A blank cell means AISHE published nothing for that
                # combination. We drop it rather than recording a zero,
                # because "not reported" and "zero students" are different
                # facts and conflating them would distort every average.
                if pd.isna(value):
                    continue

                rows.append({
                    "report": report,
                    "state_raw": current_state,
                    "state": canonical_state(current_state),
                    "ref_year": ref_year,
                    # Integer division gives the level, remainder gives the
                    # sex, because the 27 columns run level by level in
                    # Male / Female / Both triplets.
                    "level": LEVELS[index // 3],
                    "sex": SEXES[index % 3],
                    "value": float(value),
                    # AISHE grosses figures up for non-response, which leaves
                    # non-integer values. Whole numbers were reported directly.
                    "is_estimated": abs(value - round(value)) > 1e-9,
                })

        else:
            # Not a year, so either a state header or header furniture.
            if label.lower() in HEADER_LABELS:
                continue
            if re.fullmatch(r"[\d\s.]+", label):
                # The column-number row: "1", "2", "3"...
                continue
            if "table" in label.lower():
                continue
            if not any(character.isalpha() for character in label):
                continue

            current_state = label

    print(f"  {report}: {n_data_rows:>3} data rows -> {len(rows):>6,} observations")
    return pd.DataFrame(rows)


# --- Parse every report ----------------------------------------------------

paths = sorted(INTERIM_DIR.glob(f"{TABLE_ID}__*.csv"))

if not paths:
    raise SystemExit(
        f"No interim files found for {TABLE_ID}. "
        "Run analysis/01_dump_sheets.py first."
    )

print(f"Parsing {len(paths)} reports\n")

frames = []
for path in paths:
    # Filename format is "{table_id}__{report}.csv", so splitting on the
    # double underscore recovers the report year.
    report = path.stem.split("__")[1]
    frames.append(parse_report(path, report))

tidy = pd.concat(frames, ignore_index=True)


# --- Merge the split union territories --------------------------------------
# In 2019-20, Dadra & Nagar Haveli and Daman & Diu are separate rows that now
# share a canonical name. Summing them makes the series continuous. For every
# other state this groupby is a no-op, since each group holds one row.

before = len(tidy)

tidy = (
    tidy
    .groupby(["report", "state", "ref_year", "level", "sex"], as_index=False)
    .agg(
        value=("value", "sum"),
        is_estimated=("is_estimated", "max"),
        state_raw=("state_raw", lambda names: " + ".join(sorted(set(names)))),
    )
)

print(f"\nMerged split UTs: {before:,} rows -> {len(tidy):,} rows")

tidy = tidy[[
    "report", "state", "state_raw", "ref_year",
    "level", "sex", "value", "is_estimated",
]]
tidy = tidy.sort_values(["report", "state", "ref_year", "level", "sex"])


# --- Verification ----------------------------------------------------------
# Nothing is written unless every check passes. A parser that emits a file
# you cannot trust is worse than one that fails loudly.

print("\n" + "=" * 62)
print("VERIFICATION")
print("=" * 62)

failures = []

# Check 1: published All India grand totals.
# These are the figures the Ministry printed. Reproducing them from the raw
# cells is the strongest evidence that we are reading the right columns.
PUBLISHED_TOTALS = {
    "2019-20": 38_536_359,
    "2020-21": 41_380_713,
    "2021-22": 43_268_181,
    "2022-23": 44_632_261,
    "2023-24": 45_001_123,
}

print("\n1. All India grand totals (from the latest report covering each year)")
national = tidy[
    (tidy["state"] == "All India")
    & (tidy["level"] == "Grand Total")
    & (tidy["sex"] == "Both")
]

for ref_year, expected in PUBLISHED_TOTALS.items():
    matching = national[national["ref_year"] == ref_year]
    if matching.empty:
        print(f"   {ref_year}  NOT FOUND")
        failures.append(f"missing total for {ref_year}")
        continue

    # Use the most recent report covering this year.
    actual = matching.sort_values("report")["value"].iloc[-1]
    ok = abs(actual - expected) < 1
    print(
        f"   {ref_year}  parsed {actual:>16,.0f}   "
        f"published {expected:>12,}   {'PASS' if ok else 'FAIL'}"
    )
    if not ok:
        failures.append(f"total mismatch for {ref_year}")

# Check 2: Male + Female = Both.
print("\n2. Male + Female = Both")
wide = tidy.pivot_table(
    index=["report", "state", "ref_year", "level"],
    columns="sex",
    values="value",
)
wide = wide.dropna(subset=["Male", "Female", "Both"])
mismatches = (abs(wide["Male"] + wide["Female"] - wide["Both"]) > 1).sum()
print(f"   {len(wide):,} cells checked, {mismatches} mismatches "
      f"{'PASS' if mismatches == 0 else 'FAIL'}")
if mismatches:
    failures.append(f"{mismatches} sex-total mismatches")

# Check 3: the eight levels sum to Grand Total.
print("\n3. Levels sum to Grand Total")
components = tidy[(tidy["sex"] == "Both") & (tidy["level"] != "Grand Total")]
summed = components.groupby(["report", "state", "ref_year"])["value"].sum()
totals = (
    tidy[(tidy["sex"] == "Both") & (tidy["level"] == "Grand Total")]
    .set_index(["report", "state", "ref_year"])["value"]
)
comparison = pd.concat(
    [summed.rename("sum_of_levels"), totals.rename("grand_total")], axis=1
).dropna()
gap_pct = (
    (comparison["sum_of_levels"] - comparison["grand_total"])
    / comparison["grand_total"] * 100
)
off = (abs(gap_pct) > 0.5).sum()
print(f"   {len(comparison):,} state-years checked, {off} off by more than 0.5% "
      f"{'PASS' if off == 0 else 'FAIL'}")
if off:
    failures.append(f"{off} level-sum mismatches")

# Check 4: cross-report agreement on overlapping years.
print("\n4. Cross-report agreement")
grid = (
    tidy[(tidy["level"] == "Grand Total") & (tidy["sex"] == "Both")]
    .pivot_table(index=["state", "ref_year"], columns="report", values="value")
)
overlapping = grid[grid.notna().sum(axis=1) >= 2]
spread = (
    (overlapping.max(axis=1) - overlapping.min(axis=1))
    / overlapping.min(axis=1) * 100
)
worst = spread.max()
print(f"   {len(overlapping):,} state-years in 2+ reports, "
      f"largest disagreement {worst:.4f}% "
      f"{'PASS' if worst < 0.1 else 'FAIL'}")
if worst >= 0.1:
    failures.append(f"cross-report disagreement of {worst:.2f}%")

# Check 5: state coverage.
print("\n5. State coverage")
per_report = tidy.groupby("report")["state"].nunique()
for report, count in per_report.items():
    print(f"   {report}: {count} states {'PASS' if count == 37 else 'FAIL'}")
    if count != 37:
        failures.append(f"{report} has {count} states, expected 37")

# If every report has 37 states but the overall count is higher, then some
# state is spelled two ways and STATE_CANON is missing a variant. Without
# this check the mistake is invisible -- each report looks correct on its
# own while the panel silently splits one state into two.
distinct = tidy["state"].nunique()
print(f"   distinct states overall: {distinct} "
      f"{'PASS' if distinct == 37 else 'FAIL'}")
if distinct != 37:
    incomplete = tidy.groupby("state")["report"].nunique()
    for state in incomplete[incomplete < 5].index:
        variants = tidy.loc[tidy["state"] == state, "state_raw"].unique()
        print(f"      {state!r} -> raw variants: {list(variants)}")
    failures.append(f"{distinct} distinct states, expected 37 "
                    "(a name variant is missing from STATE_CANON)")


# --- Write -----------------------------------------------------------------

print("\n" + "=" * 62)

if failures:
    print("VERIFICATION FAILED -- nothing written\n")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
tidy.to_csv(OUT_PATH, index=False, encoding="utf-8")

print("All checks passed.\n")
print(f"Wrote {len(tidy):,} rows to {OUT_PATH}")
print(f"  reports:   {tidy['report'].nunique()}")
print(f"  states:    {tidy['state'].nunique()}")
print(f"  years:     {sorted(tidy['ref_year'].unique())}")
print(f"  estimated: {tidy['is_estimated'].sum():,} of {len(tidy):,} values")