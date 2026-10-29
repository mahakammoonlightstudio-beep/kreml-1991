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
    g.timeline = "flashpoint"
    g.directive_uses = {"heavy_industry": 3}
    g.focus_uses = {"factory_visit": 2}
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
        assert g2.timeline == "flashpoint"
        assert g2.directive_uses == {"heavy_industry": 3}
        assert g2.focus_uses == {"factory_visit": 2}
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
    assert g.hard_currency == 50          # v5 opening reserve
    ops.apply_ops(g, {"hc": (5, 5), "court": {"military": 60, "old_guard": -200}})
    assert g.hard_currency == 55
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
    # a GLUT year with debt: 1986, price 25, drain 3+3+7 = 13 (v5)
    h = Kremlin(0)
    h.year = 1986
    h.flags.add("debt_trap")
    before = h.hard_currency
    engine.apply_systems(h)
    assert h.hard_currency == before - 13, h.hard_currency
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


# ─────────────────────────────── v5 ──────────────────────────────
def t_five_modes():
    from kreml.content.modes import MODE_ORDER as ORDER, normalize
    assert len(ORDER) == 5, ORDER
    assert ORDER == ("easy", "medium", "hard", "extreme", "historical")
    assert normalize("normal") == "medium"          # v4 alias still works
    assert normalize("nonsense") == "medium"
    assert MODES["historical"]["rail"] is True
    assert MODES["extreme"]["lifelines"] == 1
    assert Kremlin(0, mode="normal").mode == "medium"


def t_timeline_application():
    from kreml.content.timelines import TIMELINE_ORDER, TIMELINES
    assert set(TIMELINE_ORDER) == set(TIMELINES) and len(TIMELINE_ORDER) == 4
    f = Kremlin(0, mode="medium", timeline="flashpoint")
    assert (f.year, f.end_year) == (1980, 1991) and "at_war" in f.flags
    assert f.era == "MIDDLE" and f.stats["MILITARY"] == 76
    m = Kremlin(0, mode="medium", timeline="millennium")
    assert m.end_year == 2001 and m.year == 1992 and m.era == "NEW"
    assert "treaty_signed" in m.flags and m.timeline_def.id == "millennium"
    r = Kremlin(0)
    assert r.timeline == "rails" and r.year == 1964 and r.court == {
        "old_guard": 50, "reformers": 50, "military": 50}


def t_fatigue_scaling():
    assert ops.fatigue_multiplier(0) == 1.0
    assert ops.fatigue_multiplier(1) == 0.85
    assert ops.fatigue_multiplier(99) == ops.FATIGUE_FLOOR
    raw = {"stats": {"ECONOMY": 6, "FAITH": -2}, "hc": 6,
           "court": {"old_guard": 4}}
    scaled = ops.scale_ops(raw, 0.7)
    assert scaled["stats"]["ECONOMY"] == 4        # 6 * 0.7 rounded
    assert scaled["stats"]["FAITH"] == -2         # costs never shrink
    assert scaled["hc"] == 4
    assert scaled["court"]["old_guard"] == 3
    assert raw["stats"]["ECONOMY"] == 6           # original untouched
    g = Kremlin(0)
    before = g.stats["ECONOMY"]
    ops.apply_ops(g, scaled)
    assert g.stats["ECONOMY"] == before + 4
    assert g.directive_uses == {}


