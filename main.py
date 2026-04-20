"""
Viral Video Pattern Analyzer
=============================
Usage:
    python main.py [--target 1000] [--region US] [--no-cache]

Requires:
    YOUTUBE_API_KEY environment variable (or .env file)

Steps:
  1. Collect up to --target videos from YouTube Data API v3
  2. Extract ~35 features per video
  3. Run statistical analysis to find viral patterns
  4. Print a comprehensive report + save data/report.json and data/videos.csv
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src import collector, features, analyzer, reporter

load_dotenv()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze viral YouTube video patterns")
    p.add_argument("--target", type=int, default=1000, help="Number of videos to collect (default: 1000)")
    p.add_argument("--region", default="US", help="YouTube region code (default: US)")
    p.add_argument("--no-cache", action="store_true", help="Ignore cached raw data and re-fetch")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY is not set.")
        print("  Copy .env.example to .env and add your key:")
        print("  https://console.cloud.google.com/apis/credentials")
        sys.exit(1)

    if args.no_cache and collector.RAW_CACHE.exists():
        collector.RAW_CACHE.unlink()
        print("Cache cleared.")

    # ── 1. Collect ──────────────────────────────────────────────────────────
    print(f"\nCollecting up to {args.target:,} videos (region={args.region})...")
    raw_videos = collector.collect(api_key, target=args.target, region=args.region)
    print(f"Collected {len(raw_videos):,} raw video records.")

    # ── 2. Extract features ─────────────────────────────────────────────────
    print("\nExtracting features...")
    rows = [features.extract(v) for v in raw_videos]
    rows = [r for r in rows if r is not None]
    df = pd.DataFrame(rows)
    print(f"Feature matrix: {len(df):,} videos × {len(df.columns)} features")

    if len(df) < 50:
        print("ERROR: Too few usable videos to analyze. Try --no-cache and re-run.")
        sys.exit(1)

    # ── 3. Analyze ──────────────────────────────────────────────────────────
    print("\nRunning statistical analysis...")
    results = analyzer.run(df)

    # ── 4. Report ───────────────────────────────────────────────────────────
    print("\n")
    reporter.generate(df, results)


if __name__ == "__main__":
    main()
