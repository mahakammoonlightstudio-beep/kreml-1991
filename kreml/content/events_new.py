"""The extended era (1992-2001).

Content is pure data: `builders.ev` / `builders.opt` keep the literals
short. Split out of the single v5 catalogue by tools/split_events.py;
add new events here, in the era they belong to.
"""
from __future__ import annotations

from .builders import ev, opt

EVENTS_NEW: dict[str, object] = {}

EVENTS_NEW["oligarch_weekend"] = ev(
    "oligarch_weekend", 'The Weekend Oligarchs', 'New cooperative tycoons charter steamers on the Volga weekends. Their shirts are silk; their receipts are debatable.',
    [
    opt('Tax the tycoons into sculptural innocence', {'stats': {'ECONOMY': 5, 'FAITH': 1}, 'hc': 6, 'court': {'reformers': -4}}, 'The treasury yawns; the yachts still run on tyres.'),
    opt('Seat them on a Party economic board', {'stats': {'ECONOMY': 2}, 'court': {'reformers': 6, 'old_guard': -6}, 'flag_add': 'oligarchs_seated'}, 'Cards, committees, and mutual vetoes in one room.'),
    opt('Jail the loudest, audit the rest', {'stats': {'ORDER': 3, 'ECONOMY': -3}, 'court': {'reformers': -6, 'old_guard': 5}}, 'One goes to Butyrka; capital develops a stammer.'),
    ],
    era='NEW',
)

EVENTS_NEW["brain_gain"] = ev(
    "brain_gain", 'The Return of the Engineers', 'Former emigres from Silicon Valley offer to come home with patents and briefcases. The ministries salivate quietly.',
    [
    opt('Welcome them with valas salaries', {'stats': {'ECONOMY': 4, 'PRESTIGE': 3}, 'hc': -5, 'court': {'reformers': 4}, 'flag_add': 'returnees'}, 'Labs re-acquire passports and ambition.'),
    opt('A patriotic decree, posters, no salaries', {'stats': {'FAITH': 2}}, 'Two families arrive; the posters are excellent.'),
    opt('File their letters for later', {'stats': {'PRESTIGE': -1}}, 'The briefcases fly back across the ocean.'),
    ],
    era='NEW',
)

EVENTS_NEW["siberia_2"] = ev(
    "siberia_2", 'Siberia, Second Attempt', 'Geologists find a gas field north of the circle. Pipes, frost, foreign buyers, foreign bankers, all interested.',
    [
    opt('Pour billions into pipes now', {'stats': {'ECONOMY': 6, 'PRESTIGE': 1}, 'hc': 8, 'court': {'old_guard': 2}}, 'Steel crawls north; the frost invoices in degrees.'),
    opt('Pilot the field, phase the money', {'stats': {'ECONOMY': 2}, 'hc': 3}, 'Boring, careful, and occasionally even profitable.'),
    opt('Consortium with Tokyo', {'stats': {'ECONOMY': 3, 'PRESTIGE': -2}, 'hc': 10, 'court': {'reformers': 2, 'old_guard': -4}}, 'Yen thaws the permafrost at market speed.'),
    ],
    era='NEW',
)

EVENTS_NEW["network_age"] = ev(
    "network_age", 'The Network Reaches the Union', 'Public terminals multiply in libraries and post offices. One network, forty dialects of enthusiasm.',
    [
    opt('Build one network, Soviet protocols', {'stats': {'ECONOMY': 5, 'PRESTIGE': 3, 'ORDER': -2}, 'flag_add': 'red_net_live', 'hc': -3}, "The Union acquires a nervous system with a censor's conscience."),
    opt('Connive at internal-only, jam the foreign', {'stats': {'ORDER': 2, 'FAITH': -2}}, 'The network exists; the world exists theoretically.'),
    opt('Regard the terminals as a passing fashion', {'stats': {'FAITH': -1}}, "Institutes connect anyway, through the third floor's fax."),
    ],
    era='NEW',
)

EVENTS_NEW["church_revival"] = ev(
    "church_revival", 'The Cathedrals Reopen', "Craftsmen regild domes with private donations. The State's atheist calendar looks dowdy beside it.",
    [
    opt('Support restoration with a state fund', {'stats': {'FAITH': 4, 'PRESTIGE': 2, 'ORDER': -1}, 'hc': -3, 'court': {'reformers': 2, 'old_guard': -2}}, 'Domes return to the skyline, receipts and all.'),
    opt('Let society fund its own roofs', {'stats': {'FAITH': 3}, 'court': {'reformers': 2}}, 'Sponsorship plaques bloom; the state abstains decorously.'),
    opt("Convert three to 'science museums'", {'stats': {'ORDER': 2, 'FAITH': -3}}, 'Museum guides explain frescoes with dialectical footnotes.'),
    ],
    era='NEW',
)

EVENTS_NEW["arctic_route"] = ev(
    "arctic_route", 'The Northern Sea Route Revival', 'Atomic icebreakers could open the polar lane. Freight schedules and admirals both check their watches.',
    [
    opt('Commission a new icebreaker fleet', {'stats': {'MILITARY': 2, 'PRESTIGE': 3, 'ECONOMY': 2}, 'hc': -4, 'court': {'military': 3}}, 'The Arctic learns timetables and flags.'),
    opt('Charter the route to foreign shippers', {'stats': {'ECONOMY': 3}, 'hc': 6}, 'The polar lane hums with foreign chequebooks.'),
    opt('Mothball the season as uneconomic', {'stats': {'ECONOMY': -1}}, 'The icebreakers nap; the admirals write letters.'),
    ],
    era='NEW',
)

EVENTS_NEW["wild_east_jobs"] = ev(
    "wild_east_jobs", 'The Far East Jobs Wagon', 'Chinese traders arrive in Chita with pliers and prices. Border towns grow bilingual markets overnight.',
    [
    opt('Declare a free-trade belt on the border', {'stats': {'ECONOMY': 4, 'FAITH': 1, 'ORDER': -2}, 'hc': 5, 'court': {'reformers': 3}}, 'Pliers, pepper, and state theory all appreciate.'),
    opt('KGB scrutiny of every wagon', {'stats': {'ORDER': 3, 'ECONOMY': -2}, 'court': {'old_guard': 3}}, 'Half the pliers are documented twice.'),
    opt('Plan the markets into officialdom', {'stats': {'FAITH': 1, 'ECONOMY': 1}}, 'Pliers acquire permits, margins acquire stamps.'),
    ],
    era='NEW',
)
