"""
Generates structured 50-second YouTube Shorts scripts via the Claude API.

Output schema:
  title: str
  segments: list of {
    type: "hook" | "point" | "cta"
    headline: str          – large on-screen text (≤8 words)
    body: str              – supporting text (≤15 words)
    narration: str         – full sentence read aloud
    duration: int          – seconds (all segments sum to ~50)
    bg_color: str          – hex
    accent_color: str      – hex
    animation: "slide_up" | "fade" | "zoom"
  }
"""

import json
import os
import anthropic

_SYSTEM = """\
You are a viral YouTube Shorts scriptwriter. You write punchy, fast-paced scripts
structured as JSON for automated video rendering. Every script must be exactly
50 seconds total. Use high-contrast colour palettes.

Return ONLY valid JSON — no markdown fences, no prose.
"""

_PALETTE_POOL = [
    {"bg_color": "#0f0c29", "accent_color": "#fc466b"},
    {"bg_color": "#1a1a2e", "accent_color": "#e94560"},
    {"bg_color": "#0d1b2a", "accent_color": "#00b4d8"},
    {"bg_color": "#1b1b2f", "accent_color": "#f5a623"},
    {"bg_color": "#12002f", "accent_color": "#a855f7"},
]

_USER_TMPL = """\
Topic: {topic}

Write a YouTube Shorts script as JSON with this exact shape:
{{
  "title": "<punchy title ≤ 60 chars>",
  "segments": [
    {{
      "type": "hook",
      "headline": "<≤8 words, grabs attention>",
      "body": "<≤15 words, amplifies hook>",
      "narration": "<1-2 sentences spoken aloud>",
      "duration": <5-8>,
      "bg_color": "<hex>",
      "accent_color": "<hex>",
      "animation": "<slide_up|fade|zoom>"
    }},
    ... 4-6 more segments of type "point" ...
    {{
      "type": "cta",
      "headline": "<call to action>",
      "body": "<follow / like / comment prompt>",
      "narration": "<1 sentence>",
      "duration": <4-6>,
      "bg_color": "<hex>",
      "accent_color": "<hex>",
      "animation": "fade"
    }}
  ]
}}

Rules:
- Total duration of all segments MUST equal exactly 50 seconds.
- Each segment has a unique bg_color from a dark palette.
- Headlines ≤ 8 words, body ≤ 15 words.
- Narration is punchy and matches the on-screen text.
- animation is one of: slide_up, fade, zoom
"""


def generate_script(topic: str, api_key: str | None = None) -> dict:
    """Call Claude to generate a structured script for *topic*."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": _USER_TMPL.format(topic=topic)}],
    )

    raw = response.content[0].text.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    script = json.loads(raw)
    _validate(script)
    return script


def _validate(script: dict) -> None:
    if "segments" not in script:
        raise ValueError("Script missing 'segments'")
    total = sum(s["duration"] for s in script["segments"])
    if abs(total - 50) > 2:
        raise ValueError(f"Duration sum {total}s != 50s")
    for seg in script["segments"]:
        for field in ("type", "headline", "body", "narration", "duration", "bg_color", "accent_color", "animation"):
            if field not in seg:
                raise ValueError(f"Segment missing field '{field}': {seg}")
