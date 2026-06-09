"""Convert every Parquet table to a Tableau .hyper file."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pantab

from .settings import PARQUET_DIR

HYPER_DIR = PARQUET_DIR.parent / "hyper"
HYPER_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    files = sorted(PARQUET_DIR.glob("*.parquet"))
    for p in files:
        out = HYPER_DIR / f"{p.stem}.hyper"
        print(f"  {p.name:36s} -> {out.name}")
        df = pd.read_parquet(p)
        # Hyper doesn't support float32; upcast to float64
        float32_cols = df.select_dtypes(include="float32").columns
        if len(float32_cols):
            df[float32_cols] = df[float32_cols].astype("float64")
        pantab.frame_to_hyper(df, out, table=p.stem)
    print(f"\nWrote {len(files)} hyper files to {HYPER_DIR}")


if __name__ == "__main__":
    main()