"""All game events: data only.

Three ways an event reaches the player:
  1. RANDOM_POOLS  — era-flavoured, drawn each unscripted year
  2. SCRIPTED      — pinned to a specific historical year
  3. QUEUED        — triggered by earlier choices' "queue" ops (delayed consequences)

Congress events (great plenums) replace the regular event in their year.

Each option is (label, ops, outcome_note). Options may carry additional
"requires" — unavailable options are simply not offered (branching).
"""
from ..model import Event, Option


def _opt(label: str, ops: dict, outcomes: str = "", requires: dict | None = None) -> Option:
    return Option(label=label, ops=ops, outcomes=outcomes, requires=requires or {})


def _ev(id: str, title: str, text: str, options, *, era: str = "",
        once: bool = False, requires: dict | None = None,
        alt: bool = False) -> Event:
    return Event(id=id, title=title, text=text, options=tuple(options),
                 era=era, once=once, requires=requires or {}, alt=alt)


# ══════════════════════════════════════════════════════════════════
# CATALOGUE
# ══════════════════════════════════════════════════════════════════
EVENTS: dict[str, Event] = {}

# ---------------- EARLY ERA (1964-1975) ----------------
EVENTS["vodka_shortage"] = _ev(
    "vodka_shortage", "The Vodka Shortage",
    "Distilleries ship crates but shop windows are dry. Queueing men hum mourning songs.",
    [
        _opt("Ration via Party stores", {"stats": {"FAITH": -2, "ORDER": 1}},
             "The queues thin; the grumbling thickens."),
        _opt("Import rum confidence from Cuba", {"stats": {"ECONOMY": -3, "FAITH": 2}},
             "Rum bottles arrive; confidence arrives later."),
        _opt("Deny the problem entirely", {"stats": {"FAITH": -1}},
             "Pravda announces a surplus of patience and grain spirit."),
    ], era="EARLY")

EVENTS["samizdat"] = _ev(
    "samizdat", "Dissident Samizdat",
    "KGB agents seize nine mimeographed pages typed on onionskin.",
    [
        _opt("Trial the editors", {"stats": {"ORDER": 2, "FAITH": -3, "PRESTIGE": -2}},
             "A show trial produces quiet applause and loud Western letters."),
        _opt("Let it slide", {"stats": {"FAITH": 2, "ORDER": -1}},
             "The pages pass hand to hand like legislative jokes."),
        _opt("Confine them to a psychiatric ward", {"stats": {"ORDER": 3, "FAITH": -2, "PRESTIGE": -2}},
             "Diagnosis: 'sluggish schizophrenia'. The typewriters register it."),
    ], era="EARLY")

EVENTS["kosygin_memo"] = _ev(
    "kosygin_memo", "Kosygin Wants Reforms",
    "The Premier slides you a memo: profit indicators, worker councils, honesty about steel.",
    [
        _opt("Support pilot reforms",
             {"stats": {"ECONOMY": 4, "ORDER": -2}, "flag_add": "kosygin_pilot",
              "queue": [(2, "reform_wobble")]},
             "Two factories dare to profit. A pilot regime is born."),
        _opt("Send him to the archives", {"stats": {"ECONOMY": -1, "ORDER": 2}},
             "The memo is filed. So is its author's ambition."),
        _opt("Half-measures, report as success", {"stats": {"ECONOMY": 2, "FAITH": 1}},
             "Three pilot plots. Bureaucratic applause stills all progress."),
    ], era="EARLY")

EVENTS["n1_explodes"] = _ev(
    "n1_explodes", "N1 Rocket Explodes",
    "The giant booster detonates over Baikonur and the pad becomes a crater.",
    [
        _opt("Announce 'a planned structural test'", {"stats": {"PRESTIGE": -1, "FAITH": -1}},
             "Radio Moscow inventories a successful launch of nothing."),
        _opt("Fund the N1 again", {"stats": {"ECONOMY": -4, "PRESTIGE": 2}},
             "The Chief Designers get more metal and more patience."),
        _opt("Redirect the money to the military", {"stats": {"MILITARY": 2, "PRESTIGE": -1}},
             "Generals toast the loss of their rival's toy."),
    ], era="EARLY")

EVENTS["jazz_shortwave"] = _ev(
    "jazz_shortwave", "Western Jazz on the Shortwaves",
    "Students gather near windowsills with radios, dial-volume saxophone speaking brightly.",
    [
        _opt("Jam the frequencies", {"stats": {"ORDER": 2, "FAITH": -2}},
             "Static, then more saxophone, louder."),
        _opt("Permit sanctioned jazz clubs", {"stats": {"FAITH": 3, "ORDER": -1, "PRESTIGE": 1}},
             "Melodiya issues records; youth applies irony to the lyrics."),
        _opt("Call jazz 'a CIA weapon'", {"stats": {"FAITH": -2, "PRESTIGE": -1}},
             "Even the jazz-hating Party members sigh."),
    ], era="EARLY")

EVENTS["kuzbass_strike"] = _ev(
    "kuzbass_strike", "Coal Strike in Kuzbass",
    "Miners list grievances: boots, bread, and a ration coupon of dignity.",
    [
        _opt("Send boots and meat", {"stats": {"ECONOMY": -3, "FAITH": 2}},
             "Mittens arrive wearing slogans. Back to work."),
        _opt("Send the Internal Troops", {"stats": {"ORDER": 3, "FAITH": -3}},
             "The pit resumes; so does the whispering."),
        _opt("Pretend it didn't happen", {"stats": {"FAITH": -2, "PRESTIGE": -1}},
             "Western newspapers run a headline you cannot see."),
    ], era="EARLY")

EVENTS["virgin_lands"] = _ev(
    "virgin_lands", "The Virgin Lands Fail",
    "Kazakh steppe yields dust instead of grain. Erosion grins at agronomy.",
    [
        _opt("Buy grain from the USA", {"stats": {"ECONOMY": -4, "FAITH": 1},
                                        "hc": -3},
             "Solidarity with American farmers, priced objectively."),
        _opt("Blame weather, fine no one", {"stats": {"FAITH": -1, "PRESTIGE": -1}},
             "Meteorologists invent three storms per province."),
        _opt("Rush irrigation projects", {"stats": {"ECONOMY": -2, "FAITH": 2}},
             "Concrete channels leak prestige into sand."),
    ], era="EARLY")

EVENTS["cuban_sugar"] = _ev(
    "cuban_sugar", "Cuban Sugar & Rum",
    "Havana ships sugar and rum; asks for tractors and sympathy.",
    [
        _opt("Ship tractors, pallets of parts", {"stats": {"ECONOMY": -2, "PRESTIGE": 2}},
             "Fidel sends cigars and a warm letter."),
        _opt("Send advice instead", {"stats": {"PRESTIGE": -2, "FAITH": -1}},
             "Fidel's letter mentions 'comrade patience' three times."),
        _opt("Trade sugar for oil credits", {"stats": {"ECONOMY": 2, "PRESTIGE": -1}},
             "Paperwork trickles across three ministries."),
    ], era="EARLY")

EVENTS["prague_airwaves"] = _ev(
    "prague_airwaves", "Prague Voices Flood the Airwaves",
    "Radio debates grow so lively that censorship fades at the borders.",
    [
        _opt("Tighten jamming", {"stats": {"ORDER": 2, "FAITH": -2}},
             "Cables hum; Czechoslovak whispers persist."),
        _opt("Send Party inspectors", {"stats": {"ORDER": 1, "FAITH": -1, "PRESTIGE": -1}},
             "Cables and letters, all properly stamped."),
        _opt("Admit debate is 'errant but legal'", {"stats": {"FAITH": 2, "ORDER": -2, "PRESTIGE": 1}},
             "An unnerving act of political honesty."),
    ], era="EARLY")

EVENTS["golden_orlov"] = _ev(
    "golden_orlov", "The Golden Orlov Dacha",
    "A Politburo member's new dacha grows a private boat dock. Rumours multiply.",
    [
        _opt("Ignore, as always", {"stats": {"FAITH": -1, "PRESTIGE": -1}},
             "The dock gains a second mooring."),
        _opt("Quietly reshuffle him", {"stats": {"ORDER": 1, "FAITH": 1}},
             "He becomes an ambassador with a lake view instead."),
        _opt("Public anti-corruption trial", {"stats": {"FAITH": 3, "ORDER": -3, "PRESTIGE": 2}},
             "People cheer. Officials elsewhere clear their desks."),
    ], era="EARLY")

EVENTS["vienna_defection"] = _ev(
    "vienna_defection", "Defector at the Vienna Fair",
    "A TASS correspondent shares his archive with Western services.",
    [
        _opt("Reinforce residency procedures", {"stats": {"ORDER": 1, "MILITARY": 1, "PRESTIGE": -1}},
             "Every agent reports a field meeting with paperwork."),
        _opt("Recruit tradecraft training", {"stats": {"MILITARY": 2, "ECONOMY": -1}},
             "Andropov proposes one seminar and two follow-ups."),
        _opt("Liquidate the asset abroad", {"stats": {"PRESTIGE": -2, "ORDER": 1}},
             "Details are denied before anyone asks."),
    ], era="EARLY")

