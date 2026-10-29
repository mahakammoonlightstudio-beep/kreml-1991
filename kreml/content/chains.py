"""v5 content: chain reactions and new standalone events.

A CHAIN is a set of events where each choice queues the next stage, so the
same headline develops differently depending on what you did two years ago
(Afghanistan, Chernobyl, Kosygin, gold, the Union Treaty). The engine needs
no special support: `queue` ops are already the delayed-consequence DSL.

EXTRA_EVENTS are standalone v5 additions; the pools/scripted tables in
`events.py` decide when they can appear.
"""
from __future__ import annotations

from .builders import ev, opt

CHAIN_EVENTS: dict[str, object] = {}

# ══════════════════════════════════════════════════════════════════
# CHAIN A — AFGHANISTAN (starts from the 1979 intervention)
# ══════════════════════════════════════════════════════════════════
CHAIN_EVENTS["afghan_stalemate"] = ev(
    "afghan_stalemate", "The Mountain War, Year Three",
    "The 40th Army holds the roads and none of the valleys. Field reports "
    "arrive with the same sentence, typed on different machines.",
    [
        opt("Rotate fresh divisions in",
            {"stats": {"MILITARY": -2, "ECONOMY": -3, "PRESTIGE": -1},
             "queue": [(3, "afghan_decision")]},
            "New boots, same mountains. The ledger learns to expect it."),
        opt("Fortify the cities, hold the roads",
            {"stats": {"MILITARY": -1, "ECONOMY": -2},
             "queue": [(3, "afghan_decision")]},
            "The war becomes a garrison, and a garrison becomes a habit."),
        opt("Open a quiet withdrawal file",
            {"stats": {"PRESTIGE": 1, "ORDER": -1},
             "flag_add": "afghan_withdrawing",
             "queue": [(2, "afghan_decision")]},
            "A folder appears in a safe that only three people can open."),
    ], once=True)

CHAIN_EVENTS["afghan_decision"] = ev(
    "afghan_decision", "The Afghan Decision",
    "The general staff lays three maps on the table. Only one of them has a "
    "date on the retreat road.",
    [
        opt("Withdraw entirely, on our own date",
            {"stats": {"PRESTIGE": -3, "MILITARY": -2}, "flag_rm": "at_war",
             "flag_add": "afghan_withdraw", "queue": [(1, "afghan_veterans")]},
            "Columns cross the Amu Darya. The mountains keep the receipts."),
        opt("One more season, with more artillery",
            {"stats": {"MILITARY": -4, "ECONOMY": -4, "PRESTIGE": -5},
             "flag_add": "afghan_deep", "queue": [(2, "afghan_veterans")]},
            "Artillery solves the valley; the valley grows another one."),
        opt("Negotiate a coalition in Kabul",
            {"stats": {"PRESTIGE": 2, "ORDER": -2, "FAITH": 1},
             "flag_rm": "at_war", "flag_add": "afghan_withdraw",
             "queue": [(2, "afghan_veterans")]},
            "Kabul gets a coalition; Moscow gets a communique."),
    ], once=True)

CHAIN_EVENTS["afghan_veterans"] = ev(
    "afghan_veterans", "The Veterans Come Home",
    "Trains unload young men with medals and no apartments. The Afghan "
    "generation starts writing letters to the newspapers.",
    [
        opt("Land, pensions and a ministry",
            {"stats": {"ECONOMY": -3, "FAITH": 3, "ORDER": 1}},
            "Housing queues shorten for the men who queued in the mountains."),
        opt("Parades and medals, no housing",
            {"stats": {"FAITH": -2, "ORDER": -1, "PRESTIGE": 1}},
            "The parades are excellent. The hostels are not."),
        opt("Send the loudest to the provinces",
            {"stats": {"ORDER": 2, "FAITH": -3},
             "court": {"old_guard": 3, "reformers": -2}},
            "Two organizers become deputy directors of nothing, far away."),
    ], once=True)

