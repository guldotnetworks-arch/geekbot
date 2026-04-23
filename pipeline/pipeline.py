"""
Orchestrates: topic → script → rendered MP4.
"""

from __future__ import annotations

import json
from pathlib import Path

from .script_generator import generate_script
from .graphics_renderer import render_video


def run(
    topic: str,
    output_dir: str | Path = "output",
    api_key: str | None = None,
    save_script: bool = True,
) -> dict:
    """
    Full pipeline: topic string → vertical 9:16 MP4.

    Returns a dict with keys: title, script_path, video_path.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/2] Generating script for: {topic!r}")
    script = generate_script(topic, api_key=api_key)

    slug = _slugify(script.get("title", topic))

    if save_script:
        script_path = output_dir / f"{slug}.json"
        script_path.write_text(json.dumps(script, indent=2))
        print(f"      Script saved → {script_path}")
    else:
        script_path = None

    total_dur = sum(s["duration"] for s in script["segments"])
    print(f"      Segments: {len(script['segments'])}  |  Total duration: {total_dur}s")

    video_path = output_dir / f"{slug}.mp4"
    print(f"[2/2] Rendering video → {video_path}")
    render_video(script, video_path)
    print(f"      Done. Output: {video_path}")

    return {
        "title": script.get("title"),
        "script_path": str(script_path) if script_path else None,
        "video_path": str(video_path),
    }


def run_from_script(script_path: str | Path, output_dir: str | Path = "output") -> dict:
    """Render an already-generated script JSON without calling the API."""
    script_path = Path(script_path)
    script = json.loads(script_path.read_text())
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(script.get("title", script_path.stem))
    video_path = output_dir / f"{slug}.mp4"

    print(f"Rendering {script_path.name} → {video_path}")
    render_video(script, video_path)
    return {"title": script.get("title"), "video_path": str(video_path)}


def _slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:60]