EVENTS["phantom_growth"] = _ev(
    "phantom_growth", "Gosplan's Tables Turn Negative",
    "Planned growth produces negative growth in four ministries.",
    [
        _opt("Tweak the plan numbers", {"stats": {"FAITH": -1, "ECONOMY": -1}},
             "Statistics find courage and rise a little."),
        _opt("Request foreign technology", {"stats": {"ECONOMY": 2, "PRESTIGE": -1}},
             "Fiat diesels arrive at two pilot plants."),
        _opt("Blame managers, change none", {"stats": {"FAITH": -2, "ORDER": 1}},
             "Two ministers are 'transferred for health'."),
    ], era="EARLY")

EVENTS["china_overture"] = _ev(
    "china_overture", "Beijing Sends a Quiet Overture",
    "A Chinese envoy proposes border talks and grain trade. Mao's insults remain optional.",
    [
        _opt("Embrace the rapprochement",
             {"stats": {"PRESTIGE": 2, "MILITARY": 1}, "flag_add": "china_thaw"},
             "Two red armies watch the Pacific in the same direction."),
        _opt("Send observers only", {"stats": {"PRESTIGE": 1}},
             "Delegations meet over tea; nothing binds."),
        _opt("Rebroadcast the old insults", {"stats": {"PRESTIGE": -1, "ORDER": 1}},
             "Radio Moscow's dialecticians earn their keep."),
    ], era="EARLY", once=True, requires={"not_flags": ["china_thaw"]})

EVENTS["de_gaulle"] = _ev(
    "de_gaulle", "De Gaulle Lands at Vnukovo",
    "France's President proposes trade and offers words about Europe from Atlantic to Urals.",
    [
        _opt("Sign industrial trade contracts", {"stats": {"ECONOMY": 3, "PRESTIGE": 2}},
             "French turbines and Soviet aromatics pass the mirrors."),
        _opt("Offer nuclear-era cultural exchange", {"stats": {"PRESTIGE": 3, "ECONOMY": -1},
                                                    "flag_add": "french_link"},
             "A special channel to Paris opens quietly."),
        _opt("Denounce Atlanticist France", {"stats": {"PRESTIGE": -1, "ORDER": 1}},
             "The General shrugs with imperial elegance."),
    ], era="EARLY", once=True)

EVENTS["cairo_arms"] = _ev(
    "cairo_arms", "The Cairo Bazaar",
    "An Arab client requests arms: armour, aircraft, and politically active patience.",
    [
        _opt("Provide the full package", {"stats": {"MILITARY": -2, "PRESTIGE": 2},
                                          "flag_add": "arab_arms"},
             "Moscow's arsenals find the Middle East's markets."),
        _opt("Send advisors only", {"stats": {"MILITARY": -1}},
             "Uniforms without armour; debt without delivery."),
        _opt("Politely decline", {"stats": {"PRESTIGE": -2}},
             "Cairo buys from elsewhere; your port fees shrink."),
    ], era="EARLY")

# ---------------- MIDDLE ERA (1976-1984) ----------------
EVENTS["solidarnosc"] = _ev(
    "solidarnosc", "Solidarność Rises (Poland)",
    "Gdańsk shipyard strikes spread. Jaruzelski asks for 'brotherly advice'.",
    [
        _opt("Advise martial law, send nothing", {"stats": {"ORDER": 3, "PRESTIGE": -2}},
             "Warsaw cracks down on its own; Moscow shrugs."),
        _opt("Threaten open intervention", {"stats": {"ORDER": 2, "PRESTIGE": -4}},
             "Western TV relays dark memories of 1968."),
        _opt("Send economic concessions", {"stats": {"ECONOMY": -4, "PRESTIGE": 2}},
             "Polish dockers wave Soviet shipments of meat."),
    ], era="MIDDLE")

EVENTS["grain_scandal"] = _ev(
    "grain_scandal", "Grain Import Scandal",
    "A statistician confesses the harvest is 'narratively optimistic'.",
    [
        _opt("Hide behind weather", {"stats": {"FAITH": -2, "PRESTIGE": -1}},
             "Meteorologists win an unplanned overtime bonus."),
        _opt("Buy Canadian wheat quietly", {"stats": {"ECONOMY": -3, "FAITH": 2},
                                            "hc": -4},
             "Bread appears; so do Western spot checks."),
        _opt("Punish the statisticians", {"stats": {"ORDER": 2, "FAITH": -2, "ECONOMY": -1}},
             "Numbers behave; grain does not."),
    ], era="MIDDLE")

EVENTS["andropov_dossiers"] = _ev(
    "andropov_dossiers", "Andropov's Anti-Corruption Dossiers",
    "KGB folders land on your desk: officials with dachas, mistresses, foreign watches.",
    [
        _opt("Let him strike the Old Guard", {"stats": {"ORDER": 2, "FAITH": 3, "ECONOMY": 1}},
             "Notable resignations at prestigious dachas."),
        _opt("Shelve the dossiers", {"stats": {"FAITH": -2, "PRESTIGE": -1}},
             "The files age in a locked cabinet per bureaucracy."),
        _opt("Trials, but only minor fish", {"stats": {"FAITH": -1, "ORDER": 1}},
             "Two shop managers pay for three gowns of sin."),
    ], era="MIDDLE")

EVENTS["war_scares"] = _ev(
    "war_scares", "War Scares and Crackling Radio",
    "NATO exercises read like first-strike rehearsal. The KGB wants readiness.",
    [
        _opt("Mobilize partially", {"stats": {"MILITARY": 2, "ECONOMY": -2, "PRESTIGE": -1}},
             "Tanks rumble near Vilnius. NATO grows nervous."),
        _opt("Approach quietly via GDR channels", {"stats": {"PRESTIGE": 2, "ORDER": 1}},
             "East Berlin passes a note; war painters relax."),
        _opt("Ignore the signals", {"stats": {"MILITARY": -1}},
             "History books will judge this shelf someday."),
    ], era="MIDDLE")

EVENTS["black_market_boom"] = _ev(
    "black_market_boom", "Black Market Boom",
    "Levi's jeans cost a monthly salary. Currency is 'fictitious but beloved'.",
    [
        _opt("Raid the bazaars", {"stats": {"ORDER": 2, "FAITH": -2}},
             "Seized blue jeans vanish into KGB warehouses."),
        _opt("Open Beryozka-style shops", {"stats": {"ECONOMY": 3, "FAITH": -1},
                                           "hc": 4},
             "Hard-currency boutiques soothe official appetites."),
        _opt("Look away", {"stats": {"FAITH": 1, "ORDER": -2, "ECONOMY": -1}},
             "The shadow economy pays employees and cadres alike."),
    ], era="MIDDLE")

EVENTS["oil_shock"] = _ev(
    "oil_shock", "The Oil Price Collapses",
    "Global crude tumbles. Gosplan recalculates three times, weeps once.",
    [
        _opt("Austerity in the ministries", {"stats": {"ECONOMY": 1, "FAITH": -2}},
             "Caviar at banquets is declared 'voluntary'."),
        _opt("Borrow from the West", {"stats": {"ECONOMY": 3, "PRESTIGE": -1},
                                      "hc": 8},
             "Loans buy time, and time costs interest."),
        _opt("Squeeze consumers", {"stats": {"ECONOMY": 2, "FAITH": -3}},
             "Queue discipline becomes a Party virtue."),
    ], era="MIDDLE")

EVENTS["poland_health"] = _ev(
    "poland_health", "Warsaw Requests Medical Counsel",
    "Jaruzelski's government stumbles; Warsaw solicits Soviet advisors.",
    [
        _opt("Send Soviet doctors with orders", {"stats": {"ORDER": 1, "PRESTIGE": -1, "MILITARY": 1}},
             "Your advisors' medical advice is politically vigorous."),
        _opt("Let Poles handle Poles", {"stats": {"PRESTIGE": 1, "ORDER": -1}},
             "Warsaw resolves this with its own paperwork."),
        _opt("Announce 'fraternal unity'", {"stats": {"FAITH": 1, "PRESTIGE": -1}},
             "TASS composes three paragraphs of nouns."),
    ], era="MIDDLE")

EVENTS["worker_letter"] = _ev(
    "worker_letter", "A Worker Writes About Emptiness",
    "A Leningrad worker writes: 'We greet openness, but not with empty shelves.'",
    [
        _opt("Publish the letter", {"stats": {"FAITH": 3, "ORDER": -1, "PRESTIGE": 2}},
             "Pravda prints honesty. The nation gasps, politely."),
        _opt("Reply privately, praise the man", {"stats": {"FAITH": 1, "ORDER": 1}},
             "A signed photo and ration coupons arrive."),
        _opt("Classify the letter anti-Soviet", {"stats": {"ORDER": 2, "FAITH": -3}},
             "Archive shelf B-41 gains more paper."),
    ], era="MIDDLE")

