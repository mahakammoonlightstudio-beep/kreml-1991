"""Calendar events: scripted years, congresses, queues.

Content is pure data: `builders.ev` / `builders.opt` keep the literals
short. Split out of the single v5 catalogue by tools/split_events.py;
add new events here, in the era they belong to.
"""
from __future__ import annotations

from .builders import ev, opt

EVENTS_FIXED: dict[str, object] = {}

EVENTS_FIXED["coal_miners_1989"] = ev(
    "coal_miners_1989", "The Coal Miners' Summer", 'Kuzbass, Donbass, Vorkuta: a million pick-axes strike; the trains slow to a crawl.',
    [
    opt('Concede wages, vouchers and sugar', {'stats': {'ECONOMY': -3, 'FAITH': 3, 'ORDER': -1}, 'flag_add': 'miners_conceded'}, 'The pits roar back; so do the wage accounts.'),
    opt('Declare an emergency, send internal troops', {'stats': {'ORDER': -2, 'FAITH': -4, 'PRESTIGE': -2}}, "Miners' committees go underground in every sense."),
    opt('Negotiate through union committees', {'stats': {'ECONOMY': -1, 'FAITH': 2, 'ORDER': -2}, 'flag_add': 'miners_conceded'}, 'Signed protocols nobody fully honours, official honesty.'),
    ],
)

EVENTS_FIXED["plenum_1970"] = ev(
    "plenum_1970", '☰ THE 1970 PLENUM: On Growth', 'The Central Committee gathers for grand strategy. One law of the decade gets signed here.',
    [
    opt('Sign the full Kosygin package', {'stats': {'ECONOMY': 6, 'FAITH': 2, 'ORDER': -2}, 'flag_add': 'kosygin_pilot'}, 'Profit indicators enter the law. Factory directors blink in the light.'),
    opt('Legislate organic stability', {'stats': {'ORDER': 4, 'FAITH': -2}, 'flag_add': 'stability_law'}, 'Order becomes a construction project with decades of blueprints.'),
    opt('Consumer offensive law', {'stats': {'FAITH': 5, 'ECONOMY': -2}}, "Britain's shelves seem far, but the road starts here."),
    opt('Deterrence & arms law', {'stats': {'MILITARY': 5, 'ECONOMY': -3}}, 'The rocket forces gain a decade of budget arithmetic.'),
    ],
    once=True,
)

EVENTS_FIXED["blueprint_1978"] = ev(
    "blueprint_1978", '☰ THE 1978 BLUEPRINT', 'The development congress drafts the middle-generation programme. One mission is chosen.',
    [
    opt('Siberian oil & gas blitz', {'stats': {'ECONOMY': 5, 'PRESTIGE': 1}, 'flag_add': 'siberian'}, 'Pipelines will finance something, someday, maybe.'),
    opt('Microelectronics academy', {'stats': {'PRESTIGE': 3, 'ECONOMY': -1}, 'flag_add': 'micro'}, 'A generation learns binary arithmetic and jokes about clerks.'),
    opt('Grain sovereignty programme', {'stats': {'FAITH': 3, 'ECONOMY': -2}}, 'Tractors queue to queue for tractors.'),
    opt('Ocean navy doctrine', {'stats': {'MILITARY': 4, 'ECONOMY': -3}, 'flag_add': 'navy_blue'}, 'Flags of steel splatter across the seven seas.'),
    ],
    once=True,
)

EVENTS_FIXED["acceleration_1986"] = ev(
    "acceleration_1986", '☰ THE 1986 ACCELERATION CONGRESS', 'A young Politburo tables four futures. One motion outvotes the rest by lunch.',
    [
    opt('Acceleration: rush modernization', {'stats': {'ECONOMY': 4, 'MILITARY': 2}, 'flag_add': 'accel'}, 'Bicycle factories re-tool; the wall clock gains a jet engine.'),
    opt('Glasnost above all', {'stats': {'FAITH': 4, 'ORDER': -3, 'PRESTIGE': 2}, 'flag_add': 'glasnost_early'}, 'The press breathes early and loudly.'),
    opt('Cooperative relaxations', {'stats': {'ECONOMY': 4, 'ORDER': -2}, 'flag_add': 'coops'}, 'Co-ops ferment legally from Kaliningrad to Kamchatka.'),
    opt('Motion of Party discipline', {'stats': {'ORDER': 4, 'FAITH': -2}}, 'Discipline gets its own poster and a fifth column.'),
    ],
    once=True,
)