def t_fork_fires_once():
    from kreml.content.forks import FORKS, PATH_FLAGS
    g = Kremlin(0, mode="medium")
    g.year = 1968
    first = [e.id for e in engine.collect_events(g)]
    assert "prague_spring" in first and "fork_1968" in first, first
    second = [e.id for e in engine.collect_events(g)]
    assert "fork_1968" not in second, second
    assert FORKS[1968] == "fork_1968"
    # a chosen path both marks divergence and nudges drift
    ops.apply_ops(g, {"path": "path_reform"})
    assert g.path == "path_reform" and "path_reform" in g.flags
    ops.apply_ops(g, {"path": "path_iron"})          # realignment replaces it
    assert g.path == "path_iron" and "path_reform" not in g.flags
    ops.apply_ops(g, {"path": "path_reform"})
    before = dict(g.stats)
    engine.apply_drift(g)
    assert g.stats["FAITH"] == before["FAITH"]        # -1 era drift, +1 path
    assert g.stats["ORDER"] == before["ORDER"] - 2    # -1 era drift, -1 path
    assert set(PATH_FLAGS) >= {"path_reform", "path_iron", "path_market"}
    g2 = Kremlin(0, mode="medium")
    g2.year = 1985
    ids = [e.id for e in engine.collect_events(g2)]
    assert "new_secretary" in ids and "fork_1985" in ids, ids
    # a later fork still fires: paths can be realigned, one fork per year
    ops.apply_ops(g2, {"path": "path_iron"})
    g2.year = 1989
    ids = [e.id for e in engine.collect_events(g2)]
    assert "fork_1989" in ids, ids
    ops.apply_ops(g2, {"path": "path_letgo"})
    assert g2.path == "path_letgo" and "path_iron" not in g2.flags


def t_rails_lock_alternate_content():
    from kreml.content import events as EV
    hist = Kremlin(0, mode="historical")
    hist.flags |= {"kosygin_pilot", "perestroika", "coops"}
    hist.stats["FAITH"] = 60                  # so the treaty is otherwise open
    hist.year = 1990
    ids = {d.id for _, ds in DR.available_directives(hist) for d in ds}
    for locked in ("kosygin_reforms", "legalize_cooperatives", "price_reform",
                   "special_economic_zone", "red_net", "cadres_refresh"):
        assert locked not in ids, locked
    assert "new_union_treaty" in ids          # historical content stays
    free = Kremlin(0, mode="medium")
    free.flags |= {"kosygin_pilot", "perestroika", "coops"}
    free.year = 1990
    ids = {d.id for _, ds in DR.available_directives(free) for d in ds}
    assert "price_reform" in ids and "legalize_cooperatives" in ids
    # events: alt events are never eligible, forks never fire
    assert not engine._eligible(hist, EV.EVENTS["singapore_dream"])
    assert engine._eligible(free, EV.EVENTS["singapore_dream"])
    hist.year = 1968
    assert "fork_1968" not in [e.id for e in engine.collect_events(hist)]


def t_coup_gate_is_graded():
    near = Kremlin(0)
    near.stats["MILITARY"], near.stats["ORDER"] = 50, 55     # 105
    ops.apply_ops(near, {"special": "coup_defy"})
    assert near.dead_stat() is None
    assert {"survived_coup", "coup_scarred"} <= near.flags
    assert near.stats["ORDER"] == 43 and near.court["old_guard"] == 45
    broken = Kremlin(0)
    broken.stats["MILITARY"], broken.stats["ORDER"] = 47, 47  # 94
    ops.apply_ops(broken, {"special": "coup_defy"})
    assert broken.dead_stat() is not None and broken.death_reason
    safe = Kremlin(0)
    safe.stats["MILITARY"], safe.stats["ORDER"] = 55, 55     # 110
    ops.apply_ops(safe, {"special": "coup_defy"})
    assert "survived_coup" in safe.flags and "coup_scarred" not in safe.flags
    assert safe.stats["FAITH"] == 58 and safe.stats["PRESTIGE"] == 67


def t_divergence_penalty():
    from kreml.content.endings import divergence_penalty, survival_outcome
    rails = Kremlin(0, mode="historical")
    rails.stats = {s: 80 for s in STATS}
    base = survival_outcome(rails)[1]
    rails.flags |= {"at_war", "purge", "price_done"}        # three detours
    score = survival_outcome(rails)[1]
    assert divergence_penalty(rails) == 10                   # 5 * (3 - 1)
    assert score == base - 10
    tag, _, header = survival_outcome(rails)
    assert tag == "DIVERGED" and "OFF THE RAILS" in header
    quiet = Kremlin(0, mode="historical")
    quiet.stats = {s: 80 for s in STATS}
    assert survival_outcome(quiet)[0] == "HISTORICAL"
    free = Kremlin(0, mode="medium")
    free.stats = {s: 80 for s in STATS}
    free.flags |= {"at_war", "purge", "price_done"}
    assert divergence_penalty(free) == 0