EVENTS["athletes_defect"] = _ev(
    "athletes_defect", "Soviet Athletes Defect",
    "A chess grandmaster and a hockey winger vanish in Vienna.",
    [
        _opt("Punish their trainers' staff", {"stats": {"ORDER": 2, "FAITH": -2, "PRESTIGE": -1}},
             "The word 'hostage' circulates in Western papers."),
        _opt("Improve athletes' conditions", {"stats": {"ECONOMY": -2, "FAITH": 1, "PRESTIGE": 1}},
             "New uniforms, better sport schools. Defections slow."),
        _opt("Recruit them back via KGB channels", {"stats": {"PRESTIGE": 2, "MILITARY": 1}},
             "One returns; the other writes a memoir in Paris."),
    ], era="MIDDLE")

EVENTS["brezhnev_orders"] = _ev(
    "brezhnev_orders", "Brezhnev Honours Himself",
    "A fifth Order is awarded to a portrait of a portrait.",
    [
        _opt("Publish the award", {"stats": {"FAITH": -1, "PRESTIGE": -1}},
             "Newspapers run identical photographs."),
        _opt("Award somebody else", {"stats": {"FAITH": 2, "ECONOMY": -1}},
             "A tractor driver becomes a Hero of Socialism."),
        _opt("Cancel the ceremony", {"stats": {"ORDER": -1, "FAITH": 1}},
             "The laureates grumble about 'rash collegiality'."),
    ], era="MIDDLE")

EVENTS["uzbek_cotton"] = _ev(
    "uzbek_cotton", "Uzbek Cotton Fantasy",
    "Region reports cotton by the ton. Fields, thinner, share less truth.",
    [
        _opt("Order an audit", {"stats": {"FAITH": 2, "ORDER": -2, "ECONOMY": -1}},
             "Local Party secretaries discover forgotten honesty."),
        _opt("Accept the harvest report", {"stats": {"ECONOMY": -2, "FAITH": -1}},
             "Gosplan gets cotton; the fields get questions."),
        _opt("Punish the auditors", {"stats": {"ORDER": 2, "FAITH": -2}},
             "Two honest men retire to Tashkent's quiet suburbs."),
    ], era="MIDDLE")

EVENTS["foreign_debt"] = _ev(
    "foreign_debt", "Foreign Debt Sneaks Up",
    "Trade ministry reveals the currency holdings won't cover grain debts.",
    [
        _opt("Cut military procurement bills", {"stats": {"MILITARY": -2, "ECONOMY": 2}},
             "Generals write letters; loans get cheaper."),
        _opt("Reduce imports of Western tech", {"stats": {"ECONOMY": -1, "PRESTIGE": -1}},
             "Industrial espionage fails loudly twice."),
        _opt("Sell gold reserves", {"stats": {"ECONOMY": 4, "PRESTIGE": -2},
                                    "hc": 10},
             "Swiss bankers toast 'comrade prudence'."),
    ], era="MIDDLE")

EVENTS["yugo_study"] = _ev(
    "yugo_study", "Tito's Textbooks Reach You",
    "A Dublin-style journal discusses Yugoslav self-management and its seductions.",
    [
        _opt("Study the Yugoslav model", {"stats": {"ECONOMY": 3, "ORDER": -1},
                                          "flag_add": "yugo_study"},
             "Worker councils get a respectful pamphlet."),
        _opt("Ban the book", {"stats": {"ORDER": 2, "FAITH": -1}},
             "The banned list gains one item and ten copies of courage."),
        _opt("Shelve quietly", {}, "The shelf is quiet. So is the idea."),
    ], era="MIDDLE", once=True)

EVENTS["afghan_trap"] = _ev(
    "afghan_trap", "The Mountain Trap",
    "Kabul's arithmetic worsens. Your columns eat ice and ammunition.",
    [
        _opt("Escalate with more divisions",
             {"stats": {"MILITARY": -3, "PRESTIGE": -1}, "flag_add": "afghan_deep"},
             "More tanks arrive; the mountains remain unsaleable."),
        _opt("Withdraw and cut losses",
             {"flag_rm": "at_war", "flag_add": "afghan_withdraw"},
             "Columns return across the Amu Darya. Prestige bleeds; men live."),
        _opt("Hold the present course", {"stats": {"MILITARY": -2, "ECONOMY": -1}},
             "Attrition stays attrition."),
    ], era="MIDDLE", requires={"flags": ["at_war"]})

EVENTS["pipeline_sabotage"] = _ev(
    "pipeline_sabotage", "The Pipeline Knows Sabotage",
    "A large Soviet pipe mysteriously fractures; the West whistles innocently.",
    [
        _opt("Import American turbines quietly", {"stats": {"ECONOMY": -2, "PRESTIGE": -1},
                                                  "hc": -5},
             "Third-country invoices; the embargo gains bandaids."),
        _opt("Race domestic turbines", {"stats": {"ECONOMY": -4}},
             "Two slow years; engineers reap scars and pride."),
        _opt("Ration sectors for a season", {"stats": {"ECONOMY": -3, "FAITH": -1}},
             "Shops get 'planned maintenance' excuses."),
    ], era="MIDDLE", once=True)

EVENTS["helsinki_accords"] = _ev(
    "helsinki_accords", "The Helsinki Baskets",
    "The Final Act offers trade and peace — and 'Basket III' monitors your borders.",
    [
        _opt("Sign the lot, Basket III included",
             {"stats": {"PRESTIGE": 3, "ORDER": -2}, "flag_add": "helsinki"},
             "Human-rights Helsinki Watch groups set up desks in nine capitals."),
        _opt("Sign, but file Basket III away", {"stats": {"PRESTIGE": 2, "ORDER": 1}},
             "Trade flows; the monitors queue at your embassy."),
        _opt("Refuse as 'imperialist dictation'", {"stats": {"ORDER": 1, "PRESTIGE": -2}},
             "You keep the buffers; Europe keeps the receipts."),
    ], era="MIDDLE", once=True)

# ---------------- LATE ERA (1985-1991) ----------------
EVENTS["glasnost_press"] = _ev(
    "glasnost_press", "Glasnost Surges in Print",
    "Magazines publish honest essays. Subscriptions triple and censors riot in their offices.",
    [
        _opt("Expand glasnost further", {"stats": {"FAITH": 4, "PRESTIGE": 3, "ORDER": -4}},
             "The press blooms; the Party chews nails anxiously."),
        _opt("Cap the magazines at three pages", {"stats": {"FAITH": -2, "ORDER": 1}},
             "Readers buy three extra copies for missing pages."),
        _opt("Redirect topics toward show business", {"stats": {"FAITH": -1, "PRESTIGE": -1}},
             "An interview with a pop star displaces three historians."),
    ], era="LATE")

EVENTS["karabakh"] = _ev(
    "karabakh", "Nagorno-Karabakh Erupts",
    "Armenian and Azerbaijani crowds collide. Moscow's telegram box burns.",
    [
        _opt("Send Internal Troops", {"stats": {"ORDER": 3, "FAITH": -2, "PRESTIGE": -2}},
             "Tranquillity is achieved, briefly, with barricades."),
        _opt("Promise autonomy reform", {"stats": {"FAITH": 1, "ORDER": -1, "PRESTIGE": 1}},
             "Commissions are founded; salutes are provisional."),
        _opt("Blame local nationalist elites", {"stats": {"PRESTIGE": -2, "ORDER": 1}},
             "Everyone blames somebody; nobody is satisfied."),
    ], era="LATE")

EVENTS["baltic_chain"] = _ev(
    "baltic_chain", "The Baltic Chain",
    "Two million people form a 600 km human chain across three republics.",
    [
        _opt("Acknowledge it on television", {"stats": {"FAITH": 2, "PRESTIGE": 2, "ORDER": -3}},
             "Anchors describe unity. Somebody whispers 'shows'."),
        _opt("Disperse the chain with police", {"stats": {"ORDER": 2, "FAITH": -4, "PRESTIGE": -3}},
             "Wrist links are broken by baton links."),
        _opt("Quietly re-examine the Molotov pact", {"stats": {"PRESTIGE": 3, "ORDER": -2}},
             "Historians are suddenly extremely popular."),
    ], era="LATE")

EVENTS["mic_reform"] = _ev(
    "mic_reform", "The Military-Industrial lobby argues",
    "Defence ministers demand budget; Gosplan demands survival.",
    [
        _opt("Convert factories to consumer goods", {"stats": {"ECONOMY": 3, "MILITARY": -2}},
             "Tractor plants start producing trickle-batteries."),
        _opt("Defend the MIC budget", {"stats": {"MILITARY": 2, "ECONOMY": -3}},
             "The generals applaud; the shops do not."),
        _opt("Split the difference annually", {"stats": {"ECONOMY": 1, "MILITARY": -1}},
             "Committee mathematics strikes again."),
    ], era="LATE")

