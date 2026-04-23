#!/usr/bin/env python3
"""
YouTube Shorts Pipeline
-----------------------
Usage:
  python main.py "5 Python tricks that will blow your mind"
  python main.py "Black holes explained" --output out/black_holes.mp4
  python main.py "Morning routine tips" --script-only
"""

from __future__ import annotations

import sys
from pathlib import Path

import click


@click.command()
@click.argument("topic")
@click.option(
    "--output", "-o",
    default="output/short.mp4",
    show_default=True,
    help="Path for the rendered MP4.",
)
@click.option(
    "--script-only",
    is_flag=True,
    default=False,
    help="Generate and print the script without rendering video.",
)
def main(topic: str, output: str, script_only: bool) -> None:
    """Generate a YouTube Short from TOPIC: writes a 50-second script,
    builds motion-graphic scenes, and renders a vertical 1080×1920 MP4."""

    click.echo(f"\n{'─' * 56}")
    click.echo(f"  YouTube Shorts Pipeline")
    click.echo(f"  Topic : {topic}")
    click.echo(f"{'─' * 56}\n")

    # ── 1. Script generation ─────────────────────────────────────────────────
    click.echo("Step 1/2  Generating script with Claude…")
    from pipeline.script_generator import generate_script

    try:
        script = generate_script(topic)
    except Exception as exc:
        click.echo(f"\n[ERROR] Script generation failed: {exc}", err=True)
        sys.exit(1)

    click.echo(f"\n  Title : {script.title}")
    click.echo(f"  Hook  : {script.hook}")
    click.echo(f"  Scenes: {len(script.scenes)}  |  Duration: {script.total_duration:.1f}s\n")
    for i, scene in enumerate(script.scenes):
        click.echo(
            f"    {i + 1:>2}. [{scene.duration:.1f}s] {scene.animation:<9}  "
            f"{scene.headline}  /  {scene.subtext}"
        )

    if script_only:
        click.echo("\n(--script-only: skipping render)\n")
        return

    # ── 2. Video render ──────────────────────────────────────────────────────
    click.echo(f"\nStep 2/2  Rendering video → {output}")
    from pipeline.graphics import render_video

    try:
        render_video(script, output)
    except Exception as exc:
        click.echo(f"\n[ERROR] Render failed: {exc}", err=True)
        sys.exit(1)

    out = Path(output).resolve()
    click.echo(f"\n{'─' * 56}")
    click.echo(f"  Done!  {out}")
    click.echo(f"  Format : 1080×1920  9:16  30fps  H.264")
    click.echo(f"  Length : ~{script.total_duration:.0f} seconds")
    click.echo(f"{'─' * 56}\n")


if __name__ == "__main__":
    main()
