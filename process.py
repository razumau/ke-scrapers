from collections import Counter
from itertools import groupby
from typing import List, Tuple, Iterable, Set

from renames import country_for_team, rename_team, rename_city
from utils import Team, Player


def build_base_teams(teams: Iterable[Team]) -> List[Tuple]:
    data = sorted(teams, key=lambda t: t.id)
    groups = [list(g) for _, g in groupby(data, lambda t: t.id)]
    name_counters = {
        g[0].id: Counter([t.name for t in g]).most_common(1)[0][0] for g in groups
    }
    city_counters = {
        g[0].id: Counter([t.city for t in g]).most_common(1)[0][0] for g in groups
    }

    return [
        (
            g[0].id,
            rename_team(name_counters[g[0].id]),
            rename_city(city_counters[g[0].id]),
            country_for_team(g[0]),
        )
        for g in groups
    ]


def unique_players(players: Iterable[Player]) -> Set[Tuple]:
    return {(p.first_name, p.middle_name, p.last_name, p.id) for p in players}
