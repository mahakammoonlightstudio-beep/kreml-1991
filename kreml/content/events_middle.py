"""MIDDLE era events (1976-1984).

Content is pure data: `builders.ev` / `builders.opt` keep the literals
short. Split out of the single v5 catalogue by tools/split_events.py;
add new events here, in the era they belong to.
"""
from __future__ import annotations

from .builders import ev, opt

EVENTS_MIDDLE: dict[str, object] = {}

EVENTS_MIDDLE["solidarnosc"] = ev(
    "solidarnosc", 'Solidarność Rises (Poland)', "Gdańsk shipyard strikes spread. Jaruzelski asks for 'brotherly advice'.",
    [
    opt('Advise martial law, send nothing', {'stats': {'ORDER': 3, 'PRESTIGE': -2}}, 'Warsaw cracks down on its own; Moscow shrugs.'),
    opt('Threaten open intervention', {'stats': {'ORDER': 2, 'PRESTIGE': -4}}, 'Western TV relays dark memories of 1968.'),
    opt('Send economic concessions', {'stats': {'ECONOMY': -4, 'PRESTIGE': 2}}, 'Polish dockers wave Soviet shipments of meat.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["grain_scandal"] = ev(
    "grain_scandal", 'Grain Import Scandal', "A statistician confesses the harvest is 'narratively optimistic'.",
    [
    opt('Hide behind weather', {'stats': {'FAITH': -2, 'PRESTIGE': -1}}, 'Meteorologists win an unplanned overtime bonus.'),
    opt('Buy Canadian wheat quietly', {'stats': {'ECONOMY': -3, 'FAITH': 2}, 'hc': -4}, 'Bread appears; so do Western spot checks.'),
    opt('Punish the statisticians', {'stats': {'ORDER': 2, 'FAITH': -2, 'ECONOMY': -1}}, 'Numbers behave; grain does not.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["andropov_dossiers"] = ev(
    "andropov_dossiers", "Andropov's Anti-Corruption Dossiers", 'KGB folders land on your desk: officials with dachas, mistresses, foreign watches.',
    [
    opt('Let him strike the Old Guard', {'stats': {'ORDER': 2, 'FAITH': 3, 'ECONOMY': 1}}, 'Notable resignations at prestigious dachas.'),
    opt('Shelve the dossiers', {'stats': {'FAITH': -2, 'PRESTIGE': -1}}, 'The files age in a locked cabinet per bureaucracy.'),
    opt('Trials, but only minor fish', {'stats': {'FAITH': -1, 'ORDER': 1}}, 'Two shop managers pay for three gowns of sin.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["war_scares"] = ev(
    "war_scares", 'War Scares and Crackling Radio', 'NATO exercises read like first-strike rehearsal. The KGB wants readiness.',
    [
    opt('Mobilize partially', {'stats': {'MILITARY': 2, 'ECONOMY': -2, 'PRESTIGE': -1}}, 'Tanks rumble near Vilnius. NATO grows nervous.'),
    opt('Approach quietly via GDR channels', {'stats': {'PRESTIGE': 2, 'ORDER': 1}}, 'East Berlin passes a note; war painters relax.'),
    opt('Ignore the signals', {'stats': {'MILITARY': -1}}, 'History books will judge this shelf someday.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["black_market_boom"] = ev(
    "black_market_boom", 'Black Market Boom', "Levi's jeans cost a monthly salary. Currency is 'fictitious but beloved'.",
    [
    opt('Raid the bazaars', {'stats': {'ORDER': 2, 'FAITH': -2}}, 'Seized blue jeans vanish into KGB warehouses.'),
    opt('Open Beryozka-style shops', {'stats': {'ECONOMY': 3, 'FAITH': -1}, 'hc': 4}, 'Hard-currency boutiques soothe official appetites.'),
    opt('Look away', {'stats': {'FAITH': 1, 'ORDER': -2, 'ECONOMY': -1}}, 'The shadow economy pays employees and cadres alike.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["oil_shock"] = ev(
    "oil_shock", 'The Oil Price Collapses', 'Global crude tumbles. Gosplan recalculates three times, weeps once.',
    [
    opt('Austerity in the ministries', {'stats': {'ECONOMY': 1, 'FAITH': -2}}, "Caviar at banquets is declared 'voluntary'."),
    opt('Borrow from the West', {'stats': {'ECONOMY': 3, 'PRESTIGE': -1}, 'hc': 8}, 'Loans buy time, and time costs interest.'),
    opt('Squeeze consumers', {'stats': {'ECONOMY': 2, 'FAITH': -3}}, 'Queue discipline becomes a Party virtue.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["poland_health"] = ev(
    "poland_health", 'Warsaw Requests Medical Counsel', "Jaruzelski's government stumbles; Warsaw solicits Soviet advisors.",
    [
    opt('Send Soviet doctors with orders', {'stats': {'ORDER': 1, 'PRESTIGE': -1, 'MILITARY': 1}}, "Your advisors' medical advice is politically vigorous."),
    opt('Let Poles handle Poles', {'stats': {'PRESTIGE': 1, 'ORDER': -1}}, 'Warsaw resolves this with its own paperwork.'),
    opt("Announce 'fraternal unity'", {'stats': {'FAITH': 1, 'PRESTIGE': -1}}, 'TASS composes three paragraphs of nouns.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["worker_letter"] = ev(
    "worker_letter", 'A Worker Writes About Emptiness', "A Leningrad worker writes: 'We greet openness, but not with empty shelves.'",
    [
    opt('Publish the letter', {'stats': {'FAITH': 3, 'ORDER': -1, 'PRESTIGE': 2}}, 'Pravda prints honesty. The nation gasps, politely.'),
    opt('Reply privately, praise the man', {'stats': {'FAITH': 1, 'ORDER': 1}}, 'A signed photo and ration coupons arrive.'),
    opt('Classify the letter anti-Soviet', {'stats': {'ORDER': 2, 'FAITH': -3}}, 'Archive shelf B-41 gains more paper.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["athletes_defect"] = ev(
    "athletes_defect", 'Soviet Athletes Defect', 'A chess grandmaster and a hockey winger vanish in Vienna.',
    [
    opt("Punish their trainers' staff", {'stats': {'ORDER': 2, 'FAITH': -2, 'PRESTIGE': -1}}, "The word 'hostage' circulates in Western papers."),
    opt("Improve athletes' conditions", {'stats': {'ECONOMY': -2, 'FAITH': 1, 'PRESTIGE': 1}}, 'New uniforms, better sport schools. Defections slow.'),
    opt('Recruit them back via KGB channels', {'stats': {'PRESTIGE': 2, 'MILITARY': 1}}, 'One returns; the other writes a memoir in Paris.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["brezhnev_orders"] = ev(
    "brezhnev_orders", 'Brezhnev Honours Himself', 'A fifth Order is awarded to a portrait of a portrait.',
    [
    opt('Publish the award', {'stats': {'FAITH': -1, 'PRESTIGE': -1}}, 'Newspapers run identical photographs.'),
    opt('Award somebody else', {'stats': {'FAITH': 2, 'ECONOMY': -1}}, 'A tractor driver becomes a Hero of Socialism.'),
    opt('Cancel the ceremony', {'stats': {'ORDER': -1, 'FAITH': 1}}, "The laureates grumble about 'rash collegiality'."),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["uzbek_cotton"] = ev(
    "uzbek_cotton", 'Uzbek Cotton Fantasy', 'Region reports cotton by the ton. Fields, thinner, share less truth.',
    [
    opt('Order an audit', {'stats': {'FAITH': 2, 'ORDER': -2, 'ECONOMY': -1}}, 'Local Party secretaries discover forgotten honesty.'),
    opt('Accept the harvest report', {'stats': {'ECONOMY': -2, 'FAITH': -1}}, 'Gosplan gets cotton; the fields get questions.'),
    opt('Punish the auditors', {'stats': {'ORDER': 2, 'FAITH': -2}}, "Two honest men retire to Tashkent's quiet suburbs."),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["foreign_debt"] = ev(
    "foreign_debt", 'Foreign Debt Sneaks Up', "Trade ministry reveals the currency holdings won't cover grain debts.",
    [
    opt('Cut military procurement bills', {'stats': {'MILITARY': -2, 'ECONOMY': 2}}, 'Generals write letters; loans get cheaper.'),
    opt('Reduce imports of Western tech', {'stats': {'ECONOMY': -1, 'PRESTIGE': -1}}, 'Industrial espionage fails loudly twice.'),
    opt('Sell gold reserves', {'stats': {'ECONOMY': 4, 'PRESTIGE': -2}, 'hc': 10}, "Swiss bankers toast 'comrade prudence'."),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["yugo_study"] = ev(
    "yugo_study", "Tito's Textbooks Reach You", 'A Dublin-style journal discusses Yugoslav self-management and its seductions.',
    [
    opt('Study the Yugoslav model', {'stats': {'ECONOMY': 3, 'ORDER': -1}, 'flag_add': 'yugo_study'}, 'Worker councils get a respectful pamphlet.'),
    opt('Ban the book', {'stats': {'ORDER': 2, 'FAITH': -1}}, 'The banned list gains one item and ten copies of courage.'),
    opt('Shelve quietly', {}, 'The shelf is quiet. So is the idea.'),
    ],
    era='MIDDLE', once=True,
)

EVENTS_MIDDLE["afghan_trap"] = ev(
    "afghan_trap", 'The Mountain Trap', "Kabul's arithmetic worsens. Your columns eat ice and ammunition.",
    [
    opt('Escalate with more divisions', {'stats': {'MILITARY': -3, 'PRESTIGE': -1}, 'flag_add': 'afghan_deep'}, 'More tanks arrive; the mountains remain unsaleable.'),
    opt('Withdraw and cut losses', {'flag_rm': 'at_war', 'flag_add': 'afghan_withdraw'}, 'Columns return across the Amu Darya. Prestige bleeds; men live.'),
    opt('Hold the present course', {'stats': {'MILITARY': -2, 'ECONOMY': -1}}, 'Attrition stays attrition.'),
    ],
    era='MIDDLE', requires={'flags': ['at_war']},
)

EVENTS_MIDDLE["pipeline_sabotage"] = ev(
    "pipeline_sabotage", 'The Pipeline Knows Sabotage', 'A large Soviet pipe mysteriously fractures; the West whistles innocently.',
    [
    opt('Import American turbines quietly', {'stats': {'ECONOMY': -2, 'PRESTIGE': -1}, 'hc': -5}, 'Third-country invoices; the embargo gains bandaids.'),
    opt('Race domestic turbines', {'stats': {'ECONOMY': -4}}, 'Two slow years; engineers reap scars and pride.'),
    opt('Ration sectors for a season', {'stats': {'ECONOMY': -3, 'FAITH': -1}}, "Shops get 'planned maintenance' excuses."),
    ],
    era='MIDDLE', once=True,
)

EVENTS_MIDDLE["helsinki_accords"] = ev(
    "helsinki_accords", 'The Helsinki Baskets', "The Final Act offers trade and peace — and 'Basket III' monitors your borders.",
    [
    opt('Sign the lot, Basket III included', {'stats': {'PRESTIGE': 3, 'ORDER': -2}, 'flag_add': 'helsinki'}, 'Human-rights Helsinki Watch groups set up desks in nine capitals.'),
    opt('Sign, but file Basket III away', {'stats': {'PRESTIGE': 2, 'ORDER': 1}}, 'Trade flows; the monitors queue at your embassy.'),
    opt("Refuse as 'imperialist dictation'", {'stats': {'ORDER': 1, 'PRESTIGE': -2}}, 'You keep the buffers; Europe keeps the receipts.'),
    ],
    era='MIDDLE', once=True,
)

EVENTS_MIDDLE["vatican_signal"] = ev(
    "vatican_signal", 'A Quiet Signal from the Vatican', 'The new Pope sends a private note: markets of a different kind, and an offer of intermediaries with the West.',
    [
    opt('Answer warmly, meet the emissary', {'stats': {'PRESTIGE': 2, 'FAITH': 2, 'ORDER': -1}, 'court': {'old_guard': -4, 'reformers': 2}}, 'A monsignor, a KGB man, and one lens of illy coffee.'),
    opt('Publish the note as imperialist seduction', {'stats': {'ORDER': 2, 'PRESTIGE': -2, 'FAITH': -2}}, 'TASS does theology for one afternoon.'),
    opt('File it without comment', {'stats': {'FAITH': -1}}, 'The note lives at archive shelf 14-C, famously unread.'),
    ],
    era='MIDDLE',
)

EVENTS_MIDDLE["grain_bill"] = ev(
    "grain_bill", 'The Grain Bill, Paid in Valas', 'Canadian wheat arrives reliably and invoices in convertible currency. The valas reserve is one meal shorter.',
    [
    opt('Pay in hard currency, feed everyone', {'stats': {'ECONOMY': 3, 'FAITH': 2}, 'hc': -8}, 'Bread arrives invoiced; the reserve pays and resents it.'),
    opt('Pledge machine exports instead', {'stats': {'ECONOMY': 1, 'PRESTIGE': -2}}, 'Tractors sail west; the arithmetic squeaks but holds.'),
    opt("Stall like a creditor's nightmare", {'stats': {'ECONOMY': -2, 'PRESTIGE': -3}, 'hc': 3}, 'Three letters, one law firm, and a season of shrugging.'),
    ],
    era='MIDDLE',
)
