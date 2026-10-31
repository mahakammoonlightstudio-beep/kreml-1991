# IO-flow test: save via the command bar, view the dossier, load from the
# command bar, and resume from the title screen. Input is scripted; everything
# after the scripted list falls back to EOF-driven random choices.
import io
import os
import pathlib
import sys
import builtins
from contextlib import redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from kreml import engine, persistence   # noqa: E402
from kreml.state import STATS           # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
HALL = REPO / "hall_of_fame.txt"


def with_inputs(script: list[str]):
    """Route builtins.input to a scripted queue; EOF afterwards."""
    it = iter(script)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    builtins.input = fake_input


def stage(name: str, stats_over: dict, script: list[str], must_contain: list[str]) -> bool:
    buf = io.StringIO()
    with_inputs(script)
    old_init = engine.Kremlin.__init__

    def patched_init(self, seed=None, mode="medium", timeline="rails"):
        self.mode = mode
        self.timeline = "rails"
        self.year = 1964
        self.end_year = 1991
        self.name = "Comrade Secretary"
        self.stats = {"ECONOMY": 55, "MILITARY": 70, "ORDER": 75,
                      "FAITH": 52, "PRESTIGE": 62}
        self.stats.update(stats_over)
        self.flags = set()
        self.pending = []
        self.used_events = set()
        self.used_directives = set()
        self.used_focus = set()
        self.lifelines = 3
        self.death_reason = None
        self.putschist = False
        self.ledger = []
        self.shown_press = set()
        self.hard_currency = 40
        self.court = {"old_guard": 50, "reformers": 50, "military": 50}
        self.deposed = False
        self.directive_uses = {}
        self.focus_uses = {}
        self.path = None
        self.history = []
        self.influence = 8
        self.order = None
        self.agenda = None
        self.agenda_log = []
        self.hesitations = 0
        self.rng = __import__("random").Random(11)
    engine.Kremlin.__init__ = patched_init
    ok = True
    try:
        with redirect_stdout(buf):
            engine.run(seed=11)
    except Exception as exc:
        print(f"[FAIL] {name}: engine raised {exc!r}")
        ok = False
    finally:
        engine.Kremlin.__init__ = old_init
        builtins.input = input
    out = buf.getvalue()
    for needle in must_contain:
        if needle not in out:
            print(f"[FAIL] {name}: missing line {needle!r}")
            ok = False
    if ok:
        print(f"[PASS] {name}")
    return ok


def main() -> int:
    ok = True
    # the engine writes hall-of-fame records; keep the real one intact
    backup = HALL.read_bytes() if HALL.exists() else None
    try:                              # a stale save would hijack the scripted input
        os.remove(persistence.SAVE_FILE)
    except OSError:
        pass
    ok &= stage("save+dossier+load via command bar", {s: 88 for s in STATS},
                # difficulty=2 (medium), timeline=1 (rails), name, mandate=2,
                # then the command bar: s save, d dossier, l load
                ["2", "1", "A. Sekretar", "2", "s", "d", "l"],
                ["Save filed for 1964", "DOSSIER", "State restored: 1964",
                 "FOREIGN PRESS"])
    assert persistence.has_save(), "save file should still exist after session 1"
    ok &= stage("resume from title screen", {s: 88 for s in STATS}, ["1"],
                ["A saved game exists", "Welcome back"])
    # cleanup the artifacts this test created — but never the real hall of fame
    for f in (persistence.SAVE_FILE, HALL):
        try:
            os.remove(f)
        except OSError:
            pass
    if backup is not None:
        HALL.write_bytes(backup)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