EVENTS_FIXED["nato_ultimatum_reply"] = ev(
    "nato_ultimatum_reply", 'NATO Answers the Ultimatum', "Your atomic ultimatum crashed onto NATO's desk weeks ago. The reply takes a special courier.",
    [
    opt('Back down', {'stats': {'PRESTIGE': -4, 'MILITARY': -2}}, "Silos reclose. Diplomats relearn the word 'tagebuch'."),
    opt('Hold firm', {'stats': {'MILITARY': 3, 'PRESTIGE': -6}, 'flag_add': 'brink'}, 'The world parks at the brink of midnight.'),
    opt('Open a secret hotline', {'stats': {'PRESTIGE': 3, 'MILITARY': -1}}, 'One red telephone calms one crisis.'),
    ],
)

EVENTS_FIXED["prague_spring"] = ev(
    "prague_spring", 'Prague Spring, 1968', "Dubček insists on 'socialism with a human face'. The Politburo faces faces.",
    [
    opt('Send tanks in', {'stats': {'ORDER': 4, 'PRESTIGE': -5, 'FAITH': -3}, 'flag_add': 'prague_tanks'}, "Operation Danube proceeds. The word 'normalization' acquires teeth."),
    opt('Negotiate with Dubček', {'stats': {'PRESTIGE': 3, 'ORDER': -2, 'FAITH': 2}, 'flag_add': 'prague_talks'}, 'Talks in Czech. Kissinger takes notes; the Party upholsters itself.'),
    opt('Pressure him to end reforms', {'stats': {'ORDER': 1, 'PRESTIGE': -1}}, 'Letters and telephone calls accomplish partial awkwardness.'),
    ],
)

EVENTS_FIXED["ussuri_clashes"] = ev(
    "ussuri_clashes", 'Ussuri River Border Clashes', 'Sino-Soviet skirmishes on Damansky Island. Mao recites ancient insults.',
    [
    opt('Mass troops at the border', {'stats': {'MILITARY': 3, 'ECONOMY': -3, 'PRESTIGE': -1}}, "Red banners face red banners. Somewhere, a colonel's phone rings."),
    opt('Secret talks in Beijing', {'stats': {'PRESTIGE': 2, 'ORDER': 1}, 'flag_add': 'china_thaw'}, 'Two delegations exchange tea and veiled rationales.'),
    opt('Broadcast propaganda only', {'stats': {'FAITH': 1, 'PRESTIGE': -1}}, 'Radio Moscow explains the Chinese perfidy in four dialects.'),
    ],
)

EVENTS_FIXED["afghanistan_1979"] = ev(
    "afghanistan_1979", 'Afghanistan: The Amin Problem', 'Herat burns. Taraki is dead. The Politburo holds three midnight sessions.',
    [
    opt('Intervene with the 40th Army', {'stats': {'MILITARY': 4, 'PRESTIGE': -4, 'ECONOMY': -2}, 'flag_add': 'at_war', 'queue': [(3, 'afghan_stalemate')]}, 'Soviet columns cross the Amu Darya. The mountains are patient.'),
    opt('Support the regime with materiel only', {'stats': {'MILITARY': 1, 'PRESTIGE': -1, 'ECONOMY': -1}}, 'Mi-24s and advisers cross the border; columns do not.'),
    opt('Wash your hands of Kabul', {'stats': {'PRESTIGE': 1, 'ORDER': -1}}, 'Kabul resolves its arithmetic without you. For now.'),
    ],
)

EVENTS_FIXED["olympics_1980"] = ev(
    "olympics_1980", 'Moscow Olympics, 1980', 'Sixty-five nations boycott. Mascot Mishka still waves from the stadium.',
    [
    opt('Stage the grandest Games ever', {'stats': {'PRESTIGE': 4, 'ECONOMY': -3}}, 'The closing bear sheds a tear of expensive nostalgia.'),
    opt('Use the Games for diplomacy', {'stats': {'PRESTIGE': 3, 'FAITH': 1, 'ORDER': -1}}, 'Athletes mingle; journalists file 900 stories per hour.'),
    opt('Frame the boycott as hysterics', {'stats': {'FAITH': 1, 'PRESTIGE': -2}}, "Radio Moscow regrets Western 'circle-jerking'."),
    ],
)

