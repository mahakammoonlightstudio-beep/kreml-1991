"""Tiny constructors shared by the content modules.

Content files stay PURE DATA; these helpers only keep the literals short and
give every event/directive the same defaults (including the `alt` marker that
locks alternate-history content on the historical rails).
"""
from __future__ import annotations

from ..model import Action, Directive, Event, Option


def opt(label: str, ops: dict, outcomes: str = "",
        requires: dict | None = None) -> Option:
    return Option(label=label, ops=ops, outcomes=outcomes, requires=requires or {})


def ev(id: str, title: str, text: str, options, *, era: str = "",
       once: bool = False, requires: dict | None = None,
       alt: bool = False) -> Event:
    return Event(id=id, title=title, text=text, options=tuple(options),
                 era=era, once=once, requires=requires or {}, alt=alt)


def directive(id: str, label: str, desc: str, group: str, ops: dict, *,
              requires: dict | None = None, once: bool = False,
              alt: bool = False) -> Directive:
    return Directive(id=id, label=label, desc=desc, group=group, ops=ops,
                     requires=requires or {}, once=once, alt=alt)


def action(id: str, label: str, desc: str, ops: dict, *,
           requires: dict | None = None, once: bool = False,
           alt: bool = False) -> Action:
    return Action(id=id, label=label, desc=desc, ops=ops,
                  requires=requires or {}, once=once, alt=alt)
