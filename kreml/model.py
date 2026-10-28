"""Shared data model for all content files.

Philosophy: content is DATA (frozen dataclasses), never logic. The engine
applies every effect through a tiny DSL (`ops.py`), and everything the player
sees is rendered by `ui.py`. Adding gameplay = adding data, not editing logic.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Option:
    label: str
    outcomes: str = ""
    ops: dict[str, Any] = field(default_factory=dict)
    requires: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Event:
    id: str
    title: str
    text: str
    options: tuple[Option, ...]
    era: str = ""            # "EARLY" | "MIDDLE" | "LATE" | "" (scripted/queued)
    once: bool = False
    requires: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Directive:
    id: str
    label: str
    desc: str
    group: str
    ops: dict[str, Any] = field(default_factory=dict)
    requires: dict[str, Any] = field(default_factory=dict)
    once: bool = False


@dataclass(frozen=True)
class Action:
    """A small personal matter the Secretary can additionally pursue each year."""
    id: str
    label: str
    desc: str
    ops: dict[str, Any] = field(default_factory=dict)
    requires: dict[str, Any] = field(default_factory=dict)
    once: bool = False