EVENTS_FIXED["succession_1982"] = ev(
    "succession_1982", 'Succession of 1982: The Old Guard', 'The Politburo convenes. Power is a question of arithmetic.',
    [
    opt('Consolidate quietly', {'stats': {'ORDER': 4, 'FAITH': -1}}, 'The Old Guard applauds with signet rings.'),
    opt('Promise renewal, act carefully', {'stats': {'FAITH': 3, 'ORDER': -1, 'PRESTIGE': 1}}, 'A new tone. New names. Same dachas.'),
    opt('Offer reforms immediately', {'stats': {'FAITH': 2, 'ORDER': -2, 'PRESTIGE': 2}}, 'The apparatus grumbles in fifteen languages.'),
    ],
)

EVENTS_FIXED["able_archer"] = ev(
    "able_archer", 'Able Archer 83', "NATO's communication drills look alarmingly like launch preparation.",
    [
    opt('Issue a firm nuclear warning', {'stats': {'MILITARY': 2, 'PRESTIGE': -3}}, "TASS publishes names of 'war criminals'. Diplomats drink valium tea."),
    opt('Open a back-channel to Washington', {'stats': {'PRESTIGE': 3, 'MILITARY': -1, 'ORDER': 1}}, 'A quiet lunch in Geneva prevents a loud misunderstanding.'),
    opt('Trust the KGB, raise readiness', {'stats': {'MILITARY': 3, 'PRESTIGE': -2, 'ORDER': -1}}, 'Minesweepers sail; silo doors oil their hinges.'),
    ],
)

EVENTS_FIXED["new_secretary"] = ev(
    "new_secretary", 'The New General Secretary', "Gorbachev's reform team arrives with diagrams of hope and anti-alcohol posters.",
    [
    opt('Embrace perestroika fully', {'stats': {'FAITH': 3, 'PRESTIGE': 3, 'ORDER': -3}, 'flag_add': 'perestroika'}, "The word 'acceleration' enters the dictionary with Velcro."),
    opt('Reform slowly, keep the plan', {'stats': {'ECONOMY': 2, 'FAITH': 1, 'ORDER': 1}}, 'Pilot zones open in two awkward regions.'),
    opt('Defend orthodoxy', {'stats': {'ORDER': 3, 'FAITH': -2, 'PRESTIGE': -1}}, 'The Old Guard sighs with cautious relief.'),
    ],
)

EVENTS_FIXED["chernobyl"] = ev(
    "chernobyl", 'Chernobyl, 26 April 1986', 'Reactor Block IV glows with unplanned physics. Kiev gardens prepare for May.',
    [
    opt('Admit the disaster immediately', {'stats': {'FAITH': 2, 'PRESTIGE': 3, 'ECONOMY': -3}}, 'Radiologists fly in from eleven countries. Truth is expensive and less fatal.'),
    opt('Keep it quiet, evacuate quietly', {'stats': {'FAITH': -4, 'PRESTIGE': -4}, 'flag_add': 'chernobyl_hidden', 'queue': [(1, 'chernobyl_secrecy')]}, 'Kiosks sell kilos of newsprint, none mentioning dosimeters.'),
    opt("Dismiss as 'not a catastrophe'", {'stats': {'FAITH': -2, 'PRESTIGE': -3}, 'flag_add': 'chernobyl_hidden', 'queue': [(1, 'chernobyl_secrecy')]}, 'Swedish monitoring stations foam politely.'),
    ],
)

