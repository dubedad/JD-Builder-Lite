import argparse
import json
import sqlite3
from pathlib import Path

import polars as pl

_HERE = Path(__file__).parent.parent  # ps_careers_site/
DEFAULT_DB = _HERE / "careers.sqlite"
DEFAULT_BRIDGE = Path(r"C:\Users\Administrator\projects\jobforge\data\gold\bridge_caf_ja.parquet")
MIN_CONFIDENCE = 0.70


def load_bridge(bridge_path: Path) -> dict[int, list[str]]:
    """Read bridge_caf_ja.parquet and return a mapping of jt_id -> [caf_slug, ...]."""
    df = pl.read_parquet(bridge_path)
    total_rows = len(df)

    filtered = df.filter(pl.col("confidence_score") >= MIN_CONFIDENCE)
    filtered_rows = len(filtered)

    # Group by ja_job_title_id, collect caf_occupation_id values
    grouped = (
        filtered
        .group_by("ja_job_title_id")
        .agg(pl.col("caf_occupation_id").unique())
    )

    result: dict[int, list[str]] = {}
    for row in grouped.to_dicts():
        jt_id = int(row["ja_job_title_id"])
        slugs = sorted(row["caf_occupation_id"])  # sort for deterministic output
        result[jt_id] = slugs

    unique_jt_ids = len(result)
    print(
        f"Bridge loaded\n"
        f"  Total rows in parquet : {total_rows}\n"
        f"  Rows >= {MIN_CONFIDENCE:.2f} confidence : {filtered_rows}\n"
        f"  Unique jt_ids matched  : {unique_jt_ids}"
    )
    return result


def apply_bridge(db_path: Path, bridge: dict[int, list[str]]) -> tuple[int, int]:
    """Write caf_related JSON arrays to careers.sqlite. Returns (matched, unmatched)."""
    conn = sqlite3.connect(str(db_path))

    matched = 0
    for jt_id, slugs in bridge.items():
        conn.execute(
            "UPDATE careers SET caf_related=? WHERE jt_id=?",
            (json.dumps(slugs), jt_id),
        )
        matched += conn.execute(
            "SELECT changes()"
        ).fetchone()[0]

    # Clear caf_related for all rows NOT in the bridge
    if bridge:
        placeholders = ",".join("?" * len(bridge))
        conn.execute(
            f"UPDATE careers SET caf_related=NULL WHERE jt_id NOT IN ({placeholders})",
            list(bridge.keys()),
        )
    else:
        conn.execute("UPDATE careers SET caf_related=NULL")

    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM careers").fetchone()[0]
    unmatched = total - matched
    conn.close()

    return matched, unmatched


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply CAF bridge data to careers.sqlite")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    args = parser.parse_args()

    if not args.bridge.exists():
        print(f"ERROR: Bridge parquet not found: {args.bridge}")
        raise SystemExit(1)

    bridge = load_bridge(args.bridge)
    matched, unmatched = apply_bridge(args.db, bridge)

    # Final verification
    conn = sqlite3.connect(str(args.db))
    with_caf = conn.execute("SELECT COUNT(*) FROM careers WHERE caf_related IS NOT NULL").fetchone()[0]
    conn.close()

    print(
        f"\nBridge applied\n"
        f"  Rows with CAF matches  : {matched}\n"
        f"  Rows without CAF match : {unmatched}\n"
        f"  Verified (non-null)    : {with_caf}"
    )


if __name__ == "__main__":
    main()
