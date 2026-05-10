#!/usr/bin/env python3
"""
Bootstrap an investigative EDA session.

Run this FIRST in iteration 1. It:
  1. Creates the eda_output directory structure
  2. Loads the dataset (CSV / Parquet / Excel / JSON / TSV)
  3. Prints a one-screen orientation summary
  4. Initializes empty theory_log.json and investigation_state.json
  5. Saves orientation.json snapshot for future iterations to reference

This is deterministic setup — don't waste agent tokens deriving it.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


def load_dataset(path: Path) -> pd.DataFrame:
    """Load by extension. Add formats here as needed."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Unsupported file extension: {suffix}")


def orient(df: pd.DataFrame, target: str | None) -> dict:
    """Compute a compact orientation summary."""
    info = {
        "shape": list(df.shape),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "dtypes": df.dtypes.astype(str).value_counts().to_dict(),
        "missing_total": int(df.isna().sum().sum()),
        "missing_pct_overall": round(df.isna().sum().sum() / df.size * 100, 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": list(df.columns),
    }

    miss = df.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=False)
    info["columns_with_missing"] = {c: int(n) for c, n in miss.items()}

    likely_ids = []
    for c in df.columns:
        if df[c].is_unique and df[c].dtype == "object":
            likely_ids.append(c)
        elif df[c].nunique() == len(df) and df[c].dtype != "bool":
            likely_ids.append(c)
    info["likely_id_columns"] = likely_ids

    if target and target in df.columns:
        t = df[target]
        target_info = {
            "name": target,
            "dtype": str(t.dtype),
            "n_unique": int(t.nunique()),
            "missing": int(t.isna().sum()),
        }
        if t.dtype == "object" or t.nunique() < 20:
            target_info["kind"] = "categorical/discrete"
            vc = t.value_counts(dropna=False).head(10)
            target_info["value_counts_top10"] = {str(k): int(v) for k, v in vc.items()}
            if t.nunique() == 2:
                pos_rate = (t == t.value_counts().idxmax()).mean()
                target_info["majority_class_rate"] = round(float(pos_rate), 4)
        else:
            target_info["kind"] = "continuous"
            target_info["stats"] = {
                "mean": float(t.mean()),
                "std": float(t.std()),
                "min": float(t.min()),
                "p25": float(t.quantile(0.25)),
                "median": float(t.median()),
                "p75": float(t.quantile(0.75)),
                "max": float(t.max()),
            }
        info["target"] = target_info
    elif target:
        info["target_error"] = f"Target column '{target}' not found in dataset"
    else:
        info["target"] = None

    # Suggest segment-size thresholds based on dataset size for the agent's reference
    n_rows = info["shape"][0]
    if n_rows > 10_000:
        info["segment_size_thresholds"] = {"pursue": 50, "caution": 20}
    elif n_rows > 1_000:
        info["segment_size_thresholds"] = {"pursue": 30, "caution": 15}
    elif n_rows > 200:
        info["segment_size_thresholds"] = {"pursue": 20, "caution": 10}
    else:
        info["segment_size_thresholds"] = {"pursue": 10, "caution": 5}

    return info


def setup_output_dir(out: Path) -> None:
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "auto_eda").mkdir(parents=True, exist_ok=True)

    theory_log = out / "theory_log.json"
    if not theory_log.exists():
        theory_log.write_text("[]")

    state = out / "investigation_state.json"
    if not state.exists():
        state.write_text(json.dumps({
            "open_threads": [],
            "current_thread": None,
            "completed_threads": []
        }, indent=2))


def print_summary(info: dict) -> None:
    print("=" * 70)
    print("DATASET ORIENTATION")
    print("=" * 70)
    print(f"Shape:         {info['shape'][0]:,} rows × {info['shape'][1]} cols")
    print(f"Memory:        {info['memory_mb']} MB")
    print(f"Dtypes:        {info['dtypes']}")
    print(f"Missing:       {info['missing_total']:,} cells ({info['missing_pct_overall']}%)")
    print(f"Duplicates:    {info['duplicate_rows']:,} rows")

    if info["likely_id_columns"]:
        print(f"Likely IDs:    {info['likely_id_columns']}")

    if info["columns_with_missing"]:
        print("\nColumns with missing values:")
        for c, n in list(info["columns_with_missing"].items())[:10]:
            pct = round(n / info["shape"][0] * 100, 1)
            print(f"  {c:<40} {n:>8,}  ({pct}%)")
        if len(info["columns_with_missing"]) > 10:
            print(f"  ... and {len(info['columns_with_missing']) - 10} more")

    target = info.get("target")
    if target:
        print(f"\nTarget: {target['name']} ({target.get('kind', '?')})")
        if target.get("kind") == "categorical/discrete":
            print(f"  Unique values: {target['n_unique']}")
            print(f"  Top values: {target.get('value_counts_top10', {})}")
            if "majority_class_rate" in target:
                print(f"  Majority class rate: {target['majority_class_rate']:.1%}")
        elif target.get("kind") == "continuous":
            s = target["stats"]
            print(f"  Range: [{s['min']:.3g}, {s['max']:.3g}]   mean={s['mean']:.3g}   median={s['median']:.3g}")
    elif "target_error" in info:
        print(f"\n⚠️  {info['target_error']}")
        print(f"   Available columns: {info['columns'][:20]}{'...' if len(info['columns']) > 20 else ''}")
    else:
        print("\nNo target specified (unsupervised exploration)")

    th = info["segment_size_thresholds"]
    print(f"\nSegment-size thresholds for this dataset: pursue ≥ {th['pursue']}, caution {th['caution']}–{th['pursue']-1}, ignore < {th['caution']}")
    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap investigative EDA")
    parser.add_argument("--data", required=True, type=Path, help="Path to dataset")
    parser.add_argument("--target", default=None, help="Name of target column (or omit for unsupervised)")
    parser.add_argument(
        "--output",
        default=Path("./eda_output"),
        type=Path,
        help="Output directory (default: ./eda_output)",
    )
    args = parser.parse_args()

    if not args.data.exists():
        print(f"❌ Dataset not found: {args.data}", file=sys.stderr)
        return 1

    print(f"Loading {args.data} ...")
    df = load_dataset(args.data)

    setup_output_dir(args.output)

    info = orient(df, args.target)
    info["_meta"] = {
        "dataset_path": str(args.data),
        "target": args.target,
        "bootstrapped_at": datetime.now().isoformat(timespec="seconds"),
    }

    (args.output / "orientation.json").write_text(json.dumps(info, indent=2, default=str))

    print_summary(info)
    print(f"\n✅ Setup complete. Output → {args.output}/")
    print(f"   Initialized: theory_log.json, investigation_state.json, orientation.json")
    print(f"   Next: read orientation.json and start iteration 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
