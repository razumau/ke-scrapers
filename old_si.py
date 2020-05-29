from itertools import tee, groupby
from pprint import pprint
from typing import Iterable, List

from utils import SIPlayer, SIGame, flatten

old_si_stages = [
    "Квалификационный этап",
    "1/27 финала",
    "1/9 финала",
    "1/3 финала",
    "Финал",
]


def load_si_results(year: int):
    with open(f"./txt/{year}/si.txt") as year_file:
        lines = year_file.readlines()
    all_rows = lines[:-2]
    split = split_into_stages(all_rows)
    games = [split_into_games(stage.strip(), rows) for stage, rows in split.items()]
    final = split_into_games("Финал", all_rows[-3:])
    return [*flatten(games), *final]


def pairwise(iterable: Iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def split_into_stages(rows):
    indices = [
        i
        for stage in old_si_stages
        for i, row in enumerate(rows)
        if row.startswith(stage)
    ]

    return {rows[i]: rows[i + 1 : j] for i, j in pairwise(indices)}


def split_into_games(stage_name: str, rows: List):
    stage_results = []
    name = rows[0]
    player_place = 0
    starting_index = 1
    if not name or not name.startswith("Бой"):
        game_number = 1
        starting_index = 0
        local_name = f"{stage_name} — бой {game_number}"
        name = None

    for row in rows[starting_index:]:
        if row.startswith("Бой "):
            name = row
            player_place = 0
            continue

        if (not row or row == "\n") and not name:
            game_number += 1
            player_place = 0
            local_name = f"{stage_name} — бой {game_number}"
            continue

        if not row or row == "\n":
            continue

        si_player = process_score_row(row)
        player_place += 1
        si_player.place = player_place
        stage_results.append((stage_name, name or local_name, si_player))

    data = sorted(stage_results, key=lambda r: r[1])
    groups = [list(g) for _, g in groupby(data, lambda r: r[1])]
    games = [
        SIGame(
            stage_name=group[0][0].strip(),
            game_name=group[0][1].strip(),
            players=[g[2] for g in group],
        )
        for group in groups
    ]
    return games


def process_score_row(row_str) -> SIPlayer:
    row = [r for r in row_str.split("\t") if r != " "]
    player, team = row[0], row[1]
    points = None if not row[2:] or row[2].startswith('?') else int(row[2])
    split = team.split("(")
    shootout = None if not row[3:] else sum(int(r) for r in row[3:])
    return SIPlayer(
        team=split[0][:-1],
        city=None if not split[1:] else split[1][:-1],
        first_name=player.split(" ")[1],
        last_name=player.split(" ")[0],
        points=points,
        shootout=shootout,
    )


def load_old_si_results():
    return {year: load_si_results(year) for year in range(2005, 2017)}


if __name__ == "__main__":
    year = 2005
    pprint(load_si_results(2005))
    # for year in range(2005, 2016):
    #     res = load_si_results(year)
    #     pprint(res)
