"""Unit (Store) dimension — the deep dimension. 36 attributes from the schema."""

from __future__ import annotations

import numpy as np
import pandas as pd
from faker import Faker

from ..core.registry import REGISTRY
from ..core.rng import rng_for
from ..core.settings import DATE_END, DATE_START, SEED, UNIT_COUNT
from ..core.writers import write_full

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West", "Mountain"]
STATES = [
    "AL", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]
DMAS = [
    "New York", "Los Angeles", "Chicago", "Philadelphia", "Dallas-Ft. Worth",
    "San Francisco", "Boston", "Atlanta", "Washington DC", "Houston", "Detroit",
    "Phoenix", "Seattle", "Tampa", "Miami", "Denver", "Cleveland", "Orlando",
    "Sacramento", "St. Louis", "Portland", "Pittsburgh", "Charlotte",
    "Raleigh-Durham", "Indianapolis", "Baltimore", "San Diego", "Nashville",
    "Hartford-New Haven", "Kansas City", "Salt Lake City", "Columbus OH",
    "Cincinnati", "Milwaukee", "Greenville-Spartanburg",
]
POS_SYSTEMS = ["NCR Aloha", "Toast", "Oracle Micros", "Square", "Revel", "PAR"]
STORE_TYPES = ["Inline", "Endcap", "Freestanding", "Drive-Thru Only", "Food Court"]
VENUES = ["Mall", "Strip Center", "Standalone", "Airport", "University", "Hotel", "Stadium", "Travel Plaza"]
FRANCHISE_TYPES = ["Single-Unit", "Multi-Unit", "Area Developer", "Master Franchise"]
LICENSE_TYPES = ["Standard", "Limited", "Beer & Wine", "Full Liquor"]