EVENTS["yeltsin_truck"] = _ev(
    "yeltsin_truck", "Yeltsin on a Truck",
    "Boris Yeltsin addresses crowds from a vehicle roof, fists raised.",
    [
        _opt("Expel him from the Party", {"stats": {"ORDER": 2, "FAITH": -3, "PRESTIGE": -2}},
             "He becomes a martyr with a loud voice."),
        _opt("Invite him into the leadership", {"stats": {"FAITH": 2, "ORDER": -2, "PRESTIGE": 1}},
             "He accepts awkwardly and promises brisk reform."),
        _opt("Sideline him to a construction trust", {"stats": {"FAITH": -1, "ORDER": 1}},
             "He supervises bridges; crowds dream of speeches."),
    ], era="LATE")

EVENTS["berlin_strains"] = _ev(
    "berlin_strains", "East Germany Strains",
    "Travellers flee via Hungary to Austria. Honecker asks for direction.",
    [
        _opt("Close the Hungarian border", {"stats": {"ORDER": 3, "PRESTIGE": -3}},
             "Barbed wire returns to the pan-European press."),
        _opt("Admit the Wall is obsolete", {"stats": {"FAITH": 3, "PRESTIGE": 3, "ORDER": -4}},
             "Historians collapse; tourists celebrate."),
        _opt("Blame GDR interior policy", {"stats": {"PRESTIGE": 1, "ORDER": -2}},
             "Berlin is left alone with its architected sorrow."),
    ], era="LATE", requires={"max_year": 1988})

EVENTS["market_queues"] = _ev(
    "market_queues", "Sugar, Soap and Rumours",
    "Empty shelves publish themselves on national television now.",
    [
        _opt("Army distribution squads", {"stats": {"ECONOMY": -2, "FAITH": 2, "MILITARY": -1}},
             "Soldiers unload bread convoys; applause is real."),
        _opt("Legalize farmers markets", {"stats": {"ECONOMY": 3, "FAITH": 3, "ORDER": -2}},
             "Private stalls bloom in suburban courtyards."),
        _opt("Promise 1993 prosperity", {"stats": {"FAITH": -3}},
             "Reformers note the promise; so do the shelves."),
    ], era="LATE")

EVENTS["chip_embargo"] = _ev(
    "chip_embargo", "The Western Chip Embargo",
    "US sanctions stop computer exports. Factories wait for software rivers.",
    [
        _opt("Fund domestic semiconductors", {"stats": {"ECONOMY": -4, "MILITARY": 2}},
             "Mikron's engineers squint at imported manuals."),
        _opt("Lean on the microelectronics academy",
             {"stats": {"ECONOMY": -1, "MILITARY": 2}},
             "Your choice of a decade past pays dividends here.",
             requires={"flags": ["micro"]}),
        _opt("Smuggle through third countries", {"stats": {"ECONOMY": -1, "MILITARY": 1, "PRESTIGE": -1}},
             "Two agents succeed; one walks into an airport lobby."),
        _opt("Admit the gap publicly", {"stats": {"PRESTIGE": 1, "FAITH": -2}},
             "Honesty is refreshing; factories are still idle."),
    ], era="LATE")

EVENTS["crimea_return"] = _ev(
    "crimea_return", "Crimea Wants its Homes Back",
    "Crimean Tatars petition en masse to return to their homeland.",
    [
        _opt("Permit gradual return", {"stats": {"FAITH": 3, "ORDER": -1, "PRESTIGE": 2}},
             "Trains roll south; documents are slow."),
        _opt("Deny the petitions", {"stats": {"FAITH": -2, "PRESTIGE": -2}},
             "Protests resume on the Day of Remembrance."),
        _opt("Grant symbolic autonomy", {"stats": {"FAITH": 1, "ORDER": 1}},
             "Banners and brochures, committees quietly famous."),
    ], era="LATE", once=True)

EVENTS["caviar_conference"] = _ev(
    "caviar_conference", "The Caviar Congress",
    "Party congress debates reform while serving sturgeon to 5,000 delegates.",
    [
        _opt("Serve plain bread instead", {"stats": {"FAITH": 3, "ORDER": -1}},
             "Delegates chew; delegates think."),
        _opt("Export the caviar for currency", {"stats": {"ECONOMY": 2, "FAITH": -1}},
             "Swiss hotels praise Soviet cuisine."),
        _opt("Ignore the imagery", {"stats": {"FAITH": -2, "PRESTIGE": -1}},
             "A cartoonist wins an international prize."),
    ], era="LATE")

EVENTS["spitak_quake"] = _ev(
    "spitak_quake", "Armenian Earthquake Relief",
    "Spitak is ruined. The Army arrives with tents and inadequate logistics.",
    [
        _opt("Accept Western aid openly", {"stats": {"PRESTIGE": 3, "FAITH": 2}},
             "American rescuers fly in; props to both flags."),
        _opt("Rely only on Soviet forces", {"stats": {"MILITARY": 1, "FAITH": -2}},
             "Logistics chafe; handwritten notes rescue some."),
        _opt("Blame local builders", {"stats": {"FAITH": -3, "PRESTIGE": -1}},
             "Very few people accept this explanation."),
    ], era="LATE", once=True)

EVENTS["referendum_fever"] = _ev(
    "referendum_fever", "Referendum Fever",
    "Republics ask: 'Renewed federation or independence?'",
    [
        _opt("Draft a new Union Treaty", {"stats": {"FAITH": 3, "ORDER": -2, "PRESTIGE": 2}},
             "Paper glistens with fresh compromise."),
        _opt("Strengthen federal courts instead", {"stats": {"ORDER": 2, "FAITH": -2}},
             "Lawyers become the new national pastime."),
        _opt("Boycott the referendum", {"stats": {"ORDER": -3, "FAITH": -1}},
             "The ballot box finds other employers."),
    ], era="LATE")

EVENTS["coops_press"] = _ev(
    "coops_press", "Co-op Millionaires in the Press",
    "Your legalized cooperatives produced millionaires. So do the headlines.",
    [
        _opt("Let private wealth breathe", {"stats": {"FAITH": 2, "ORDER": -2}},
             "The rich become a topic, then a habit."),
        _opt("Tax the new millionaires", {"stats": {"ECONOMY": 2, "FAITH": -1, "ORDER": 1}},
             "Luxury cars learn the tax office's address."),
        _opt("Ban cooperatives again", {"stats": {"ORDER": 2, "FAITH": -2},
                                        "flag_rm": "coops"},
             "Bureaucracy dusts victory medals from 1929."),
    ], era="LATE", once=True, requires={"flags": ["coops"]})

EVENTS["mr_archives"] = _ev(
    "mr_archives", "The Molotov–Ribbentrop Archive",
    "Old protocols surface about the secret protocols of 1939. Historians hold their pens.",
    [
        _opt("Admit the protocol exists", {"stats": {"PRESTIGE": 3, "ORDER": -2, "FAITH": 1},
                                            "flag_add": "mr_admitted"},
             "The Commission publishes truth with footnotes."),
        _opt("Deny the protocol exists", {"stats": {"PRESTIGE": -2}},
             "Denial photocopies itself into every argument."),
        _opt("Commission quiet historians", {"stats": {"PRESTIGE": 1, "ORDER": -1}},
             "A report live-draws in five guarded copies."),
    ], era="LATE", once=True, requires={"min_year": 1988})

EVENTS["vodka_campaign"] = _ev(
    "vodka_campaign", "The Anti-Alcohol Campaign",
    "Reformers demand a sober Union. Vodka is half of agriculture's cashflow.",
    [
        _opt("Cut sales hard, close distilleries",
             {"stats": {"ECONOMY": -4, "FAITH": -3, "ORDER": 2}, "flag_add": "dry_decade"},
             "Sugar vanishes into home brew; Sobriety Societies multiply."),
        _opt("Half-measures: higher prices only", {"stats": {"ECONOMY": -1, "FAITH": -1, "ORDER": 1}},
             "Queues lengthen politely at wine departments."),
        _opt("Refuse: 'The people have earned their glasses'",
             {"stats": {"FAITH": 3, "PRESTIGE": -1, "ECONOMY": 1}},
             "The Old Guard toasts you privately; doctors send memoranda."),
    ], era="LATE", once=True, requires={"min_year": 1985})

EVENTS["nomenklatura_rift"] = _ev(
    "nomenklatura_rift", "The Nomenklatura Rift",
    "Young technocrats want markets and market-grade privileges. The Old Guard wants lunch.",
    [
        _opt("Side with the technocrats",
             {"stats": {"FAITH": 2, "ORDER": -2, "ECONOMY": 2}, "flag_add": "cadres_rift"},
             "Ministries fill with calculators and expensive watches."),
        _opt("Side with the Old Guard", {"stats": {"ORDER": 3, "FAITH": -2, "ECONOMY": -1}},
             "Loyalty restored; three bright deputy ministers retire early."),
        _opt("Split the committees and hope", {"stats": {"ORDER": -1, "ECONOMY": 1}},
             "Nobody is satisfied; paperwork doubles."),
    ], era="LATE", once=True, requires={"any_flags": ["perestroika", "reformer", "cadres_refresh"]})

