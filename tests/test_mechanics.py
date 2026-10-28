# Mechanic-level checks for the v3 systems (no player input needed).
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from kreml import engine, ops, persistence          # noqa: E402
from kreml.state import Kremlin, STATS              # noqa: E402
from kreml.content import directives as DR          # noqa: E402
from kreml.content.modes import MODES               # noqa: E402
from kreml.content.endings import survival_outcome  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        fn()
        results.append((name, True, ""))
    except Exception as exc:
        results.append((name, False, str(exc)))


def t_queued_event():
    g = Kremlin(0)
    ops.apply_ops(g, {"queue": [(1, "nato_ultimatum_reply")]})
    g.year += 1                    # 1965: the delayed reply now comes due
    collected = engine.collect_events(g)
    assert any(e.id == "nato_ultimatum_reply" for e in collected), collected


def t_rested_softening():
    g = Kremlin(0)
    g.flags.add("rested")
    softened, used = ops.consume_rest(g, {"stats": {"ECONOMY": -4, "FAITH": 2}})
    assert used and softened["stats"]["ECONOMY"] == -2 and softened["stats"]["FAITH"] == 2
    # only one softening: flag is consumed
    _, used2 = ops.consume_rest(g, {"stats": {"ECONOMY": -4}})
    assert not used2


def t_random_tuple_op():
    g = Kremlin(0)
    ops.apply_ops(g, {"stats": {"ECONOMY": (2, 3)}})
    assert 57 <= g.stats["ECONOMY"] <= 58  # 55 + randint(2..3)


def t_conditional_directive():
    g = Kremlin(0)
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "kosygin_reforms" not in ids
    assert "legalize_cooperatives" not in ids
    g.flags.add("kosygin_pilot")
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "kosygin_reforms" in ids
    g.year = 1985
    g.flags.add("kosygin_full")
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "legalize_cooperatives" in ids
    ops.apply_ops(g, {"flag_add": "coops"})
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "price_reform" not in ids           # min_year 1988
    g.year = 1989
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "price_reform" in ids


def t_focus_gating():
    from kreml.content import actions as AC
    g = Kremlin(0)
    ids = {a.id for a in AC.available_actions(g)}
    assert "space_check" in ids                  # MILITARY 70 >= 50
    g.stats["MILITARY"] = 40
    ids = {a.id for a in AC.available_actions(g)}
    assert "space_check" not in ids


def t_coup_failure():
    g = Kremlin(0)
    g.stats["MILITARY"] = 30
    g.stats["ORDER"] = 30
    ops.apply_ops(g, {"special": "coup_defy"})
    assert g.dead_stat() is not None
    assert g.death_reason is not None


def t_coup_success_flags():
    g = Kremlin(0)
    g.stats["MILITARY"] = 60
    g.stats["ORDER"] = 60
    ops.apply_ops(g, {"special": "coup_defy"})
    assert "survived_coup" in g.flags


def t_war_attrition():
    g = Kremlin(0)
    g.flags.add("at_war")
    m0, e0, f0 = g.stats["MILITARY"], g.stats["ECONOMY"], g.stats["FAITH"]
    engine.apply_drift(g)
    assert g.stats["MILITARY"] == m0 - 1 - 2   # drift -1, war -2
    assert g.stats["ECONOMY"] == e0 - 2 - 1    # drift -2, war -1
    assert g.stats["FAITH"] == f0 - 1 - 1


def t_erа_and_clamps():
    g = Kremlin(0)
    g.year = 1985
    assert g.era == "LATE"
    g.stats["ECONOMY"] = 150
    ops.apply_ops(g, {"stats": {"PRESTIGE": -200}})
    assert g.stats["PRESTIGE"] == 0


def t_congress_year():
    g = Kremlin(0)
    g.year = 1970
    collected = engine.collect_events(g)
    assert collected[0].id == "plenum_1970", collected


