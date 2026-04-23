from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


class Scene(BaseModel):
    id: int
    duration: float
    headline: str
    subtext: str
    bg_color_start: str
    bg_color_end: str
    accent_color: str
    animation: Literal["slide_up", "fade_in", "zoom_in"]
    transition: Literal["fade", "slide_left", "wipe"]

    @field_validator("duration")
    @classmethod
    def clamp_duration(cls, v: float) -> float:
        return max(3.0, min(v, 15.0))

    @field_validator("bg_color_start", "bg_color_end", "accent_color", mode="before")
    @classmethod
    def ensure_hex(cls, v: str) -> str:
        if not v.startswith("#"):
            v = "#" + v
        return v


class Script(BaseModel):
    topic: str
    title: str
    hook: str
    scenes: list[Scene]
    total_duration: float
