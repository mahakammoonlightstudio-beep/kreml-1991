"""Endings, legacy titles, scoring, and the divergence report.

The divergence report lists where the player's choices bent real history —
the alternate-history payoff of every flag that decisions planted.
"""
from __future__ import annotations

import os
import datetime

from .. import ui
from ..state import Kremlin, STATS
from .modes import MODES
from .forks import PATH_EPILOGUE
from .timelines import get as get_timeline

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HALL_FILE = os.path.join(ROOT, "hall_of_fame.txt")

DEATH_TEXT = {
    "ECONOMY": "The economy is a rumour. Shop windows professionally empty; the rouble a collector's item.",
    "MILITARY": "The Pentagon smells blood. Bases ring the Union like a slow-motion noose.",
    "ORDER": "Republics declare themselves, one after another. The Kremlin guards polish floors for new tenants.",
    "FAITH": "Mass uprisings everywhere. Crowds carry portraits of nobody at all.",
    "PRESTIGE": "Isolated, sanctioned, a parody of itself. The Union's passport earns nothing abroad.",
}

DIVERGENCE_FLAGS = {
    "at_war":            "The 40th Army still grinds through the Afghan mountains.",
    "afghan_withdraw":   "Kabul was left to learn arithmetic on its own.",
    "afghan_deep":       "Escalation deepened the mountain war beyond all plans.",
    "kosygin_pilot":     "Gosplan runs pilot plots where profit is legal.",
    "kosygin_full":      "The market reforms of Kosygin 2.0 became law.",
    "coops":             "Private cooperatives exist legally.",
    "price_done":        "Prices were set free — the rouble learned to float.",
    "sez":               "Special economic zones opened capitalist pockets of the coast.",
    "free_port":         "A Pacific free port grew where a closed city once stood.",
    "dry_decade":        "The anti-alcohol campaign left distilleries empty and moonshine rich.",
    "cadres_refresh":    "The nomenklatura was regenerated with young technocrats.",
    "cadres_rift":       "Technocrats rule the ministries; the Old Guard dines in silence.",
    "helsinki":          "Helsinki Basket III monitors visit officially, now.",
    "treaty_signed":     "The Renewed Union Treaty was signed — a Union by consent.",
    "miners_conceded":   "The coal miners' summer was answered with concessions.",
    "purge":             "Portraits were once again signed in blood.",
    "retrench":          "Soviet garrisons came home years early.",
    "atomic_ultimatum":  "An atomic ultimatum was slammed onto NATO's table.",
    "brink":             "The world parked at the edge of nuclear midnight.",
    "china_thaw":        "Beijing and Moscow sing harmony, not radio war.",
    "french_link":       "A secret channel runs to Paris.",
    "arab_arms":         "Moscow's arsenals circulate through the Arab street.",
    "yugo_study":        "Tito's heretical textbooks got their own shelf in Gosplan.",
    "micro":             "The microelectronics academy of 1978 quietly won the decade.",
    "navy_blue":         "The ocean navy doctrine spread Soviet flag arrays.",
    "accel":             "Acceleration rushed factories before their time.",
    "glasnost_early":    "Glasnost was legislated years before its time.",
    "stability_law":     "Stability became a law with decades of blueprints.",
    "siberian":          "The Siberian resource blitz became the decade's spine.",
    "perestroika":       "Perestroika became the century's saving word.",
    "mr_admitted":       "Moscow officially admitted the secret protocols of 1939.",
    "survived_coup":     "August 1991 ended with your voice, not the tanks'.",
    "chernobyl_hidden":  "Reactor number four's secret died with the silence.",
    # ── v4 flags ──
    "pipelines":         "A second pipeline doubled the export arteries westward.",
    "gold_sold":         "Gold reserves were quietly melted into foreign accounts.",
    "debt_trap":         "Western banks quietly became the Union's second treasury.",
    "rouble_zone_solid": "One hard rouble held the nine treasuries together.",
    "charter_signed":    "The Union Charter defined a federation of equals.",
    "market_union":      "The market union was declared — sofas, auditors, and all.",
    "tech_leap":         "The millennium congress bet the decade on chips and biotech.",
    "red_net":           "OGAS-II finally wired the Union: one protocol, forty dialects.",
    "red_net_live":      "A single Soviet network stitched libraries to post offices.",
    "returnees":         "Silicon Valley émigrés came home with briefcases of ambition.",
    "old_names":         "Leningrad, Tver and Samara recovered their lights and their names.",
    "names_stay":        "The revolutionary names stayed; the twentieth century kept its spelling.",
    "oligarchs_seated":  "The weekend tycoons were entitled rather than purified.",
    "survived_plot":     "A velvet room one Thursday met you, and blinked.",
    "made_deals":        "A Thursday plenum was bought with dachas and dusk appointments.",
    "red_initiative":    "The millennium broadcast proposed retiring the bomb early.",
    # ── v5 divergence lines ──
    "path_hardline":     "The hard line became doctrine, then furniture.",
    "path_reform":       "The reform line became the Union's second official language.",
    "path_neutral":      "Silence was chosen at the right moment, twice.",
    "path_accel":        "Acceleration was taught as the decade that almost worked.",
    "path_glasnost":     "Glasnost arrived years before its time and stayed.",
    "path_iron":         "Iron discipline held the corridors and emptied the shelves.",
    "path_letgo":        "The empire's edges were released; the centre held.",
    "path_hold":         "The held line cost the Pact and bought the decade.",
    "path_market":       "The empire was traded for a market, receipts kept.",
}

