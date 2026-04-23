from __future__ import annotations

import json
import os

import anthropic
from dotenv import load_dotenv

from .models import Script

load_dotenv()

_client: anthropic.Anthropic | None = None

_SYSTEM = """\
You are a YouTube Shorts script writer. Create punchy, viral short-form video scripts.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
"""

_PROMPT = """\
Create a 50-second YouTube Shorts script about: {topic}

Requirements:
- 6–8 scenes; scene durations must sum to exactly 50 seconds
- Each scene headline: ≤8 words, bold and impactful
- Each scene subtext: ≤18 words, clarifies or supports the headline
- Dark, cinematic color theme with vibrant accent colors
- Vary animations across scenes: slide_up, fade_in, zoom_in
- Vary transitions across scenes: fade, slide_left, wipe
- First scene is the hook — grab attention immediately
- Last scene is the CTA — tell viewers to like/follow/subscribe

Return JSON matching this schema exactly (no other text):
{{
  "topic": "{topic}",
  "title": "catchy short title ≤60 chars",
  "hook": "opening hook line ≤15 words",
  "scenes": [
    {{
      "id": 1,
      "duration": 7.0,
      "headline": "Bold headline text",
      "subtext": "Supporting explanation text here",
      "bg_color_start": "#1a1a2e",
      "bg_color_end": "#16213e",
      "accent_color": "#e94560",
      "animation": "slide_up",
      "transition": "fade"
    }}
  ],
  "total_duration": 50.0
}}

Use a consistent dark theme (deep navy, charcoal, dark purple, etc.).
Pick vivid accent colors that match the topic's energy.
"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def generate_script(topic: str) -> Script:
    """Call Claude to generate a structured 50-second Shorts script."""
    client = _get_client()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": _PROMPT.format(topic=topic)}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if the model wraps the JSON anyway
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw

    data = json.loads(raw)
    script = Script(**data)

    # Clamp total_duration to the actual sum so downstream code is accurate
    script.total_duration = sum(s.duration for s in script.scenes)
    return script