def t_chernobyl_and_congress_1986():
    g = Kremlin(0)
    g.year = 1986
    collected = engine.collect_events(g)
    ids = [e.id for e in collected]
    assert "acceleration_1986" in ids and "chernobyl" in ids, ids
    # the quiet option plants the hidden flag
    ev = next(e for e in collected if e.id == "chernobyl")
    opts = {o.label: o for o in ev.options}
    ops.apply_ops(g, opts["Keep it quiet, evacuate quietly"].ops)
    assert "chernobyl_hidden" in g.flags


# ─────────────────────────────── v3 ───────────────────────────────
def t_difficulty_drift():
    g = Kremlin(0, mode="hard")
    assert g.lifelines == 2 and g.mode == "hard"
    g.year = 1970                       # EARLY era
    before = dict(g.stats)
    engine.apply_drift(g)
    want = MODES["hard"]["drift"]["EARLY"]
    for s, dv in want.items():
        assert g.stats[s] == before[s] + dv, s
    # easy mode: 5 reserves and gentler economy drift
    e = Kremlin(0, mode="easy")
    assert e.lifelines == MODES["easy"]["lifelines"] == 5
    even = dict(e.stats)
    e.year = 1987                       # LATE era
    engine.apply_drift(e)
    assert e.stats["ECONOMY"] == even["ECONOMY"] + MODES["easy"]["drift"]["LATE"]["ECONOMY"]


def t_save_load_roundtrip():
    tmp = pathlib.Path(__file__).resolve().parent / "_tmp_save.json"
    g = Kremlin(7, mode="hard")
    g.name = "Test Comrade"
    g.stats["FAITH"] = 88
    g.flags |= {"kosygin_full", "at_war"}
    g.pending = [(1990, "nato_ultimatum_reply")]
    g.used_events.add("chernobyl")
    g.used_directives.add("price_reform")
    g.lifelines = 1
    g.putschist = True
    g.ledger = [(1984, "directive: Price reform")]
    g.shown_press = {"quiet_market"}
    g.hard_currency = 66
    g.court = {"old_guard": 11, "reformers": 70, "military": 45}
    g.deposed = False
    ops.apply_ops(g, {"stats": {"ECONOMY": (3, 3), "ORDER": 5}})
    snap = g.rng.getstate()                 # snapshot AFTER the random roll
    try:
        ok = persistence.save_game(g, path=str(tmp))
        assert ok
        g2 = persistence.load_game(path=str(tmp))
        assert g2 is not None
        assert g2.name == "Test Comrade" and g2.year == 1964 and g2.mode == "hard"
        assert g2.stats["FAITH"] == 88 and g2.stats["ECONOMY"] == g.stats["ECONOMY"]
        assert g2.stats["ORDER"] == g.stats["ORDER"] == 80
        assert g2.flags == g.flags and g2.pending == [(1990, "nato_ultimatum_reply")]
        assert g2.used_events == {"chernobyl"} and g2.putschist
        assert g2.lifelines == 1 and g2.ledger == g.ledger and g2.shown_press == {"quiet_market"}
        assert g2.hard_currency == 66
        assert g2.court == {"old_guard": 11, "reformers": 70, "military": 45}
        assert g2.deposed is False
        assert g2.rng.getstate() == snap
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def t_near_miss_outcome():
    g = Kremlin(0)
    g.stats = {"ECONOMY": 90, "MILITARY": 90, "ORDER": 9, "FAITH": 90, "PRESTIGE": 90}
    tag, score_nm, hdr = survival_outcome(g)
    assert tag == "NEAR-MISS" and "PRAYER" in hdr, (tag, hdr)
    g3 = Kremlin(0)
    g3.stats = {s: 90 for s in STATS}
    _, score_plain, _ = survival_outcome(g3)
    assert score_nm < score_plain                       # the prayer costs 25 points
    g2 = Kremlin(0)
    g2.stats = {s: 90 for s in STATS}
    g2.flags.add("treaty_signed")
    tag2, score_ok, hdr2 = survival_outcome(g2)
    assert tag2 == "SURVIVED"
    base = sum(g2.stats.values()) + 2 * (g2.year - 1964)
    assert score_ok == base + 6                         # treaty bonus