# ---------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------
def final_score(g: Kremlin) -> int:
    """Gauge sum plus 2 survival points per year governed.

    v5 counts years from the timeline's own start: a 1992-2001 Millennium run
    gets ten years' credit, not thirty-seven.
    """
    return sum(g.stats.values()) + 2 * (g.year - get_timeline(g.timeline).year)


def legacy_title(score: int) -> str:
    """v5 raises the tiers: fatigue lowers every run's ceiling, so the old
    thresholds handed the top title to any Millennium."""
    if score >= 470:
        return "GENERALISSIMUS OF HISTORY ★"
    if score >= 400:
        return "Hero of Socialist Labour (twice)"
    if score >= 330:
        return "A steady hand — the Union endures"
    if score >= 260:
        return "Survivor of queues and committees"
    return "Footnote in an unpublished archive"


# ── v5: the historical rails count your detours ───────────────────
def divergence_count(g: Kremlin) -> int:
    return sum(1 for flag in DIVERGENCE_FLAGS if flag in g.flags)


def divergence_penalty(g: Kremlin) -> int:
    """Score cost of leaving the rails (HISTORICAL mode only)."""
    per = MODES.get(g.mode, MODES["medium"]).get("divergence", 0)
    if not per:
        return 0
    return min(40, per * max(0, divergence_count(g) - 1))


# Closing lines per timeline, on top of the generic ending text.
TIMELINE_EPILOGUE: dict[tuple[str, str], str] = {
    ("rails", "survived"): "The appointed Secretary outlived the appointment.",
    ("rails", "millennium"): "The timetable was rewritten in the same handwriting.",
    ("reform", "survived"): "Kosygin's memo became a school of government.",
    ("reform", "millennium"): "The 1965 pilot was, in the end, the whole century's plan.",
    ("flashpoint", "survived"): "Twelve years handed over late held the line.",
    ("flashpoint", "millennium"): "The generation that inherited a war inherited a century.",
    ("millennium", "millennium"): "Ten years that were never supposed to exist, used well.",
    ("millennium", "survived"): "A decade of argument, which is how unions live.",
}


# ---------------------------------------------------------------
# Divergence report
# ---------------------------------------------------------------
def divergence_report(g: Kremlin) -> None:
    lines = [text for flag, text in DIVERGENCE_FLAGS.items() if flag in g.flags]
    print()
    print(ui.paint(" ═══ DIVERGENCE REPORT — where you bent real history ═══", ui.C.BB))
    if not lines:
        print(ui.paint("   History stayed exactly on its rails.", ui.C.DIM))
    for ln in lines:
        print(ui.paint("   ☄ " + ln, ui.C.W))
    print()


# ---------------------------------------------------------------
# Hall of fame persistence
# ---------------------------------------------------------------
def record_hall(name: str, score: int, title: str, tag: str = "SURVIVED",
                mode: str = "medium", timeline: str = "rails") -> None:
    try:
        stamp = datetime.date.today().isoformat()
        difficulty = MODES.get(mode, MODES["medium"])["label"]
        era = get_timeline(timeline).label
        with open(HALL_FILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} | {name} | {tag} · {difficulty} · {era} | "
                    f"score {score:3d} | {title}\n")
    except OSError:
        pass


