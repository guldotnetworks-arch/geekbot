"""
Statistical pattern analysis for viral video data.

Core questions answered:
  1. Which features correlate most strongly with view count?
  2. How do top-10% viral videos differ from the rest on every feature?
  3. What are the optimal ranges for key numeric features?
  4. Which day/hour/duration buckets produce the most views on average?

All results are pure Python dicts so reporter.py can format them freely.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


VIRAL_PERCENTILE = 90  # top-10% = "viral tier"

# Features we want detailed range analysis for
RANGE_FEATURES = [
    "title_len",
    "title_word_count",
    "duration_minutes",
    "tag_count",
    "desc_len",
    "desc_hashtag_count",
    "title_emotional_word_count",
    "channel_subscribers",
]

# Categorical / ordinal features for group-mean analysis
GROUP_FEATURES = {
    "upload_day_of_week": [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ],
    "upload_hour": None,   # raw numeric groups
    "category_id": None,
    "channel_subscriber_bucket": [
        "<1K", "1K-10K", "10K-100K", "100K-1M", "1M-10M", "10M+"
    ],
    "is_short": ["Regular", "Short (≤60s)"],
    "has_captions": ["No captions", "Has captions"],
    "definition_hd": ["SD", "HD"],
    "upload_is_weekend": ["Weekday", "Weekend"],
    "title_has_question": ["No question mark", "Has question mark"],
    "title_has_exclamation": ["No exclamation", "Has exclamation"],
    "title_has_number": ["No number", "Has number"],
    "title_has_brackets": ["No brackets", "Has brackets"],
    "desc_has_chapters": ["No chapters", "Has chapters"],
}


def _drop_outliers(series: pd.Series, z_thresh: float = 4.0) -> pd.Series:
    """Remove extreme statistical outliers before range analysis."""
    z = (series - series.mean()) / series.std(ddof=1)
    return series[z.abs() < z_thresh]


def correlations(df: pd.DataFrame) -> list[dict]:
    """Spearman rank correlations between every numeric feature and view count."""
    numeric = df.select_dtypes(include=[np.number]).drop(
        columns=["views"], errors="ignore"
    )
    results = []
    for col in numeric.columns:
        valid = df[["views", col]].dropna()
        if len(valid) < 30:
            continue
        rho, pval = scipy_stats.spearmanr(valid["views"], valid[col])
        results.append(
            {
                "feature": col,
                "spearman_rho": round(float(rho), 4),
                "p_value": float(pval),
                "significant": pval < 0.05,
            }
        )
    results.sort(key=lambda x: abs(x["spearman_rho"]), reverse=True)
    return results


def viral_vs_rest(df: pd.DataFrame) -> list[dict]:
    """
    For each numeric feature compare the viral tier (top VIRAL_PERCENTILE%)
    against the rest using Mann-Whitney U test and effect size (rank-biserial r).
    """
    threshold = df["views"].quantile(VIRAL_PERCENTILE / 100)
    viral = df[df["views"] >= threshold]
    rest = df[df["views"] < threshold]

    numeric = df.select_dtypes(include=[np.number]).drop(
        columns=["views"], errors="ignore"
    )
    results = []
    for col in numeric.columns:
        v = viral[col].dropna()
        r = rest[col].dropna()
        if len(v) < 5 or len(r) < 5:
            continue
        stat, pval = scipy_stats.mannwhitneyu(v, r, alternative="two-sided")
        n1, n2 = len(v), len(r)
        # rank-biserial correlation as effect size
        effect = (2 * stat) / (n1 * n2) - 1

        results.append(
            {
                "feature": col,
                "viral_median": round(float(v.median()), 4),
                "rest_median": round(float(r.median()), 4),
                "viral_mean": round(float(v.mean()), 4),
                "rest_mean": round(float(r.mean()), 4),
                "effect_size": round(float(effect), 4),
                "p_value": float(pval),
                "significant": pval < 0.05,
            }
        )
    results.sort(key=lambda x: abs(x["effect_size"]), reverse=True)
    return results


def optimal_ranges(df: pd.DataFrame) -> dict[str, dict]:
    """
    For each RANGE_FEATURES, find the value bucket that produces the
    highest median view count, using quantile-based binning.
    """
    output: dict[str, dict] = {}
    for feat in RANGE_FEATURES:
        if feat not in df.columns:
            continue
        clean = df[[feat, "views"]].dropna()
        clean = clean[clean[feat] > 0]
        if len(clean) < 30:
            continue

        # Use 5 quantile bins; fall back to 4 if not enough distinct values
        for n_bins in (5, 4, 3):
            try:
                clean = clean.copy()
                clean["_bin"] = pd.qcut(clean[feat], q=n_bins, duplicates="drop")
                break
            except ValueError:
                continue
        else:
            continue

        stats = (
            clean.groupby("_bin", observed=True)["views"]
            .agg(["median", "mean", "count"])
            .reset_index()
        )
        stats.columns = ["range", "median_views", "mean_views", "video_count"]
        best = stats.loc[stats["median_views"].idxmax()]

        output[feat] = {
            "bins": [
                {
                    "range": str(row["range"]),
                    "median_views": int(row["median_views"]),
                    "mean_views": int(row["mean_views"]),
                    "video_count": int(row["video_count"]),
                }
                for _, row in stats.iterrows()
            ],
            "best_range": str(best["range"]),
            "best_range_median_views": int(best["median_views"]),
        }
    return output


def group_averages(df: pd.DataFrame) -> dict[str, list[dict]]:
    """Mean and median view counts grouped by categorical features."""
    output: dict[str, list[dict]] = {}
    for feat, labels in GROUP_FEATURES.items():
        if feat not in df.columns:
            continue
        grp = (
            df.groupby(feat)["views"]
            .agg(["median", "mean", "count"])
            .reset_index()
        )
        grp.columns = [feat, "median_views", "mean_views", "video_count"]
        grp = grp.sort_values("median_views", ascending=False)

        rows = []
        for _, row in grp.iterrows():
            key = row[feat]
            if labels and isinstance(key, (int, np.integer)) and key < len(labels):
                label = labels[int(key)]
            else:
                label = str(key)
            rows.append(
                {
                    "group": label,
                    "raw_value": int(key) if isinstance(key, (int, np.integer)) else str(key),
                    "median_views": int(row["median_views"]),
                    "mean_views": int(row["mean_views"]),
                    "video_count": int(row["video_count"]),
                }
            )
        output[feat] = rows
    return output


def summary_stats(df: pd.DataFrame) -> dict:
    """High-level dataset summary."""
    threshold = df["views"].quantile(VIRAL_PERCENTILE / 100)
    return {
        "total_videos": len(df),
        "viral_threshold_views": int(threshold),
        "viral_video_count": int((df["views"] >= threshold).sum()),
        "median_views": int(df["views"].median()),
        "mean_views": int(df["views"].mean()),
        "max_views": int(df["views"].max()),
        "min_views": int(df["views"].min()),
        "viral_percentile": VIRAL_PERCENTILE,
    }


def run(df: pd.DataFrame) -> dict:
    """Run all analyses and return a single results dict."""
    return {
        "summary": summary_stats(df),
        "correlations": correlations(df),
        "viral_vs_rest": viral_vs_rest(df),
        "optimal_ranges": optimal_ranges(df),
        "group_averages": group_averages(df),
    }