EVENTS["singapore_dream"] = _ev(
    "singapore_dream", "The Singapore Envelope",
    "A minister returns from the tropics with charts: tax havens, ports, miracles.",
    [
        _opt("Build a free port on the Pacific",
             {"stats": {"ECONOMY": 5, "ORDER": -3, "PRESTIGE": 2}, "flag_add": "free_port"},
             "Container cranes rise over Severodvinsk-daydreams."),
        _opt("File it under 'bourgeois economics'", {"stats": {"ORDER": 2, "FAITH": -1}},
             "The envelope gains a stamp and a dust coat."),
        _opt("Trial one zone only, quietly", {"stats": {"ECONOMY": 2, "ORDER": -1}},
             "Nakhodka learns accounting by fire."),
    ], era="LATE", once=True, alt=True,
    requires={"any_flags": ["price_done", "coops", "kosygin_full"]})

EVENTS["coal_miners_1989"] = _ev(
    "coal_miners_1989", "The Coal Miners' Summer",
    "Kuzbass, Donbass, Vorkuta: a million pick-axes strike; the trains slow to a crawl.",
    [
        _opt("Concede wages, vouchers and sugar",
             {"stats": {"ECONOMY": -3, "FAITH": 3, "ORDER": -1}, "flag_add": "miners_conceded"},
             "The pits roar back; so do the wage accounts."),
        _opt("Declare an emergency, send internal troops",
             {"stats": {"ORDER": -2, "FAITH": -4, "PRESTIGE": -2}},
             "Miners' committees go underground in every sense."),
        _opt("Negotiate through union committees",
             {"stats": {"ECONOMY": -1, "FAITH": 2, "ORDER": -2}, "flag_add": "miners_conceded"},
             "Signed protocols nobody fully honours, official honesty."),
    ])

# ---------------- CONGRESS EVENTS (replace the year's event) ----------------
EVENTS["plenum_1970"] = _ev(
    "plenum_1970", "☰ THE 1970 PLENUM: On Growth",
    "The Central Committee gathers for grand strategy. One law of the decade gets signed here.",
    [
        _opt("Sign the full Kosygin package",
             {"stats": {"ECONOMY": 6, "FAITH": 2, "ORDER": -2}, "flag_add": "kosygin_pilot"},
             "Profit indicators enter the law. Factory directors blink in the light."),
        _opt("Legislate organic stability",
             {"stats": {"ORDER": 4, "FAITH": -2}, "flag_add": "stability_law"},
             "Order becomes a construction project with decades of blueprints."),
        _opt("Consumer offensive law",
             {"stats": {"FAITH": 5, "ECONOMY": -2}},
             "Britain's shelves seem far, but the road starts here."),
        _opt("Deterrence & arms law",
             {"stats": {"MILITARY": 5, "ECONOMY": -3}},
             "The rocket forces gain a decade of budget arithmetic."),
    ], once=True)

EVENTS["blueprint_1978"] = _ev(
    "blueprint_1978", "☰ THE 1978 BLUEPRINT", 
    "The development congress drafts the middle-generation programme. One mission is chosen.",
    [
        _opt("Siberian oil & gas blitz",
             {"stats": {"ECONOMY": 5, "PRESTIGE": 1}, "flag_add": "siberian"},
             "Pipelines will finance something, someday, maybe."),
        _opt("Microelectronics academy",
             {"stats": {"PRESTIGE": 3, "ECONOMY": -1}, "flag_add": "micro"},
             "A generation learns binary arithmetic and jokes about clerks."),
        _opt("Grain sovereignty programme",
             {"stats": {"FAITH": 3, "ECONOMY": -2}},
             "Tractors queue to queue for tractors."),
        _opt("Ocean navy doctrine",
             {"stats": {"MILITARY": 4, "ECONOMY": -3}, "flag_add": "navy_blue"},
             "Flags of steel splatter across the seven seas."),
    ], once=True)

EVENTS["acceleration_1986"] = _ev(
    "acceleration_1986", "☰ THE 1986 ACCELERATION CONGRESS",
    "A young Politburo tables four futures. One motion outvotes the rest by lunch.",
    [
        _opt("Acceleration: rush modernization",
             {"stats": {"ECONOMY": 4, "MILITARY": 2}, "flag_add": "accel"},
             "Bicycle factories re-tool; the wall clock gains a jet engine."),
        _opt("Glasnost above all",
             {"stats": {"FAITH": 4, "ORDER": -3, "PRESTIGE": 2}, "flag_add": "glasnost_early"},
             "The press breathes early and loudly."),
        _opt("Cooperative relaxations",
             {"stats": {"ECONOMY": 4, "ORDER": -2}, "flag_add": "coops"},
             "Co-ops ferment legally from Kaliningrad to Kamchatka."),
        _opt("Motion of Party discipline",
             {"stats": {"ORDER": 4, "FAITH": -2}},
             "Discipline gets its own poster and a fifth column."),
    ], once=True)

# ---------------- QUEUED / DELAYED EVENTS ----------------
EVENTS["nato_ultimatum_reply"] = _ev(
    "nato_ultimatum_reply", "NATO Answers the Ultimatum",
    "Your atomic ultimatum crashed onto NATO's desk weeks ago. The reply takes a special courier.",
    [
        _opt("Back down", {"stats": {"PRESTIGE": -4, "MILITARY": -2}},
             "Silos reclose. Diplomats relearn the word 'tagebuch'."),
        _opt("Hold firm", {"stats": {"MILITARY": 3, "PRESTIGE": -6}, "flag_add": "brink"},
             "The world parks at the brink of midnight."),
        _opt("Open a secret hotline", {"stats": {"PRESTIGE": 3, "MILITARY": -1}},
             "One red telephone calms one crisis."),
    ])

# ══════════════════════════════════════════════════════════════════
# POOLS & SCRIPTED YEARS
# ══════════════════════════════════════════════════════════════════
RANDOM_POOLS: dict[str, tuple[str, ...]] = {
    "EARLY": (
        "vodka_shortage", "samizdat", "kosygin_memo", "n1_explodes",
        "jazz_shortwave", "kuzbass_strike", "virgin_lands", "cuban_sugar",
        "prague_airwaves", "golden_orlov", "vienna_defection",
        "phantom_growth", "china_overture", "de_gaulle", "cairo_arms",
        "cosmonaut_letter", "baikal_pulp", "gagarin_crash",
    ),
    "MIDDLE": (
        "solidarnosc", "grain_scandal", "andropov_dossiers", "war_scares",
        "black_market_boom", "oil_shock", "poland_health", "worker_letter",
        "athletes_defect", "brezhnev_orders", "uzbek_cotton", "foreign_debt",
        "yugo_study", "afghan_trap", "pipeline_sabotage", "helsinki_accords",
        "vatican_signal", "grain_bill",
        "vietnam_peace", "sakharov_nobel", "polish_pope", "grain_embargo",
        "petrov_1983",
    ),
    "LATE": (
        "glasnost_press", "karabakh", "baltic_chain", "mic_reform",
        "yeltsin_truck", "berlin_strains", "market_queues", "chip_embargo",
        "crimea_return", "caviar_conference", "spitak_quake",
        "referendum_fever", "coops_press", "mr_archives",
        "vodka_campaign", "nomenklatura_rift", "singapore_dream",
        "name_duel", "cassette_wave",
        "malta_summit", "alma_ata_1991",
    ),
    "NEW": (
        "oligarch_weekend", "brain_gain", "siberia_2", "network_age",
        "church_revival", "arctic_route", "wild_east_jobs",
        "ruble_crash_1994", "default_1998", "kursk_2000", "mir_2001",
    ),
}

# Congress years: the congress event replaces the regular random event.
CONGRESS_YEARS: dict[int, str] = {1970: "plenum_1970", 1978: "blueprint_1978",
                                  1986: "acceleration_1986",
                                  1996: "millennium_congress"}

# Historical crises pinned to their years.
SCRIPTED: dict[int, tuple[str, ...]] = {
    1968: ("prague_spring",),
    1969: ("ussuri_clashes",),
    1979: ("afghanistan_1979",),
    1980: ("olympics_1980",),
    1982: ("succession_1982",),
    1983: ("able_archer",),
    1985: ("new_secretary",),
    1986: ("chernobyl",),
    1987: ("reykjavik",),
    1989: ("wall_falls", "coal_miners_1989"),
    1991: ("august_coup",),
    # ── v4: the extended era (fires only if you earned 1992-2001) ──
    1992: ("rouble_zone",),
    1993: ("union_charter",),
    1997: ("asian_flu_1997",),
    1999: ("nato_east_1999",),
    2000: ("millennium_message",),
}

# ---- scripted historical events (registered below the catalogue) ----
EVENTS["prague_spring"] = _ev(
    "prague_spring", "Prague Spring, 1968",
    "Dubček insists on 'socialism with a human face'. The Politburo faces faces.",
    [
        _opt("Send tanks in", {"stats": {"ORDER": 4, "PRESTIGE": -5, "FAITH": -3},
                               "flag_add": "prague_tanks"},
             "Operation Danube proceeds. The word 'normalization' acquires teeth."),
        _opt("Negotiate with Dubček", {"stats": {"PRESTIGE": 3, "ORDER": -2, "FAITH": 2},
                                        "flag_add": "prague_talks"},
             "Talks in Czech. Kissinger takes notes; the Party upholsters itself."),
        _opt("Pressure him to end reforms", {"stats": {"ORDER": 1, "PRESTIGE": -1}},
             "Letters and telephone calls accomplish partial awkwardness."),
    ])

