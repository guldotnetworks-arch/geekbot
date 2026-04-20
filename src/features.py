"""
Feature extraction from raw YouTube API video records.

Produces a flat dict per video that pandas can consume directly.
Every feature is numeric or boolean (cast to int) so the analyzer
can run correlations and group comparisons without further encoding.
"""

import re
from datetime import datetime, timezone
from typing import Any

import isodate

# Words consistently found in high-engagement titles
EMOTIONAL_WORDS = {
    "shocking", "unbelievable", "insane", "incredible", "amazing", "epic",
    "crazy", "emotional", "heartbreaking", "hilarious", "terrifying",
    "mind-blowing", "stunning", "outrageous", "disgusting", "beautiful",
    "secret", "exposed", "caught", "banned", "deleted", "leaked",
    "surprising", "unexpected", "impossible", "dangerous", "extreme",
    "viral", "breaking", "urgent", "warning", "exclusive", "rare",
    "worst", "best", "biggest", "smallest", "fastest", "funniest",
}

POWER_WORDS = {
    "how", "why", "what", "when", "who", "where",
    "never", "always", "every", "must", "need", "should",
    "free", "new", "now", "today", "finally", "still",
    "just", "only", "last", "first",
}


def _safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _duration_seconds(iso_duration: str) -> int:
    try:
        return int(isodate.parse_duration(iso_duration).total_seconds())
    except Exception:
        return 0


def _title_features(title: str) -> dict:
    words = title.split()
    lower = title.lower()
    token_set = set(re.findall(r"[a-z]+", lower))

    caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
    numbers_in_title = len(re.findall(r"\d+", title))
    brackets = len(re.findall(r"[\[\(]", title))

    return {
        "title_len": len(title),
        "title_word_count": len(words),
        "title_has_question": int("?" in title),
        "title_has_exclamation": int("!" in title),
        "title_has_number": int(bool(numbers_in_title)),
        "title_number_count": numbers_in_title,
        "title_caps_word_count": caps_words,
        "title_has_brackets": int(brackets > 0),
        "title_bracket_count": brackets,
        "title_emotional_word_count": len(token_set & EMOTIONAL_WORDS),
        "title_power_word_count": len(token_set & POWER_WORDS),
        "title_colon": int(":" in title),
        "title_pipe": int("|" in title),
        "title_emoji_count": len(re.findall(r"[^\u0000-\u024F]", title)),
    }


def _description_features(desc: str) -> dict:
    if not desc:
        return {
            "desc_len": 0,
            "desc_line_count": 0,
            "desc_link_count": 0,
            "desc_hashtag_count": 0,
            "desc_timestamp_count": 0,
            "desc_has_chapters": 0,
            "desc_cta_count": 0,
        }

    links = len(re.findall(r"https?://\S+", desc))
    hashtags = len(re.findall(r"#\w+", desc))
    timestamps = len(re.findall(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", desc))
    # CTA phrases common in high-performing videos
    ctas = len(re.findall(
        r"\b(subscribe|like|comment|share|follow|click|watch|join|buy|get)\b",
        desc.lower(),
    ))

    return {
        "desc_len": len(desc),
        "desc_line_count": desc.count("\n"),
        "desc_link_count": links,
        "desc_hashtag_count": hashtags,
        "desc_timestamp_count": timestamps,
        "desc_has_chapters": int(timestamps >= 3),
        "desc_cta_count": ctas,
    }


def _timing_features(published_at: str) -> dict:
    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except Exception:
        return {
            "upload_hour": -1,
            "upload_day_of_week": -1,
            "upload_month": -1,
            "upload_year": -1,
            "upload_is_weekend": 0,
        }

    return {
        "upload_hour": dt.hour,
        "upload_day_of_week": dt.weekday(),  # 0=Monday, 6=Sunday
        "upload_month": dt.month,
        "upload_year": dt.year,
        "upload_is_weekend": int(dt.weekday() >= 5),
    }


def _engagement_features(stats: dict, duration_s: int) -> dict:
    views = _safe_int(stats.get("viewCount"))
    likes = _safe_int(stats.get("likeCount"))
    comments = _safe_int(stats.get("commentCount"))

    like_rate = likes / views if views > 0 else 0.0
    comment_rate = comments / views if views > 0 else 0.0
    views_per_second = views / duration_s if duration_s > 0 else 0.0

    return {
        "views": views,
        "likes": likes,
        "comments": comments,
        "like_rate": like_rate,
        "comment_rate": comment_rate,
        "engagement_rate": like_rate + comment_rate,
        "views_per_second_duration": views_per_second,
        "comments_disabled": int(stats.get("commentCount") is None),
        "likes_hidden": int(stats.get("likeCount") is None),
    }


def _channel_features(channel: dict) -> dict:
    ch_stats = channel.get("statistics", {})
    subscribers = _safe_int(ch_stats.get("subscriberCount"))
    total_videos = _safe_int(ch_stats.get("videoCount"))

    return {
        "channel_subscribers": subscribers,
        "channel_total_videos": total_videos,
        "channel_subscriber_bucket": _subscriber_bucket(subscribers),
    }


def _subscriber_bucket(subs: int) -> int:
    """Ordinal bucket: 0=<1K, 1=1K-10K, 2=10K-100K, 3=100K-1M, 4=1M-10M, 5=10M+"""
    thresholds = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]
    for i, t in enumerate(thresholds):
        if subs < t:
            return i
    return len(thresholds)


def extract(video: dict) -> dict | None:
    """Return a flat feature dict for one raw API video record, or None if malformed."""
    snippet = video.get("snippet")
    stats = video.get("statistics")
    content = video.get("contentDetails")
    if not (snippet and stats and content):
        return None

    views = _safe_int(stats.get("viewCount"))
    if views == 0:
        return None

    duration_s = _duration_seconds(content.get("duration", "PT0S"))
    if duration_s == 0:
        return None

    row: dict = {"video_id": video.get("id", "")}
    row.update(_title_features(snippet.get("title", "")))
    row.update(_description_features(snippet.get("description", "")))
    row.update(_timing_features(snippet.get("publishedAt", "")))
    row.update(_engagement_features(stats, duration_s))
    row.update(_channel_features(video.get("_channel", {})))

    row["duration_seconds"] = duration_s
    row["duration_minutes"] = duration_s / 60
    row["tag_count"] = len(snippet.get("tags", []))
    row["category_id"] = snippet.get("categoryId", "0")
    row["default_language"] = snippet.get("defaultLanguage", "")
    row["has_captions"] = int(content.get("caption", "false") == "true")
    row["definition_hd"] = int(content.get("definition", "") == "hd")
    row["is_short"] = int(duration_s <= 60)

    return row
