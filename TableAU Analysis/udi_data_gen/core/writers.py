"""Parquet writers that stream chunks into a single file per table."""

from __future__ import annotations

import time
from contextlib import contextmanager
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .settings import PARQUET_DIR, PARQUET_ROW_GROUP_SIZE


def _slug(table_name: str) -> str:
    return table_name.lower().replace(" ", "_")


def parquet_path(table_name: str) -> Path:
    return PARQUET_DIR / f"{_slug(table_name)}.parquet"


class ParquetStreamWriter:
    """Append DataFrame chunks to a single Parquet file via pyarrow."""

    def __init__(self, table_name: str, schema: pa.Schema | None = None):
        self.path = parquet_path(table_name)
        self.table_name = table_name
        self._writer: pq.ParquetWriter | None = None
        self._schema = schema
        self.rows = 0

    def write(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        table = pa.Table.from_pandas(df, preserve_index=False)
        if self._writer is None:
            self._schema = table.schema
            self._writer = pq.ParquetWriter(
                self.path,
                self._schema,
                compression="snappy",
            )
        else:
            # Align to first-seen schema
            try:
                table = table.cast(self._schema, safe=False)
            except Exception:
                pass
        self._writer.write_table(table, row_group_size=PARQUET_ROW_GROUP_SIZE)
        self.rows += len(df)

    def close(self) -> None:
        if self._writer is not None:
            self._writer.close()


@contextmanager
def stream_writer(table_name: str):
    w = ParquetStreamWriter(table_name)
    try:
        yield w
    finally:
        w.close()


def write_full(table_name: str, df: pd.DataFrame) -> int:
    with stream_writer(table_name) as w:
        w.write(df)
        return w.rows


def file_size_mb(table_name: str) -> float:
    p = parquet_path(table_name)
    return p.stat().st_size / (1024 * 1024) if p.exists() else 0.0


class Timer:
    def __init__(self, label: str):
        self.label = label

    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed = time.perf_counter() - self.t0