EVENTS["ussuri_clashes"] = _ev(
    "ussuri_clashes", "Ussuri River Border Clashes",
    "Sino-Soviet skirmishes on Damansky Island. Mao recites ancient insults.",
    [
        _opt("Mass troops at the border", {"stats": {"MILITARY": 3, "ECONOMY": -3, "PRESTIGE": -1}},
             "Red banners face red banners. Somewhere, a colonel's phone rings."),
        _opt("Secret talks in Beijing", {"stats": {"PRESTIGE": 2, "ORDER": 1},
                                          "flag_add": "china_thaw"},
             "Two delegations exchange tea and veiled rationales."),
        _opt("Broadcast propaganda only", {"stats": {"FAITH": 1, "PRESTIGE": -1}},
             "Radio Moscow explains the Chinese perfidy in four dialects."),
    ])

EVENTS["afghanistan_1979"] = _ev(
    "afghanistan_1979", "Afghanistan: The Amin Problem",
    "Herat burns. Taraki is dead. The Politburo holds three midnight sessions.",
    [
        _opt("Intervene with the 40th Army",
             {"stats": {"MILITARY": 4, "PRESTIGE": -4, "ECONOMY": -2},
              "flag_add": "at_war", "queue": [(3, "afghan_stalemate")]},
             "Soviet columns cross the Amu Darya. The mountains are patient."),
        _opt("Support the regime with materiel only", {"stats": {"MILITARY": 1, "PRESTIGE": -1, "ECONOMY": -1}},
             "Mi-24s and advisers cross the border; columns do not."),
        _opt("Wash your hands of Kabul", {"stats": {"PRESTIGE": 1, "ORDER": -1}},
             "Kabul resolves its arithmetic without you. For now."),
    ])

EVENTS["olympics_1980"] = _ev(
    "olympics_1980", "Moscow Olympics, 1980",
    "Sixty-five nations boycott. Mascot Mishka still waves from the stadium.",
    [
        _opt("Stage the grandest Games ever", {"stats": {"PRESTIGE": 4, "ECONOMY": -3}},
             "The closing bear sheds a tear of expensive nostalgia."),
        _opt("Use the Games for diplomacy", {"stats": {"PRESTIGE": 3, "FAITH": 1, "ORDER": -1}},
             "Athletes mingle; journalists file 900 stories per hour."),
        _opt("Frame the boycott as hysterics", {"stats": {"FAITH": 1, "PRESTIGE": -2}},
             "Radio Moscow regrets Western 'circle-jerking'."),
    ])

EVENTS["succession_1982"] = _ev(
    "succession_1982", "Succession of 1982: The Old Guard",
    "The Politburo convenes. Power is a question of arithmetic.",
    [
        _opt("Consolidate quietly", {"stats": {"ORDER": 4, "FAITH": -1}},
             "The Old Guard applauds with signet rings."),
        _opt("Promise renewal, act carefully", {"stats": {"FAITH": 3, "ORDER": -1, "PRESTIGE": 1}},
             "A new tone. New names. Same dachas."),
        _opt("Offer reforms immediately", {"stats": {"FAITH": 2, "ORDER": -2, "PRESTIGE": 2}},
             "The apparatus grumbles in fifteen languages."),
    ])

EVENTS["able_archer"] = _ev(
    "able_archer", "Able Archer 83",
    "NATO's communication drills look alarmingly like launch preparation.",
    [
        _opt("Issue a firm nuclear warning", {"stats": {"MILITARY": 2, "PRESTIGE": -3}},
             "TASS publishes names of 'war criminals'. Diplomats drink valium tea."),
        _opt("Open a back-channel to Washington", {"stats": {"PRESTIGE": 3, "MILITARY": -1, "ORDER": 1}},
             "A quiet lunch in Geneva prevents a loud misunderstanding."),
        _opt("Trust the KGB, raise readiness", {"stats": {"MILITARY": 3, "PRESTIGE": -2, "ORDER": -1}},
             "Minesweepers sail; silo doors oil their hinges."),
    ])

EVENTS["new_secretary"] = _ev(
    "new_secretary", "The New General Secretary",
    "Gorbachev's reform team arrives with diagrams of hope and anti-alcohol posters.",
    [
        _opt("Embrace perestroika fully",
             {"stats": {"FAITH": 3, "PRESTIGE": 3, "ORDER": -3},
              "flag_add": "perestroika"},
             "The word 'acceleration' enters the dictionary with Velcro."),
        _opt("Reform slowly, keep the plan", {"stats": {"ECONOMY": 2, "FAITH": 1, "ORDER": 1}},
             "Pilot zones open in two awkward regions."),
        _opt("Defend orthodoxy", {"stats": {"ORDER": 3, "FAITH": -2, "PRESTIGE": -1}},
             "The Old Guard sighs with cautious relief."),
    ])

EVENTS["chernobyl"] = _ev(
    "chernobyl", "Chernobyl, 26 April 1986",
    "Reactor Block IV glows with unplanned physics. Kiev gardens prepare for May.",
    [
        _opt("Admit the disaster immediately", {"stats": {"FAITH": 2, "PRESTIGE": 3, "ECONOMY": -3}},
             "Radiologists fly in from eleven countries. Truth is expensive and less fatal."),
        _opt("Keep it quiet, evacuate quietly",
             {"stats": {"FAITH": -4, "PRESTIGE": -4}, "flag_add": "chernobyl_hidden",
              "queue": [(1, "chernobyl_secrecy")]},
             "Kiosks sell kilos of newsprint, none mentioning dosimeters."),
        _opt("Dismiss as 'not a catastrophe'",
             {"stats": {"FAITH": -2, "PRESTIGE": -3}, "flag_add": "chernobyl_hidden",
              "queue": [(1, "chernobyl_secrecy")]},
             "Swedish monitoring stations foam politely."),
    ])

EVENTS["reykjavik"] = _ev(
    "reykjavik", "Reykjavik Summit",
    "Reagan will not bury SDI. Gorbachev won't bury SDI either. Iceland yawns.",
    [
        _opt("Hunt for the grand bargain", {"stats": {"PRESTIGE": 4, "MILITARY": -2}},
             "No deal, but the world watches two leaders talk honestly."),
        _opt("Demand SDI scrapped first", {"stats": {"PRESTIGE": -1, "MILITARY": 1}},
             "Reagan quotes a proverb about negotiation and stubbornness."),
        _opt("Propose smaller, verifiable cuts", {"stats": {"PRESTIGE": 3, "MILITARY": -1}},
             "INF takes its first baby steps in Reykjavik's silence."),
    ])

EVENTS["wall_falls"] = _ev(
    "wall_falls", "The Berlin Wall Falls",
    "Crowds dance on the Wall. Guards watch, then watch some more.",
    [
        _opt("Order non-intervention, publicly", {"stats": {"PRESTIGE": 4, "FAITH": 3, "ORDER": -4}},
             "'Frankfurt is our answer.' The GDR transitions into a museum."),
        _opt("Request Warsaw Pact deliberation", {"stats": {"ORDER": 1, "PRESTIGE": -1, "FAITH": -1}},
             "Statements are composed; hammers arrive unstamped."),
        _opt("Stay silent entirely", {"stats": {"PRESTIGE": -2, "FAITH": -1, "ORDER": -2}},
             "Silence translated by both sides as opportunism."),
    ])

EVENTS["august_coup"] = _ev(
    "august_coup", "The August Coup, 1991",
    "The Emergency Committee seizes the studios. Tanks idle at the bridges.",
    [
        _opt("Defy the coup from the radio", {"special": "coup_defy"},
             "The nation listens. History holds its breath."),
        _opt("Back the Emergency Committee", {"special": "coup_join"},
             "The studios switch to Swan Lake; your signature appears on the decrees."),
        _opt("Remain carefully absent", {"special": "coup_absent"},
             "You are, officially, resting in a secure dacha."),
    ])

# ══════════════════════════════════════════════════════════════════
# v4: PALACE INTRIGUE (queued by the engine when a faction despairs)
# ══════════════════════════════════════════════════════════════════
EVENTS["palace_coup"] = _ev(
    "palace_coup", "The Velvet Meeting",
    "The Politburo has reserved your own conference room for Thursday. "
    "Nobody will say what the agenda is. Everybody smiles too tightly.",
    [
        _opt("Walk in and face the plenum", {"special": "coup_fight"},
             "Room 14, third floor. Bring accomplices and everyone else."),
        _opt("Buy the plenum off",
             {"stats": {"ORDER": -3, "ECONOMY": -3}, "hc": -6,
              "court": {"old_guard": 20, "reformers": -8},
              "flag_add": "made_deals"},
             "Dachas, titles, and the radio timetable change hands."),
        _opt("Appeal over their heads", {"special": "coup_people"},
             "The miners, the Party youth, the kitchens.",
             requires={"stats": {"FAITH": 45}}),
    ], once=True)

