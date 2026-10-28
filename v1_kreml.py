#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 ☭  К Р Е М Л Ь   1 9 9 1  ☭
 A text-based Soviet Union survival game.

 You are General Secretary of the CPSU, 1964 - 1991.
 Keep the Union alive for 28 years:
   - ECONOMY   (Gosplan's five-year plans)
   - MILITARY  (the Red Army and rocket forces)
   - ORDER     (control over society and republics)
   - FAITH     (the people's belief in the State)
   - PRESTIGE  (national standing in the Cold War)
 If any gauge reaches 0, the Kremlin falls.

 Run:  python kreml_1991.py          (normal)
       python kreml_1991.py --drama  (typewriter effect)
       python kreml_1991.py --seed 42
 Type 'q' at any menu to retire early.
============================================================
"""

from __future__ import annotations

import os
import sys
import time
import random
import datetime

# ---------------------------------------------------------------
# Console setup (Windows ANSI + UTF-8)
# ---------------------------------------------------------------
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if os.name == "nt":
    os.system("")  # Enables ANSI escape codes on Windows 10+

GAME_DIR = os.path.dirname(os.path.abspath(__file__))
HALL_FILE = os.path.join(GAME_DIR, "hall_of_fame.txt")


class C:
    """ANSI colours."""
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    BL = "\033[94m"
    MG = "\033[95m"
    CY = "\033[96m"
    W = "\033[97m"
    BM = "\033[1m\033[91m"   # bold red
    BG = "\033[1m\033[92m"   # bold green
    BB = "\033[1m"           # bold
    DIM = "\033[90m"
    X = "\033[0m"


def c(text: str, code: str) -> str:
    return f"{code}{text}{C.X}"


DRAMA = False
USE_COLOUR = sys.stdout.isatty() if sys.stdout else True


def paint(text: str, code: str) -> str:
    if USE_COLOUR:
        return c(text, code)
    return text


def slow(text: str, delay: float = 0.012) -> None:
    if DRAMA:
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
    else:
        print(text)


def hr(char: str = "─", width: int = 78) -> str:
    return char * width


def clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------
# Stats
# ---------------------------------------------------------------
STATS = ("ECONOMY", "MILITARY", "ORDER", "FAITH", "PRESTIGE")
STAT_LABEL = {
    "ECONOMY":  "Economy   (Gosplan)",
    "MILITARY": "Military  (Red Army)",
    "ORDER":    "Order     (Control)",
    "FAITH":    "People    (Belief)",
    "PRESTIGE": "Prestige  (World)",
}
STAT_COLOUR = {
    "ECONOMY": C.Y,
    "MILITARY": C.R,
    "ORDER": C.MG,
    "FAITH": C.G,
    "PRESTIGE": C.CY,
}


def stat_colour_num(v: int, base: str) -> str:
    if v < 25:
        return C.BM
    if v < 45:
        return C.Y
    return base


def bar(v: int, width: int = 30) -> str:
    filled = int(round(v * width / 100))
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------
# The game state
# ---------------------------------------------------------------
class Kremlin:
    def __init__(self, seed: int | None):
        self.year = 1964
        self.end_year = 1991
        self.name = "Comrade Secretary"
        self.stats = {"ECONOMY": 55, "MILITARY": 70, "ORDER": 75,
                      "FAITH": 52, "PRESTIGE": 62}
        self.flags: set[str] = set()          # e.g. 'at_war_afghanistan'
        self.chernobyl_buried = False
        self.putschist = False
        self.reformed = False
        self.death_reason: str | None = None
        self.rng = random.Random(seed)

    # ----- helpers -------------------------------------------------
    def delta(self, **deltas: int) -> None:
        for k, v in deltas.items():
            self.stats[k] = clamp(self.stats[k] + v)

    def dead_stat(self) -> str | None:
        for s in STATS:
            if self.stats[s] <= 0:
                return s
        return None

    def forced_event_list(self, era: str) -> list[dict]:
        return RANDOM_EVENTS[era]

    def era(self) -> str:
        if self.year <= 1975:
            return "EARLY"
        if self.year <= 1984:
            return "MIDDLE"
        return "LATE"


# ---------------------------------------------------------------
# Yearly real-world flavour lines
# ---------------------------------------------------------------
HISTORY = {
    1964: "Khrushchev has been 'retired for reasons of health'. The Central Committee looks to you.",
    1965: "The Kosygin reforms dangle before Gosplan: profit, accountability... heresy?",
    1966: "The Tenth World Festival of Youth prepares to flood Tbilisi with Western music.",
    1967: "The fiftieth anniversary of October is celebrated with parades and fresh paint.",
    1968: "Tanks are idling outside Prague. Dubček talks of 'socialism with a human face'.",
    1969: "Border clashes crackle along the Ussuri river. Mao is no friend.",
    1970: "Zorki cameras and Zil trucks roll out. The N1 moon rocket awaits its next flight.",
    1971: "Gosplan meets for the Ninth Five-Year Plan. The Party breathes slow, thick smoke.",
    1972: "Nixon flies to Moscow. SALT negotiations open over samovar tea.",
    1973: "The OPEC embargo sends oil prices soaring. Currency flows toward the Urals pipelines.",
    1974: "Voznesensky recites to packed stadiums. Western correspondents fill hotel lobbies.",
    1975: "The Apollo–Soyuz docking is photographed as the world shrinks to one orbit.",
    1976: "The Twenty-Fifth Party Congress convenes. Brezhnev reads written greetings to himself.",
    1977: "A new Constitution praises the 'developed socialist society'. The archives multiply.",
    1978: "The N1 has been cancelled for years; the Energia designers whisper of new rockets.",
    1979: "Soviet advisors remain in Kabul while the Politburo argues about Hafizullah Amin.",
    1980: "Moscow hosts the Summer Olympics while Solidarność strikes in Gdańsk.",
    1981: "Wojciech Jaruzelski declares martial law in Warsaw. The West fumes and schemes.",
    1982: "Leonid Ilyich Brezhnev is dead. The Politburo convenes behind closed doors.",
    1983: "Able Archer 83: NATO rehearsal scares the KGB into believing first strike is imminent.",
    1984: "Konstantin Chernenko coughs through his one real year in power. The economy sags.",
    1985: "A younger Gorbachev takes the general secretary's chair. The ceiling leaks.",
    1986: "Reactor Block IV of the Chernobyl plant is burning. TASS is silent; the West is not.",
    1987: "Reykjavik: Reagan refuses to bury SDI. The accord collapses in Iceland's ash.",
    1988: "The Nineteenth Party Conference opens windows of glasnost. Something is listening.",
    1989: "The Berlin Wall falls on live television. The Politburo watches on censored tapes.",
    1990: "Republics declare sovereignty one after another, like dominoes in slow motion.",
    1991: "Tanks idle outside Moscow. The Emergency Committee meets in the Kremlin at dusk.",
}


# ---------------------------------------------------------------
# Standing directives (menu shown every year)
# ---------------------------------------------------------------
DIRECTIVES = [
    ("Five-Year Plan: heavy industry", "Cement, steel, more cement.",
     {"ECONOMY": 6, "FAITH": -2, "ORDER": 1}),
    ("Consumer goods & light industry", "Refrigerators, TVs, better shoes.",
     {"ECONOMY": 3, "FAITH": 4}),
    ("Military buildup", "New tanks, new rockets, new uniforms.",
     {"MILITARY": 6, "ECONOMY": -3}),
    ("Espionage & intelligence ops", "The KGB loves quiet paperwork.",
     {"PRESTIGE": 3, "MILITARY": 2}),
    ("Space science & exploration", "Cosmonauts and robots on the Moon.",
     {"PRESTIGE": 5, "ECONOMY": 1}),
    ("Culture, sport & education", "Libraries, stadiums, lyrical films.",
     {"FAITH": 3, "PRESTIGE": 2, "ORDER": -1}),
    ("Agriculture reform", "Private plot concessions, tractors promised.",
     {"ECONOMY": 2, "FAITH": 3, "ORDER": -1}),
    ("KGB crackdown", "Silence is the mother of order... allegedly.",
     {"ORDER": 6, "FAITH": -3, "PRESTIGE": -2}),
    ("Relax censorship (soft glasnost)", "Let writers breathe a little.",
     {"FAITH": 4, "ORDER": -3, "PRESTIGE": 1}),
    ("Détente diplomacy", "Summits, treaties, handshakes.",
     {"PRESTIGE": 5, "MILITARY": -1}),
    ("Oil & gas exports", "Purchases abroad with pipeline money.",
     {"ECONOMY": 4, "PRESTIGE": 1}),
    ("Party discipline & propaganda", "Posters, meetings, correct slogans.",
     {"ORDER": 3, "FAITH": 2, "ECONOMY": -1}),
]


# ---------------------------------------------------------------
# Random events per era.
# Each event: title, text, options of (label, deltas, note)
# ---------------------------------------------------------------
RANDOM_EVENTS: dict[str, list[dict]] = {
    "EARLY": [
        {"t": "The Vodka Shortage",
         "x": "Distilleries ship crates but shop windows are dry. Queueing men hum mourning songs.",
         "o": [("Ration via Party stores", {"FAITH": -2, "ORDER": 1}, "The queues thin; the grumbling thickens."),
               ("Import luggage confidence from Cuba", {"ECONOMY": -3, "FAITH": 2}, "Rum bottles arrive. Cuba ships sugar, confidence arrives later."),
               ("Deny the problem entirely", {"FAITH": -1}, "Pravda reports a surplus of patience and grain spirit.")]},
        {"t": "Dissident Samizdat",
         "x": "KGB agents seize nine mimeographed pages typed on onionskin.",
         "o": [("Trial the editors", {"ORDER": 2, "FAITH": -3, "PRESTIGE": -2}, "A show trial produces quiet applause and loud Western letters."),
               ("Let it slide", {"FAITH": 2, "ORDER": -1}, "The pages pass hand to hand like legislative jokes."),
               ("Purge them into a psychiatric ward", {"ORDER": 3, "FAITH": -2, "PRESTIGE": -2}, "Diagnosis: 'sluggish schizophrenia'. The typewriters register it.")]},
        {"t": "Kosygin Wants Reforms",
         "x": "The Premier slides you a memo: profit indicators, worker councils, honesty about steel.",
         "o": [("Support pilot reforms", {"ECONOMY": 4, "ORDER": -2}, "Two factories dare to profit. Applause is cautious."),
               ("Send him to the archives", {"ECONOMY": -1, "ORDER": 2}, "The memo is filed. So is its author's ambition."),
               ("Half-measures, report as success", {"ECONOMY": 2, "FAITH": 1}, "Three pilot plots. Bureaucratic applause stills all progress.")]},
        {"t": "N1 Rocket Explodes",
         "x": "The giant booster detonates over Baikonur and the pad becomes a crater.",
         "o": [("Announce 'a planned fabric destruction'", {"PRESTIGE": -1, "FAITH": -1}, "Radio Moscow inventories a successful launch of nothing."),
               ("Fund the N1 again", {"ECONOMY": -4, "PRESTIGE": 2}, "The Chief Designers get more metal and more patience."),
               ("Redirect the money to the military", {"MILITARY": 2, "PRESTIGE": -1}, "Generals toast the loss of their rival's toy.")]},
        {"t": "Western Jazz on Radio Luxembourg",
         "x": "Students gather near windowsills with dial-volume radios singing bravely.",
         "o": [("Jam the frequencies", {"ORDER": 2, "FAITH": -2}, "Static, then dynamic saxophone speaking Bulgarian."),
               ("Permit sanctioned jazz clubs", {"FAITH": 3, "ORDER": -1, "PRESTIGE": 1}, "Melodiya issues records; youth applies irony to the lyrics."),
               ("Call jazz 'a CIA weapon'", {"FAITH": -2, "PRESTIGE": -1}, "Even the jazz-hating Party members sigh.")]},
        {"t": "Coal Strike in Kuzbass",
         "x": "Miners list grievances: boots, bread, and a ration coupon of dignity.",
         "o": [("Send boots and meat", {"ECONOMY": -3, "FAITH": 2}, "Mittens arrive wearing slogans. Back to work."),
               ("Send the Internal Troops", {"ORDER": 3, "FAITH": -3}, "The pit resumes; so does the whispering."),
               ("Pretend it didn't happen", {"FAITH": -2, "PRESTIGE": -1}, "Western newspapers run a headline you can't see.")]},
        {"t": "The Virgin Lands Fail",
         "x": "Kazakh steppe yields dust instead of grain. Erosion grins at agronomy.",
         "o": [("Buy grain from the USA", {"ECONOMY": -4, "FAITH": 1}, "Solidarity with American farmers, priced objectively."),
               ("Blame weather, fine no one", {"FAITH": -1, "PRESTIGE": -1}, "Meteorologists invent three storms per province."),
               ("Rush irrigation projects", {"ECONOMY": -2, "FAITH": 2}, "Concrete channels leak prestige into sand.")]},
        {"t": "Cuban Sugar & Rum",
         "x": "Havana ships sugar and rum; asks for tractors and sympathy.",
         "o": [("Ship tractors, pallets of parts", {"ECONOMY": -2, "PRESTIGE": 2}, "Fidel sends cigars and a warm letter."),
               ("Send advice instead", {"PRESTIGE": -2, "FAITH": -1}, "Fidel's letter mentions 'comrade patience' three times."),
               ("Trade sugar for oil credits", {"ECONOMY": 2, "PRESTIGE": -1}, "Paperwork trickles across three ministries.")]},
        {"t": "Prague Voices Amateurs",
         "x": "Radio Prague relays debate so lively, censorship fades at the borders.",
         "o": [("Tighten jamming", {"ORDER": 2, "FAITH": -2}, "Cables hum; Czechoslovak whispers persist."),
               ("Send Party inspectors", {"ORDER": 1, "FAITH": -1, "PRESTIGE": -1}, "Cables and letters, all properly stamped."),
               ("Admit debate is 'errant but legal'", {"FAITH": 2, "ORDER": -2, "PRESTIGE": 1}, "An unnerving act of political honesty.")]},
        {"t": "The Golden Orlov",
         "x": "A Politburo member's new dacha grows a private submarine dock. Rumours multiply.",
         "o": [("Ignore, as always", {"FAITH": -2, "PRESTIGE": -1}, "The dock gains a second mooring."),
               ("Quietly reshuffle him", {"ORDER": 1, "FAITH": 1}, "He becomes an ambassador with a lake view instead."),
               ("Public anti-corruption trial", {"FAITH": 3, "ORDER": -3, "PRESTIGE": 2}, "People cheer. Officials elsewhere clear their desks.")]},
        {"t": "Defector at the Vienna Fair",
         "x": "A TASS correspondent shares his archive with Western services.",
         "o": [("Reinforce residency procedures", {"ORDER": 1, "MILITARY": 1, "PRESTIGE": -1}, "Every agent reports a field meeting with paperwork."),
               ("Recruit tradecraft training", {"MILITARY": 2, "ECONOMY": -1}, "Yuri Andropov proposes one seminar and two follow-ups."),
               ("Liquidate the asset abroad", {"PRESTIGE": -2, "ORDER": 1}, "Details are denied before anyone asks.")]},
        {"t": "Planned Reforms Fail Again",
         "x": "Gosplan's tables produce negative growth in four ministries.",
         "o": [("Tweak plan numbers", {"FAITH": -1, "ECONOMY": -1}, "Statistics find courage and rise a little."),
               ("Request foreign technology", {"ECONOMY": 2, "PRESTIGE": -1}, "Fiat diesels arrive at two pilot plants."),
               ("Blame managers, change none", {"FAITH": -2, "ORDER": 1}, "Two ministers are 'transferred for health'.")]},
    ],
    "MIDDLE": [
        {"t": "Solidarność Rises (Poland)",
         "x": "Gdańsk shipyard strikes spread. Jaruzelski asks for 'brotherly advice'.",
         "o": [("Advise martial law, send nothing", {"ORDER": 3, "PRESTIGE": -2}, "Warsaw cracks down on its own; Moscow shrugs."),
               ("Threaten open intervention", {"ORDER": 2, "PRESTIGE": -4}, "Western TV relays dark memories of 1968."),
               ("Send economic concessions", {"ECONOMY": -4, "PRESTIGE": 2}, "Polish dockers wave Soviet shipments of meat.")]},
        {"t": "Grain Import Scandal",
         "x": "Statistician confesses the 1979 harvest is 'narratively optimistic'.",
         "o": [("Hide behind weather", {"FAITH": -2, "PRESTIGE": -1}, "Meteorologists win an unplanned overtime bonus."),
               ("Buy Canadian wheat quietly", {"ECONOMY": -3, "FAITH": 2}, "Bread appears; so do Western spot checks."),
               ("Punish the statisticians", {"ORDER": 2, "FAITH": -2, "ECONOMY": -1}, "Numbers behave; grain does not.")]},
        {"t": "Andropov's Anti-Corruption Drive",
         "x": "KGB dossiers land on your desk: officials with dachas, mistresses, foreign watches.",
         "o": [("Let him strike the Old Guard", {"ORDER": 2, "FAITH": 3, "ECONOMY": 1}, "Notable suicides at prestigious dachas."),
               ("Shelve the dossiers", {"FAITH": -2, "PRESTIGE": -1}, "The files age in a locked cabinet per bureaucracy."),
               ("Trials, but select only minor fish", {"FAITH": -1, "ORDER": 1}, "Two shop managers pay for three gowns of sin.")]},
        {"t": "Able Archer-like Scares",
         "x": "NATO exercises read like first-strike rehearsal. The KGB wants mobilization.",
         "o": [("Mobilize partially", {"MILITARY": 2, "ECONOMY": -2, "PRESTIGE": -1}, "Tanks rumble near Vilnius. NATO grows nervous."),
               ("Approach quietly via GDR channels", {"PRESTIGE": 2, "ORDER": 1}, "East Berlin passes a note; war painters relax."),
               ("Ignore the signals", {"MILITARY": -1}, "History books will judge this shelf someday.")]},
        {"t": "Black Market Boom",
         "x": "Levi's jeans cost a monthly salary. Currency is 'fictitious but beloved'.",
         "o": [("Raid bazaars", {"ORDER": 2, "FAITH": -2}, "Seized blue jeans vanish into KGB warehouses."),
               ("Open 'Beryozka'-style shops", {"ECONOMY": 3, "FAITH": -1}, "Hard-currency boutiques soothe official appetites."),
               ("Look away", {"FAITH": 1, "ORDER": -2, "ECONOMY": -1}, "The shadow economy pays employees and cadres alike.")]},
        {"t": "Oil Price Collapse, Part One",
         "x": "Global crude tumbles. Gosplan recalculates three times, weeps once.",
         "o": [("Austerity in ministries", {"ECONOMY": 1, "FAITH": -2}, "Caviar at banquets is declared 'voluntary'."),
               ("Borrow from the West", {"ECONOMY": 3, "PRESTIGE": -1}, "Loans buy time, and time costs interest."),
               ("Squeeze consumers", {"ECONOMY": 2, "FAITH": -3}, "Queue discipline becomes a Party virtue.")]},
        {"t": "Polish Martial Law Health Scare",
         "x": "Jaruzelski collapses; Warsaw solicits Soviet medical advisors.",
         "o": [("Send Soviet doctors with orders", {"ORDER": 1, "PRESTIGE": -1, "MILITARY": 1}, "Your advisors' medical advice is politically vigorous."),
               ("Let Poles handle Poles", {"PRESTIGE": 1, "ORDER": -1}, "Warsaw resolves this with its own paperwork."),
               ("Announce 'fraternal unity'", {"FAITH": 1, "PRESTIGE": -1}, "TASS composes three paragraphs of nouns.")]},
        {"t": "Swimmer's Letter on Glasnost",
         "x": "A Leningrad worker writes: 'We greet openness, but not with empty shelves.'",
         "o": [("Publish the letter", {"FAITH": 3, "ORDER": -1, "PRESTIGE": 2}, "Pravda prints honesty. The nation gasps, politely."),
               ("Reply privately, praise chelovek", {"FAITH": 1, "ORDER": 1}, "A signed photo and ration coupons arrive."),
               ("Classify the letter 'anti-Soviet'", {"ORDER": 2, "FAITH": -3}, "Archive shelf B-41 gains more paper.")]},
        {"t": "Soviet Athletes Defect",
         "x": "A chess grandmaster and a hockey winger vanish in Vienna.",
         "o": [("Punish their trainer's staff", {"ORDER": 2, "FAITH": -2, "PRESTIGE": -1}, "The words 'hostage' circulate in Western papers."),
               ("Improve athletes' conditions", {"ECONOMY": -2, "FAITH": 1, "PRESTIGE": 1}, "New uniforms, better sport schools. Defections slow."),
               ("Recruit them back via KGB channels", {"PRESTIGE": 2, "MILITARY": 1}, "One returns; the other writes a memoir in Paris.")]},
        {"t": "Brezhnev Honours Himself",
         "x": "A fifth Order is awarded to a portrait of a portrait.",
         "o": [("Publish the award", {"FAITH": -1, "PRESTIGE": -1}, "Newspapers run identical photographs."),
               ("Award somebody else", {"FAITH": 2, "ECONOMY": -1}, "A tractor driver becomes a Hero of Socialism."),
               ("Cancel the ceremony", {"ORDER": -1, "FAITH": 1}, "The laureates grumble about 'rash collegiality'.")]},
        {"t": "Uzbek Cotton Fantasy",
         "x": "Region reported cotton by the ton. Fields, thinner, share less truth.",
         "o": [("Order an audit", {"FAITH": 2, "ORDER": -2, "ECONOMY": -1}, "Local Party secretaries discover forgotten honesty."),
               ("Accept the harvest report", {"ECONOMY": -2, "FAITH": -1}, "Gosplan gets cotton; the fields get questions."),
               ("Punish the auditors", {"ORDER": 2, "FAITH": -2}, "Two honest men retire to Tashkent's quiet suburbs.")]},
        {"t": "Foreign Debt Sneaks Up",
         "x": "Trade ministry reveals the currency holdings won't cover grain debts.",
         "o": [("Cut military procurement bills", {"MILITARY": -2, "ECONOMY": 2}, "Generals write letters; loans get cheaper."),
               ("Reduce imports of Western tech", {"ECONOMY": -1, "PRESTIGE": -1}, "Industrial espionage fails loudly twice."),
               ("Sell gold reserves", {"ECONOMY": 4, "PRESTIGE": -2}, "Swiss bankers toast 'comarade prudence'.")]},
    ],
    "LATE": [
        {"t": "Glasnost Surges in Print",
         "x": "Magazines publish honest essays. Subscriptions triple and censors riot in their offices.",
         "o": [("Expand glasnost further", {"FAITH": 4, "PRESTIGE": 3, "ORDER": -4}, "The press blooms; the Party chews nails anxiously."),
               ("Cap the magazines at three pages", {"FAITH": -2, "ORDER": 1}, "Readers buy three extra copies for missing pages."),
               ("Redirect topics toward show business", {"FAITH": -1, "PRESTIGE": -1}, "An interview with a pop star displaces three historians.")]},
        {"t": "Nagorno-Karabakh Erupts",
         "x": "Armenian and Azerbaijani crowds collide. Moscow's telegram box burns.",
         "o": [("Send Internal Troops", {"ORDER": 3, "FAITH": -2, "PRESTIGE": -2}, "Tranquillity is achieved, briefly, with barricades."),
               ("Promise autonomy reform", {"FAITH": 1, "ORDER": -1, "PRESTIGE": 1}, "Commissions are founded; salutes are provisional."),
               ("Blame local nationalist elites", {"PRESTIGE": -2, "ORDER": 1}, "Everyone blames somebody; nobody is satisfied.")]},
        {"t": "The Baltic Chain",
         "x": "Two million people form a 600 km human chain across three republics.",
         "o": [("Acknowledge it on television", {"FAITH": 2, "PRESTIGE": 2, "ORDER": -3}, "Anchors describe unity. Somebody whispers 'shows'."),
               ("Disperse the chain with police", {"ORDER": 2, "FAITH": -4, "PRESTIGE": -3}, "Wrist links are broken by baton links."),
               ("Quietly re-examine the Molotov pact", {"PRESTIGE": 3, "ORDER": -2}, "Historians are suddenly extremely popular.")]},
        {"t": "Reform of the Military-Industrial Complex",
         "x": "Defense ministers demand budget; Gosplan demands survival.",
         "o": [("Convert factories to consumer goods", {"ECONOMY": 3, "MILITARY": -2}, "Tractor plants start producing trickle-batteries."),
               ("Defend the MIC budget", {"MILITARY": 2, "ECONOMY": -3}, "The generals applaud; the shops do not."),
               ("Split the difference annually", {"ECONOMY": 1, "MILITARY": -1}, "Committee mathematics strikes again.")]},
        {"t": "Yeltsin on a Truck",
         "x": "Boris Yeltsin addresses crowds from a vehicle roof, fists raised.",
         "o": [("Expel him from the Party", {"ORDER": 2, "FAITH": -3, "PRESTIGE": -2}, "He becomes a martyr with a loud voice."),
               ("Invite him into the leadership", {"FAITH": 2, "ORDER": -2, "PRESTIGE": 1}, "He accepts awkwardly and promises brisk reform."),
               ("Sideline him to a construction trust", {"FAITH": -1, "ORDER": 1}, "He supervises bridges; crowds dream of speeches.")]},
        {"t": "East Germany Strains",
         "x": "Travellers flee via Hungary to Austria. Honecker asks for direction.",
         "o": [("Close the Hungarian border", {"ORDER": 3, "PRESTIGE": -3}, "Barbed wire returns to the pan-European press."),
               ("Admit the Wall is obsolete", {"FAITH": 3, "PRESTIGE": 3, "ORDER": -4}, "Historians collapse; tourists celebrate."),
               ("Blame GDR interior policy", {"PRESTIGE": 1, "ORDER": -2}, "Berlin is left alone with its architected sorrow.")]},
        {"t": "Sugar, Soap and Rumours",
         "x": "Empty shelves publish themselves on national television now.",
         "o": [("Strike-squad distribution by the Army", {"ECONOMY": -2, "FAITH": 2, "MILITARY": -1}, "Soldiers unload bread convoys; applause is real."),
               ("Legalize farmer markets", {"ECONOMY": 3, "FAITH": 3, "ORDER": -2}, "Private stalls bloom in suburban courtyards."),
               ("Promise 1993 prosperity", {"FAITH": -3}, "Referendum results will be delivered later.")]},
        {"t": "Western Theatre of Chips",
         "x": "US sanctions stop computer exports. Factories wait for binary trousers.",
         "o": [("Fund domestic semiconductors", {"ECONOMY": -4, "MILITARY": 2}, "Mikron's pupils squint at imported manuals."),
               ("Smuggle through third countries", {"ECONOMY": -1, "MILITARY": 1, "PRESTIGE": -1}, "Two agents succeed; one walks into an airport lobby."),
               ("Admit the gap publicly", {"PRESTIGE": 1, "FAITH": -2}, "Honesty is refreshing; factories are still idle.")]},
        {"t": "Crimea Wants Autonomy",
         "x": "Crimean Tatars petition en masse to return to their homeland.",
         "o": [("Permit gradual return", {"FAITH": 3, "ORDER": -1, "PRESTIGE": 2}, "Trains roll south; documents are slow."),
               ("Deny the petitions", {"FAITH": -2, "PRESTIGE": -2}, "Protests resume on the Day of Remembrance."),
               ("Grant symbolic autonomy", {"FAITH": 1, "ORDER": 1}, "Banners and brochures, committees quietly famous.")]},
        {"t": "The Caviar Conference",
         "x": "Party congress debates reform while serving sturgeon to 5000 delegates.",
         "o": [("Serve plain bread instead", {"FAITH": 3, "ORDER": -1}, "Delegates chew; delegates think."),
               ("Export the caviar for currency", {"ECONOMY": 2, "FAITH": -1}, "Swiss hotels praise Soviet cuisine."),
               ("Ignore the imagery", {"FAITH": -2, "PRESTIGE": -1}, "A cartoonist wins an international prize.")]},
        {"t": "Armenian Earthquake Relief",
         "x": "Spitak is ruined. The Army arrives with tents and inadequate logistics.",
         "o": [("Accept Western aid openly", {"PRESTIGE": 3, "FAITH": 2}, "American rescuers fly in; props to both flags."),
               ("Rely only on Soviet forces", {"MILITARY": 1, "FAITH": -2}, "Logistics chafe; handwritten notes rescue some."),
               ("Blame local builders", {"FAITH": -3, "PRESTIGE": -1}, "Very few people accept this explanation.")]},
        {"t": "Referendum Fever",
         "x": "Republics ask: 'Renewed federation or independence?'",
         "o": [("Draft a new Union Treaty", {"FAITH": 3, "ORDER": -2, "PRESTIGE": 2}, "Paper glistens with fresh compromise."),
               ("Strengthen federal courts instead", {"ORDER": 2, "FAITH": -2}, "Lawyers become the new national pastime."),
               ("Boycott the referendum", {"ORDER": -3, "FAITH": -1}, "The ballot box finds other employers.")]},
    ],
}


# ---------------------------------------------------------------
# Scripted historical events by year
# ---------------------------------------------------------------
def ev_stalingrad_style(_g: "Kremlin") -> dict:
    return {"t": "Succession of 1982: The Old Guard", "x": "The Politburo convenes. Power is a question of arithmetic.",
            "o": [("Consolidate quietly", {"ORDER": 4, "FAITH": -1}, "The Old Guard applauds with signet rings."),
                  ("Promise renewal, act carefully", {"FAITH": 3, "ORDER": -1, "PRESTIGE": 1}, "A new tone. New names. Same dachas."),
                  ("Offer reforms immediately", {"FAITH": 2, "ORDER": -2, "PRESTIGE": 2}, "The apparatus grumbles in fifteen languages.")]}


def scripted_event(year: int) -> dict | None:
    if year == 1968:
        return {"t": "Prague Spring, 1968",
                "x": "Dubček insists on 'socialism with a human face'. The Politburo faces faces.",
                "o": [("Send tanks in", {"ORDER": 4, "PRESTIGE": -5, "FAITH": -3},
                       "Operation Danube proceeds. The word 'normalization' acquires teeth."),
                      ("Negotiate with Dubček", {"PRESTIGE": 3, "ORDER": -2, "FAITH": 2},
                       "Talks in Czech. Kissinger takes notes; the Party upholsters itself."),
                      ("Pressure him to end reforms", {"ORDER": 1, "PRESTIGE": -1},
                       "Letters and telephone calls accomplish partial awkwardness.")]}
    if year == 1969:
        return {"t": "Ussuri River Border Clashes",
                "x": "Sino-Soviet skirmishes on Damansky Island. Mao recites ancient insults.",
                "o": [("Mass troops at the border", {"MILITARY": 3, "ECONOMY": -3, "PRESTIGE": -1},
                       "Red banners face red banners. Somewhere, a colonel's phone rings."),
                      ("Secret talks in Beijing", {"PRESTIGE": 2, "ORDER": 1},
                       "Two delegations exchange tea and veiled rationales."),
                      ("Broadcast propaganda only", {"FAITH": 1, "PRESTIGE": -1},
                       "Radio Moscow explains the Chinese perfidy in four dialects.")]}
    if year == 1979:
        return {"t": "Afghanistan: The Amin Problem",
                "x": "Herat burns. Taraki is dead. The Politburo holds three midnight sessions.",
                "o": [("Intervene with the 40th Army", {"flags_add": "at_war", "MILITARY": 4, "PRESTIGE": -4, "ECONOMY": -2},
                       "Soviet columns cross the Amu Darya. The mountains are patient."),
                      ("Support the regime with materiel only", {"MILITARY": 1, "PRESTIGE": -1, "ECONOMY": -1},
                       "Mi-24s and advisers cross the border; columns do not."),
                      ("Wash your hands of Kabul", {"PRESTIGE": 1, "ORDER": -1},
                       "Kabul resolves its arithmetic without you. For now.")]}
    if year == 1980:
        return {"t": "Moscow Olympics, 1980",
                "x": "Sixty-five nations boycott. Mascot Mishka still waves from the stadium.",
                "o": [("Stage the grandest Games ever", {"PRESTIGE": 4, "ECONOMY": -3},
                       "The closing bear sheds a tear of expensive nostalgia."),
                      ("Use the Games for diplomacy", {"PRESTIGE": 3, "FAITH": 1, "ORDER": -1},
                       "Athletes mingle; journalists file 900 stories per hour."),
                      ("Frame the boycott as hysterics", {"FAITH": 1, "PRESTIGE": -2},
                       "Radio Moscow regrets Western 'circle-jerking'.")]}
    if year == 1982:
        return ev_stalingrad_style(1982)
    if year == 1983:
        return {"t": "Able Archer 83",
                "x": "NATO's communication drills look alarmingly like launch preparation.",
                "o": [("Issue a firm nuclear warning", {"MILITARY": 2, "PRESTIGE": -3},
                       "TASS publishes names of 'war criminals'. Diplomats drink valium tea."),
                      ("Open a back-channel to Washington", {"PRESTIGE": 3, "MILITARY": -1, "ORDER": 1},
                       "A quiet lunch in Geneva prevents a loud misunderstanding."),
                      ("Trust KR-1 intelligence, raise readiness", {"MILITARY": 3, "PRESTIGE": -2, "ORDER": -1},
                       "Minesweepers sail; silo doors oil their hinges.")]}
    if year == 1985:
        return {"t": "The New General Secretary",
                "x": "Gorbachev's reform team arrives with diagrams of hope and anti-alcohol posters.",
                "o": [("Embrace perestroika fully", {"flags_add": "perestroika", "FAITH": 3, "PRESTIGE": 3, "ORDER": -3},
                       "The word 'acceleration' enters the dictionary with Velcro."),
                      ("Reform slowly, keep the plan", {"ECONOMY": 2, "FAITH": 1, "ORDER": 1},
                       "Pilot zones open in two awkward regions."),
                      ("Defend orthodoxy", {"ORDER": 3, "FAITH": -2, "PRESTIGE": -1},
                       "The Old Guard sighs with cautious relief.")]}
    if year == 1986:
        return {"t": "Chernobyl, 26 April 1986",
                "x": "Reactor Block IV glows with unplanned physics. Kiev gardens prepare for May.",
                "o": [("Admit the disaster immediately", {"FAITH": 2, "PRESTIGE": 3, "ECONOMY": -3},
                       "Radiologists fly in from eleven countries. The truth is expensive and less fatal."),
                      ("Keep it quiet, evacuate quietly", {"flags_add": "chernobyl_hidden", "FAITH": -4, "PRESTIGE": -4},
                       "Kiosks sell kilos of newsprint, none of it mentioning dosimeters."),
                      ("Dismiss as 'not a catastrophe'", {"flags_add": "chernobyl_hidden", "FAITH": -2, "PRESTIGE": -3},
                       "Swedish monitoring stations foam politely.")]}
    if year == 1987:
        return {"t": "Reykjavik Summit",
                "x": "Reagan will not bury SDI. Gorbachev won't bury SDI either. Iceland yawns.",
                "o": [("Hunt for the grand bargain", {"PRESTIGE": 4, "MILITARY": -2},
                       "No deal, but the world watches two leaders talk honestly."),
                      ("Demand SDI scrapped first", {"PRESTIGE": -1, "MILITARY": 1},
                       "Reagan quotes a proverb about negotiation and stubbornness."),
                      ("Propose smaller, verifiable cuts", {"PRESTIGE": 3, "MILITARY": -1},
                       "INF takes its first baby steps in Reykjavik's silence.")]}
    if year == 1989:
        return {"t": "The Berlin Wall Falls",
                "x": "Crowds dance on the Wall. Guards watch, then watch some more.",
                "o": [("Order non-intervention, publicly", {"PRESTIGE": 4, "FAITH": 3, "ORDER": -4},
                       "'Frankfurt is our answer.' The GDR transitions into a museum."),
                      ("Request Warsaw Pact deliberation", {"ORDER": 1, "PRESTIGE": -1, "FAITH": -1},
                       "Statements are composed; hammers arrive unlented."),
                      ("Stay silent entirely", {"PRESTIGE": -2, "FAITH": -1, "ORDER": -2},
                       "Silence translated by both sides as opportunism.")]}
    if year == 1991:
        return {"t": "The August Coup, 1991",
                "x": "The Emergency Committee seizes the studios. Tanks idle at the bridges.",
                "o": [("Defy the coup from the radio", {"special": "coup_defy"},
                       "The nation listens. History holds its breath."),
                      ("Back the Emergency Committee", {"special": "coup_join"},
                       "The studios switch to Swan Lake; your signature appears on the decrees."),
                      ("Remain carefully absent", {"special": "coup_absent"},
                       "You are, officially, resting in a secure dacha.")]}
    return None


# ---------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------
def ask_choice(prompt: str, limit: int, game: Kremlin) -> int:
    """0 = retire, 1..limit = option, EOF = random valid choice."""
    while True:
        try:
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            return game.rng.randint(1, limit)
        raw = raw.strip().lower()
        if raw in {"q", "quit", "retire", "0"}:
            return 0
        try:
            n = int(raw)
        except ValueError:
            print(paint("  ✗ Comrade, that is not on the form.", C.R))
            continue
        if 1 <= n <= limit:
            return n
        print(paint("  ✗ That dossier is off the table. Choose again.", C.R))


def postgame(text: str) -> None:
    print()
    print(paint("═" * 78, C.BB))
    slow(text)
    print(paint("═" * 78, C.BB))
    print()


# ---------------------------------------------------------------
# Display
# ---------------------------------------------------------------
BANNER = r"""
        ★  ☭  ★
   К Р Е М Л Ь
      1 9 9 1
"""


def show_banner() -> None:
    print()
    print(paint(BANNER, C.BM))
    print(paint("  A GENERAL SECRETARY SURVIVAL SIMULATOR", C.BB))
    print(paint("  1964 ────────────── ► 1991", C.DIM))
    print()
    print(paint("  The Politburo awaits your signature, Comrade.", C.W))
    print()


def show_stats(g: Kremlin) -> None:
    print(paint(f"  ━━━━━━━━━━━━━━━━━━ ☭  YEAR {g.year}  ☭ ━━━━━━━━━━━━━━━━━━", C.BB))
    for s in STATS:
        v = g.stats[s]
        col = stat_colour_num(v, STAT_COLOUR[s])
        warn = paint("  ⚠ CRITICAL", C.BM) if v < 25 else ""
        line = f"   {STAT_LABEL[s]:<22} {paint(bar(v), col)} {v:>3}{warn}"
        print(line)
    print()


def show_directives_menu() -> None:
    print(paint("  ── YEARLY DIRECTIVE ───────────────────────────────────────", C.BB))
    for i, (title, desc, _) in enumerate(DIRECTIVES, 1):
        print(f"   {paint(f'{i:>2}', C.BB)}. {paint(title, C.W)}  {paint('· ' + desc, C.DIM)}")
    print(paint("   ( 0. Retire / resign )", C.DIM))
    print()


# ---------------------------------------------------------------
# Main loop pieces
# ---------------------------------------------------------------
def briefing(g: Kremlin) -> None:
    print()
    print(paint(f"  ☭ {g.year} ☭", C.BM))
    line = HISTORY.get(g.year)
    if line:
        slow(paint("  " + line, C.W))


def yearly_drift(g: Kremlin) -> None:
    """Peaceful erosion of the Soviet system."""
    e = g.era()
    base = {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1}
    if e == "LATE":
        base["ECONOMY"] = -3
    for k, v in base.items():
        g.stats[k] = clamp(g.stats[k] + v)
    # Superpower health bonuses ------------------------------------------------
    if g.stats["MILITARY"] >= 80 and g.stats["ECONOMY"] >= 60:
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 1)
    if g.stats["ECONOMY"] >= 65:
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 1)
    if "perestroika" in g.flags and g.stats["ORDER"] >= 40:
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 1)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 1)
    # War attrition ------------------------------------------------------------
    if "at_war" in g.flags:
        g.stats["MILITARY"] = clamp(g.stats["MILITARY"] - 2)
        g.stats["ECONOMY"] = clamp(g.stats["ECONOMY"] - 1)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] - 1)


def apply_event(g: Kremlin, ev: dict) -> str | None:
    """Returns 'quit' if the retire flag fired, otherwise None."""
    print()
    print(paint("  ┌────────────── EVENT ───────────────────┐", C.BB))
    slow(paint("  ☈ " + ev["t"], C.BM))
    slow(paint("  " + ev["x"], C.W))
    print(paint("  └────────────────────────────────────────┘", C.DIM))
    options = ev["o"]
    for i, opt in enumerate(options, 1):
        label = opt[0]
        note = opt[2] if len(opt) > 2 else ""
        print(f"   {paint(f'{i:>2}', C.BB)}. {paint(label, C.W)}")
        if note:
            print(f"       {paint(note, C.DIM)}")
    choice = ask_choice("  ❯ Your decision: ", len(options), g)
    if choice == 0:
        return "quit"
    opt = options[choice - 1]
    specials: dict[str, str] = {}
    deltas: dict[str, int] = {}
    if len(opt) > 1 and isinstance(opt[1], dict):
        for key, val in opt[1].items():
            if key == "flags_add":
                g.flags.add(val)                    # may be a single flag word
            elif key == "special":
                specials[val] = "1"
            elif key in STATS:
                deltas[key] = val
    for k, v in deltas.items():
        g.stats[k] = clamp(g.stats[k] + v)
    for sp in specials:
        handle_special(sp, g)
    return None


def handle_special(s: str, g: Kremlin) -> None:
    if s == "coup_defy":
        need = g.stats["MILITARY"] + g.stats["ORDER"]
        if need >= 110:
            g.stats["FAITH"] = clamp(g.stats["FAITH"] + 6)
            g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 5)
            postgame(paint("  ★ The Committee hesitates. Radio waves carry your voice for three days;\n"
                           "    drunken sailors defect; armoured convoys park and drink tea. THE UNION HOLDS.", C.BG))
            g.flags.add("survived_coup")
        else:
            g.stats["FAITH"] = 0
            g.stats["ORDER"] = 0
            g.death_reason = "The August Coup succeeded. Your voice was one of many, then none."
    elif s == "coup_join":
        g.putschist = True
        g.stats["ORDER"] = clamp(g.stats["ORDER"] + 8)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] - 12)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] - 12)
    elif s == "coup_absent":
        g.stats["ORDER"] = clamp(g.stats["ORDER"] - 4)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] - 4)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] - 3)


# ---------------------------------------------------------------
# Endings
# ---------------------------------------------------------------
DEATH_TEXT = {
    "ECONOMY": "The economy is a rumour. Shop windows professionally empty; the rouble a collector's item.",
    "MILITARY": "The Pentagon smells blood. Bases ring the Union like a slow-motion noose.",
    "ORDER": "Republics declare themselves, one after another. The Kremlin guards polish floors for new tenants.",
    "FAITH": "Mass uprisings everywhere. Crowds carry portraits of nobody at all.",
    "PRESTIGE": "Isolated, sanctioned, parody of itself. The Union's passport earns nothing abroad.",
}


def final_score(g: Kremlin) -> int:
    """Sum of gauges plus 2 survival points per year governed."""
    return sum(g.stats.values()) + 2 * (g.year - 1964)


def ending_collapse(g: Kremlin) -> int:
    score = final_score(g)
    stat = g.dead_stat()
    reason = g.death_reason or DEATH_TEXT.get(stat, "The Union dissolves.")
    postgame(paint(f"  ██ COLLAPSE, {g.year} ██\n  {reason}", C.BM))
    legacy = f"Removed from the portraits in {g.year}"
    avg = score // 2  # collapses lose half their score
    print(paint(f"  Governed years: {g.year - 1964}   Final gauges →  {g.stats}", C.W))
    print(paint(f"  Legacy score: {avg} — {legacy}", C.BB))
    record_hall(g.name, avg, legacy, collapsed=True)
    return avg


def ending_retire(g: Kremlin) -> int:
    score = final_score(g)
    postgame(paint("  ★ You resigned and retired to a comfortable dacha.", C.Y))
    legacy = legacy_title(score)
    print(paint(f"  Governed years: {g.year - 1964}   Final gauges →  {g.stats}", C.W))
    print(paint(f"  Legacy score: {score} — {legacy}", C.BB))
    record_hall(g.name, score, legacy)
    return score


def ending_union_survives(g: Kremlin) -> int:
    score = final_score(g)
    text = ("  ██ THE UNION SURVIVES ██\n"
            "  December 26, 1991: the flag over the Kremlin remains red.\n"
            "  Historians argue whether it was your cunning, luck, or the weather.")
    if "survived_coup" in g.flags:
        text += "\n  The August Coup is remembered as your finest hour."
    elif g.putschist:
        text += "\n  The Emergency Committee, which you quietly directed, is remembered\n  differently: in whispered tones, in courtrooms."
    if "perestroika" in g.flags:
        text += "\n  Years later, 'perestroika' is taught as the word that saved the century —\n  or speeds its multiplication into paperwork."
    postgame(paint(text, C.BG))
    legacy = legacy_title(score)
    print(paint(f"  Governed years: 27   Final gauges →  {g.stats}", C.W))
    print(paint(f"  Legacy score: {score} — {legacy}", C.BB))
    record_hall(g.name, score, legacy)
    return score


def legacy_title(score: int) -> str:
    if score >= 450:
        return "GENERALISSIMUS OF HISTORY ★"
    if score >= 380:
        return "Hero of Socialist Labour (twice)"
    if score >= 300:
        return "A steady hand — the Union endures"
    if score >= 220:
        return "Survivor of queues and committees"
    return "Footnote in an unpublished archive"


def record_hall(name: str, score: int, title: str, collapsed: bool = False) -> None:
    try:
        stamp = datetime.date.today().isoformat()
        tag = "COLLAPSED" if collapsed else "SURVIVED"
        with open(HALL_FILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} | {name} | {tag} | score {score:3d} | {title}\n")
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
    print(paint(" ═══ HALL OF FAME (last records) ═══", C.Y))
    for ln in lines[-5:]:
        print("   " + paint(ln, C.DIM))
    print()


# ---------------------------------------------------------------
# Setup: name and difficulty
# ---------------------------------------------------------------
DIFFICULTIES = [
    ("Appointed by the Old Guard",
     "Order +6, Faith −4, Economy +2. Stalinesque paperwork welcomes you.",
     {"ORDER": 6, "FAITH": -4, "ECONOMY": 2}),
    ("Balanced committee choice",
     "A quiet vote. The dacha stays as it is.",
     {}),
    ("Dark-horse reformer",
     "Faith +6, Prestige +4, Order −8. The Old Guard sharpens its teeth.",
     {"FAITH": 6, "PRESTIGE": 4, "ORDER": -8}),
]


def introduction(g: Kremlin) -> int:
    show_banner()
    show_hall_top()
    print(paint("  Before the year begins, the Politburo asks two questions.", C.W))
    print()
    try:
        name = input("  Your name for the history books: ").strip()
    except (EOFError, KeyboardInterrupt):
        name = ""
    g.name = name or "Comrade Secretary"
    print()
    for i, (title, desc, _) in enumerate(DIFFICULTIES, 1):
        print(f"   {paint(f'{i}', C.BB)}. {paint(title, C.W)}")
        print(f"      {paint(desc, C.DIM)}")
    d = ask_choice("  ❯ Your mandate: ", len(DIFFICULTIES), g)
    if d == 0:
        return 0
    _, _, eff = DIFFICULTIES[d - 1]
    g.delta(**eff)
    print()
    slow(paint(f"  ☭ Welcome, {g.name}. The Union is yours. Try not to lose it.", C.BG))
    print()
    slow(paint("  HOW TO PLAY: each year, pick ONE directive and answer ONE event.", C.W))
    slow(paint("  Keep all five gauges above zero until 1991. 'q' quits any menu.", C.W))
    print()
    return d


# ---------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------
def main() -> None:
    global DRAMA
    args = sys.argv[1:]
    seed: int | None = None
    if "--drama" in args:
        DRAMA = True
    if "-seed" in args:
        i = args.index("-seed")
        try:
            seed = int(args[i + 1])
        except (IndexError, ValueError):
            seed = None
    if "--seed" in args:
        i = args.index("--seed")
        try:
            seed = int(args[i + 1])
        except (IndexError, ValueError):
            seed = None

    g = Kremlin(seed)
    d = introduction(g)
    if d == 0:
        print(paint("  You declined the appointment. History notices briefly.", C.Y))
        return

    while g.year <= g.end_year:
        if g.dead_stat():
            ending_collapse(g)
            return
        briefing(g)
        show_stats(g)
        show_directives_menu()
        dr = ask_choice("  ❯ Directive of the year: ", len(DIRECTIVES), g)
        if dr == 0:
            ending_retire(g)
            return
        title, _desc, deltas = DIRECTIVES[dr - 1]
        # Directive effect sometimes overshoots/undershoots slightly (weather, mood)
        wob = g.rng.randint(-1, 1)
        g.delta(**{k: v + (wob if k == "ECONOMY" else 0) for k, v in deltas.items()})
        slow(paint(f"  ▸ Directive issued: {title}", C.G))

        # One event per year: scripted first, else random from era pool
        ev = scripted_event(g.year)
        if ev is None:
            pool = g.forced_event_list(g.era())
            ev = pool[g.rng.randrange(len(pool))]
        res = apply_event(g, ev)
        if res == "quit":
            ending_retire(g)
            return

        # Special scripted 1991 coup check: if death triggered there, end now
        if g.year == 1991:
            if g.dead_stat():
                ending_collapse(g)
                return
            ending_union_survives(g)
            return

        yearly_drift(g)
        g.year += 1

    # Shouldn't reach here, but just in case:
    ending_union_survives(g)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
