"""DimDate — 10 years of daily grain with fiscal calendar."""

from __future__ import annotations

import pandas as pd

from ..core.registry import REGISTRY
from ..core.settings import DATE_END, DATE_START
from ..core.writers import write_full


def generate() -> int:
    idx = pd.date_range(DATE_START, DATE_END, freq="D")
    df = pd.DataFrame({"CalendarDate": idx.date})
    df["DateKey"] = (idx.year * 10_000 + idx.month * 100 + idx.day).astype("int32")
    df["Year"] = idx.year.astype("int16")
    df["Quarter"] = idx.quarter.astype("int8")
    df["Month"] = idx.month.astype("int8")
    df["MonthName"] = idx.strftime("%B")
    df["Week"] = idx.isocalendar().week.values.astype("int8")
    df["DayOfMonth"] = idx.day.astype("int8")
    df["DayOfWeek"] = (idx.dayofweek + 1).astype("int8")  # 1=Mon
    df["DayName"] = idx.strftime("%A")
    df["IsWeekend"] = (idx.dayofweek >= 5).astype("int8")
    # Simple US-style holiday flag (Thanksgiving Thu of Nov, Christmas, NYE, July 4)
    is_holiday = (
        ((idx.month == 12) & (idx.day.isin([24, 25, 31])))
        | ((idx.month == 1) & (idx.day == 1))
        | ((idx.month == 7) & (idx.day == 4))
    ).astype("int8")
    df["IsHoliday"] = is_holiday
    # Fiscal year starts in February for variety
    fy = idx.year.where(idx.month >= 2, idx.year - 1)
    df["FiscalYear"] = fy.astype("int16")
    fq = ((idx.month - 2) % 12 // 3 + 1)
    df["FiscalQuarter"] = fq.astype("int8")

    REGISTRY.date_index = pd.DatetimeIndex(idx)
    return write_full("DimDate", df)
