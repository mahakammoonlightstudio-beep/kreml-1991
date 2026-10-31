"""All game events: the catalogue index.

Content lives in era modules, so a single event is easy to find:

  events_early.py   1964-1975          events_late.py    1985-1991
  events_middle.py  1976-1984          events_new.py     1992-2001
  events_fixed.py   scripted years, congresses and queued consequences
  events_v6.py      flash crises and the political additions
  chains.py         the five chain reactions
  forks.py          the three divergence forks

This module only assembles them and declares WHEN they may appear:

  1. RANDOM_POOLS  — era-flavoured, drawn each unscripted year
  2. SCRIPTED      — pinned to a specific historical year
  3. QUEUED        — triggered by earlier choices' "queue" ops
"""
from __future__ import annotations

from .chains import CHAIN_EVENTS, EXTRA_EVENTS
from .events_early import EVENTS_EARLY
from .events_fixed import EVENTS_FIXED
from .events_late import EVENTS_LATE
from .events_middle import EVENTS_MIDDLE
from .events_new import EVENTS_NEW
from .events_v6 import V6_EVENTS, V6_POOL_ADDITIONS
from .forks import FORK_EVENTS, FORKS

EVENTS: dict[str, object] = {}
for _group in (EVENTS_EARLY, EVENTS_MIDDLE, EVENTS_LATE, EVENTS_NEW,
               EVENTS_FIXED, EXTRA_EVENTS, CHAIN_EVENTS, FORK_EVENTS,
               V6_EVENTS):
    EVENTS.update(_group)

RANDOM_POOLS: dict[str, tuple[str, ...]] = {'EARLY': ('vodka_shortage',
           'samizdat',
           'kosygin_memo',
           'n1_explodes',
           'jazz_shortwave',
           'kuzbass_strike',
           'virgin_lands',
           'cuban_sugar',
           'prague_airwaves',
           'golden_orlov',
           'vienna_defection',
           'phantom_growth',
           'china_overture',
           'de_gaulle',
           'cairo_arms',
           'cosmonaut_letter',
           'baikal_pulp',
           'gagarin_crash'),
 'MIDDLE': ('solidarnosc',
            'grain_scandal',
            'andropov_dossiers',
            'war_scares',
            'black_market_boom',
            'oil_shock',
            'poland_health',
            'worker_letter',
            'athletes_defect',
            'brezhnev_orders',
            'uzbek_cotton',
            'foreign_debt',
            'yugo_study',
            'afghan_trap',
            'pipeline_sabotage',
            'helsinki_accords',
            'vatican_signal',
            'grain_bill',
            'vietnam_peace',
            'sakharov_nobel',
            'polish_pope',
            'grain_embargo',
            'petrov_1983'),
 'LATE': ('glasnost_press',
          'karabakh',
          'baltic_chain',
          'mic_reform',
          'yeltsin_truck',
          'berlin_strains',
          'market_queues',
          'chip_embargo',
          'crimea_return',
          'caviar_conference',
          'spitak_quake',
          'referendum_fever',
          'coops_press',
          'mr_archives',
          'vodka_campaign',
          'nomenklatura_rift',
          'singapore_dream',
          'name_duel',
          'cassette_wave',
          'malta_summit',
          'alma_ata_1991'),
 'NEW': ('oligarch_weekend',
         'brain_gain',
         'siberia_2',
         'network_age',
         'church_revival',
         'arctic_route',
         'wild_east_jobs',
         'ruble_crash_1994',
         'default_1998',
         'kursk_2000',
         'mir_2001')}

# v6 additions are appended, never rewritten, so the v5 draw probabilities hold.
for _era, _ids in V6_POOL_ADDITIONS.items():
    RANDOM_POOLS[_era] = RANDOM_POOLS[_era] + tuple(_ids)

# Congress years: the congress event replaces the regular random event.
CONGRESS_YEARS: dict[int, str] = {1970: 'plenum_1970',
 1978: 'blueprint_1978',
 1986: 'acceleration_1986',
 1996: 'millennium_congress'}

# Historical crises pinned to their years.
SCRIPTED: dict[int, tuple[str, ...]] = {1968: ('prague_spring',),
 1969: ('ussuri_clashes',),
 1979: ('afghanistan_1979',),
 1980: ('olympics_1980',),
 1982: ('succession_1982',),
 1983: ('able_archer',),
 1985: ('new_secretary',),
 1986: ('chernobyl',),
 1987: ('reykjavik',),
 1989: ('wall_falls', 'coal_miners_1989'),
 1991: ('august_coup',),
 1992: ('rouble_zone',),
 1993: ('union_charter',),
 1997: ('asian_flu_1997',),
 1999: ('nato_east_1999',),
 2000: ('millennium_message',)}

FORKS = FORKS
