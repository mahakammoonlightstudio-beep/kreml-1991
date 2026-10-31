"""EARLY era events (1964-1975).

Content is pure data: `builders.ev` / `builders.opt` keep the literals
short. Split out of the single v5 catalogue by tools/split_events.py;
add new events here, in the era they belong to.
"""
from __future__ import annotations

from .builders import ev, opt

EVENTS_EARLY: dict[str, object] = {}

EVENTS_EARLY["vodka_shortage"] = ev(
    "vodka_shortage", 'The Vodka Shortage', 'Distilleries ship crates but shop windows are dry. Queueing men hum mourning songs.',
    [
    opt('Ration via Party stores', {'stats': {'FAITH': -2, 'ORDER': 1}}, 'The queues thin; the grumbling thickens.'),
    opt('Import rum confidence from Cuba', {'stats': {'ECONOMY': -3, 'FAITH': 2}}, 'Rum bottles arrive; confidence arrives later.'),
    opt('Deny the problem entirely', {'stats': {'FAITH': -1}}, 'Pravda announces a surplus of patience and grain spirit.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["samizdat"] = ev(
    "samizdat", 'Dissident Samizdat', 'KGB agents seize nine mimeographed pages typed on onionskin.',
    [
    opt('Trial the editors', {'stats': {'ORDER': 2, 'FAITH': -3, 'PRESTIGE': -2}}, 'A show trial produces quiet applause and loud Western letters.'),
    opt('Let it slide', {'stats': {'FAITH': 2, 'ORDER': -1}}, 'The pages pass hand to hand like legislative jokes.'),
    opt('Confine them to a psychiatric ward', {'stats': {'ORDER': 3, 'FAITH': -2, 'PRESTIGE': -2}}, "Diagnosis: 'sluggish schizophrenia'. The typewriters register it."),
    ],
    era='EARLY',
)

EVENTS_EARLY["kosygin_memo"] = ev(
    "kosygin_memo", 'Kosygin Wants Reforms', 'The Premier slides you a memo: profit indicators, worker councils, honesty about steel.',
    [
    opt('Support pilot reforms', {'stats': {'ECONOMY': 4, 'ORDER': -2}, 'flag_add': 'kosygin_pilot', 'queue': [(2, 'reform_wobble')]}, 'Two factories dare to profit. A pilot regime is born.'),
    opt('Send him to the archives', {'stats': {'ECONOMY': -1, 'ORDER': 2}}, "The memo is filed. So is its author's ambition."),
    opt('Half-measures, report as success', {'stats': {'ECONOMY': 2, 'FAITH': 1}}, 'Three pilot plots. Bureaucratic applause stills all progress.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["n1_explodes"] = ev(
    "n1_explodes", 'N1 Rocket Explodes', 'The giant booster detonates over Baikonur and the pad becomes a crater.',
    [
    opt("Announce 'a planned structural test'", {'stats': {'PRESTIGE': -1, 'FAITH': -1}}, 'Radio Moscow inventories a successful launch of nothing.'),
    opt('Fund the N1 again', {'stats': {'ECONOMY': -4, 'PRESTIGE': 2}}, 'The Chief Designers get more metal and more patience.'),
    opt('Redirect the money to the military', {'stats': {'MILITARY': 2, 'PRESTIGE': -1}}, "Generals toast the loss of their rival's toy."),
    ],
    era='EARLY',
)

EVENTS_EARLY["jazz_shortwave"] = ev(
    "jazz_shortwave", 'Western Jazz on the Shortwaves', 'Students gather near windowsills with radios, dial-volume saxophone speaking brightly.',
    [
    opt('Jam the frequencies', {'stats': {'ORDER': 2, 'FAITH': -2}}, 'Static, then more saxophone, louder.'),
    opt('Permit sanctioned jazz clubs', {'stats': {'FAITH': 3, 'ORDER': -1, 'PRESTIGE': 1}}, 'Melodiya issues records; youth applies irony to the lyrics.'),
    opt("Call jazz 'a CIA weapon'", {'stats': {'FAITH': -2, 'PRESTIGE': -1}}, 'Even the jazz-hating Party members sigh.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["kuzbass_strike"] = ev(
    "kuzbass_strike", 'Coal Strike in Kuzbass', 'Miners list grievances: boots, bread, and a ration coupon of dignity.',
    [
    opt('Send boots and meat', {'stats': {'ECONOMY': -3, 'FAITH': 2}}, 'Mittens arrive wearing slogans. Back to work.'),
    opt('Send the Internal Troops', {'stats': {'ORDER': 3, 'FAITH': -3}}, 'The pit resumes; so does the whispering.'),
    opt("Pretend it didn't happen", {'stats': {'FAITH': -2, 'PRESTIGE': -1}}, 'Western newspapers run a headline you cannot see.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["virgin_lands"] = ev(
    "virgin_lands", 'The Virgin Lands Fail', 'Kazakh steppe yields dust instead of grain. Erosion grins at agronomy.',
    [
    opt('Buy grain from the USA', {'stats': {'ECONOMY': -4, 'FAITH': 1}, 'hc': -3}, 'Solidarity with American farmers, priced objectively.'),
    opt('Blame weather, fine no one', {'stats': {'FAITH': -1, 'PRESTIGE': -1}}, 'Meteorologists invent three storms per province.'),
    opt('Rush irrigation projects', {'stats': {'ECONOMY': -2, 'FAITH': 2}}, 'Concrete channels leak prestige into sand.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["cuban_sugar"] = ev(
    "cuban_sugar", 'Cuban Sugar & Rum', 'Havana ships sugar and rum; asks for tractors and sympathy.',
    [
    opt('Ship tractors, pallets of parts', {'stats': {'ECONOMY': -2, 'PRESTIGE': 2}}, 'Fidel sends cigars and a warm letter.'),
    opt('Send advice instead', {'stats': {'PRESTIGE': -2, 'FAITH': -1}}, "Fidel's letter mentions 'comrade patience' three times."),
    opt('Trade sugar for oil credits', {'stats': {'ECONOMY': 2, 'PRESTIGE': -1}}, 'Paperwork trickles across three ministries.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["prague_airwaves"] = ev(
    "prague_airwaves", 'Prague Voices Flood the Airwaves', 'Radio debates grow so lively that censorship fades at the borders.',
    [
    opt('Tighten jamming', {'stats': {'ORDER': 2, 'FAITH': -2}}, 'Cables hum; Czechoslovak whispers persist.'),
    opt('Send Party inspectors', {'stats': {'ORDER': 1, 'FAITH': -1, 'PRESTIGE': -1}}, 'Cables and letters, all properly stamped.'),
    opt("Admit debate is 'errant but legal'", {'stats': {'FAITH': 2, 'ORDER': -2, 'PRESTIGE': 1}}, 'An unnerving act of political honesty.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["golden_orlov"] = ev(
    "golden_orlov", 'The Golden Orlov Dacha', "A Politburo member's new dacha grows a private boat dock. Rumours multiply.",
    [
    opt('Ignore, as always', {'stats': {'FAITH': -1, 'PRESTIGE': -1}}, 'The dock gains a second mooring.'),
    opt('Quietly reshuffle him', {'stats': {'ORDER': 1, 'FAITH': 1}}, 'He becomes an ambassador with a lake view instead.'),
    opt('Public anti-corruption trial', {'stats': {'FAITH': 3, 'ORDER': -3, 'PRESTIGE': 2}}, 'People cheer. Officials elsewhere clear their desks.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["vienna_defection"] = ev(
    "vienna_defection", 'Defector at the Vienna Fair', 'A TASS correspondent shares his archive with Western services.',
    [
    opt('Reinforce residency procedures', {'stats': {'ORDER': 1, 'MILITARY': 1, 'PRESTIGE': -1}}, 'Every agent reports a field meeting with paperwork.'),
    opt('Recruit tradecraft training', {'stats': {'MILITARY': 2, 'ECONOMY': -1}}, 'Andropov proposes one seminar and two follow-ups.'),
    opt('Liquidate the asset abroad', {'stats': {'PRESTIGE': -2, 'ORDER': 1}}, 'Details are denied before anyone asks.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["phantom_growth"] = ev(
    "phantom_growth", "Gosplan's Tables Turn Negative", 'Planned growth produces negative growth in four ministries.',
    [
    opt('Tweak the plan numbers', {'stats': {'FAITH': -1, 'ECONOMY': -1}}, 'Statistics find courage and rise a little.'),
    opt('Request foreign technology', {'stats': {'ECONOMY': 2, 'PRESTIGE': -1}}, 'Fiat diesels arrive at two pilot plants.'),
    opt('Blame managers, change none', {'stats': {'FAITH': -2, 'ORDER': 1}}, "Two ministers are 'transferred for health'."),
    ],
    era='EARLY',
)

EVENTS_EARLY["china_overture"] = ev(
    "china_overture", 'Beijing Sends a Quiet Overture', "A Chinese envoy proposes border talks and grain trade. Mao's insults remain optional.",
    [
    opt('Embrace the rapprochement', {'stats': {'PRESTIGE': 2, 'MILITARY': 1}, 'flag_add': 'china_thaw'}, 'Two red armies watch the Pacific in the same direction.'),
    opt('Send observers only', {'stats': {'PRESTIGE': 1}}, 'Delegations meet over tea; nothing binds.'),
    opt('Rebroadcast the old insults', {'stats': {'PRESTIGE': -1, 'ORDER': 1}}, "Radio Moscow's dialecticians earn their keep."),
    ],
    era='EARLY', once=True, requires={'not_flags': ['china_thaw']},
)

EVENTS_EARLY["de_gaulle"] = ev(
    "de_gaulle", 'De Gaulle Lands at Vnukovo', "France's President proposes trade and offers words about Europe from Atlantic to Urals.",
    [
    opt('Sign industrial trade contracts', {'stats': {'ECONOMY': 3, 'PRESTIGE': 2}}, 'French turbines and Soviet aromatics pass the mirrors.'),
    opt('Offer nuclear-era cultural exchange', {'stats': {'PRESTIGE': 3, 'ECONOMY': -1}, 'flag_add': 'french_link'}, 'A special channel to Paris opens quietly.'),
    opt('Denounce Atlanticist France', {'stats': {'PRESTIGE': -1, 'ORDER': 1}}, 'The General shrugs with imperial elegance.'),
    ],
    era='EARLY', once=True,
)

EVENTS_EARLY["cairo_arms"] = ev(
    "cairo_arms", 'The Cairo Bazaar', 'An Arab client requests arms: armour, aircraft, and politically active patience.',
    [
    opt('Provide the full package', {'stats': {'MILITARY': -2, 'PRESTIGE': 2}, 'flag_add': 'arab_arms'}, "Moscow's arsenals find the Middle East's markets."),
    opt('Send advisors only', {'stats': {'MILITARY': -1}}, 'Uniforms without armour; debt without delivery.'),
    opt('Politely decline', {'stats': {'PRESTIGE': -2}}, 'Cairo buys from elsewhere; your port fees shrink.'),
    ],
    era='EARLY',
)

EVENTS_EARLY["cosmonaut_letter"] = ev(
    "cosmonaut_letter", "The Cosmonaut's Open Letter", 'A twice-decorated hero writes to the newspapers about mission bureaucracy. The editorial board sweats in triplicate.',
    [
    opt('Print the letter', {'stats': {'FAITH': 3, 'PRESTIGE': 2, 'ORDER': -2}, 'court': {'reformers': 4, 'old_guard': -3}}, 'Honesty becomes a prestige technology overnight.'),
    opt('Recall the pilot quietly', {'stats': {'ORDER': 3, 'FAITH': -2, 'PRESTIGE': -1}, 'court': {'old_guard': 3}}, 'The letter browbeats itself into a drawer in Baikonur.'),
    opt('Invite him to the Kremlin', {'stats': {'FAITH': 2, 'PRESTIGE': 1}, 'court': {'reformers': 2, 'military': 1}}, 'Tea, medals, and a private word about gyroscopes.'),
    ],
    era='EARLY', once=True,
)

EVENTS_EARLY["baikal_pulp"] = ev(
    "baikal_pulp", 'Baikal: The Wood-Pulp Problem', "Scientists petition against the pulp mill's pipe. Lake Baikal is officially a biography and unofficially a drain.",
    [
    opt('Close the cellulose line', {'stats': {'ECONOMY': -3, 'FAITH': 3, 'PRESTIGE': 2}, 'court': {'reformers': 3, 'old_guard': -3}}, "The pipe closes; the world's deepest lake breathes."),
    opt('Keep running, gag the scientists', {'stats': {'ORDER': 2, 'FAITH': -3, 'ECONOMY': 1}}, 'Institutes learn which printers ask questions.'),
    opt('Announce the fifteen-year modernisation plan', {'stats': {'ECONOMY': -1, 'FAITH': 1, 'ORDER': 1}}, 'A committee now owns the problem.'),
    ],
    era='EARLY',
)
