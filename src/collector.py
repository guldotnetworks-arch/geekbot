"""
YouTube Data API v3 collector.

Fetches up to `target` videos using:
  1. Trending videos across all 18 content categories (cheapest: 1 unit/call)
  2. Keyword search for high-view-count videos to fill any gap (100 units/call)
  3. Batch video-detail lookups (videos.list, 50 per call, 1 unit/call)
  4. Batch channel lookups for subscriber counts (channels.list, 50 per call, 1 unit/call)

Saves raw API responses to data/raw_videos.json so reruns skip collection.
YouTube Data API v3 daily quota: 10,000 units.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

RAW_CACHE = Path("data/raw_videos.json")

# All YouTube video category IDs (US region)
CATEGORY_IDS = [
    "1",   # Film & Animation
    "2",   # Autos & Vehicles
    "10",  # Music
    "15",  # Pets & Animals
    "17",  # Sports
    "19",  # Travel & Events
    "20",  # Gaming
    "22",  # People & Blogs
    "23",  # Comedy
    "24",  # Entertainment
    "25",  # News & Politics
    "26",  # Howto & Style
    "27",  # Education
    "28",  # Science & Technology
    "29",  # Nonprofits & Activism
]

# Search queries that surface viral content from different eras
VIRAL_SEARCH_QUERIES = [
    "most viewed 2024",
    "viral video 2024",
    "most viral 2023",
    "trending viral clips",
    "viral moments 2024",
    "viral challenge 2024",
    "viral prank 2023",
    "viral music video 2024",
    "viral sports moment",
    "viral funny 2024",
]


def _build_client(api_key: str):
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)


def _safe_request(request, retries: int = 3, backoff: float = 2.0):
    for attempt in range(retries):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status in (429, 500, 503) and attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
            else:
                raise


def fetch_trending_ids(client, region: str = "US") -> list[str]:
    """Return up to 50 trending video IDs per category."""
    ids: list[str] = []
    for cat_id in CATEGORY_IDS:
        try:
            resp = _safe_request(
                client.videos().list(
                    part="id",
                    chart="mostPopular",
                    regionCode=region,
                    videoCategoryId=cat_id,
                    maxResults=50,
                )
            )
            ids.extend(item["id"] for item in resp.get("items", []))
        except HttpError:
            pass  # category may not have trending in this region
    return list(dict.fromkeys(ids))  # deduplicate preserving order


def fetch_search_ids(client, needed: int) -> list[str]:
    """Fill remaining quota via search.list (100 units/call, up to 50 results/call)."""
    ids: list[str] = []
    per_query = max(1, needed // len(VIRAL_SEARCH_QUERIES) + 1)

    for query in VIRAL_SEARCH_QUERIES:
        if len(ids) >= needed:
            break
        page_token: Optional[str] = None
        collected = 0
        while collected < per_query and len(ids) < needed:
            try:
                resp = _safe_request(
                    client.search().list(
                        part="id",
                        q=query,
                        type="video",
                        order="viewCount",
                        maxResults=50,
                        pageToken=page_token,
                    )
                )
            except HttpError:
                break
            for item in resp.get("items", []):
                vid_id = item["id"].get("videoId")
                if vid_id:
                    ids.append(vid_id)
                    collected += 1
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    return list(dict.fromkeys(ids))


def fetch_video_details(client, video_ids: list[str]) -> list[dict]:
    """Batch fetch full video details (50 per API call)."""
    details: list[dict] = []
    chunks = [video_ids[i : i + 50] for i in range(0, len(video_ids), 50)]
    for chunk in tqdm(chunks, desc="Fetching video details"):
        try:
            resp = _safe_request(
                client.videos().list(
                    part="snippet,statistics,contentDetails,status",
                    id=",".join(chunk),
                )
            )
            details.extend(resp.get("items", []))
        except HttpError:
            pass
    return details


def fetch_channel_details(client, channel_ids: list[str]) -> dict[str, dict]:
    """Batch fetch channel statistics keyed by channel ID."""
    result: dict[str, dict] = {}
    unique = list(dict.fromkeys(channel_ids))
    chunks = [unique[i : i + 50] for i in range(0, len(unique), 50)]
    for chunk in tqdm(chunks, desc="Fetching channel details"):
        try:
            resp = _safe_request(
                client.channels().list(
                    part="statistics,snippet",
                    id=",".join(chunk),
                )
            )
            for item in resp.get("items", []):
                result[item["id"]] = item
        except HttpError:
            pass
    return result


def collect(api_key: str, target: int = 1000, region: str = "US") -> list[dict]:
    """
    Collect `target` viral videos with full metadata.
    Caches results to data/raw_videos.json on success.
    Returns list of enriched video dicts.
    """
    if RAW_CACHE.exists():
        print(f"Loading cached data from {RAW_CACHE}")
        with RAW_CACHE.open() as f:
            return json.load(f)

    client = _build_client(api_key)

    print("Step 1/4  Fetching trending video IDs...")
    trending_ids = fetch_trending_ids(client, region)
    print(f"  Got {len(trending_ids)} trending IDs")

    remaining = max(0, target - len(trending_ids))
    search_ids: list[str] = []
    if remaining > 0:
        print(f"Step 2/4  Fetching {remaining} more IDs via search...")
        search_ids = fetch_search_ids(client, remaining)
        print(f"  Got {len(search_ids)} search IDs")

    all_ids = list(dict.fromkeys(trending_ids + search_ids))[:target]
    print(f"Step 3/4  Fetching details for {len(all_ids)} videos...")
    videos = fetch_video_details(client, all_ids)

    channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v]
    print(f"Step 4/4  Fetching {len(set(channel_ids))} channel profiles...")
    channels = fetch_channel_details(client, channel_ids)

    # Embed channel data into each video record
    for video in videos:
        ch_id = video.get("snippet", {}).get("channelId", "")
        video["_channel"] = channels.get(ch_id, {})

    RAW_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with RAW_CACHE.open("w") as f:
        json.dump(videos, f)
    print(f"Saved {len(videos)} videos to {RAW_CACHE}")

    return videos
