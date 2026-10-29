"""Browser driver for КРЕМЛЬ 1991 — the real game, one answer at a time.

A browser cannot block *inside* Python waiting for a keystroke, so this driver
does the next best thing: it **replays**. Every time the page has one more
answer, the driver runs the whole game from 1964 again with the answers
collected so far, lets the output fall into a buffer, and stops the instant the
game asks for a line it does not have yet (``NeedInput``).

The game is deterministic for a given ``(seed, mode, timeline, answers)`` — the
RNG is re-seeded on every replay and nothing reads the clock — so the replayed
prefix is byte-identical and only the new suffix is sent to the page.

This module is plain Python: the browser loads it into Pyodide, and
``tests/test_web_driver.py`` runs it under CPython, which is how the replay
contract is verified without a browser.
"""
from __future__ import annotations

import builtins
import contextlib
import io
import os
import random
import sys
import traceback


class NeedInput(BaseException):
    """The game wants a line the page has not supplied yet.

    Deliberately a ``BaseException``: the game's own ``except (EOFError,
    KeyboardInterrupt)`` / ``except Exception`` handlers must not swallow it.
    """


class Session:
    """One browser session: a seed, a difficulty, a timeline, and the answers."""

    MAX_ANSWERS = 4000          # a runaway guard, not a game rule

    def __init__(self, game_root: str = "/game", seed: int | None = None) -> None:
        self.game_root = os.path.abspath(game_root)
        if self.game_root not in sys.path:
            sys.path.insert(0, self.game_root)
        self.seed = seed
        self.mode = None
        self.timeline = None
        self.answers: list[str] = []
        self.transcript = ""
        self.done = False

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def start(self, mode: str | None = None, timeline: str | None = None,
              seed: int | None = None) -> dict:
        """Begin a new run; returns the first batch of output."""
        self.mode = mode
        self.timeline = timeline
        if seed is not None:
            self.seed = seed
        elif self.seed is None:
            self.seed = random.SystemRandom().randrange(1, 2 ** 31)
        self.answers = []
        self.transcript = ""
        self.done = False
        out = self.run()
        out["reset"] = True
        return out

    def answer(self, text: str) -> dict:
        """Feed one line (the player's answer) and replay to the next prompt."""
        if self.done:
            return {"text": "", "reset": False, "done": True}
        if len(self.answers) >= self.MAX_ANSWERS:
            self.done = True
            return {"text": "\n\n[web build] too many answers — run stopped.\n",
                    "reset": False, "done": True}
        self.answers.append("" if text is None else str(text))
        return self.run()

    def snapshot(self) -> dict:
        """Everything needed to replay this run later (page: localStorage)."""
        return {"seed": self.seed, "mode": self.mode,
                "timeline": self.timeline, "answers": list(self.answers)}

    def restore(self, data: dict) -> dict:
        self.mode = data.get("mode")
        self.timeline = data.get("timeline")
        self.seed = data.get("seed")
        self.answers = [str(a) for a in data.get("answers") or []]
        self.transcript = ""
        self.done = False
        out = self.run()
        out["reset"] = True
        return out

    def run(self) -> dict:
        """Replay the game with the answers so far; return the new output."""
        from kreml import engine, ui, persistence

        saved = (ui.ANIM, ui.DRAMA, ui._use_colour)
        # Deterministic, coloured, instant: the browser terminal does the rest.
        ui.ANIM = False
        ui.DRAMA = False
        ui._use_colour = True

        # Never offer to resume at boot: the replay must always start at 1964.
        # ('l' typed later still reaches the real loader and works in-session.)
        real_load = persistence.load_game
        calls = {"n": 0}

        def load_probe(path=None):
            calls["n"] += 1
            if calls["n"] == 1:
                return None
            return real_load(path)

        persistence.load_game = load_probe
        answers = list(self.answers)
        buf = io.StringIO()
        done = False
        try:
            with contextlib.redirect_stdout(buf):
                with _stdin(answers):
                    engine.run(self.seed, mode=self.mode, timeline=self.timeline)
            done = True
        except NeedInput:
            done = False
        except BaseException:                      # surface it, never wedge
            if buf.tell():
                buf.write("\n")
            buf.write(traceback.format_exc())
            done = True
        finally:
            persistence.load_game = real_load
            ui.ANIM, ui.DRAMA, ui._use_colour = saved

        text = buf.getvalue().replace("\r\n", "\n")
        prefix = self.transcript
        reset = not text.startswith(prefix)
        new = text if reset else text[len(prefix):]
        self.transcript = text
        self.done = done
        return {"text": new, "reset": reset, "done": done}


# ----------------------------------------------------------------------
# stdin replacement
# ----------------------------------------------------------------------
@contextlib.contextmanager
def _stdin(answers: list[str]):
    """Echo a real prompt+answer into the transcript, or stop the replay."""
    original = builtins.input

    def fake_input(prompt: str = "") -> str:
        if prompt:
            sys.stdout.write(str(prompt))      # what the terminal would show
        if not answers:
            raise NeedInput()
        line = answers.pop(0)
        sys.stdout.write(str(line) + "\n")     # the echo of the typed answer
        return line

    builtins.input = fake_input
    try:
        yield
    finally:
        builtins.input = original
