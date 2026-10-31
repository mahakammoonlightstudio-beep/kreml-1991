"""LATE era events (1985-1991).

Content is pure data: `builders.ev` / `builders.opt` keep the literals
short. Split out of the single v5 catalogue by tools/split_events.py;
add new events here, in the era they belong to.
"""
from __future__ import annotations

from .builders import ev, opt

EVENTS_LATE: dict[str, object] = {}

EVENTS_LATE["glasnost_press"] = ev(
    "glasnost_press", 'Glasnost Surges in Print', 'Magazines publish honest essays. Subscriptions triple and censors riot in their offices.',
    [
    opt('Expand glasnost further', {'stats': {'FAITH': 4, 'PRESTIGE': 3, 'ORDER': -4}}, 'The press blooms; the Party chews nails anxiously.'),
    opt('Cap the magazines at three pages', {'stats': {'FAITH': -2, 'ORDER': 1}}, 'Readers buy three extra copies for missing pages.'),
    opt('Redirect topics toward show business', {'stats': {'FAITH': -1, 'PRESTIGE': -1}}, 'An interview with a pop star displaces three historians.'),
    ],
    era='LATE',
)

EVENTS_LATE["karabakh"] = ev(
    "karabakh", 'Nagorno-Karabakh Erupts', "Armenian and Azerbaijani crowds collide. Moscow's telegram box burns.",
    [
    opt('Send Internal Troops', {'stats': {'ORDER': 3, 'FAITH': -2, 'PRESTIGE': -2}}, 'Tranquillity is achieved, briefly, with barricades.'),
    opt('Promise autonomy reform', {'stats': {'FAITH': 1, 'ORDER': -1, 'PRESTIGE': 1}}, 'Commissions are founded; salutes are provisional.'),
    opt('Blame local nationalist elites', {'stats': {'PRESTIGE': -2, 'ORDER': 1}}, 'Everyone blames somebody; nobody is satisfied.'),
    ],
    era='LATE',
)

EVENTS_LATE["baltic_chain"] = ev(
    "baltic_chain", 'The Baltic Chain', 'Two million people form a 600 km human chain across three republics.',
    [
    opt('Acknowledge it on television', {'stats': {'FAITH': 2, 'PRESTIGE': 2, 'ORDER': -3}}, "Anchors describe unity. Somebody whispers 'shows'."),
    opt('Disperse the chain with police', {'stats': {'ORDER': 2, 'FAITH': -4, 'PRESTIGE': -3}}, 'Wrist links are broken by baton links.'),
    opt('Quietly re-examine the Molotov pact', {'stats': {'PRESTIGE': 3, 'ORDER': -2}}, 'Historians are suddenly extremely popular.'),
    ],
    era='LATE',
)

EVENTS_LATE["mic_reform"] = ev(
    "mic_reform", 'The Military-Industrial lobby argues', 'Defence ministers demand budget; Gosplan demands survival.',
    [
    opt('Convert factories to consumer goods', {'stats': {'ECONOMY': 3, 'MILITARY': -2}}, 'Tractor plants start producing trickle-batteries.'),
    opt('Defend the MIC budget', {'stats': {'MILITARY': 2, 'ECONOMY': -3}}, 'The generals applaud; the shops do not.'),
    opt('Split the difference annually', {'stats': {'ECONOMY': 1, 'MILITARY': -1}}, 'Committee mathematics strikes again.'),
    ],
    era='LATE',
)

EVENTS_LATE["yeltsin_truck"] = ev(
    "yeltsin_truck", 'Yeltsin on a Truck', 'Boris Yeltsin addresses crowds from a vehicle roof, fists raised.',
    [
    opt('Expel him from the Party', {'stats': {'ORDER': 2, 'FAITH': -3, 'PRESTIGE': -2}}, 'He becomes a martyr with a loud voice.'),
    opt('Invite him into the leadership', {'stats': {'FAITH': 2, 'ORDER': -2, 'PRESTIGE': 1}}, 'He accepts awkwardly and promises brisk reform.'),
    opt('Sideline him to a construction trust', {'stats': {'FAITH': -1, 'ORDER': 1}}, 'He supervises bridges; crowds dream of speeches.'),
    ],
    era='LATE',
)