# ══════════════════════════════════════════════════════════════════
# v4: EXTRA CATALOGUE — existing eras
# ══════════════════════════════════════════════════════════════════

# ---- EARLY additions ----
EVENTS["cosmonaut_letter"] = _ev(
    "cosmonaut_letter", "The Cosmonaut's Open Letter",
    "A twice-decorated hero writes to the newspapers about mission "
    "bureaucracy. The editorial board sweats in triplicate.",
    [
        _opt("Print the letter",
             {"stats": {"FAITH": 3, "PRESTIGE": 2, "ORDER": -2},
              "court": {"reformers": 4, "old_guard": -3}},
             "Honesty becomes a prestige technology overnight."),
        _opt("Recall the pilot quietly",
             {"stats": {"ORDER": 3, "FAITH": -2, "PRESTIGE": -1},
              "court": {"old_guard": 3}},
             "The letter browbeats itself into a drawer in Baikonur."),
        _opt("Invite him to the Kremlin",
             {"stats": {"FAITH": 2, "PRESTIGE": 1},
              "court": {"reformers": 2, "military": 1}},
             "Tea, medals, and a private word about gyroscopes."),
    ], era="EARLY", once=True)

EVENTS["baikal_pulp"] = _ev(
    "baikal_pulp", "Baikal: The Wood-Pulp Problem",
    "Scientists petition against the pulp mill's pipe. Lake Baikal is "
    "officially a biography and unofficially a drain.",
    [
        _opt("Close the cellulose line",
             {"stats": {"ECONOMY": -3, "FAITH": 3, "PRESTIGE": 2},
              "court": {"reformers": 3, "old_guard": -3}},
             "The pipe closes; the world's deepest lake breathes."),
        _opt("Keep running, gag the scientists",
             {"stats": {"ORDER": 2, "FAITH": -3, "ECONOMY": 1}},
             "Institutes learn which printers ask questions."),
        _opt("Announce the fifteen-year modernisation plan",
             {"stats": {"ECONOMY": -1, "FAITH": 1, "ORDER": 1}},
             "A committee now owns the problem."),
    ], era="EARLY")

# ---- MIDDLE additions ----
EVENTS["vatican_signal"] = _ev(
    "vatican_signal", "A Quiet Signal from the Vatican",
    "The new Pope sends a private note: markets of a different kind, "
    "and an offer of intermediaries with the West.",
    [
        _opt("Answer warmly, meet the emissary",
             {"stats": {"PRESTIGE": 2, "FAITH": 2, "ORDER": -1},
              "court": {"old_guard": -4, "reformers": 2}},
             "A monsignor, a KGB man, and one lens of illy coffee."),
        _opt("Publish the note as imperialist seduction",
             {"stats": {"ORDER": 2, "PRESTIGE": -2, "FAITH": -2}},
             "TASS does theology for one afternoon."),
        _opt("File it without comment",
             {"stats": {"FAITH": -1}},
             "The note lives at archive shelf 14-C, famously unread."),
    ], era="MIDDLE")

EVENTS["grain_bill"] = _ev(
    "grain_bill", "The Grain Bill, Paid in Valas",
    "Canadian wheat arrives reliably and invoices in convertible currency. "
    "The valas reserve is one meal shorter.",
    [
        _opt("Pay in hard currency, feed everyone",
             {"stats": {"ECONOMY": 3, "FAITH": 2}, "hc": -8},
             "Bread arrives invoiced; the reserve pays and resents it."),
        _opt("Pledge machine exports instead",
             {"stats": {"ECONOMY": 1, "PRESTIGE": -2}},
             "Tractors sail west; the arithmetic squeaks but holds."),
        _opt("Stall like a creditor's nightmare",
             {"stats": {"ECONOMY": -2, "PRESTIGE": -3}, "hc": 3},
             "Three letters, one law firm, and a season of shrugging."),
    ], era="MIDDLE")

# ---- LATE additions ----
EVENTS["name_duel"] = _ev(
    "name_duel", "The Battle of the Names",
    "A city council votes to restore Leningrad, Tver and Samara. The "
    "typesetters ask for a final answer before the next print run.",
    [
        _opt("Restore the old names",
             {"stats": {"ORDER": -3, "FAITH": 3},
              "court": {"reformers": 3, "old_guard": -2},
              "flag_add": "old_names"},
             "Street plates unscrew; taxi drivers retrain for months."),
        _opt("Keep the revolutionary names",
             {"stats": {"ORDER": 2, "FAITH": -2},
              "court": {"old_guard": 2},
              "flag_add": "names_stay"},
             "The city keeps its twentieth-century name and its composure."),
        _opt("Rename one metro station, call it a thaw",
             {"stats": {"FAITH": 1}},
             "Both histories get a compromise mural."),
    ], era="LATE")

EVENTS["cassette_wave"] = _ev(
    "cassette_wave", "The Cassette Season",
    "Walkmans, VHS decks and luggage full of dubbing cross the borders "
    "faster than customs can think.",
    [
        _opt("Customs blitz at the borders",
             {"stats": {"ORDER": 2, "FAITH": -2}, "hc": 3},
             "The fines fill a small valas account and a large folklore."),
        _opt("License a Melodiya pop wave",
             {"stats": {"FAITH": 3, "ECONOMY": -1},
              "court": {"reformers": 2}},
             "Domestic bands inherit a generation politely."),
        _opt("Officially notice nothing",
             {"stats": {"FAITH": 2, "ORDER": -2}},
             "The state stops competing with a plastic box."),
    ], era="LATE", once=True)

# ══════════════════════════════════════════════════════════════════
# v4: THE EXTENDED ERA (1992-2001), if you earn the extension
# ══════════════════════════════════════════════════════════════════

# ---- scripted years ----
EVENTS["rouble_zone"] = _ev(
    "rouble_zone", "The Rouble Zone Question",
    "Republic treasuries start printing their own coupons. The single "
    "currency argues with nine ambitions.",
    [
        _opt("One hard rouble, one Union treasury",
             {"stats": {"ECONOMY": 5, "ORDER": 2, "FAITH": 1}, "hc": -6,
              "court": {"reformers": 3},
              "flag_add": "rouble_zone_solid"},
             "The printing presses relearn their address."),
        _opt("Peg VPN coupons to the rouble",
             {"stats": {"ECONOMY": 2, "ORDER": -1}},
             "Exchange offices grow eponyms and margins."),
        _opt("Abandon money policy to the republics",
             {"stats": {"ORDER": -5, "FAITH": -3, "ECONOMY": -3}},
             "Nine currencies bloom; the queues keep one language."),
    ], once=True)

EVENTS["union_charter"] = _ev(
    "union_charter", "The Union Charter",
    "A constitutional convention argues the architecture of the renewed "
    "state. Two drafts, three committees, one hall.",
    [
        _opt("A federation of equals",
             {"stats": {"FAITH": 5, "PRESTIGE": 2, "ORDER": -3},
              "court": {"reformers": 6, "old_guard": -4},
              "flag_add": "charter_signed"},
             "Republics sign smaller words and mean them."),
        _opt("Strengthen the centre, interim powers",
             {"stats": {"ORDER": 4, "FAITH": -2},
              "court": {"old_guard": 4}},
             "'Interim' becomes a decade's favourite adjective."),
        _opt("Let the general staff draft the chapter",
             {"stats": {"ORDER": 3, "FAITH": -4},
              "court": {"military": 4}},
             "The constitution acquires artillery terminology."),
    ], once=True)

EVENTS["asian_flu_1997"] = _ev(
    "asian_flu_1997", "Tigers Stumble in Asia",
    "Finance collapses in Bangkok, Seoul, Jakarta. The contagion walks "
    "toward the Union's exchanges on monthly wire reports.",
    [
        _opt("Cushion the currency with the valas",
             {"stats": {"ECONOMY": 2}, "hc": -8},
             "The reserve absorbs the sneeze with a grimace."),
        _opt("Substitute imports behind a tariff wall",
             {"stats": {"ECONOMY": 1, "ORDER": 1}, "hc": 2},
             "Domestic factories inherit other people's markets."),
        _opt("Call a socialist common-fund conference",
             {"stats": {"PRESTIGE": 3, "ECONOMY": 1}, "hc": 4,
              "court": {"reformers": -2}},
             "Partners push gold into a shared hat."),
    ], once=True)

EVENTS["nato_east_1999"] = _ev(
    "nato_east_1999", "NATO Steps East",
    "The alliance flags over former Warsaw barracks. The western border "
    "reads like a list of moved furniture.",
    [
        _opt("Sign the partnership treaty anyway",
             {"stats": {"PRESTIGE": 4, "MILITARY": -2}, "hc": 3},
             "Pollen, partnerships, and cups of coffee get traded."),
        _opt("Counter the alliance in the UN",
             {"stats": {"PRESTIGE": 1}, "court": {"military": 3}},
             "A veto, a communique, and veto leverage stored for later."),
        _opt("Re-deploy the missile formations",
             {"stats": {"MILITARY": 3, "ECONOMY": -4, "PRESTIGE": -3},
              "court": {"military": 5, "old_guard": 2}},
             "Trains roll west; NATO's telephones run hot."),
    ], once=True)