# ══════════════════════════════════════════════════════════════════
# CHAIN B — CHERNOBYL (starts from the cover-up)
# ══════════════════════════════════════════════════════════════════
CHAIN_EVENTS["chernobyl_secrecy"] = ev(
    "chernobyl_secrecy", "The Dosimeters Are Missing",
    "A year after the reactor, Western stations still publish iodine maps. "
    "Your own scientists ask, in writing, for permission to be honest.",
    [
        opt("Confess the dosimeters now",
            {"stats": {"PRESTIGE": 2, "FAITH": 2, "ORDER": -1}},
            "The admission is late, expensive, and finally believed."),
        opt("Hold the line; the West measures anyway",
            {"stats": {"FAITH": -3, "ORDER": 2},
             "queue": [(2, "chernobyl_reckoning")]},
            "TASS publishes weather. The wind publishes caesium."),
        opt("Blame the operators, quietly",
            {"stats": {"ORDER": 1, "FAITH": -2, "PRESTIGE": -2},
             "queue": [(2, "chernobyl_reckoning")]},
            "Six men take the blame; a seventh takes notes."),
    ], once=True)

CHAIN_EVENTS["chernobyl_reckoning"] = ev(
    "chernobyl_reckoning", "The Chernobyl Reckoning",
    "A commission asks for the archive. The archive asks for protection. "
    "The zone, still fenced, asks for nothing at all.",
    [
        opt("Publish the commission's report",
            {"stats": {"FAITH": 3, "PRESTIGE": 3, "ORDER": -3}},
            "Footnotes, dosimeters, and a nation reading its own safety record."),
        opt("Classify it for thirty years",
            {"stats": {"ORDER": 3, "FAITH": -3, "PRESTIGE": -2}},
            "The report joins the protocols on the sealed shelf."),
        opt("Exile the commission, keep the zone",
            {"stats": {"ORDER": 2, "FAITH": -1, "ECONOMY": -2}},
            "The engineers are transferred; the fence is repainted."),
    ], once=True)

# ══════════════════════════════════════════════════════════════════
# CHAIN C — KOSYGIN (starts from the pilot reforms of the 1960s)
# ══════════════════════════════════════════════════════════════════
CHAIN_EVENTS["reform_wobble"] = ev(
    "reform_wobble", "The Pilot Plots Wobble",
    "Two profitable factories, four envious ministries, one harvest that "
    "decides whether the experiment survives the winter.",
    [
        opt("Defend the experiment in the Politburo",
            {"stats": {"ECONOMY": 3, "ORDER": -2},
             "court": {"reformers": 5, "old_guard": -5},
             "queue": [(3, "reform_law")]},
            "Profit indicators get a defender with a signature."),
        opt("Freeze the pilot until the harvest",
            {"stats": {"ECONOMY": -1, "ORDER": 1}, "flag_rm": "kosygin_pilot"},
            "The experiment is stored carefully, and forgotten carefully."),
        opt("Expand it to fifty plants",
            {"stats": {"ECONOMY": 2, "FAITH": 1, "ORDER": -1},
             "court": {"old_guard": -3}, "queue": [(3, "reform_law")]},
            "Fifty directors discover the word 'margin'."),
    ], once=True)

CHAIN_EVENTS["reform_law"] = ev(
    "reform_law", "The Reform Reaches the Statute Book",
    "Gosplan's lawyers have drafted the clause. It is four lines long and "
    "would outlive everyone in the room.",
    [
        opt("Codify profit indicators",
            {"stats": {"ECONOMY": 5, "ORDER": -3}, "flag_add": "kosygin_full",
             "court": {"reformers": 6, "old_guard": -8}},
            "The clause becomes law, and the law becomes a school of thought."),
        opt("Shelve the law, praise the pilot",
            {"stats": {"ORDER": 2, "ECONOMY": -1}, "flag_rm": "kosygin_pilot"},
            "The draft is praised in the preamble and buried in the annex."),
        opt("Pilot twenty more plants next plan",
            {"stats": {"ECONOMY": 2, "ORDER": -1}},
            "Twenty more plants, twenty more arguments, no law."),
    ], once=True)