EVENTS_LATE["berlin_strains"] = ev(
    "berlin_strains", 'East Germany Strains', 'Travellers flee via Hungary to Austria. Honecker asks for direction.',
    [
    opt('Close the Hungarian border', {'stats': {'ORDER': 3, 'PRESTIGE': -3}}, 'Barbed wire returns to the pan-European press.'),
    opt('Admit the Wall is obsolete', {'stats': {'FAITH': 3, 'PRESTIGE': 3, 'ORDER': -4}}, 'Historians collapse; tourists celebrate.'),
    opt('Blame GDR interior policy', {'stats': {'PRESTIGE': 1, 'ORDER': -2}}, 'Berlin is left alone with its architected sorrow.'),
    ],
    era='LATE', requires={'max_year': 1988},
)

EVENTS_LATE["market_queues"] = ev(
    "market_queues", 'Sugar, Soap and Rumours', 'Empty shelves publish themselves on national television now.',
    [
    opt('Army distribution squads', {'stats': {'ECONOMY': -2, 'FAITH': 2, 'MILITARY': -1}}, 'Soldiers unload bread convoys; applause is real.'),
    opt('Legalize farmers markets', {'stats': {'ECONOMY': 3, 'FAITH': 3, 'ORDER': -2}}, 'Private stalls bloom in suburban courtyards.'),
    opt('Promise 1993 prosperity', {'stats': {'FAITH': -3}}, 'Reformers note the promise; so do the shelves.'),
    ],
    era='LATE',
)

EVENTS_LATE["chip_embargo"] = ev(
    "chip_embargo", 'The Western Chip Embargo', 'US sanctions stop computer exports. Factories wait for software rivers.',
    [
    opt('Fund domestic semiconductors', {'stats': {'ECONOMY': -4, 'MILITARY': 2}}, "Mikron's engineers squint at imported manuals."),
    opt('Lean on the microelectronics academy', {'stats': {'ECONOMY': -1, 'MILITARY': 2}}, 'Your choice of a decade past pays dividends here.', {'flags': ['micro']}),
    opt('Smuggle through third countries', {'stats': {'ECONOMY': -1, 'MILITARY': 1, 'PRESTIGE': -1}}, 'Two agents succeed; one walks into an airport lobby.'),
    opt('Admit the gap publicly', {'stats': {'PRESTIGE': 1, 'FAITH': -2}}, 'Honesty is refreshing; factories are still idle.'),
    ],
    era='LATE',
)

EVENTS_LATE["crimea_return"] = ev(
    "crimea_return", 'Crimea Wants its Homes Back', 'Crimean Tatars petition en masse to return to their homeland.',
    [
    opt('Permit gradual return', {'stats': {'FAITH': 3, 'ORDER': -1, 'PRESTIGE': 2}}, 'Trains roll south; documents are slow.'),
    opt('Deny the petitions', {'stats': {'FAITH': -2, 'PRESTIGE': -2}}, 'Protests resume on the Day of Remembrance.'),
    opt('Grant symbolic autonomy', {'stats': {'FAITH': 1, 'ORDER': 1}}, 'Banners and brochures, committees quietly famous.'),
    ],
    era='LATE', once=True,
)

EVENTS_LATE["caviar_conference"] = ev(
    "caviar_conference", 'The Caviar Congress', 'Party congress debates reform while serving sturgeon to 5,000 delegates.',
    [
    opt('Serve plain bread instead', {'stats': {'FAITH': 3, 'ORDER': -1}}, 'Delegates chew; delegates think.'),
    opt('Export the caviar for currency', {'stats': {'ECONOMY': 2, 'FAITH': -1}}, 'Swiss hotels praise Soviet cuisine.'),
    opt('Ignore the imagery', {'stats': {'FAITH': -2, 'PRESTIGE': -1}}, 'A cartoonist wins an international prize.'),
    ],
    era='LATE',
)

