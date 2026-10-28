"""The world market & the Politburo's court weather: pure data.

Two v4 systems are driven from here:

  1. OIL MARKET  — a yearly crude price index (0-100). While the Union exports
     oil & gas, the index sets how much hard currency (valas) the year brings.
     Historically shaped: the 1973 embargo boom, the 1980 peak, the 1986
     collapse, the late-1990s trough and the 2000s recovery.
  2. COURT DRIFT — per-era baseline mood drift for the three Kremlin factions
     (old_guard / reformers / military). Content may shift moods further with
     the "court" op key; the engine checks each year whether a faction is
     despairing enough to book the velvet conference room.
"""

# Nominal oil price index by year (0-100). Missing years fall back to 40.
OIL_YEARS: dict[int, int] = {
    1964: 42, 1965: 42, 1966: 43, 1967: 44, 1968: 44,
    1969: 45, 1970: 45, 1971: 44, 1972: 46,
    1973: 62, 1974: 76, 1975: 70,                  # the OPEC embargo boom
    1976: 66, 1977: 64, 1978: 61,
    1979: 70, 1980: 85,                            # the Iranian peak
    1981: 80, 1982: 73, 1983: 68, 1984: 65, 1985: 60,
    1986: 25, 1987: 28, 1988: 30, 1989: 32, 1990: 34,   # the great glut
    1991: 32,
    1992: 36, 1993: 34, 1994: 35, 1995: 40, 1996: 42,   # a soft recovery
    1997: 38, 1998: 24,                          # the Asian-financial trough
    1999: 41, 2000: 58, 2001: 52,                # the new millennium recovery
}

DEFAULT_OIL = 40


def oil_price(year: int) -> int:
    return OIL_YEARS.get(year, DEFAULT_OIL)


def oil_status(year: int) -> str:
    """A one-word read of the market for the stats panel."""
    p = oil_price(year)
    if p >= 70:
        return "BOOM"
    if p >= 45:
        return "STEADY"
    if p <= 30:
        return "GLUT"
    return "SOFT"


# ---------------------------------------------------------------
# Court (faction moods)
# ---------------------------------------------------------------
# Per-era baseline drift. The moods regress a little toward 50 every year
# (the engine adds ambient noise), and era drift pushes the political weather:
#   EARLY  — ossification: the Old Guard thickens, reformers starve.
#   MIDDLE — gerontocracy: everyone drifts apart, the army grumbles quietly.
#   LATE   — perestroika tension: reformers rise, the Old Guard panics,
#            the army loses budget arguments.
#   NEW    — the survival era: reformers empowered, the Old Guard evaporates,
#            the general staff re-finds its pride.
COURT_DRIFT: dict[str, dict[str, int]] = {
    "EARLY":  {"old_guard": +1, "reformers": -1, "military": 0},
    "MIDDLE": {"old_guard": +1, "reformers": -1, "military": -1},
    "LATE":   {"old_guard": -1, "reformers": +1, "military": -1},
    "NEW":    {"old_guard": -1, "reformers": +1, "military": +1},
}

# A faction whose mood drops to this level starts booking rooms.
COUP_THRESHOLD = 15

# Mood above this counts as enthusiastic (small yearly blessing).
LOVE_THRESHOLD = 80
