"""
etl/load.py
───────────
Bulk-loads cleaned parquet files from data/processed/ into PostgreSQL
using psycopg2's COPY for maximum throughput.

Run:  python -m etl.load
"""

import io
import os
import logging
import pandas as pd
import psycopg2
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pitwall:changeme@localhost:5432/pitwall_db"
)


def get_conn():
    return psycopg2.connect(DB_URL)


def copy_df(cur, df: pd.DataFrame, table: str, columns: list[str]):
    """Bulk-insert a DataFrame into a PostgreSQL table via COPY."""
    buf = io.StringIO()
    df[columns].to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)
    cur.copy_expert(
        f"COPY {table} ({', '.join(columns)}) FROM STDIN "
        f"WITH (FORMAT csv, NULL '\\N')",
        buf
    )
    log.info("  COPY → %-20s  %d rows", table, len(df))


def load_all():
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # ── circuits ───────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "circuits.parquet")
        cur.execute("TRUNCATE circuits CASCADE")
        copy_df(cur, df, "circuits", [
            "circuit_id", "circuit_ref", "name", "location",
            "country", "lat", "lng", "alt", "url"
        ])

        # ── races ──────────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "races.parquet")
        cur.execute("TRUNCATE races CASCADE")
        copy_df(cur, df, "races", [
            "race_id", "season", "round", "circuit_id", "name", "date", "url"
        ])

        # ── constructors ───────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "constructors.parquet")
        cur.execute("TRUNCATE constructors CASCADE")
        copy_df(cur, df, "constructors", [
            "constructor_id", "constructor_ref", "name", "nationality", "url"
        ])

        # ── drivers ────────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "drivers.parquet")
        cur.execute("TRUNCATE drivers CASCADE")
        copy_df(cur, df, "drivers", [
            "driver_id", "driver_ref", "number", "code",
            "forename", "surname", "dob", "nationality", "url"
        ])

        # ── results ────────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "results.parquet")
        cur.execute("TRUNCATE results CASCADE")
        copy_df(cur, df, "results", [
            "result_id", "race_id", "driver_id", "constructor_id",
            "number", "grid", "position", "position_text", "position_order",
            "points", "laps", "time", "milliseconds",
            "fastest_lap", "rank", "fastest_lap_time", "fastest_lap_speed", "status_id"
        ])

        # ── qualifying ─────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "qualifying.parquet")
        cur.execute("TRUNCATE qualifying CASCADE")
        copy_df(cur, df, "qualifying", [
            "qualify_id", "race_id", "driver_id", "constructor_id",
            "number", "position", "q1", "q2", "q3"
        ])

        # ── pit_stops ──────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "pit_stops.parquet")
        cur.execute("TRUNCATE pit_stops CASCADE")
        copy_df(cur, df, "pit_stops", [
            "race_id", "driver_id", "stop", "lap",
            "time", "duration", "milliseconds"
        ])

        # ── bvi_scores ─────────────────────────────────────────────────────
        df = pd.read_parquet(PROCESSED_DIR / "bvi_scores.parquet")
        cur.execute("TRUNCATE bvi_scores CASCADE")
        copy_df(cur, df, "bvi_scores", [
            "constructor_id", "season", "total_points", "wins", "podiums",
            "entries", "dnf_rate", "pts_finish_rate",
            "perf_score", "cons_score", "expo_score", "bvi", "tier"
        ])

        conn.commit()
        log.info("All tables loaded successfully.")

    except Exception as exc:
        conn.rollback()
        log.error("Load failed: %s", exc)
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_all()