EVENTS_LATE["spitak_quake"] = ev(
    "spitak_quake", 'Armenian Earthquake Relief', 'Spitak is ruined. The Army arrives with tents and inadequate logistics.',
    [
    opt('Accept Western aid openly', {'stats': {'PRESTIGE': 3, 'FAITH': 2}}, 'American rescuers fly in; props to both flags.'),
    opt('Rely only on Soviet forces', {'stats': {'MILITARY': 1, 'FAITH': -2}}, 'Logistics chafe; handwritten notes rescue some.'),
    opt('Blame local builders', {'stats': {'FAITH': -3, 'PRESTIGE': -1}}, 'Very few people accept this explanation.'),
    ],
    era='LATE', once=True,
)

EVENTS_LATE["referendum_fever"] = ev(
    "referendum_fever", 'Referendum Fever', "Republics ask: 'Renewed federation or independence?'",
    [
    opt('Draft a new Union Treaty', {'stats': {'FAITH': 3, 'ORDER': -2, 'PRESTIGE': 2}}, 'Paper glistens with fresh compromise.'),
    opt('Strengthen federal courts instead', {'stats': {'ORDER': 2, 'FAITH': -2}}, 'Lawyers become the new national pastime.'),
    opt('Boycott the referendum', {'stats': {'ORDER': -3, 'FAITH': -1}}, 'The ballot box finds other employers.'),
    ],
    era='LATE',
)

EVENTS_LATE["coops_press"] = ev(
    "coops_press", 'Co-op Millionaires in the Press', 'Your legalized cooperatives produced millionaires. So do the headlines.',
    [
    opt('Let private wealth breathe', {'stats': {'FAITH': 2, 'ORDER': -2}}, 'The rich become a topic, then a habit.'),
    opt('Tax the new millionaires', {'stats': {'ECONOMY': 2, 'FAITH': -1, 'ORDER': 1}}, "Luxury cars learn the tax office's address."),
    opt('Ban cooperatives again', {'stats': {'ORDER': 2, 'FAITH': -2}, 'flag_rm': 'coops'}, 'Bureaucracy dusts victory medals from 1929.'),
    ],
    era='LATE', once=True, requires={'flags': ['coops']},
)

EVENTS_LATE["mr_archives"] = ev(
    "mr_archives", 'The Molotov–Ribbentrop Archive', 'Old protocols surface about the secret protocols of 1939. Historians hold their pens.',
    [
    opt('Admit the protocol exists', {'stats': {'PRESTIGE': 3, 'ORDER': -2, 'FAITH': 1}, 'flag_add': 'mr_admitted'}, 'The Commission publishes truth with footnotes.'),
    opt('Deny the protocol exists', {'stats': {'PRESTIGE': -2}}, 'Denial photocopies itself into every argument.'),
    opt('Commission quiet historians', {'stats': {'PRESTIGE': 1, 'ORDER': -1}}, 'A report live-draws in five guarded copies.'),
    ],
    era='LATE', once=True, requires={'min_year': 1988},
)

EVENTS_LATE["vodka_campaign"] = ev(
    "vodka_campaign", 'The Anti-Alcohol Campaign', "Reformers demand a sober Union. Vodka is half of agriculture's cashflow.",
    [
    opt('Cut sales hard, close distilleries', {'stats': {'ECONOMY': -4, 'FAITH': -3, 'ORDER': 2}, 'flag_add': 'dry_decade'}, 'Sugar vanishes into home brew; Sobriety Societies multiply.'),
    opt('Half-measures: higher prices only', {'stats': {'ECONOMY': -1, 'FAITH': -1, 'ORDER': 1}}, 'Queues lengthen politely at wine departments.'),
    opt("Refuse: 'The people have earned their glasses'", {'stats': {'FAITH': 3, 'PRESTIGE': -1, 'ECONOMY': 1}}, 'The Old Guard toasts you privately; doctors send memoranda.'),
    ],
    era='LATE', once=True, requires={'min_year': 1985},
)