# ══════════════════════════════════════════════════════════════════
# CHAIN D — GOLD & VALAS (starts from the quiet gold sales)
# ══════════════════════════════════════════════════════════════════
CHAIN_EVENTS["gold_rumour"] = ev(
    "gold_rumour", "A Rumour About the Vault",
    "A Swiss paper prints the shipping manifests. The vault is emptier than "
    "the official inventory and the difference has a foreign bank account.",
    [
        opt("Confirm the sales, buy grain",
            {"stats": {"ECONOMY": 2, "PRESTIGE": -2}, "hc": 8},
            "Bread on the shelves, bullion in someone else's ledger."),
        opt("Deny everything, twice",
            {"stats": {"PRESTIGE": -1, "FAITH": -1},
             "queue": [(2, "gold_audit")]},
            "The denial is printed on paper whose price just went up."),
        opt("Stop selling; the vault stays shut",
            {"stats": {"ECONOMY": -1}, "hc": -2,
             "court": {"old_guard": 2}},
            "The keeper of the vault sleeps with the keys again."),
    ], once=True)

CHAIN_EVENTS["gold_audit"] = ev(
    "gold_audit", "The Gold Audit",
    "A Supreme Soviet deputy demands the reserve ledger. Half the chamber "
    "already knows what it says; the other half wants it read aloud.",
    [
        opt("Open the ledgers to the Supreme Soviet",
            {"stats": {"FAITH": 3, "PRESTIGE": 2, "ORDER": -2}},
            "The numbers are read out, and the room learns arithmetic."),
        opt("Seal the vault and the file",
            {"stats": {"ORDER": 2, "FAITH": -2}},
            "Two locks, one signature, no questions."),
        opt("Blame the Swiss bankers",
            {"stats": {"PRESTIGE": -2, "FAITH": 1}},
            "A foreign villain is found, and immediately overused."),
    ], once=True)

# ══════════════════════════════════════════════════════════════════
# CHAIN E — THE UNION TREATY (starts when the treaty is signed)
# ══════════════════════════════════════════════════════════════════
CHAIN_EVENTS["treaty_sabotage"] = ev(
    "treaty_sabotage", "Sabotage of the Signature",
    "Nine republics signed. Three ministries have since discovered that the "
    "treaty requires them to lose an argument to a provincial committee.",
    [
        opt("Outvote the saboteurs in the Soviet",
            {"stats": {"FAITH": 3, "ORDER": -2, "PRESTIGE": 2},
             "queue": [(2, "treaty_pressure")]},
            "The treaty wins a vote it should have lost."),
        opt("Purge the signatories' opponents",
            {"stats": {"ORDER": 3, "FAITH": -3},
             "court": {"old_guard": 5, "reformers": -6},
             "queue": [(2, "treaty_pressure")]},
            "The treaty is enforced by the people who opposed it."),
        opt("Delay the signing a year",
            {"stats": {"FAITH": -2, "ORDER": -1}, "flag_add": "treaty_delayed",
             "queue": [(3, "treaty_pressure")]},
            "One year of committees, and a signature that keeps its hat on."),
    ], once=True)

CHAIN_EVENTS["treaty_pressure"] = ev(
    "treaty_pressure", "The Treaty Under Load",
    "The charter is young enough to be argued about and old enough to be "
    "blamed. Two republics want a renegotiation, one wants out.",
    [
        opt("Hold the union together, clause by clause",
            {"stats": {"FAITH": 3, "ORDER": -2, "PRESTIGE": 2}},
            "Negotiation becomes the Union's permanent industry."),
        opt("Let the reluctant republic go",
            {"stats": {"PRESTIGE": 1, "ORDER": -4, "FAITH": 1}},
            "One flag leaves the mast; the rest are repainted."),
        opt("Recentralise the charter",
            {"stats": {"ORDER": 4, "FAITH": -4},
             "court": {"old_guard": 4, "reformers": -5}},
            "The centre wins the paragraph and loses the decade."),
    ], once=True)

