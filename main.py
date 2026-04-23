#!/usr/bin/env python3
"""
YouTube Shorts Pipeline – CLI entry point.

Usage:
  python main.py generate "The Science of Sleep"
  python main.py render path/to/script.json
"""

import os
import sys

import click
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """Generate viral YouTube Shorts from a topic."""


@cli.command()
@click.argument("topic")
@click.option("--output-dir", "-o", default="output", show_default=True, help="Output directory")
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key")
@click.option("--no-script", is_flag=True, help="Do not save the intermediate script JSON")
def generate(topic: str, output_dir: str, api_key: str | None, no_script: bool):
    """Generate a script AND render the video for TOPIC."""
    from pipeline.pipeline import run

    result = run(topic, output_dir=output_dir, api_key=api_key, save_script=not no_script)
    click.echo(f"\nTitle      : {result['title']}")
    if result["script_path"]:
        click.echo(f"Script     : {result['script_path']}")
    click.echo(f"Video      : {result['video_path']}")


@cli.command()
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--output-dir", "-o", default="output", show_default=True)
def render(script_path: str, output_dir: str):
    """Render a previously generated script JSON into an MP4."""
    from pipeline.pipeline import run_from_script

    result = run_from_script(script_path, output_dir=output_dir)
    click.echo(f"\nTitle : {result['title']}")
    click.echo(f"Video : {result['video_path']}")


if __name__ == "__main__":
    cli()