EVENTS_LATE["nomenklatura_rift"] = ev(
    "nomenklatura_rift", 'The Nomenklatura Rift', 'Young technocrats want markets and market-grade privileges. The Old Guard wants lunch.',
    [
    opt('Side with the technocrats', {'stats': {'FAITH': 2, 'ORDER': -2, 'ECONOMY': 2}, 'flag_add': 'cadres_rift'}, 'Ministries fill with calculators and expensive watches.'),
    opt('Side with the Old Guard', {'stats': {'ORDER': 3, 'FAITH': -2, 'ECONOMY': -1}}, 'Loyalty restored; three bright deputy ministers retire early.'),
    opt('Split the committees and hope', {'stats': {'ORDER': -1, 'ECONOMY': 1}}, 'Nobody is satisfied; paperwork doubles.'),
    ],
    era='LATE', once=True, requires={'any_flags': ['perestroika', 'reformer', 'cadres_refresh']},
)

EVENTS_LATE["singapore_dream"] = ev(
    "singapore_dream", 'The Singapore Envelope', 'A minister returns from the tropics with charts: tax havens, ports, miracles.',
    [
    opt('Build a free port on the Pacific', {'stats': {'ECONOMY': 5, 'ORDER': -3, 'PRESTIGE': 2}, 'flag_add': 'free_port'}, 'Container cranes rise over Severodvinsk-daydreams.'),
    opt("File it under 'bourgeois economics'", {'stats': {'ORDER': 2, 'FAITH': -1}}, 'The envelope gains a stamp and a dust coat.'),
    opt('Trial one zone only, quietly', {'stats': {'ECONOMY': 2, 'ORDER': -1}}, 'Nakhodka learns accounting by fire.'),
    ],
    era='LATE', once=True, requires={'any_flags': ['price_done', 'coops', 'kosygin_full']}, alt=True,
)

EVENTS_LATE["name_duel"] = ev(
    "name_duel", 'The Battle of the Names', 'A city council votes to restore Leningrad, Tver and Samara. The typesetters ask for a final answer before the next print run.',
    [
    opt('Restore the old names', {'stats': {'ORDER': -3, 'FAITH': 3}, 'court': {'reformers': 3, 'old_guard': -2}, 'flag_add': 'old_names'}, 'Street plates unscrew; taxi drivers retrain for months.'),
    opt('Keep the revolutionary names', {'stats': {'ORDER': 2, 'FAITH': -2}, 'court': {'old_guard': 2}, 'flag_add': 'names_stay'}, 'The city keeps its twentieth-century name and its composure.'),
    opt('Rename one metro station, call it a thaw', {'stats': {'FAITH': 1}}, 'Both histories get a compromise mural.'),
    ],
    era='LATE',
)

EVENTS_LATE["cassette_wave"] = ev(
    "cassette_wave", 'The Cassette Season', 'Walkmans, VHS decks and luggage full of dubbing cross the borders faster than customs can think.',
    [
    opt('Customs blitz at the borders', {'stats': {'ORDER': 2, 'FAITH': -2}, 'hc': 3}, 'The fines fill a small valas account and a large folklore.'),
    opt('License a Melodiya pop wave', {'stats': {'FAITH': 3, 'ECONOMY': -1}, 'court': {'reformers': 2}}, 'Domestic bands inherit a generation politely.'),
    opt('Officially notice nothing', {'stats': {'FAITH': 2, 'ORDER': -2}}, 'The state stops competing with a plastic box.'),
    ],
    era='LATE', once=True,
)
