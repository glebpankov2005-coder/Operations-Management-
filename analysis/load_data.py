"""
Canonical data loaders for the ASSA ABLOY / DHL Bemmel warehouse project.

Two raw datasets:
  1. STORAGE (inventory snapshots) - 3 monthly files (01-04, 01-05, 01-06 2025).
     NOTE: each storage file has a 1-row title banner above the real header,
     so the real header is on the SECOND row -> read with header=1.
     Grain: one row per inventory DETAIL record (DTLNUM) = a stored load/qty
     of a PART at a LOCATION on the snapshot DATE.
  2. OUTBOUND (shipping/picking transactions) - 3 monthly files (202504/05/06).
     Grain: one row per ORDER LINE picked & shipped.

All loaders return tidy pandas DataFrames. Numeric coercion is applied but
NO values are silently corrected - suspect values are kept and flagged by the
data-quality module.
"""
import os
import glob
import pandas as pd
import warnings

warnings.filterwarnings("ignore", message="Workbook contains no default style")

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# ---- numeric columns per dataset (stored as text/object in the raw files) ----
STORAGE_NUMERIC = [
    "LOC LENGTH", "LOC HEIGHT", "LOC WIDTH",
    "QTY", "PA QTY", "PA LEN", "PA HGT", "PA WID", "PA WGT",
    "CS QTY", "CS LEN", "CS HGT", "CS WID", "CS WGT",
    "EA LEN", "EA HGT", "EA WID", "EA WGT",
]
OUTBOUND_NUMERIC = [
    "UNIT PRICE", "PICKED QTY", "ORDER NO", "LINE",
    "PALL FLAG", "PALL LINES", "PALL LIFTS",
    "LIST FLAG", "LIST LINES", "LIST LIFTS",
    "TROLLEY FLAG", "TROLLEY LINES", "TROLLEY LIFTS",
    "SHIPMENT PACKED CARTONS", "SHIPMENT PACKED PALLETS",
    "SHIPMENT STAGED PALLETS", "RE-LABEL", "CPOTYP",
]


def _coerce_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_storage(path):
    """Load one STORAGE snapshot file (header on 2nd row)."""
    df = pd.read_excel(path, sheet_name="Sheet1", header=1, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    df = _coerce_numeric(df, STORAGE_NUMERIC)
    df["SOURCE_FILE"] = os.path.basename(path)
    if "DATE" in df.columns:
        df["SNAPSHOT_DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    return df


def load_outbound(path):
    """Load one OUTBOUND transaction file."""
    df = pd.read_excel(path, sheet_name="Sheet1", engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    df = _coerce_numeric(df, OUTBOUND_NUMERIC)
    df["SOURCE_FILE"] = os.path.basename(path)
    return df


def all_storage():
    files = sorted(glob.glob(os.path.join(RAW, "ASSA STORAGE DETAILS*.xlsx")))
    return {os.path.basename(f): load_storage(f) for f in files}


def all_outbound():
    files = sorted(glob.glob(os.path.join(RAW, "*ASSA OUTBOUND DETAILS.xlsx")))
    return {os.path.basename(f): load_outbound(f) for f in files}


def combined_outbound():
    """All outbound months stacked into one frame."""
    return pd.concat(all_outbound().values(), ignore_index=True)


if __name__ == "__main__":
    st = all_storage()
    ob = all_outbound()
    print("STORAGE snapshots:")
    for k, v in st.items():
        print(f"  {k}: {len(v):,} rows x {v.shape[1]} cols")
    print("OUTBOUND months:")
    for k, v in ob.items():
        print(f"  {k}: {len(v):,} rows x {v.shape[1]} cols")