def t_press_pick():
    g = Kremlin(0, mode="normal")
    g.year = 1986
    g.flags.add("kosygin_full")
    g.stats["FAITH"] = 25          # kill 'Queues and Machine Guns' (needs FAITH 30+)
    g.stats["ORDER"] = 50          # kill the iron headline as well
    engine._press_line(g)
    assert "quiet_market" in g.shown_press      # the only strong headline left
    # fallbacks never get consumed
    f = Kremlin(0)
    f.year = 1966
    engine._press_line(f)
    assert not f.shown_press
    # after a conditional is used up, a later year falls back without crashing
    g.shown_press.add("quiet_market")
    g.flags.clear()
    engine._press_line(g)


def t_new_directive_gates():
    g = Kremlin(0)
    g.year = 1990
    g.stats["FAITH"] = 55
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "new_union_treaty" in ids and "cadres_refresh" not in ids
    ops.apply_ops(g, {"stats": {"FAITH": -20}})     # now below the 55 threshold
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "new_union_treaty" not in ids
    g.stats["FAITH"] = 80
    g.flags.add("perestroika")
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "cadres_refresh" in ids
    ops.apply_ops(g, {"flag_add": "coops"})
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "special_economic_zone" in ids


def t_new_events_in_pools():
    from kreml.content import events as EV
    assert "helsinki_accords" in EV.RANDOM_POOLS["MIDDLE"]
    assert "vodka_campaign" in EV.RANDOM_POOLS["LATE"]
    assert "coal_miners_1989" in EV.SCRIPTED[1989]
    g = Kremlin(0)
    g.year = 1989
    ids = [e.id for e in engine.collect_events(g)]
    assert "wall_falls" in ids and "coal_miners_1989" in ids, ids
    # singapore_dream is gated behind a market path (requirement check, not draw)
    sg = EV.EVENTS["singapore_dream"]
    plain = Kremlin(0)
    ok, _ = ops.check_requires(plain, sg.requires)
    assert not ok
    market = Kremlin(0)
    market.flags.add("price_done")
    ok, _ = ops.check_requires(market, sg.requires)
    assert ok
    # vodka_campaign only opens mid-1980s
    early = Kremlin(0)
    early.year = 1975
    ok, _ = ops.check_requires(early, EV.EVENTS["vodka_campaign"].requires)
    assert not ok


def t_dossier_and_ledger():
    from kreml import dossier
    g = Kremlin(0)
    g.ledger = [(1984, "directive: Price reform"),
                (1985, "event: Chernobyl, 26 April 1986 → OK")]
    g.shown_press = {"fb_late"}
    dossier.show_roadmap(g)             # full render, must not raise
    g.pending = [(1985, "nato_ultimatum_reply")]
    dossier.show_roadmap(g)             # pipeline section too


# ─────────────────────────────── v4 ───────────────────────────────
def t_valas_and_court_ops():
    from kreml.state import FACTIONS
    g = Kremlin(0)
    ops.apply_ops(g, {"hc": (5, 5), "court": {"military": 60, "old_guard": -200}})
    assert g.hard_currency == 45
    assert g.court["military"] == 100          # clamped
    assert all(0 <= g.court[f] <= 100 for f in FACTIONS)
    assert g.court["old_guard"] == 0
    ops.apply_ops(g, {"hc": -500})
    assert g.hard_currency == 0


def t_valas_and_court_requirements():
    g = Kremlin(0)
    g.hard_currency = 20
    ok, _ = ops.check_requires(g, {"hc": 20})
    assert ok
    ok, _ = ops.check_requires(g, {"hc": 21})
    assert not ok
    ok, _ = ops.check_requires(g, {"hc_max": 25})
    assert ok
    ok, _ = ops.check_requires(g, {"hc_max": 10})
    assert not ok
    g.court["military"] = 40
    ok, _ = ops.check_requires(g, {"court_min": {"military": 40}})
    assert ok
    ok, _ = ops.check_requires(g, {"court_min": {"military": 41}})
    assert not ok
    ok, _ = ops.check_requires(g, {"court_max": {"military": 15}})
    assert not ok