# ══════════════════════════════════════════════════════════════════
# STANDALONE v5 EVENTS
# ══════════════════════════════════════════════════════════════════
EXTRA_EVENTS: dict[str, object] = {}

EXTRA_EVENTS["gagarin_crash"] = ev(
    "gagarin_crash", "The First Cosmonaut's Last Flight",
    "Yuri Gagarin's training jet is down near Kirzhach. The world's first "
    "spaceman is a closed casket and an open question about the programme.",
    [
        opt("A state funeral, a full inquiry",
            {"stats": {"PRESTIGE": 2, "FAITH": 2, "ECONOMY": -1}},
            "The report is honest; the queue outside the Hall of Columns is long."),
        opt("Bury him quietly, ground the fleet",
            {"stats": {"MILITARY": -2, "PRESTIGE": -2, "ORDER": 1}},
            "The fleet waits; the newspapers print a smaller photograph."),
        opt("Blame the weather, launch again",
            {"stats": {"PRESTIGE": -1, "MILITARY": 1, "FAITH": -2}},
            "The next launch is scheduled before the flowers wilt."),
    ], era="EARLY", once=True, requires={"min_year": 1968})

EXTRA_EVENTS["sakharov_nobel"] = ev(
    "sakharov_nobel", "The Physicist and the Prize",
    "The Nobel Committee has awarded the Peace Prize to Andrei Sakharov, "
    "who is currently in Gorky and not currently invited anywhere.",
    [
        opt("Let him collect it, with a lecture",
            {"stats": {"PRESTIGE": 4, "FAITH": 2, "ORDER": -4},
             "court": {"reformers": 5, "old_guard": -5}},
            "A scientist walks onto a foreign stage and describes his own country."),
        opt("Forbid the trip, allow the telegram",
            {"stats": {"ORDER": 2, "FAITH": -2, "PRESTIGE": -2}},
            "The telegram is warm; the airports remain closed."),
        opt("Release him and his wife as a gift",
            {"stats": {"PRESTIGE": 3, "FAITH": 3, "ORDER": -3},
             "court": {"reformers": 4}},
            "Two exiles buy more goodwill than a sports festival."),
    ], era="MIDDLE", once=True, requires={"min_year": 1975})

EXTRA_EVENTS["polish_pope"] = ev(
    "polish_pope", "A Polish Pope",
    "Karol Wojtyła is elected in Rome. A million Poles will walk to a field "
    "in Kraków, and every one of them will walk past a Party office.",
    [
        opt("Allow the pilgrimage, watch from the sidelines",
            {"stats": {"FAITH": 4, "ORDER": -3, "PRESTIGE": 2},
             "court": {"old_guard": -4, "reformers": 2}},
            "The crowds are enormous, orderly, and impossible to report accurately."),
        opt("Denounce it as imperialist theatre",
            {"stats": {"ORDER": 2, "PRESTIGE": -3, "FAITH": -3}},
            "TASS writes three paragraphs; Warsaw papers write none."),
        opt("Invite him east for a cultural visit",
            {"stats": {"PRESTIGE": 3, "FAITH": 1, "ORDER": -2}},
            "A visit is negotiated with four protocols and one silence."),
    ], era="MIDDLE", once=True, requires={"min_year": 1978})

