"""
etl/transform.py
────────────────
Reads raw Kaggle CSVs from data/raw/, cleans and normalises them,
computes BVI scores for each constructor × season, and writes
processed outputs to data/processed/.

Run:  python -m etl.transform
"""

import os
import logging
import pandas as pd
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Seasons to include in BVI analysis
BVI_SEASONS = list(range(2018, 2024))

# DNF-related status IDs (from Kaggle status.csv)
DNF_KEYWORDS = [
    "Accident", "Collision", "Engine", "Gearbox", "Hydraulics",
    "Mechanical", "Retired", "Disqualified", "Suspension", "Brakes",
    "Electrical", "Wheel", "Transmission", "Differential", "Oil",
    "Fire", "Throttle", "Steering", "Clutch", "Puncture",
    "Spin", "Overheating",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def minmax(series: pd.Series) -> pd.Series:
    """Min-max normalise a series to [0, 1]. Returns 0.5 if constant."""
    rng = series.max() - series.min()
    if rng == 0:
        return pd.Series(0.5, index=series.index)
    return (series - series.min()) / rng


def read(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing: {path}. Download from Kaggle and place in data/raw/."
        )
    return pd.read_csv(path)


# ── Load raw tables ──────────────────────────────────────────────────────────

def load_raw() -> dict[str, pd.DataFrame]:
    log.info("Loading raw CSVs from %s …", RAW_DIR)
    tables = {}
    files = {
        "circuits":     "circuits.csv",
        "constructors": "constructors.csv",
        "drivers":      "drivers.csv",
        "races":        "races.csv",
        "results":      "results.csv",
        "qualifying":   "qualifying.csv",
        "pit_stops":    "pit_stops.csv",
        "status":       "status.csv",
    }
    for key, fname in files.items():
        tables[key] = read(fname)
        log.info("  %-15s  %d rows", key, len(tables[key]))
    return tables


# ── Clean individual tables ──────────────────────────────────────────────────

def clean_circuits(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"circuitId": "circuit_id", "circuitRef": "circuit_ref"})
    df["alt"] = pd.to_numeric(df["alt"], errors="coerce").fillna(0).astype(int)
    return df[["circuit_id", "circuit_ref", "name", "location", "country",
               "lat", "lng", "alt", "url"]]


def clean_races(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"raceId": "race_id", "year": "season",
                             "circuitId": "circuit_id"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df[["race_id", "season", "round", "circuit_id", "name", "date", "url"]]


def clean_constructors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"constructorId": "constructor_id",
                             "constructorRef": "constructor_ref"})
    return df[["constructor_id", "constructor_ref", "name", "nationality", "url"]]


def clean_drivers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"driverId": "driver_id", "driverRef": "driver_ref"})
    df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
    return df[["driver_id", "driver_ref", "number", "code",
               "forename", "surname", "dob", "nationality", "url"]]


def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        "resultId": "result_id", "raceId": "race_id",
        "driverId": "driver_id", "constructorId": "constructor_id",
        "positionText": "position_text", "positionOrder": "position_order",
        "fastestLap": "fastest_lap", "fastestLapTime": "fastest_lap_time",
        "fastestLapSpeed": "fastest_lap_speed", "statusId": "status_id",
    })
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)
    df["milliseconds"] = pd.to_numeric(df["milliseconds"], errors="coerce")
    return df[[
        "result_id", "race_id", "driver_id", "constructor_id",
        "number", "grid", "position", "position_text", "position_order",
        "points", "laps", "time", "milliseconds",
        "fastest_lap", "rank", "fastest_lap_time", "fastest_lap_speed", "status_id",
    ]]


def clean_qualifying(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        "qualifyId": "qualify_id", "raceId": "race_id",
        "driverId": "driver_id", "constructorId": "constructor_id",
    })
    return df[["qualify_id", "race_id", "driver_id", "constructor_id",
               "number", "position", "q1", "q2", "q3"]]


def clean_pit_stops(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"raceId": "race_id", "driverId": "driver_id"})
    df["milliseconds"] = pd.to_numeric(df["milliseconds"], errors="coerce")
    return df[["race_id", "driver_id", "stop", "lap", "time", "duration", "milliseconds"]]


# ── BVI computation ───────────────────────────────────────────────────────────