def t_world_year():
    from kreml import engine
    g = Kremlin(0)
    g.flags.add("pipelines")            # boom year 1974: price 76
    g.year = 1974
    start = g.hard_currency             # 40
    engine.apply_systems(g)
    # bonus (76-40)//6=6 +2 pipelines = 8, drain 3 → +5; still below 75, no resonance
    assert g.hard_currency == start + 5, g.hard_currency
    assert g.stats["ECONOMY"] == 55 and g.stats["PRESTIGE"] == 62
    # a GLUT year with debt: 1986, price 25, drain 3+3+5 = 11
    h = Kremlin(0)
    h.year = 1986
    h.flags.add("debt_trap")
    before = h.hard_currency
    engine.apply_systems(h)
    assert h.hard_currency == before - 11, h.hard_currency
    assert h.hard_currency >= 15        # low, but not yet dry → no gauge penalty
    assert h.stats["ECONOMY"] == 55 and h.stats["FAITH"] == 52
    # a DRY reserve pains the gauges
    d = Kremlin(0)
    d.year = 1986
    d.hard_currency = 9
    d.flags.add("debt_trap")
    engine.apply_systems(d)             # drain 3+3+5 = 11 → 0; dry note hits gauges
    assert d.hard_currency == 0
    assert d.stats["ECONOMY"] == 52 and d.stats["FAITH"] == 51


def t_court_danger_queues_coup():
    from kreml import engine
    g = Kremlin(0)
    g.year = 1971
    g.court["old_guard"] = 5            # despairing faction
    engine.apply_systems(g)
    assert any(eid == "palace_coup" for _, eid in g.pending), g.pending
    # while a plot is already pending, no second booking
    n_before = len(g.pending)
    engine.apply_systems(g)
    assert len(g.pending) == n_before


def t_coup_handlers():
    from kreml.state import FACTIONS
    g = Kremlin(0)
    g.stats["ORDER"] = 70
    g.stats["MILITARY"] = 70
    g.stats["FAITH"] = 80
    ops.apply_ops(g, {"special": "coup_fight"})    # strong enough to hold
    assert "survived_plot" in g.flags and not g.deposed
    assert all(g.court[f] >= 30 for f in FACTIONS)
    h = Kremlin(0)
    h.stats["ORDER"] = 30
    h.stats["MILITARY"] = 30
    h.court["old_guard"] = 10
    ops.apply_ops(h, {"special": "coup_fight"})
    assert h.deposed and h.death_reason
    p = Kremlin(0)
    p.stats["FAITH"] = 70
    ops.apply_ops(p, {"special": "coup_people"})
    assert "survived_plot" in p.flags and not p.deposed
    q = Kremlin(0)
    q.stats["FAITH"] = 30
    ops.apply_ops(q, {"special": "coup_people"})
    assert q.deposed and q.death_reason


def t_palace_coup_event_shape():
    from kreml.content import events as EV
    ev = EV.EVENTS["palace_coup"]
    labels = {o.label for o in ev.options}
    assert "Walk in and face the plenum" in labels
    # the third option is gated on FAITH ≥ 45
    third = next(o for o in ev.options if o.label.startswith("Appeal"))
    plain = Kremlin(0)
    plain.stats["FAITH"] = 30
    ok, _ = ops.check_requires(plain, third.requires)
    assert not ok
    plain.stats["FAITH"] = 55
    ok, _ = ops.check_requires(plain, third.requires)
    assert ok


def t_new_era_content():
    from kreml.content import events as EV
    assert len(EV.RANDOM_POOLS["NEW"]) >= 6
    assert EV.SCRIPTED[1999] == ("nato_east_1999",)
    assert EV.CONGRESS_YEARS.get(1996) == "millennium_congress"
    g = Kremlin(0)
    g.year = 1996
    ids = [e.id for e in engine.collect_events(g)]
    assert "millennium_congress" in ids, ids
    # extended-era directives gate on the years
    g.year = 1991
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "eurasian_market" not in ids
    g.year = 1994
    hist = Kremlin(0)
    hist.year = 1993
    assert hist.era == "NEW"


