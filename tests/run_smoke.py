# Smoke tests: run the engine headless (stdin EOF => the game chooses randomly)
# with buffed / crippled initial stats to exercise every code path.
import sys
import os
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from kreml import engine                              # noqa: E402
from kreml.state import STATS                         # noqa: E402
from kreml.content.modes import MODES                 # noqa: E402


def _patch(stats_over, mode="normal"):
    def patched_init(self, seed=None, mode=mode, timeline="rails"):
        if mode not in MODES:
            mode = "medium"
        self.mode = mode
        self.timeline = timeline or "rails"
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
        self.lifelines = MODES[mode]["lifelines"]
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
        self.rng = __import__("random").Random(seed)
    engine.Kremlin.__init__ = patched_init


def scenario(name: str, stats_over: dict, mode: str = "normal") -> bool:
    _patch(stats_over, mode)
    try:
        engine.run(seed=None, mode=mode)
        print(f"[PASS] {name}")
        return True
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"[FAIL] {name}: {exc}")
        return False


def main() -> int:
    ok = True
    # the engine appends hall-of-fame records; keep the real file intact
    hall = pathlib.Path(__file__).resolve().parent.parent / "hall_of_fame.txt"
    backup = hall.read_bytes() if hall.exists() else None
    try:
        ok &= scenario("full 1964-1991 run (BALANCED)", {s: 90 for s in STATS})
        ok &= scenario("collapse-run, IRON GRASP (economy near zero)",
                       {"ECONOMY": 4}, mode="hard")
        ok &= scenario("reform playground, SWEEPING REFORMS",
                       {"ECONOMY": 75, "ORDER": 60}, mode="easy")
        ok &= scenario("flash-crisis run (v6, clock unarmed)",
                       {"ECONOMY": 70}, mode="flash")
    finally:
        if backup is not None:
            hall.write_bytes(backup)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
