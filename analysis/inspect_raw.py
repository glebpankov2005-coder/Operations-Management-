"""
PHASE 0 - DATA INGESTION: raw file inspection.
Scans every raw Excel file and prints structure: sheets, shape, columns,
dtypes, non-null counts, and a few sample rows. No cleaning, no assumptions.
"""
import os
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 240)
pd.set_option("display.max_colwidth", 40)

files = sorted(f for f in os.listdir(RAW) if f.lower().endswith(".xlsx"))

for fn in files:
    path = os.path.join(RAW, fn)
    print("=" * 100)
    print("FILE:", fn)
    print("=" * 100)
    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
    except Exception as e:
        print("  !! could not open:", e)
        continue
    print("  sheets:", xls.sheet_names)
    for sheet in xls.sheet_names:
        # read only header + first rows fast for structure, then full for counts
        df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
        print("-" * 100)
        print(f"  SHEET: {sheet}  ->  rows={len(df):,}  cols={df.shape[1]}")
        print("-" * 100)
        info = pd.DataFrame({
            "column": df.columns.astype(str),
            "dtype": [str(df[c].dtype) for c in df.columns],
            "non_null": [int(df[c].notna().sum()) for c in df.columns],
            "nulls": [int(df[c].isna().sum()) for c in df.columns],
            "n_unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
            "sample": [repr(df[c].dropna().iloc[0]) if df[c].notna().any() else "" for c in df.columns],
        })
        print(info.to_string(index=False))
        print("  first 3 rows:")
        print(df.head(3).to_string(index=False))
        print()
