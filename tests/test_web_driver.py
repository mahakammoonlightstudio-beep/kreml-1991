"""Checks for the browser build's replay driver (docs/play/kreml_web.py).

The browser cannot block on a keystroke, so the driver replays the game from
1964 with every answer collected so far and stops at the next question. These
tests run that driver under CPython and assert the contract the page relies on:

  * a replay is deterministic (same seed + answers → same transcript),
  * the replayed prefix never changes (so the page can only append),
  * echoing answers keeps the transcript readable,
  * save/load typed at the command bar still work inside a session,
  * a finished run reports done instead of hanging.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs", "play"))

from kreml import persistence, ui                      # noqa: E402
from kreml.content import endings                      # noqa: E402
import kreml_web                                       # noqa: E402

PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"[PASS] {name}")
    except AssertionError as exc:
        FAIL.append(name)
        print(f"[FAIL] {name}: {exc}")


class sandbox:
    """Keep saves and hall-of-fame records out of the real repo."""

    def __enter__(self):
        self.tmp = tempfile.mkdtemp()
        self.saved = (persistence.SAVE_FILE, endings.HALL_FILE)
        persistence.SAVE_FILE = os.path.join(self.tmp, "save.json")
        endings.HALL_FILE = os.path.join(self.tmp, "hall.txt")
        return self

    def __exit__(self, *exc):
        persistence.SAVE_FILE, endings.HALL_FILE = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)
        return False


def session(seed: int = 42) -> kreml_web.Session:
    return kreml_web.Session(game_root=ROOT, seed=seed)


def at_command_bar(s: kreml_web.Session) -> bool:
    tail = [ln for ln in s.transcript.split("\n") if ln.strip()]
    return bool(tail) and "[Enter] proceed" in tail[-1]


def next_answer(s: kreml_web.Session) -> str:
    return "" if at_command_bar(s) else "1"


def play_to_command_bar(s: kreml_web.Session, limit: int = 60) -> None:
    """Answer menus inside a year until the command bar is waiting again."""
    for _ in range(limit):
        if at_command_bar(s):
            return
        s.answer("1")
    raise AssertionError("never reached the command bar")


def play(s: kreml_web.Session, limit: int = 400) -> dict:
    """Answer until the game ends; returns the last driver result."""
    out = s.start("medium", "rails")
    out = s.answer("Comrade Test")           # the name for the history books
    out = s.answer("2")                      # the mandate
    for _ in range(limit):
        if out["done"]:
            return out
        out = s.answer(next_answer(s))
    raise AssertionError(f"game did not finish in {limit} answers")


# ----------------------------------------------------------------------
def t_first_prompt_and_prefix() -> None:
    with sandbox():
        s = session()
        out = s.start("medium", "rails")
        assert out["reset"] is True, "the first batch must reset the terminal"
        assert out["done"] is False, "a fresh game must wait for a name"
        assert "Your name for the history books" in out["text"], out["text"][-200:]
        assert "BALANCED" in out["text"], "the chosen difficulty is skipped, not asked"

        nxt = s.answer("Comrade Test")
        assert nxt["reset"] is False, "the replayed prefix must not change"
        assert "Comrade Test" in nxt["text"], "answers are echoed into the transcript"
        assert nxt["text"].startswith("Comrade Test"), nxt["text"][:80]


def t_replay_is_deterministic() -> None:
    with sandbox():
        a, b = session(7), session(7)
        for s in (a, b):
            s.start("medium", "rails")
            for line in ("Tester", "1", "2", "1", "3", "1", ""):
                s.answer(line)
        assert a.transcript == b.transcript, "same seed + answers must replay identically"

        c = session(8)
        c.start("medium", "rails")
        c.answer("Tester")
        assert c.transcript != a.transcript, "a different seed must be a different Union"


def t_transcript_prefix_is_stable() -> None:
    with sandbox():
        s = session()
        s.start("medium", "rails")
        previous = s.transcript
        for line in ("Tester", "2", "1", "2", "1", "1", ""):
            out = s.answer(line)
            assert out["reset"] is False, f"reset after answer {line!r}"
            assert s.transcript.startswith(previous), "the transcript rewound"
            assert out["text"], "every answer should produce new output"
            previous = s.transcript


def t_command_bar_save_and_load() -> None:
    with sandbox():
        s = session()
        s.start("medium", "rails")
        s.answer("Tester")
        s.answer("2")
        assert at_command_bar(s), "after the mandate the command bar should be waiting"
        out = s.answer("s")
        assert "Save filed" in out["text"], out["text"][-300:]
        s.answer("")                         # play 1964: focus, directive, events
        play_to_command_bar(s)
        assert "YEAR 1964" in s.transcript
        out = s.answer("l")                  # back to the saved year
        assert "State restored" in out["text"], out["text"][-300:]
        assert "1964" in s.transcript[-4000:]


def t_boot_never_asks_to_resume() -> None:
    """A save left in the folder must not derail a replay."""
    with sandbox():
        s = session()
        s.start("medium", "rails")
        s.answer("Tester")
        s.answer("2")
        s.answer("s")                        # now kreml_save.json exists
        other = session()                    # a second session, same folder
        out = other.start("medium", "rails")
        assert "A saved game exists" not in out["text"], "the boot probe leaked into the replay"
        assert "Your name for the history books" in out["text"]


def t_finished_run_ends_cleanly() -> None:
    with sandbox():
        s = session()
        out = play(s)
        assert out["done"] is True
        assert "Legacy score" in s.transcript, "an ending must be reached"
        assert "Traceback" not in s.transcript, "the game must not crash"
        after = s.answer("1")
        assert after["done"] is True and after["text"] == "", "a finished run takes no input"


def t_colours_do_not_leak_out() -> None:
    before = (ui.ANIM, ui.DRAMA, ui._use_colour)
    with sandbox():
        s = session()
        out = s.start("medium", "rails")
        assert "\x1b[" in out["text"], "the browser terminal wants coloured output"
    assert (ui.ANIM, ui.DRAMA, ui._use_colour) == before, "ui globals must be restored"


def t_snapshot_restores_the_same_run() -> None:
    with sandbox():
        s = session(11)
        s.start("medium", "rails")
        s.answer("Tester")
        s.answer("2")
        snap = s.snapshot()
        assert snap["seed"] == 11 and snap["mode"] == "medium"
        assert snap["answers"] == ["Tester", "2"]

        resumed = kreml_web.Session(game_root=ROOT)
        out = resumed.restore(snap)
        assert out["reset"] is True
        assert resumed.transcript == s.transcript, "restoring replays the same session"


def main() -> int:
    check("web: first prompt & append-only prefix", t_first_prompt_and_prefix)
    check("web: replay is deterministic", t_replay_is_deterministic)
    check("web: transcript prefix stays stable", t_transcript_prefix_is_stable)
    check("web: save & load at the command bar", t_command_bar_save_and_load)
    check("web: boot never offers to resume", t_boot_never_asks_to_resume)
    check("web: a finished run ends cleanly", t_finished_run_ends_cleanly)
    check("web: colours do not leak into other runs", t_colours_do_not_leak_out)
    check("web: snapshot/restore round-trip", t_snapshot_restores_the_same_run)
    print()
    if FAIL:
        print(f"{len(FAIL)} failed, {len(PASS)} passed")
        return 1
    print(f"{len(PASS)}/{len(PASS)} web driver checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