def t_extension_qualifies():
    from kreml import engine
    g = Kremlin(0)
    g.stats["FAITH"] = 60
    assert engine.qualifies_for_new_era(g)
    g.stats["FAITH"] = 40
    assert not engine.qualifies_for_new_era(g)          # no treaty, faith < 55
    g.flags.add("treaty_signed")
    assert engine.qualifies_for_new_era(g)             # treaty subs for faith
    g.hard_currency = 5
    assert not engine.qualifies_for_new_era(g)         # valas too dry anyway
    g.hard_currency = 40
    g.stats["PRESTIGE"] = 10                            # a gauge under 25 blocks
    assert not engine.qualifies_for_new_era(g)


def t_red_millennium_outcome():
    g = Kremlin(0)
    g.end_year = 2001
    g.year = 2001
    g.stats = {s: 85 for s in STATS}
    g.hard_currency = 50
    tag, score, hdr = survival_outcome(g)
    assert tag == "MILLENNIUM" and "MILLENNIUM" in hdr
    base = sum(g.stats.values()) + 2 * (g.year - 1964)
    assert score == base + 8                            # the millennium bonus
    g2 = Kremlin(0)
    g2.end_year = 1991
    g2.year = 2001                                      # same governed years, no extension
    g2.stats = {s: 85 for s in STATS}
    tag2, score2, _ = survival_outcome(g2)
    assert tag2 == "SURVIVED" and score2 == score - 8


def t_new_events_and_directives():
    from kreml.content import events as EV
    assert "cosmonaut_letter" in EV.RANDOM_POOLS["EARLY"]
    assert "grain_bill" in EV.RANDOM_POOLS["MIDDLE"]
    assert "cassette_wave" in EV.RANDOM_POOLS["LATE"]
    g = Kremlin(0)
    g.year = 1983
    g.hard_currency = 20                 # desperate enough for gold_sale
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "gold_sale" in ids and "second_pipeline" in ids  # pipeline: min 1975 ok
    g.hard_currency = 60
    ids = {d.id for _, ds in DR.available_directives(g) for d in ds}
    assert "gold_sale" not in ids        # hc_max 30 gate


def main() -> int:
    check("queued delayed event fires next year", t_queued_event)
    check("dacha rest halves next event damage", t_rested_softening)
    check("(min,max) random op rolls", t_random_tuple_op)
    check("conditional directive gating chain", t_conditional_directive)
    check("focus action stat gating", t_focus_gating)
    check("coup failure collapses", t_coup_failure)
    check("coup success sets flag", t_coup_success_flags)
    check("war attrition applies", t_war_attrition)
    check("era detection & clamping", t_erа_and_clamps)
    check("congress replaces its year", t_congress_year)
    check("chernobyl hidden flag option", t_chernobyl_and_congress_1986)
    check("difficulty drift & reserves", t_difficulty_drift)
    check("save/load round-trip", t_save_load_roundtrip)
    check("near-miss & treaty outcomes", t_near_miss_outcome)
    check("western press selection", t_press_pick)
    check("new directive gates", t_new_directive_gates)
    check("new events in pools/pools gating", t_new_events_in_pools)
    check("dossier renders ledger & pipeline", t_dossier_and_ledger)
    # ── v4 ──
    check("valas & court ops apply and clamp", t_valas_and_court_ops)
    check("valas & court requirement vocab", t_valas_and_court_requirements)
    check("world market year (boom & glut)", t_world_year)
    check("court danger books the velvet room", t_court_danger_queues_coup)
    check("palace coup handlers fight/appeal", t_coup_handlers)
    check("palace coup event shape & gating", t_palace_coup_event_shape)
    check("extended-era content & congress 1996", t_new_era_content)
    check("extension qualification gates", t_extension_qualifies)
    check("red millennium outcome bonuses", t_red_millennium_outcome)
    check("new events, valas directives", t_new_events_and_directives)
    failed = [r for r in results if not r[1]]
    for name, ok, err in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {err}" if err else ""))
    print()
    print(f"{len(results) - len(failed)}/{len(results)} mechanic checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
