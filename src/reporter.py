"""
Report generation: console output + JSON/CSV export.

Console output is designed to be read top-to-bottom as a narrative.
Files are saved to data/report.json and data/videos.csv.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

REPORT_JSON = Path("data/report.json")
VIDEOS_CSV = Path("data/videos.csv")

# Features to spotlight in the "top signals" section
SPOTLIGHT_FEATURES = {
    "title_len": "Title character length",
    "title_word_count": "Title word count",
    "title_emotional_word_count": "Emotional words in title",
    "title_has_question": "Title ends with question",
    "title_has_number": "Title contains a number",
    "title_has_brackets": "Title has [ ] or ( )",
    "title_caps_word_count": "ALL-CAPS words in title",
    "duration_minutes": "Video duration (minutes)",
    "tag_count": "Number of tags",
    "desc_len": "Description length",
    "desc_has_chapters": "Description has chapter timestamps",
    "desc_cta_count": "Call-to-action phrases in description",
    "has_captions": "Has captions/subtitles",
    "definition_hd": "HD video",
    "is_short": "YouTube Short (≤60s)",
    "upload_is_weekend": "Uploaded on weekend",
    "channel_subscribers": "Channel subscriber count",
    "engagement_rate": "Like+comment rate",
}


def _fmt_num(n: int | float) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def _bar(value: float, max_val: float, width: int = 20) -> str:
    filled = int(round(value / max_val * width)) if max_val > 0 else 0
    return "█" * filled + "░" * (width - filled)


def _section(title: str) -> None:
    print(f"\n{'═' * 70}")
    print(f"  {title.upper()}")
    print("═" * 70)


def _subsection(title: str) -> None:
    print(f"\n  ── {title} ──")


def print_summary(summary: dict) -> None:
    _section("Dataset Summary")
    print(f"  Videos analyzed   : {summary['total_videos']:,}")
    print(f"  Viral threshold   : {_fmt_num(summary['viral_threshold_views'])} views (top {100 - summary['viral_percentile']}%)")
    print(f"  Viral videos      : {summary['viral_video_count']:,}")
    print(f"  Median views      : {_fmt_num(summary['median_views'])}")
    print(f"  Mean views        : {_fmt_num(summary['mean_views'])}")
    print(f"  Max views         : {_fmt_num(summary['max_views'])}")


def print_top_correlations(correlations: list[dict], top_n: int = 15) -> None:
    _section(f"Top {top_n} Features Correlated with View Count (Spearman ρ)")
    sig = [c for c in correlations if c["significant"]][:top_n]
    max_rho = max((abs(c["spearman_rho"]) for c in sig), default=1.0)
    for c in sig:
        rho = c["spearman_rho"]
        label = SPOTLIGHT_FEATURES.get(c["feature"], c["feature"])
        direction = "+" if rho >= 0 else "-"
        bar = _bar(abs(rho), max_rho)
        print(f"  {direction}{abs(rho):.3f}  {bar}  {label}")


def print_viral_differences(viral_vs_rest: list[dict], top_n: int = 20) -> None:
    _section(f"How Top-10%% Viral Videos Differ (Mann-Whitney, top {top_n} by effect size)")
    sig = [r for r in viral_vs_rest if r["significant"]][:top_n]
    print(f"  {'Feature':<38} {'Viral median':>13} {'Rest median':>12}  {'Effect':>7}")
    print(f"  {'-'*38} {'-'*13} {'-'*12}  {'-'*7}")
    for r in sig:
        label = SPOTLIGHT_FEATURES.get(r["feature"], r["feature"])
        label = label[:37]
        v_med = _fmt_num(r["viral_median"])
        r_med = _fmt_num(r["rest_median"])
        eff = r["effect_size"]
        arrow = "▲" if eff > 0 else "▼"
        print(f"  {label:<38} {v_med:>13} {r_med:>12}  {arrow}{abs(eff):.3f}")


def print_optimal_ranges(optimal_ranges: dict) -> None:
    _section("Optimal Feature Ranges (by median view count)")
    for feat, data in optimal_ranges.items():
        label = SPOTLIGHT_FEATURES.get(feat, feat)
        print(f"\n  {label}")
        max_med = max(b["median_views"] for b in data["bins"])
        for b in data["bins"]:
            marker = " ◀ BEST" if b["range"] == data["best_range"] else ""
            bar = _bar(b["median_views"], max_med, width=16)
            print(
                f"    {b['range']:>22}  {bar}  {_fmt_num(b['median_views'])} median  "
                f"(n={b['video_count']}){marker}"
            )


def print_group_averages(group_averages: dict, feature_priority: list[str] | None = None) -> None:
    _section("Performance by Group")
    priority = feature_priority or [
        "upload_day_of_week",
        "upload_hour",
        "channel_subscriber_bucket",
        "is_short",
        "has_captions",
        "definition_hd",
        "upload_is_weekend",
        "title_has_question",
        "title_has_exclamation",
        "title_has_number",
        "title_has_brackets",
        "desc_has_chapters",
    ]
    for feat in priority:
        rows = group_averages.get(feat)
        if not rows:
            continue
        from src.analyzer import GROUP_FEATURES  # avoid circular at module level
        label_map = GROUP_FEATURES.get(feat)
        feat_label = SPOTLIGHT_FEATURES.get(feat, feat.replace("_", " ").title())
        _subsection(feat_label)
        max_med = max(r["median_views"] for r in rows)
        for r in rows[:10]:  # cap at 10 groups for readability
            bar = _bar(r["median_views"], max_med, width=14)
            print(
                f"    {r['group']:>22}  {bar}  {_fmt_num(r['median_views'])} median  "
                f"(n={r['video_count']})"
            )


def print_winning_formula(results: dict) -> None:
    """Synthesize the findings into a concise checklist."""
    _section("The Winning Formula — Patterns Shared by Viral Videos")

    vr = {r["feature"]: r for r in results["viral_vs_rest"] if r["significant"]}
    opt = results["optimal_ranges"]
    grp = results["group_averages"]

    findings: list[str] = []

    # Title length
    if "title_len" in opt:
        best = opt["title_len"]["best_range"]
        findings.append(f"Title length in the sweet spot: {best} characters")

    # Emotional words
    if "title_emotional_word_count" in vr:
        d = vr["title_emotional_word_count"]
        if d["effect_size"] > 0.05:
            findings.append(
                f"More emotional trigger words in title (viral median: {d['viral_median']:.1f} vs {d['rest_median']:.1f})"
            )

    # Numbers in title
    if "title_has_number" in vr:
        d = vr["title_has_number"]
        winner = "WITH" if d["viral_mean"] > d["rest_mean"] else "WITHOUT"
        findings.append(f"Titles {winner} numbers perform better (effect {d['effect_size']:+.3f})")

    # Duration
    if "duration_minutes" in opt:
        best = opt["duration_minutes"]["best_range"]
        findings.append(f"Duration sweet spot: {best} minutes")

    # Tags
    if "tag_count" in opt:
        best = opt["tag_count"]["best_range"]
        findings.append(f"Tag count sweet spot: {best} tags")

    # Captions
    if "has_captions" in vr:
        d = vr["has_captions"]
        if d["effect_size"] > 0.03:
            findings.append("Videos WITH captions get significantly more views")

    # HD
    if "definition_hd" in vr:
        d = vr["definition_hd"]
        if d["effect_size"] > 0.03:
            findings.append("HD videos outperform SD")

    # Chapters
    if "desc_has_chapters" in vr:
        d = vr["desc_has_chapters"]
        if d["effect_size"] > 0.03:
            findings.append("Descriptions with chapter timestamps (≥3 timestamps) get more views")

    # Best upload day
    day_rows = grp.get("upload_day_of_week", [])
    if day_rows:
        best_day = day_rows[0]["group"]
        findings.append(f"Best upload day: {best_day}")

    # Best upload hour
    hour_rows = grp.get("upload_hour", [])
    if hour_rows:
        best_hour = hour_rows[0]["raw_value"]
        findings.append(f"Best upload hour (UTC): {best_hour:02d}:00")

    # Shorts vs regular
    short_rows = grp.get("is_short", [])
    if short_rows:
        best_short = short_rows[0]["group"]
        findings.append(f"{best_short} videos lead in median view count")

    # Channel size
    ch_rows = grp.get("channel_subscriber_bucket", [])
    if ch_rows:
        best_tier = ch_rows[0]["group"]
        findings.append(f"Highest-performing channel size tier: {best_tier} subscribers")

    for i, f in enumerate(findings, 1):
        print(f"  {i:>2}. {f}")


def save_files(df: pd.DataFrame, results: dict) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_JSON.open("w") as f:
        json.dump(results, f, indent=2, default=str)
    df.to_csv(VIDEOS_CSV, index=False)
    print(f"\n  Saved: {REPORT_JSON}")
    print(f"  Saved: {VIDEOS_CSV}")


def generate(df: pd.DataFrame, results: dict) -> None:
    print_summary(results["summary"])
    print_top_correlations(results["correlations"])
    print_viral_differences(results["viral_vs_rest"])
    print_optimal_ranges(results["optimal_ranges"])
    print_group_averages(results["group_averages"])
    print_winning_formula(results)
    save_files(df, results)