def t_extension_needs_thirty_valas():
    g = Kremlin(0)
    g.stats["FAITH"] = 60
    g.hard_currency = 30
    assert engine.qualifies_for_new_era(g)
    g.hard_currency = 29
    assert not engine.qualifies_for_new_era(g)      # v5: the gate was raised


def t_timeline_endings_and_hall_tag():
    from kreml.content.endings import TIMELINE_EPILOGUE, _epilogue
    g = Kremlin(0, mode="medium", timeline="reform")
    g.stats = {s: 80 for s in STATS}
    assert "Kosygin's memo" in " ".join(_epilogue(g))
    assert ("reform", "survived") in TIMELINE_EPILOGUE
    g.path = "path_hardline"
    assert any("hard line" in ln for ln in _epilogue(g))


def t_all_queue_targets_exist():
    """Every delayed consequence in the content must point at a real event."""
    from kreml.content import events as EV
    missing, bad_delay = [], []
    for ev in EV.EVENTS.values():
        for o in ev.options:
            for delay, target in (o.ops.get("queue") or []):
                if target not in EV.EVENTS:
                    missing.append((ev.id, target))
                if not isinstance(delay, int) or delay < 0:
                    bad_delay.append((ev.id, target, delay))
    for d in DR.DIRECTIVES:
        for delay, target in (d.ops.get("queue") or []):
            if target not in EV.EVENTS:
                missing.append((d.id, target))
    assert not missing, missing
    assert not bad_delay, bad_delay


def t_chain_reactions_wired():
    """The five v5 chains start from the right decisions and progress."""
    from kreml.content import events as EV
    # triggers
    memo = next(o for o in EV.EVENTS["kosygin_memo"].options
                if o.label.startswith("Support"))
    assert memo.ops["queue"][0][1] == "reform_wobble"
    for o in EV.EVENTS["chernobyl"].options:
        if o.ops.get("flag_add") == "chernobyl_hidden":
            assert o.ops["queue"][0][1] == "chernobyl_secrecy"
    intervene = next(o for o in EV.EVENTS["afghanistan_1979"].options
                     if o.label.startswith("Intervene"))
    assert intervene.ops["queue"][0][1] == "afghan_stalemate"
    gold = next(d for d in DR.DIRECTIVES if d.id == "gold_sale")
    assert gold.ops["queue"][0][1] == "gold_rumour"
    treaty = next(d for d in DR.DIRECTIVES if d.id == "new_union_treaty")
    assert treaty.ops["queue"][0][1] == "treaty_sabotage"
    # progression: stage 1 queues stage 2 with the right delay
    g = Kremlin(0)
    g.year = 1982
    ops.apply_ops(g, {"queue": [(3, "afghan_decision")]})
    g.year = 1984
    ids = [e.id for e in engine.collect_events(g)]
    assert "afghan_decision" not in ids                  # not due yet
    g.year = 1985
    ids = [e.id for e in engine.collect_events(g)]
    assert "afghan_decision" in ids, ids
    # the withdraw option actually ends the war and queues the veterans
    withdraw = next(o for o in EV.EVENTS["afghan_decision"].options
                    if o.label.startswith("Withdraw"))
    g.flags.add("at_war")
    ops.apply_ops(g, withdraw.ops)
    assert "at_war" not in g.flags and "afghan_withdraw" in g.flags
    assert g.pending and g.pending[-1][1] == "afghan_veterans"


def t_grumble_costs_and_glut_pressure():
    from kreml.content import world as WORLD
    g = Kremlin(0)
    g.year = 1986
    g.court["reformers"] = WORLD.GRUMBLE_THRESHOLD - 1  # grumbling, not plotting
    eco = g.stats["ECONOMY"]
    engine.apply_systems(g)
    assert g.stats["ECONOMY"] == eco - 1               # neglect costs a point
    assert not any(eid == "palace_coup" for _, eid in g.pending)