EXTRA_EVENTS["grain_embargo"] = ev(
    "grain_embargo", "The Grain Embargo",
    "Washington suspends grain sales after Afghanistan. Buenos Aires and "
    "Ottawa quietly raise their prices by a third.",
    [
        opt("Buy elsewhere, pay the premium",
            {"stats": {"ECONOMY": -4, "FAITH": 2}, "hc": -6},
            "The bread arrives; the invoice arrives first."),
        opt("Slaughter the herds, hold the currency",
            {"stats": {"ECONOMY": -2, "FAITH": -2}, "hc": 3},
            "Meat counters empty; the valas account holds for one more quarter."),
        opt("Ration and promise the harvest",
            {"stats": {"FAITH": -3, "ORDER": 2, "ECONOMY": 1}},
            "Coupons are printed in two colours, both grey."),
    ], era="MIDDLE", once=True, requires={"min_year": 1980})

EXTRA_EVENTS["petrov_1983"] = ev(
    "petrov_1983", "The Satellite Alarm",
    "The early-warning system reports five inbound missiles. The duty "
    "officer has minutes to decide whether the system or his judgment is wrong.",
    [
        opt("Commend the officer; review the system",
            {"stats": {"PRESTIGE": 2, "MILITARY": 1, "ORDER": -1}},
            "A single lieutenant-colonel saves a century and gets an office."),
        opt("Raise readiness quietly",
            {"stats": {"MILITARY": 2, "PRESTIGE": -2}, "hc": -3},
            "Silos oil their hinges; the world sleeps badly for a week."),
        opt("Replace the system, blame the software",
            {"stats": {"ECONOMY": -3, "MILITARY": 1}},
            "New computers, same alarms, better manuals."),
    ], era="MIDDLE", once=True, requires={"min_year": 1983})

EXTRA_EVENTS["vietnam_peace"] = ev(
    "vietnam_peace", "The Paris Accords",
    "Hanoi and Washington sign in Paris. Your advisers recommend a victory "
    "statement, a naval visit, or an invoice.",
    [
        opt("A victory statement, twenty paragraphs",
            {"stats": {"PRESTIGE": 2, "FAITH": -1, "ORDER": 1}},
            "The world has stopped counting the paragraphs."),
        opt("Naval visit to Haiphong",
            {"stats": {"MILITARY": 1, "PRESTIGE": -1}, "hc": -2},
            "A cruiser anchors where the maps are still being drawn."),
        opt("Invoice them for the anti-aircraft",
            {"stats": {"ECONOMY": 2, "PRESTIGE": -2}, "hc": 4},
            "The guns were free; the reloads are not."),
    ], era="MIDDLE", once=True, requires={"min_year": 1973})

EXTRA_EVENTS["malta_summit"] = ev(
    "malta_summit", "Malta, In The Rain",
    "A summit on a storm-worn ship. The agenda says arms control; the "
    "weather insists on the end of the Cold War.",
    [
        opt("Declare the Cold War over",
            {"stats": {"PRESTIGE": 5, "FAITH": 2, "MILITARY": -2}},
            "Two men in raincoats end a contest neither of them started."),
        opt("Offer deep unilateral cuts",
            {"stats": {"PRESTIGE": 4, "MILITARY": -3, "ECONOMY": 2}},
            "Tanks go home; the savings arrive late and quietly."),
        opt("Attend, agree, announce nothing",
            {"stats": {"PRESTIGE": 1, "ORDER": 1}},
            "A communique of six sentences; four of them are about weather."),
    ], era="LATE", once=True, requires={"min_year": 1989})

EXTRA_EVENTS["alma_ata_1991"] = ev(
    "alma_ata_1991", "The Alma-Ata Protocol",
    "Eleven republics meet in Kazakhstan to decide what, exactly, survived "
    "the coup and the treaty. The word 'union' is in quotation marks.",
    [
        opt("Sign the protocol, keep the centre",
            {"stats": {"FAITH": 4, "ORDER": -2, "PRESTIGE": 2},
             "flag_add": "treaty_signed"},
            "Eleven signatures, one mast, and an agreement to keep talking."),
        opt("Sign, but move the capital's powers to the republics",
            {"stats": {"FAITH": 2, "ORDER": -4, "ECONOMY": 2}},
            "The centre becomes a postbox with a flag on it."),
        opt("Refuse the protocol, rule by decree",
            {"stats": {"ORDER": 5, "FAITH": -5, "PRESTIGE": -4}},
            "The decree is printed in one newspaper, in one city."),
    ], era="LATE", once=True, requires={"min_year": 1991, "max_year": 1991})