def compute_bvi(results: pd.DataFrame, races: pd.DataFrame,
                status: pd.DataFrame, constructors: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Brand Value Index for every constructor × season combination.

    BVI = Performance × 0.40 + Consistency × 0.30 + Exposure × 0.30

    All dimension scores are min-max normalised within each season (0–100).
    """
    log.info("Computing BVI scores for seasons %s …", BVI_SEASONS)

    # Identify DNF status IDs
    dnf_ids = set(
        status[status["status"].str.contains(
            "|".join(DNF_KEYWORDS), case=False, na=False
        )]["statusId"].tolist()
    )

    # Filter to analysis seasons
    season_races = races[races["season"].isin(BVI_SEASONS)][
        ["raceId", "season"]
    ]
    merged = results.merge(season_races, on="raceId")
    merged = merged.merge(
        constructors[["constructorId", "name"]],
        on="constructorId"
    )

    raw_rows = []
    for season, grp in merged.groupby("season"):
        for (cid, cname), g in grp.groupby(["constructorId", "name"]):
            entries = len(g)

            # Performance signals
            total_points = g["points"].sum()
            wins = int((g["positionOrder"] == 1).sum())
            podiums = int((g["positionOrder"] <= 3).sum())
            podium_rate = podiums / entries if entries else 0.0

            # Consistency signals
            dnf_count = int(g["statusId"].isin(dnf_ids).sum())
            dnf_rate = dnf_count / entries if entries else 0.0
            pts_finish_rate = float((g["points"] > 0).sum()) / entries if entries else 0.0
            valid = g[g["grid"] > 0]
            avg_delta = float((valid["grid"] - valid["positionOrder"]).mean()) \
                if len(valid) > 0 else 0.0

            # Exposure proxy
            broadcast_proxy = podiums * 1.0 + wins * 2.0

            raw_rows.append({
                "constructor_id":   cid,
                "constructor":      cname,
                "season":           int(season),
                "total_points":     float(total_points),
                "wins":             wins,
                "podiums":          podiums,
                "entries":          entries,
                "dnf_rate":         round(dnf_rate, 4),
                "pts_finish_rate":  round(pts_finish_rate, 4),
                "avg_delta":        round(avg_delta, 4),
                "broadcast_proxy":  broadcast_proxy,
                "podium_rate":      round(podium_rate, 4),
            })

    df = pd.DataFrame(raw_rows)

    # Normalise within each season and compute weighted BVI
    bvi_rows = []
    for season, g in df.groupby("season"):
        d = g.copy().reset_index(drop=True)

        perf = (
            minmax(d["total_points"])  * 0.50
            + minmax(d["podium_rate"]) * 0.30
            + minmax(d["wins"].astype(float)) * 0.20
        ) * 100

        cons = (
            minmax(1 - d["dnf_rate"])        * 0.40
            + minmax(d["pts_finish_rate"])    * 0.40
            + minmax(d["avg_delta"])          * 0.20
        ) * 100

        expo = (
            minmax(d["broadcast_proxy"]) * 0.70
            + minmax(d["podiums"].astype(float)) * 0.30
        ) * 100

        d["perf_score"] = perf.round(2)
        d["cons_score"] = cons.round(2)
        d["expo_score"] = expo.round(2)
        d["bvi"] = (
            d["perf_score"] * 0.40
            + d["cons_score"] * 0.30
            + d["expo_score"] * 0.30
        ).round(2)
        d["tier"] = d["bvi"].apply(
            lambda x: 1 if x >= 75 else (2 if x >= 50 else 3)
        )
        bvi_rows.append(d)

    return pd.concat(bvi_rows, ignore_index=True)


# ── Main pipeline ────────────────────────────────────────────────────────────

def run():
    raw = load_raw()

    # Clean each table
    circuits     = clean_circuits(raw["circuits"])
    races        = clean_races(raw["races"])
    constructors = clean_constructors(raw["constructors"])
    drivers      = clean_drivers(raw["drivers"])
    results      = clean_results(raw["results"])
    qualifying   = clean_qualifying(raw["qualifying"])
    pit_stops    = clean_pit_stops(raw["pit_stops"])

    # Save cleaned tables
    for name, df in [
        ("circuits",     circuits),
        ("races",        races),
        ("constructors", constructors),
        ("drivers",      drivers),
        ("results",      results),
        ("qualifying",   qualifying),
        ("pit_stops",    pit_stops),
    ]:
        out = OUT_DIR / f"{name}.parquet"
        df.to_parquet(out, index=False)
        log.info("Saved  %s  (%d rows)", out, len(df))

    # Compute BVI — needs original column names for merge
    bvi = compute_bvi(raw["results"], raw["races"], raw["status"], raw["constructors"])
    bvi.to_parquet(OUT_DIR / "bvi_scores.parquet", index=False)
    bvi.to_csv(OUT_DIR / "bvi_scores.csv", index=False)
    log.info("Saved  data/processed/bvi_scores.parquet  (%d rows)", len(bvi))
    log.info("BVI computation complete.")

    # Summary
    s23 = bvi[bvi["season"] == 2023].sort_values("bvi", ascending=False)
    log.info("\n=== 2023 BVI Top 5 ===")
    for _, r in s23.head(5).iterrows():
        log.info("  %-20s  BVI=%.1f  Tier=%d", r["constructor"], r["bvi"], r["tier"])


if __name__ == "__main__":
    run()
