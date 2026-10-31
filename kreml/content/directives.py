"""Yearly directives (big public policies) and crisis lifelines.

Menu groups follow the order in GROUP_ORDER. Conditional directives only
appear when their requirements are met — that is the branching backbone of
the alternate-history layer.
"""
from ..model import Directive, Option
from ..ops import check_requires  # noqa: F401  (re-exported for keyboard convenience)
from ..state import Kremlin
from .modes import MODES


def make_directive(id: str, label: str, desc: str, group: str, ops: dict, *,
                   requires: dict | None = None, once: bool = False,
                   alt: bool = False) -> Directive:
    return Directive(id=id, label=label, desc=desc, group=group,
                     ops=ops, requires=requires or {}, once=once, alt=alt)


def on_rails(g: Kremlin) -> bool:
    """HISTORICAL RAILS locks every alternate-history lever."""
    return bool(MODES.get(g.mode, MODES["medium"]).get("rail"))


DIRECTIVES: tuple[Directive, ...] = (
    # ── Economy ────────────────────────────────────────────────────────────
    make_directive("heavy_industry", "Five-Year Plan: heavy industry",
                   "Cement, steel, more cement.", "Economy",
                   {"stats": {"ECONOMY": 6, "FAITH": -2, "ORDER": 1},
                    "court": {"old_guard": 3, "military": 2}}),
    make_directive("consumer_goods", "Consumer goods & light industry",
                   "Refrigerators, TVs, better shoes.", "Economy",
                   {"stats": {"ECONOMY": 3, "FAITH": 4},
                    "court": {"reformers": 3}}),
    make_directive("agriculture_reform", "Agriculture reform",
                   "Private plot concessions, tractors promised.", "Economy",
                   {"stats": {"ECONOMY": 2, "FAITH": 4, "ORDER": -1}, "hc": 2,
                    "court": {"reformers": 3}}),
    make_directive("oil_gas_exports", "Oil & gas exports",
                   "Purchases abroad with pipeline money.", "Economy",
                   {"stats": {"ECONOMY": 4, "PRESTIGE": 1}, "hc": 6}),
    make_directive("second_pipeline", "The Second Pipeline to Europe",
                   "Urengoy sniffs out foreign wallets. Pumps, valves, deutschmarks.",
                   "Economy",
                   {"stats": {"ECONOMY": 4, "PRESTIGE": 1}, "hc": 12,
                    "flag_add": "pipelines"},
                   requires={"min_year": 1975}, once=True),
    make_directive("gold_sale", "Sell gold reserves (quietly)",
                   "The special export account refills; the Swiss suspect nothing loudly.",
                   "Economy",
                   {"stats": {"ECONOMY": 3, "PRESTIGE": -1}, "hc": 20,
                    "flag_add": "gold_sold", "queue": [(2, "gold_rumour")]},
                   requires={"hc_max": 30}, once=True),
    make_directive("western_loans", "Borrow from the West",
                   "Ten-year paper at eight points. Time is bought; time bills.",
                   "Economy",
                   {"stats": {"ECONOMY": 5}, "hc": 14, "flag_add": "debt_trap"},
                   requires={"min_year": 1980}, once=True),
    make_directive("kosygin_reforms", "UNLEASH Kosygin 2.0 market reforms",
                   "Profit indicators become law. Gosplan trembles.", "Economy",
                   {"stats": {"ECONOMY": 12, "ORDER": -6, "FAITH": 3},
                    "flag_add": "kosygin_full",
                    "court": {"reformers": 10, "old_guard": -8}},
                   requires={"flags": ["kosygin_pilot"]}, once=True, alt=True),
    make_directive("legalize_cooperatives", "Legalize private cooperatives",
                   "Pioneering co-ops may lawfully sell vegetables, films, and haircuts.",
                   "Economy",
                   {"stats": {"ECONOMY": 8, "FAITH": 4, "ORDER": -5},
                    "flag_add": "coops",
                    "court": {"reformers": 6, "old_guard": -6}},
                   requires={"any_flags": ["kosygin_full", "perestroika"],
                             "min_year": 1984}, once=True, alt=True),
    make_directive("price_reform", "Price reform: the rouble retrains",
                   "Prices float to where bread actually is.", "Economy",
                   {"stats": {"ECONOMY": 10, "FAITH": -5, "ORDER": -7},
                    "flag_add": "price_done",
                    "court": {"reformers": 8, "old_guard": -10}},
                   requires={"flags": ["coops"], "min_year": 1988}, once=True,
                   alt=True),
    make_directive("special_economic_zone", "Special economic zones (Nakhodka model)",
                   "Four swathes of coast learn Mandarin-style incentives.", "Economy",
                   {"stats": {"ECONOMY": 7, "ORDER": -4, "PRESTIGE": 2},
                    "flag_add": "sez"},
                   requires={"any_flags": ["price_done", "coops"],
                             "min_year": 1988}, once=True, alt=True),

    # ── Defense & state ----------------------------------------------------
    make_directive("military_buildup", "Military buildup",
                   "New tanks, new rockets, new uniforms.", "Defense",
                   {"stats": {"MILITARY": 6, "ECONOMY": -3},
                    "court": {"military": 6}}),
    make_directive("espionage", "Espionage & intelligence ops",
                   "The KGB loves quiet paperwork.", "Defense",
                   {"stats": {"PRESTIGE": 3, "MILITARY": 2}, "hc": 3,
                    "court": {"old_guard": 2, "military": 2}}),
    make_directive("atomic_ultimatum", "Atomic ultimatum to NATO",
                   "Silo doors open a crack. The world holds its breath.", "Defense",
                   {"stats": {"MILITARY": 1, "PRESTIGE": -10, "ORDER": 4},
                    "flag_add": "atomic_ultimatum",
                    "queue": [(1, "nato_ultimatum_reply")],
                    "court": {"military": 4, "old_guard": 2}},
                   requires={"stats": {"MILITARY": 85}, "max_year": 1983},
                   once=True),
    make_directive("party_purge", "Great Party purge (show trials)",
                   "Old comrades read confessions aloud. The archives expand.", "Defense",
                   {"stats": {"ORDER": 8, "FAITH": -6, "PRESTIGE": -4, "ECONOMY": -2},
                    "flag_add": "purge",
                    "court": {"old_guard": 10, "reformers": -12, "military": -3}},
                   requires={"stats": {"ORDER": 55}, "max_year": 1985}, once=True),

    # ── Society & culture --------------------------------------------------
    make_directive("culture_sport", "Culture, sport & education",
                   "Libraries, stadiums, lyrical films.", "Society",
                   {"stats": {"FAITH": 3, "PRESTIGE": 2, "ORDER": -1},
                    "court": {"reformers": 2}}),
    make_directive("kgb_crackdown", "KGB crackdown",
                   "Silence is the mother of order... allegedly.", "Society",
                   {"stats": {"ORDER": 7, "FAITH": -3, "PRESTIGE": -2},
                    "court": {"old_guard": 6, "military": -2, "reformers": -3}}),
    make_directive("soft_glasnost", "Relax censorship (soft glasnost)",
                   "Let writers breathe a little.", "Society",
                   {"stats": {"FAITH": 4, "ORDER": -3, "PRESTIGE": 1},
                    "court": {"reformers": 6, "old_guard": -5}}),
    make_directive("party_discipline", "Party discipline & propaganda",
                   "Posters, meetings, correct slogans.", "Society",
                   {"stats": {"ORDER": 4, "FAITH": 2, "ECONOMY": -1},
                    "court": {"old_guard": 4, "reformers": -2}}),
    make_directive("cadres_refresh", "Regenerate the nomenklatura",
                   "Grey heads rotate out; technocrats and Party youth step in.", "Society",
                   {"stats": {"FAITH": 3, "ORDER": 2, "ECONOMY": 1},
                    "flag_add": "cadres_refresh",
                    "court": {"reformers": 6, "old_guard": -8}},
                   requires={"any_flags": ["perestroika", "reformer"],
                             "min_year": 1985}, once=True, alt=True),

    # ── Foreign policy ------------------------------------------------------
    make_directive("detente", "Détente diplomacy",
                   "Summits, treaties, handshakes.", "Foreign",
                   {"stats": {"PRESTIGE": 5, "MILITARY": -1}, "hc": 2,
                    "court": {"old_guard": -3, "reformers": 3, "military": -3}}),
    make_directive("new_union_treaty", "Sign the Renewed Union Treaty",
                   "Nine republics re-enter the Union by signature, not by tank.",
                   "Foreign",
                   {"stats": {"FAITH": 4, "PRESTIGE": 3, "ORDER": -5},
                    "flag_add": "treaty_signed", "queue": [(1, "treaty_sabotage")],
                    "court": {"reformers": 8, "old_guard": -8, "military": -6}},
                   requires={"min_year": 1989, "stats": {"FAITH": 55}}, once=True),
    make_directive("china_open", "Economic opening toward Beijing",
                   "Border trade hums; old insults stay in the drawer.", "Foreign",
                   {"stats": {"ECONOMY": 3, "PRESTIGE": 2},
                    "flag_add": "china_thaw",
                    "court": {"military": -2}},
                   requires={"min_year": 1980, "not_flags": ["china_thaw"]},
                   once=True),
    make_directive("war_pact_retrench", "Warsaw Pact retrenchment",
                   "Garrisons come home early. The empire exhales.", "Foreign",
                   {"stats": {"MILITARY": -4, "ECONOMY": 5, "PRESTIGE": 2},
                    "flag_add": "retrench",
                    "court": {"military": -8}},
                   requires={"min_year": 1985}, once=True, alt=True),
    make_directive("eurasian_market", "A Eurasian Common Market",
                   "Budapest to Baku: one tariff shelf, nine warehouses, no tanks.",
                   "Foreign",
                   {"stats": {"ECONOMY": 8, "PRESTIGE": 4, "ORDER": -2},
                    "hc": 10, "flag_add": "union_market"},
                   requires={"min_year": 1992}, once=True, alt=True),

    # ── Science & space -----------------------------------------------------
    make_directive("space_science", "Space science & exploration",
                   "Cosmonauts and robots on the Moon.", "Science",
                   {"stats": {"PRESTIGE": 5, "ECONOMY": 1}}),
    make_directive("red_net", "OGAS-II: the All-Union data network",
                   "Glushkov's ghost gets funding: terminals, teletext, one protocol.",
                   "Science",
                   {"stats": {"ECONOMY": 6, "PRESTIGE": 3, "ORDER": -1},
                    "flag_add": "red_net"},
                   requires={"min_year": 1984}, once=True, alt=True),

    # ── v6 additions ───────────────────────────────────────────────────────
    make_directive("consumer_credit", "Consumer credit & instalment shops",
                   "Refrigerators on twenty-four months; the rouble learns patience.",
                   "Economy",
                   {"stats": {"ECONOMY": 4, "FAITH": 3}, "hc": -3,
                    "flag_add": "consumer_credit",
                    "court": {"reformers": 2}},
                   requires={"min_year": 1972}),
    make_directive("food_programme", "The Food Programme",
                   "Storage, roads and a promise: meat by 1990, or a very good excuse.",
                   "Economy",
                   {"stats": {"ECONOMY": 3, "FAITH": 4, "ORDER": -1}, "hc": -4,
                    "court": {"old_guard": -2}},
                   requires={"min_year": 1982}, once=True),
    make_directive("officer_corps", "Professionalise the officer corps",
                   "Academies, staff tours, and fewer promotions by telephone.",
                   "Defense",
                   {"stats": {"MILITARY": 4, "ORDER": 2, "ECONOMY": -2},
                    "court": {"military": 4}}),
    make_directive("veterans_ministry", "A Ministry for the Afghan veterans",
                   "Housing warrants, prosthetics and a telephone that answers.",
                   "Defense",
                   {"stats": {"FAITH": 3, "ORDER": 2, "ECONOMY": -2},
                    "court": {"military": 2}},
                   requires={"any_flags": ["at_war", "afghan_deep",
                                           "afghan_withdraw"]}, once=True),
    make_directive("televised_presser", "A televised press conference",
                   "Live, unscripted, and four questions about the shelves.",
                   "Society",
                   {"stats": {"FAITH": 4, "PRESTIGE": 2, "ORDER": -3},
                    "influence": 1, "court": {"reformers": 3}},
                   requires={"min_year": 1986}),
    make_directive("amnesty", "Amnesty for political prisoners",
                   "The camps empty by decree; the files stay exactly where they are.",
                   "Society",
                   {"stats": {"FAITH": 5, "PRESTIGE": 3, "ORDER": -4},
                    "flag_add": "amnesty",
                    "court": {"reformers": 6, "old_guard": -8}},
                   requires={"min_year": 1987}, once=True, alt=True),
    make_directive("helsinki_followup", "The Helsinki follow-up conference",
                   "Basket III gets a second meeting, and a second set of monitors.",
                   "Foreign",
                   {"stats": {"PRESTIGE": 4, "ORDER": -1}, "hc": 2,
                    "court": {"reformers": 2}},
                   requires={"flags": ["helsinki"]}, once=True),
    make_directive("gulf_mediation", "Mediate in the Gulf",
                   "Two belligerents, one mediator, and a very large invoice.",
                   "Foreign",
                   {"stats": {"PRESTIGE": 5, "ECONOMY": 1, "MILITARY": -1},
                    "influence": 2, "court": {"military": -2}},
                   requires={"min_year": 1987}, once=True),
    make_directive("mir_station", "Mir-2: a permanent station",
                   "One station, six docks, and a scientific budget that survives a winter.",
                   "Science",
                   {"stats": {"PRESTIGE": 4, "ECONOMY": 2}, "hc": -3,
                    "court": {"military": 2}},
                   requires={"min_year": 1986}, once=True),
)

