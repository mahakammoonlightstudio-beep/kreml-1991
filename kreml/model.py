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
    era: str = ""            # "EARLY" | "MIDDLE" | "LATE" | "NEW" | "" (scripted/queued)
    once: bool = False
    requires: dict[str, Any] = field(default_factory=dict)
    alt: bool = False        # alternate-history content: locked on the rails


@dataclass(frozen=True)
class Directive:
    id: str
    label: str
    desc: str
    group: str
    ops: dict[str, Any] = field(default_factory=dict)
    requires: dict[str, Any] = field(default_factory=dict)
    once: bool = False
    alt: bool = False        # alternate-history content: locked on the rails


@dataclass(frozen=True)
class Action:
    """A small personal matter the Secretary can additionally pursue each year."""
    id: str
    label: str
    desc: str
    ops: dict[str, Any] = field(default_factory=dict)
    requires: dict[str, Any] = field(default_factory=dict)
    once: bool = False
    alt: bool = False


@dataclass(frozen=True)
class Timeline:
    """A starting scenario: where history hands you the keys.

    `id` is persisted, so timelines may be added freely; `year`/`end_year`
    move the whole run, `stats`/`flags`/`court`/`hc` overwrite the opening
    position, and `mandate` says whether the 1964 Politburo vote still
    happens (it does not in timelines already past 1964).
    """
    id: str
    label: str
    desc: str
    year: int = 1964
    end_year: int = 1991
    stats: dict[str, int] = field(default_factory=dict)
    flags: tuple[str, ...] = ()
    court: dict[str, int] = field(default_factory=dict)
    hc: int = 50
    mandate: bool = True