EVENTS_FIXED["reykjavik"] = ev(
    "reykjavik", 'Reykjavik Summit', "Reagan will not bury SDI. Gorbachev won't bury SDI either. Iceland yawns.",
    [
    opt('Hunt for the grand bargain', {'stats': {'PRESTIGE': 4, 'MILITARY': -2}}, 'No deal, but the world watches two leaders talk honestly.'),
    opt('Demand SDI scrapped first', {'stats': {'PRESTIGE': -1, 'MILITARY': 1}}, 'Reagan quotes a proverb about negotiation and stubbornness.'),
    opt('Propose smaller, verifiable cuts', {'stats': {'PRESTIGE': 3, 'MILITARY': -1}}, "INF takes its first baby steps in Reykjavik's silence."),
    ],
)

EVENTS_FIXED["wall_falls"] = ev(
    "wall_falls", 'The Berlin Wall Falls', 'Crowds dance on the Wall. Guards watch, then watch some more.',
    [
    opt('Order non-intervention, publicly', {'stats': {'PRESTIGE': 4, 'FAITH': 3, 'ORDER': -4}}, "'Frankfurt is our answer.' The GDR transitions into a museum."),
    opt('Request Warsaw Pact deliberation', {'stats': {'ORDER': 1, 'PRESTIGE': -1, 'FAITH': -1}}, 'Statements are composed; hammers arrive unstamped.'),
    opt('Stay silent entirely', {'stats': {'PRESTIGE': -2, 'FAITH': -1, 'ORDER': -2}}, 'Silence translated by both sides as opportunism.'),
    ],
)

EVENTS_FIXED["august_coup"] = ev(
    "august_coup", 'The August Coup, 1991', 'The Emergency Committee seizes the studios. Tanks idle at the bridges.',
    [
    opt('Defy the coup from the radio', {'special': 'coup_defy'}, 'The nation listens. History holds its breath.'),
    opt('Back the Emergency Committee', {'special': 'coup_join'}, 'The studios switch to Swan Lake; your signature appears on the decrees.'),
    opt('Remain carefully absent', {'special': 'coup_absent'}, 'You are, officially, resting in a secure dacha.'),
    ],
)

EVENTS_FIXED["palace_coup"] = ev(
    "palace_coup", 'The Velvet Meeting', 'The Politburo has reserved your own conference room for Thursday. Nobody will say what the agenda is. Everybody smiles too tightly.',
    [
    opt('Walk in and face the plenum', {'special': 'coup_fight'}, 'Room 14, third floor. Bring accomplices and everyone else.'),
    opt('Buy the plenum off', {'stats': {'ORDER': -3, 'ECONOMY': -3}, 'hc': -6, 'court': {'old_guard': 20, 'reformers': -8}, 'flag_add': 'made_deals'}, 'Dachas, titles, and the radio timetable change hands.'),
    opt('Appeal over their heads', {'special': 'coup_people'}, 'The miners, the Party youth, the kitchens.', {'stats': {'FAITH': 45}}),
    ],
    once=True,
)

EVENTS_FIXED["rouble_zone"] = ev(
    "rouble_zone", 'The Rouble Zone Question', 'Republic treasuries start printing their own coupons. The single currency argues with nine ambitions.',
    [
    opt('One hard rouble, one Union treasury', {'stats': {'ECONOMY': 5, 'ORDER': 2, 'FAITH': 1}, 'hc': -6, 'court': {'reformers': 3}, 'flag_add': 'rouble_zone_solid'}, 'The printing presses relearn their address.'),
    opt('Peg republic coupons to the rouble', {'stats': {'ECONOMY': 2, 'ORDER': -1}}, 'Exchange offices grow eponyms and margins.'),
    opt('Abandon money policy to the republics', {'stats': {'ORDER': -5, 'FAITH': -3, 'ECONOMY': -3}}, 'Nine currencies bloom; the queues keep one language.'),
    ],
    once=True,
)

EVENTS_FIXED["union_charter"] = ev(
    "union_charter", 'The Union Charter', 'A constitutional convention argues the architecture of the renewed state. Two drafts, three committees, one hall.',
    [
    opt('A federation of equals', {'stats': {'FAITH': 5, 'PRESTIGE': 2, 'ORDER': -3}, 'court': {'reformers': 6, 'old_guard': -4}, 'flag_add': 'charter_signed'}, 'Republics sign smaller words and mean them.'),
    opt('Strengthen the centre, interim powers', {'stats': {'ORDER': 4, 'FAITH': -2}, 'court': {'old_guard': 4}}, "'Interim' becomes a decade's favourite adjective."),
    opt('Let the general staff draft the chapter', {'stats': {'ORDER': 3, 'FAITH': -4}, 'court': {'military': 4}}, 'The constitution acquires artillery terminology.'),
    ],
    once=True,
)