GROUP_ORDER = ("Economy", "Defense", "Society", "Foreign", "Science")

# ---------------------------------------------------------------
# Crisis lifelines: offered by the engine when a gauge turns critical.
# Each use consumes one reserve (three per game).
# ---------------------------------------------------------------
LIFELINES: tuple[Option, ...] = (
    Option("Inject currency reserves into Gosplan",
           "Soviet gold quietly covers three months of shelves.",
           {"stats": {"ECONOMY": 7, "PRESTIGE": -1}}),
    Option("Emergency KGB sweep",
           "Telephones tremble; order firms up for a season.",
           {"stats": {"ORDER": 6, "FAITH": -3}}),
    Option("Nationwide subsidy & payout",
           "Bread prices held; gratitude ripples through the queue.",
           {"stats": {"FAITH": 5, "ECONOMY": -2}}),
    Option("Accelerate strategic missile upgrades",
           "New warheads gleam; the general staff straightens its backs.",
           {"stats": {"MILITARY": 5, "ECONOMY": -2}}),
)


def available_directives(g: Kremlin) -> list[tuple[str, list[Directive]]]:
    """Returns menu groups (in GROUP_ORDER) holding only available directives."""
    groups: dict[str, list[Directive]] = {}
    rails = on_rails(g)
    for d in DIRECTIVES:
        if rails and d.alt:            # historical mode keeps history's levers
            continue
        if d.once and d.id in g.used_directives:
            continue
        ok, _ = check_requires(g, d.requires)
        if not ok:
            continue
        groups.setdefault(d.group, []).append(d)
    return [(name, groups[name]) for name in GROUP_ORDER if name in groups]