EXTRA_EVENTS["ruble_crash_1994"] = ev(
    "ruble_crash_1994", "The Rouble's Tuesday",
    "The currency loses a quarter of its value between Monday and lunch. "
    "The exchange offices run out of chalk and then out of currency.",
    [
        opt("Defend the rouble with the valas",
            {"stats": {"ECONOMY": 3}, "hc": -10},
            "The reserve pays for a Tuesday that ends on Wednesday."),
        opt("Let it float, blame the speculators",
            {"stats": {"ECONOMY": -3, "PRESTIGE": -2, "FAITH": -2}},
            "The speculators are identified, and immediately become bankers."),
        opt("Introduce a hard coupon for imports",
            {"stats": {"ECONOMY": 1, "ORDER": 2, "FAITH": -3}, "hc": 4},
            "Two currencies, one queue, three exchange rates."),
    ], era="NEW", once=True, requires={"min_year": 1994})

EXTRA_EVENTS["default_1998"] = ev(
    "default_1998", "The Default",
    "The treasury cannot roll the paper over. Foreign banks stop answering "
    "the telephone, and the telephone starts answering in English.",
    [
        opt("Default openly, restructure with the IMF",
            {"stats": {"ECONOMY": -2, "PRESTIGE": -2}, "hc": 6,
             "flag_add": "imf_deal"},
            "The default is announced, negotiated, and survived."),
        opt("Borrow from the banks that still answer",
            {"stats": {"ECONOMY": 2}, "hc": -8, "flag_add": "debt_trap"},
            "Time is bought at a rate the ministry refuses to say aloud."),
        opt("Pay in oil and gold instead of paper",
            {"stats": {"ECONOMY": 1, "PRESTIGE": 1}, "hc": -5},
            "Barrels settle an argument that roubles could not."),
    ], era="NEW", once=True, requires={"min_year": 1998})

EXTRA_EVENTS["kursk_2000"] = ev(
    "kursk_2000", "The Kursk",
    "The submarine is on the bottom, the crew is out of air, and the navy "
    "has been saying 'situation under control' for eleven hours.",
    [
        opt("Accept foreign rescue teams at once",
            {"stats": {"PRESTIGE": 3, "FAITH": 2, "MILITARY": -3}},
            "Norwegian divers arrive before the admiral finishes his sentence."),
        opt("Keep the fleet's pride, dive alone",
            {"stats": {"MILITARY": 1, "FAITH": -4, "PRESTIGE": -3}},
            "The pride is preserved; the crew is not."),
        opt("Wait, then announce it honestly",
            {"stats": {"FAITH": -1, "PRESTIGE": -1, "ORDER": 1}},
            "The announcement is late, complete, and believed by nobody."),
    ], era="NEW", once=True, requires={"min_year": 1999})

EXTRA_EVENTS["mir_2001"] = ev(
    "mir_2001", "Mir Comes Down",
    "The station is twenty years old and out of attitude control. The "
    "deorbit window is three orbits wide and the world is watching.",
    [
        opt("Bring it down safely over the Pacific",
            {"stats": {"PRESTIGE": 3, "FAITH": 1, "ECONOMY": -3}},
            "A controlled splash, and a documentary crew at mission control."),
        opt("Save it with one last mission",
            {"stats": {"PRESTIGE": 1, "ECONOMY": 1}, "hc": -5},
            "An old station gets a young budget and one extra year."),
        opt("Let it burn; fund the next one",
            {"stats": {"ECONOMY": 2, "PRESTIGE": -2, "FAITH": -2}},
            "The debris is catalogued; the successor is a slide."),
    ], era="NEW", once=True, requires={"min_year": 2000})