EVENTS_FIXED["asian_flu_1997"] = ev(
    "asian_flu_1997", 'Tigers Stumble in Asia', "Finance collapses in Bangkok, Seoul, Jakarta. The contagion walks toward the Union's exchanges on monthly wire reports.",
    [
    opt('Cushion the currency with the valas', {'stats': {'ECONOMY': 2}, 'hc': -8}, 'The reserve absorbs the sneeze with a grimace.'),
    opt('Substitute imports behind a tariff wall', {'stats': {'ECONOMY': 1, 'ORDER': 1}, 'hc': 2}, "Domestic factories inherit other people's markets."),
    opt('Call a socialist common-fund conference', {'stats': {'PRESTIGE': 3, 'ECONOMY': 1}, 'hc': 4, 'court': {'reformers': -2}}, 'Partners push gold into a shared hat.'),
    ],
    once=True,
)

EVENTS_FIXED["nato_east_1999"] = ev(
    "nato_east_1999", 'NATO Steps East', 'The alliance flags over former Warsaw barracks. The western border reads like a list of moved furniture.',
    [
    opt('Sign the partnership treaty anyway', {'stats': {'PRESTIGE': 4, 'MILITARY': -2}, 'hc': 3}, 'Pollen, partnerships, and cups of coffee get traded.'),
    opt('Counter the alliance in the UN', {'stats': {'PRESTIGE': 1}, 'court': {'military': 3}}, 'A veto, a communique, and veto leverage stored for later.'),
    opt('Re-deploy the missile formations', {'stats': {'MILITARY': 3, 'ECONOMY': -4, 'PRESTIGE': -3}, 'court': {'military': 5, 'old_guard': 2}}, "Trains roll west; NATO's telephones run hot."),
    ],
    once=True,
)

EVENTS_FIXED["millennium_message"] = ev(
    "millennium_message", 'The Millennium Message', "The Union's new-century broadcast proposes its first great act: the cameras of the world are tuned.",
    [
    opt('Propose global nuclear zero by 2010', {'stats': {'PRESTIGE': 8, 'FAITH': 3, 'MILITARY': -4}, 'flag_add': 'red_initiative'}, 'The doctrine of the millennium: the bomb retires early.'),
    opt('Announce the silicon-and-space moonshot', {'stats': {'ECONOMY': 3, 'PRESTIGE': 5}, 'hc': -5, 'court': {'reformers': 4}}, 'Terminals and tractors both wait for the rocket.'),
    opt('A decade of order and festivals', {'stats': {'ORDER': 3, 'FAITH': 2}, 'court': {'old_guard': 4}}, 'Banners, parades, punctual buses: a safest of centuries.'),
    ],
    once=True,
)

EVENTS_FIXED["millennium_congress"] = ev(
    "millennium_congress", '☰ THE 1996 RED MILLENNIUM CONGRESS', "Survival settled, the Central Committee debates the coming decade's mission. Four motions, one future.",
    [
    opt('Declare the market union', {'stats': {'ECONOMY': 5, 'ORDER': -3}, 'court': {'reformers': 6, 'old_guard': -6}, 'flag_add': 'market_union'}, 'Prices, auditors, and a stock exchange acquire sofas.'),
    opt('Legislate the social guarantee decade', {'stats': {'FAITH': 5, 'ECONOMY': -3}, 'court': {'old_guard': 3, 'reformers': 2}}, "Pensions, schools, sanatoria: the decade's true bearings."),
    opt('The high-tech leap (chips & biotech)', {'stats': {'ECONOMY': 4, 'PRESTIGE': 3}, 'court': {'reformers': 3}, 'flag_add': 'tech_leap'}, "Laboratories inherit the decade's toys."),
    opt('The imperial belt: military renewal', {'stats': {'MILITARY': 5, 'ECONOMY': -3}, 'court': {'military': 4, 'reformers': -3}}, 'New uniforms keep the old map drawn.'),
    ],
    once=True,
)