def generate() -> int:
    rng = rng_for("Unit")
    fake = Faker("en_US")
    Faker.seed(SEED)

    n = UNIT_COUNT
    sbr_seq = np.arange(5_000_001, 5_000_001 + n, dtype="int64")
    unit_numbers = np.array([f"U{100000 + i:06d}" for i in range(n)])

    # Assign each unit to a brand
    if REGISTRY.brand_keys.size == 0:
        raise RuntimeError("Brand must be generated before Unit")
    brand_assignment = rng.choice(REGISTRY.brand_keys, size=n)

    # Cache pools for faker speed
    fake_cities_pool = [fake.city() for _ in range(1500)]
    fake_zips_pool = [fake.zipcode() for _ in range(3000)]
    fake_street_pool = [fake.street_address() for _ in range(4000)]
    fake_name_pool = [fake.name() for _ in range(2500)]
    fake_company_pool = [fake.company() for _ in range(800)]

    open_start = pd.Timestamp("2005-01-01")
    open_end = pd.Timestamp("2023-12-31")
    open_day_offsets = rng.integers(0, (open_end - open_start).days, n)
    open_dates = pd.to_datetime(open_start + pd.to_timedelta(open_day_offsets, unit="D"))

    # ~5% closed: pick a close date 180d - 8yrs after open, capped at DATE_END
    closed_mask = rng.random(n) < 0.05
    end_dt = pd.Timestamp(DATE_END)
    close_day_offsets = rng.integers(180, 8 * 365, n)
    candidate_close = open_dates + pd.to_timedelta(close_day_offsets, unit="D")
    candidate_close = candidate_close.where(candidate_close <= end_dt, end_dt)
    close_dates = pd.Series(pd.NaT, index=range(n), dtype="datetime64[ns]")
    close_dates.loc[closed_mask] = candidate_close[closed_mask].values
    close_dates = pd.to_datetime(close_dates)

    # Lease expiration: 1-15 years after open
    lease_day_offsets = rng.integers(365, 15 * 365, n)
    lease_dates = open_dates + pd.to_timedelta(lease_day_offsets, unit="D")

    # Next remodel: -1 year to +7 years from DATE_END
    rem_day_offsets = rng.integers(-365, 7 * 365, n)
    next_remodel = end_dt + pd.to_timedelta(rem_day_offsets, unit="D")

    df = pd.DataFrame({
        "SBRSequence": sbr_seq,
        "UnitNumber": unit_numbers,
        "AcceptsGiftCards": rng.choice(["Y", "N"], n, p=[0.92, 0.08]),
        "Address": rng.choice(fake_street_pool, n),
        "City": rng.choice(fake_cities_pool, n),
        "CloseDate": close_dates,
        "CoBrandGroupNumber": np.where(
            rng.random(n) < 0.10,
            np.array([f"CB{i:05d}" for i in rng.integers(1, 600, n)]),
            None,
        ),
        "CoBranded": np.where(rng.random(n) < 0.10, "Y", "N"),
        "CompanyOwned": np.where(rng.random(n) < 0.18, "Y", "N"),
        "Country": rng.choice(["US", "CA", "MX"], n, p=[0.92, 0.06, 0.02]),
        "DistrictManager": rng.choice(fake_name_pool[:400], n),
        "DMA": rng.choice(DMAS, n),
        "FranchiseBusinessConsultant": rng.choice(fake_name_pool[400:800], n),
        "MarketingManager": rng.choice(fake_name_pool[800:1200], n),
        "Franchisee": rng.choice(fake_company_pool, n),
        "FranchisePartner": np.where(rng.random(n) < 0.3, rng.choice(fake_name_pool[1200:1800], n), None),
        "FranchiseeGroup": rng.choice([f"FG-{i:04d}" for i in range(1, 300)], n),
        "FranchiseType": rng.choice(FRANCHISE_TYPES, n, p=[0.5, 0.3, 0.15, 0.05]),
        "HasLegacyUnitNumber": rng.choice(["Y", "N"], n, p=[0.15, 0.85]),
        "Latitude": rng.uniform(24.5, 49.0, n).round(6),
        "LeaseExpirationDate": lease_dates,
        "LicenseType": rng.choice(LICENSE_TYPES, n, p=[0.55, 0.2, 0.15, 0.10]),
        "Longitude": rng.uniform(-125.0, -66.5, n).round(6),
        "NextRemodelDate": next_remodel,
        "OpenDate": open_dates,
        "PointOfSale": rng.choice(POS_SYSTEMS, n),
        "Region": rng.choice(REGIONS, n),
        "RVP": rng.choice(fake_name_pool[1800:2000], n),
        "SBRName": np.array([f"Store {u}" for u in unit_numbers]),
        "SBRSequence_attr": sbr_seq,  # placeholder, will be dropped
        "SiteSpecificLocation": np.where(rng.random(n) < 0.4, rng.choice(["Airport", "Mall", "Hospital", "University", "Stadium"], n), None),
        "State": rng.choice(STATES, n),
        "SBRStatus": np.where(closed_mask, "Closed", "Open"),
        "StoreType": rng.choice(STORE_TYPES, n, p=[0.20, 0.10, 0.45, 0.10, 0.15]),
        "Venue": rng.choice(VENUES, n),
        "VenueTradNonTradByFreq": rng.choice(["Traditional", "Non-Traditional"], n, p=[0.78, 0.22]),
        "ZipCode": rng.choice(fake_zips_pool, n),
    })

    # Fix column to match schema name (only one SBRSequence column)
    df = df.drop(columns=["SBRSequence_attr"])

    # Populate registry maps for fact generators
    REGISTRY.unit_keys = sbr_seq
    REGISTRY.unit_open_date = {
        int(k): pd.Timestamp(v) for k, v in zip(sbr_seq, open_dates)
    }
    REGISTRY.unit_close_date = {
        int(k): (None if pd.isna(v) else pd.Timestamp(v))
        for k, v in zip(sbr_seq, close_dates)
    }
    REGISTRY.unit_brand = dict(zip(sbr_seq.tolist(), brand_assignment.tolist()))

    return write_full("Unit", df)