def show_hall_top() -> None:
    try:
        with open(HALL_FILE, encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except OSError:
        return
    if not lines:
        return
    print(ui.paint(" ══ HALL OF FAME (last records) ══", ui.C.Y))
    for ln in lines[-5:]:
        print("   " + ui.paint(ln, ui.C.DIM))
    print()


# ---------------------------------------------------------------
# Endings
# ---------------------------------------------------------------
def ending_collapse(g: Kremlin) -> int:
    reason = g.death_reason or DEATH_TEXT.get(g.dead_stat() or "", "The Union dissolves.")
    tag = "DEPOSED" if g.deposed else "COLLAPSED"
    header = ("  ██ REMOVED, {} ██".format(g.year) if g.deposed
              else "  ██ COLLAPSE, {} ██".format(g.year))
    detail = ("  The Politburo grieves formally and governs informally by Friday."
              if g.deposed else None)
    print()
    print(ui.paint("═" * 78, ui.C.BB))
    print(ui.paint(header, ui.C.BM))
    if detail:
        print(ui.paint(detail, ui.C.W))
    print(ui.paint("  " + reason, ui.C.W))
    print(ui.paint("═" * 78, ui.C.BB))
    avg = final_score(g) // 2
    print(ui.paint(f"  Governed years: {g.year - get_timeline(g.timeline).year}   "
                   f"Final gauges → {g.stats}", ui.C.W))
    print(ui.paint(f"  Valas reserve: {g.hard_currency} · "
                   f"Politburo {g.court['old_guard']}/{g.court['reformers']}/{g.court['military']}", ui.C.W))
    print(ui.paint(f"  Legacy score: {avg} — Removed from the portraits", ui.C.BB))
    for _ln in _epilogue(g):
        print(ui.paint("   " + _ln, ui.C.W))
    divergence_report(g)
    record_hall(g.name, avg, "Removed from the portraits", tag=tag, mode=g.mode, timeline=g.timeline)
    return avg


def ending_retire(g: Kremlin) -> int:
    score = final_score(g)
    print()
    print(ui.paint("═" * 78, ui.C.BB))
    print(ui.paint("  ★ You resigned and retired to a comfortable dacha.", ui.C.Y))
    print(ui.paint("═" * 78, ui.C.BB))
    print(ui.paint(f"  Governed years: {g.year - get_timeline(g.timeline).year}   "
                   f"Final gauges → {g.stats}", ui.C.W))
    legend = legacy_title(score)
    print(ui.paint(f"  Legacy score: {score} — {legend}", ui.C.BB))
    for _ln in _epilogue(g):
        print(ui.paint("   " + _ln, ui.C.W))
    divergence_report(g)
    record_hall(g.name, score, legend, tag="RETIRED", mode=g.mode, timeline=g.timeline)
    return score


def survival_outcome(g: Kremlin) -> tuple[str, int, str]:
    """Pure verdict for a survived run: (tag, final score, header line).

    Adjustments:
      - near-miss       (any gauge < 10): −25 score, 'NEAR-MISS' tag
      - treaty bonus    (treaty_signed): +6 score
      - golden cushion  (valas ≥ 70): +4 score
      - red millennium  (survived to 2001): +8 score
      - rails detour    (HISTORICAL mode): −5 per divergence after the first
    """
    score = final_score(g)
    near_miss = min(g.stats.values()) < 10
    if near_miss:
        score = max(0, score - 25)
    if "treaty_signed" in g.flags:
        score += 6
    if g.hard_currency >= 70:
        score += 4
    if g.end_year >= 2001:
        score += 8
    detour = divergence_penalty(g)
    score = max(0, score - detour)
    rails = MODES.get(g.mode, {}).get("rail", False)
    if g.end_year >= 2001:
        header = "██ THE RED MILLENNIUM — THE UNION NEVER LEFT ██" if not near_miss \
            else "██ THE RED MILLENNIUM — HELD BY A PRAYER ██"
        tag = "NEAR-MISS" if near_miss else "MILLENNIUM"
    elif near_miss:
        header = "██ THE UNION SURVIVES — BY A PRAYER ██"
        tag = "NEAR-MISS"
    elif rails and divergence_count(g) > 2:
        header = "██ THE UNION SURVIVES — OFF THE RAILS ██"
        tag = "DIVERGED"
    else:
        header = "██ THE UNION SURVIVES ██"
        tag = "HISTORICAL" if rails else "SURVIVED"
    return tag, score, header


def ending_kind(g: Kremlin) -> str:
    if g.deposed or g.dead_stat() is not None:
        return "collapse"
    if g.end_year >= 2001:
        return "millennium"
    return "survived"


def _epilogue(g: Kremlin) -> list[str]:
    """Timeline + path closing lines for any ending."""
    out = []
    line = TIMELINE_EPILOGUE.get((g.timeline, ending_kind(g)))
    if line:
        out.append(line)
    if g.path and g.path in PATH_EPILOGUE:
        out.append(PATH_EPILOGUE[g.path])
    return out


def ending_union_survives(g: Kremlin) -> int:
    tag, score, header = survival_outcome(g)
    near_miss = tag == "NEAR-MISS"
    text = (f"  {header}\n"
            "  December 26, 1991: the flag over the Kremlin remains red.")
    if near_miss:
        text += ("\n  Historians argue why it didn't fall. Some write it was you.\n"
                 "  Most write it was inertia, and quote the gauges.")
    else:
        text += "\n  Historians argue whether it was your cunning, luck, or the weather."
    if "survived_coup" in g.flags:
        text += "\n  The August Coup is remembered as your finest hour."
    elif g.putschist:
        text += ("\n  The Emergency Committee, which you quietly directed, is remembered\n"
                 "  differently: in whispered tones, in courtrooms.")
    if "treaty_signed" in g.flags:
        text += ("\n  The Renewed Union Treaty holds: consent replaced fear, nine republics\n"
                 "  stayed by signature rather than by tank.")
    if "perestroika" in g.flags:
        text += ("\n  Years later, 'perestroika' is taught as the word that saved the century —\n"
                 "  or sped its multiplication into paperwork.")
    print()
    print(ui.paint("═" * 78, ui.C.BB))
    for ln in text.split("\n"):
        print(ui.paint(ln, ui.C.BG))
    print(ui.paint("═" * 78, ui.C.BB))
    legend = legacy_title(score)
    if near_miss:
        legend = "Survived by a prayer — " + legend.lower()
    print(ui.paint(f"  Governed years: {g.year - get_timeline(g.timeline).year}   "
                   f"Final gauges → {g.stats}", ui.C.W))
    print(ui.paint(f"  Valas reserve: {g.hard_currency} · "
                   f"Politburo {g.court['old_guard']}/{g.court['reformers']}/{g.court['military']}", ui.C.W))
    print(ui.paint(f"  Legacy score: {score} — {legend}", ui.C.BB))
    for _ln in _epilogue(g):
        print(ui.paint("   " + _ln, ui.C.W))
    divergence_report(g)
    record_hall(g.name, score, legend, tag=tag, mode=g.mode, timeline=g.timeline)
    return score


def ending_red_millennium(g: Kremlin) -> int:
    tag, score, header = survival_outcome(g)
    near_miss = tag == "NEAR-MISS"
    text = (f"  {header}\n"
            "  January 1, 2001: the red flag opens the century — and the ledger")
    if near_miss:
        text += ("\n note-says: 'barely'. Inertia again claims the authorship.\n"
                 "  The queues kept the Union; the Union kept you.")
    else:
        text += ("\n  records a Union that bent every rule set for its death.\n"
                 "  The market entered; the flag stayed; the Party argues in daylight now,\n"
                 "  which is how the century's most successful habit ends: arguing.")
    if "union_market" in g.flags or "market_union" in g.flags:
        text += "\n  Budapest to Baku queue at one tariff shelf: the common market held."
    if "rouble_zone_solid" in g.flags:
        text += "\n  One hard rouble survived the coupon wars of 1992."
    if "nato_east_1999" in g.used_events:
        text += "\n  NATO stepped east in 1999; the Union, somehow, was already past caring."
    if "survived_plot" in g.flags:
        text += "\n  More than one velvet Thursday ended with your chair exactly where it was."
    if "treaty_signed" in g.flags:
        text += "\n  The 1991 treaty still binds: nine republics by signature, not by tank."
    print()
    print(ui.paint("═" * 78, ui.C.BB))
    for ln in text.split("\n"):
        print(ui.paint(ln, ui.C.BG))
    print(ui.paint("═" * 78, ui.C.BB))
    legend = legacy_title(score)
    if near_miss:
        legend = "Held by a prayer to 2001 — " + legend.lower()
    else:
        legend = "Author of the Red Millennium — " + legend.lower()
    print(ui.paint(f"  Governed years: {g.year - get_timeline(g.timeline).year}   "
                   f"Final gauges → {g.stats}", ui.C.W))
    print(ui.paint(f"  Valas reserve: {g.hard_currency} · "
                   f"Politburo {g.court['old_guard']}/{g.court['reformers']}/{g.court['military']}", ui.C.W))
    print(ui.paint(f"  Legacy score: {score} — {legend}", ui.C.BB))
    for _ln in _epilogue(g):
        print(ui.paint("   " + _ln, ui.C.W))
    divergence_report(g)
    record_hall(g.name, score, legend, tag=tag, mode=g.mode, timeline=g.timeline)
    return score