EVENTS["millennium_message"] = _ev(
    "millennium_message", "The Millennium Message",
    "The Union's new-century broadcast proposes its first great act: "
    "the cameras of the world are tuned.",
    [
        _opt("Propose global nuclear zero by 2010",
             {"stats": {"PRESTIGE": 8, "FAITH": 3, "MILITARY": -4},
              "flag_add": "red_initiative"},
             "The doctrine of the millennium: the bomb retires early."),
        _opt("Announce the silicon-and-space moonshot",
             {"stats": {"ECONOMY": 3, "PRESTIGE": 5}, "hc": -5,
              "court": {"reformers": 4}},
             "Terminals and tractors both wait for the rocket."),
        _opt("A decade of order and festivals",
             {"stats": {"ORDER": 3, "FAITH": 2},
              "court": {"old_guard": 4}},
             "Banners, parades, punctual buses: a safest of centuries."),
    ], once=True)

# ---- congress ----
EVENTS["millennium_congress"] = _ev(
    "millennium_congress", "☰ THE 1996 RED MILLENNIUM CONGRESS",
    "Survival settled, the Central Committee debates the coming decade's "
    "mission. Four motions, one future.",
    [
        _opt("Declare the market union",
             {"stats": {"ECONOMY": 5, "ORDER": -3},
              "court": {"reformers": 6, "old_guard": -6},
              "flag_add": "market_union"},
             "Prices, auditors, and a stock exchange acquire sofas."),
        _opt("Legislate the social guarantee decade",
             {"stats": {"FAITH": 5, "ECONOMY": -3},
              "court": {"old_guard": 3, "reformers": 2}},
             "Pensions, schools, sanatoria: the decade's true bearings."),
        _opt("The high-tech leap (chips & biotech)",
             {"stats": {"ECONOMY": 4, "PRESTIGE": 3},
              "court": {"reformers": 3}, "flag_add": "tech_leap"},
             "Laboratories inherit the decade's toys."),
        _opt("The imperial belt: military renewal",
             {"stats": {"MILITARY": 5, "ECONOMY": -3},
              "court": {"military": 4, "reformers": -3}},
             "New uniforms keep the old map drawn."),
    ], once=True)

# ---- NEW era random pool ----
EVENTS["oligarch_weekend"] = _ev(
    "oligarch_weekend", "The Weekend Oligarchs",
    "New cooperative tycoons charter steamers on the Volga weekends. "
    "Their shirts are silk; their receipts are debatable.",
    [
        _opt("Tax the tycoons into sculptural innocence",
             {"stats": {"ECONOMY": 5, "FAITH": 1}, "hc": 6,
              "court": {"reformers": -4}},
             "The treasury yawns; the yachts still run on tyres."),
        _opt("Seat them on a Party economic board",
             {"stats": {"ECONOMY": 2},
              "court": {"reformers": 6, "old_guard": -6},
              "flag_add": "oligarchs_seated"},
             "Cards, committees, and mutual vetoes in one room."),
        _opt("Jail the loudest, audit the rest",
             {"stats": {"ORDER": 3, "ECONOMY": -3},
              "court": {"reformers": -6, "old_guard": 5}},
             "One goes to Butyrka; capital develops a stammer."),
    ], era="NEW")

EVENTS["brain_gain"] = _ev(
    "brain_gain", "The Return of the Engineers",
    "Former emigres from Silicon Valley offer to come home with patents "
    "and briefcases. The ministries salivate quietly.",
    [
        _opt("Welcome them with valas salaries",
             {"stats": {"ECONOMY": 4, "PRESTIGE": 3}, "hc": -5,
              "court": {"reformers": 4},
              "flag_add": "returnees"},
             "Labs re-acquire passports and ambition."),
        _opt("A patriotic decree, posters, no salaries",
             {"stats": {"FAITH": 2}},
             "Two families arrive; the posters are excellent."),
        _opt("File their letters for later",
             {"stats": {"PRESTIGE": -1}},
             "The briefcases fly back across the ocean."),
    ], era="NEW")

EVENTS["siberia_2"] = _ev(
    "siberia_2", "Siberia, Second Attempt",
    "Geologists find a gas field north of the circle. Pipes, frost, "
    "foreign buyers, foreign bankers, all interested.",
    [
        _opt("Pour billions into pipes now",
             {"stats": {"ECONOMY": 6, "PRESTIGE": 1}, "hc": 8,
              "court": {"old_guard": 2}},
             "Steel crawls north; the frost invoices in degrees."),
        _opt("Pilot the field, phase the money",
             {"stats": {"ECONOMY": 2}, "hc": 3},
             "Boring, careful, and occasionally even profitable."),
        _opt("Consortium with Tokyo",
             {"stats": {"ECONOMY": 3, "PRESTIGE": -2}, "hc": 10,
              "court": {"reformers": 2, "old_guard": -4}},
             "Yen thaws the permafrost at market speed."),
    ], era="NEW")

EVENTS["network_age"] = _ev(
    "network_age", "The Network Reaches the Union",
    "Public terminals multiply in libraries and post offices. One "
    "network, forty dialects of enthusiasm.",
    [
        _opt("Build one network, Soviet protocols",
             {"stats": {"ECONOMY": 5, "PRESTIGE": 3, "ORDER": -2},
              "flag_add": "red_net_live", "hc": -3},
             "The Union acquires a nervous system with a censor's conscience."),
        _opt("Connive at internal-only, jam the foreign",
             {"stats": {"ORDER": 2, "FAITH": -2}},
             "The network exists; the world exists theoretically."),
        _opt("Regard the terminals as a passing fashion",
             {"stats": {"FAITH": -1}},
             "Institutes connect anyway, through the third floor's fax."),
    ], era="NEW")

EVENTS["church_revival"] = _ev(
    "church_revival", "The Cathedrals Reopen",
    "Craftsmen regild domes with private donations. The State's atheist "
    "calendar looks dowdy beside it.",
    [
        _opt("Support restoration with a state fund",
             {"stats": {"FAITH": 4, "PRESTIGE": 2, "ORDER": -1}, "hc": -3,
              "court": {"reformers": 2, "old_guard": -2}},
             "Domes return to the skyline, receipts and all."),
        _opt("Let society fund its own roofs",
             {"stats": {"FAITH": 3},
              "court": {"reformers": 2}},
             "Sponsorship plaques bloom; the state abstains decorously."),
        _opt("Convert three to 'science museums'",
             {"stats": {"ORDER": 2, "FAITH": -3}},
             "Museum guides explain frescoes with dialectical footnotes."),
    ], era="NEW")

EVENTS["arctic_route"] = _ev(
    "arctic_route", "The Northern Sea Route Revival",
    "Atomic icebreakers could open the polar lane. Freight schedules "
    "and admirals both check their watches.",
    [
        _opt("Commission a new icebreaker fleet",
             {"stats": {"MILITARY": 2, "PRESTIGE": 3, "ECONOMY": 2}, "hc": -4,
              "court": {"military": 3}},
             "The Arctic learns timetables and flags."),
        _opt("Charter the route to foreign shippers",
             {"stats": {"ECONOMY": 3}, "hc": 6},
             "The polar lane hums with foreign chequebooks."),
        _opt("Mothball the season as uneconomic",
             {"stats": {"ECONOMY": -1}},
             "The icebreakers nap; the admirals write letters."),
    ], era="NEW")

EVENTS["wild_east_jobs"] = _ev(
    "wild_east_jobs", "The Far East Jobs Wagon",
    "Chinese traders arrive in Chita with pliers and prices. Border "
    "towns grow bilingual markets overnight.",
    [
        _opt("Declare a free-trade belt on the border",
             {"stats": {"ECONOMY": 4, "FAITH": 1, "ORDER": -2}, "hc": 5,
              "court": {"reformers": 3}},
             "Pliers, pepper, and state theory all appreciate."),
        _opt("KGB scrutiny of every wagon",
             {"stats": {"ORDER": 3, "ECONOMY": -2},
              "court": {"old_guard": 3}},
             "Half the pliers are documented twice."),
        _opt("Plan the markets into officialdom",
             {"stats": {"FAITH": 1, "ECONOMY": 1}},
             "Pliers acquire permits, margins acquire stamps."),
    ], era="NEW")

# ══════════════════════════════════════════════════════════════════
# v5: chain reactions, new standalone events, divergence forks
# ══════════════════════════════════════════════════════════════════
from .chains import CHAIN_EVENTS, EXTRA_EVENTS          # noqa: E402
from .forks import FORK_EVENTS, FORKS                   # noqa: E402

EVENTS.update(EXTRA_EVENTS)
EVENTS.update(CHAIN_EVENTS)
EVENTS.update(FORK_EVENTS)

# Forks are appended by the engine on their year; expose them for the dossier.
FORKS = FORKS