def t_ui_visuals():
    import io
    from contextlib import redirect_stdout
    from kreml import ui
    for v in (0, 1, 49, 50, 99, 100):
        assert len(ui.bar(v, 30)) == 30, (v, ui.bar(v, 30))
        assert len(ui.bar(v, 6)) == 6
    assert set(ui.bar(0)) == {"░"} and set(ui.bar(100)) == {"█"}
    assert ui.bar(50, 10).count("█") == 5
    assert any(ch in ui.bar(13, 20) for ch in ui._SUB)      # fractional cell
    assert ui.sparkline([]) == ""
    sp = ui.sparkline([1, 2, 3, 4, 5, 6, 7, 8], 8)
    assert len(sp) == 8 and sp[0] == "▁" and sp[-1] == "█"
    assert len(ui.sparkline([50] * 9, 5)) == 5              # flat series, capped
    assert ui.arrow(3) == "▲" and ui.arrow(-2) == "▼" and ui.arrow(0) == "·"
    buf = io.StringIO()
    old, ui.ANIM = ui.ANIM, False
    try:
        with redirect_stdout(buf):
            ui.year_banner(1968)
            ui.stats_panel(lambda: {s: 60 for s in STATS}, 1968, 2, "EARLY",
                           mode_tag="BALANCED", reserves_cap=3, hc=40,
                           court={"old_guard": 60, "reformers": 40, "military": 30},
                           world="STEADY", timeline="RAILS OF HISTORY",
                           history=[{"year": 1966, "stats": {s: 50 for s in STATS},
                                     "hc": 38, "oil": 42},
                                    {"year": 1967, "stats": {s: 55 for s in STATS},
                                     "hc": 46, "oil": 50},
                                    {"year": 1968, "stats": {s: 55 for s in STATS},
                                     "hc": 41, "oil": 44}])
            from kreml import dossier as D
            g = Kremlin(0)
            g.history = [{"year": 1965, "stats": {s: 50 for s in STATS},
                          "hc": 40, "oil": 42},
                         {"year": 1966, "stats": {s: 45 for s in STATS},
                          "hc": 36, "oil": 41},
                         {"year": 1967, "stats": {s: 52 for s in STATS},
                          "hc": 44, "oil": 47}]
            D.show_roadmap(g)
    finally:
        ui.ANIM = old
    out = buf.getvalue()
    assert "1968" in out and "▓" not in out.splitlines()[0]
    assert "▁" in out and "▲" in out          # 55 vs 60 now reads as a rise
    assert "TREND" in out
    # the animated path must not crash (sleeps neutralised for the test)
    old_sleep = ui.time.sleep
    buf2 = io.StringIO()
    try:
        ui.time.sleep = lambda *_: None
        ui.ANIM = True
        with redirect_stdout(buf2):
            ui.year_banner(1970)
    finally:
        ui.time.sleep = old_sleep
        ui.ANIM = False
    assert "1970" in buf2.getvalue() and "░" in buf2.getvalue()


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
    # ── v5 ──
    check("five modes + v4 alias", t_five_modes)
    check("timeline presets apply", t_timeline_application)
    check("plan fatigue scaling", t_fatigue_scaling)
    check("divergence forks fire once", t_fork_fires_once)
    check("historical rails lock alt content", t_rails_lock_alternate_content)
    check("1991 coup gate is graded", t_coup_gate_is_graded)
    check("rails divergence penalty", t_divergence_penalty)
    check("millennium needs 30 valas", t_extension_needs_thirty_valas)
    check("timeline endings & epilogue", t_timeline_endings_and_hall_tag)
    check("every queue target exists", t_all_queue_targets_exist)
    check("chain reactions wired", t_chain_reactions_wired)
    check("grumbling court & glut pressure", t_grumble_costs_and_glut_pressure)
    check("ui visuals: bars, sparklines, panels", t_ui_visuals)
    failed = [r for r in results if not r[1]]
    for name, ok, err in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {err}" if err else ""))
    print()
    print(f"{len(results) - len(failed)}/{len(results)} mechanic checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
