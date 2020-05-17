from pprint import pprint
from typing import Tuple, List
from itertools import takewhile
import re
from utils import BRGame, BRGroupTeamResult, flatten


br_stages_2005 = [
    "Предварительный этап",
    "Второй этап",
    "Топ-8",
    "Бой за третье место",
    "Финал",
]
old_br_stages = [
    "Предварительный этап",
    "Топ-8",
    "Полуфинал",
    "Бой за третье место",
    "Финал",
]

old_years = list(range(2006, 2017))
game_format = re.compile(r"[\d]+:[\d]+")


def process_games_row(row, team, all_games, stage):
    yield from (
        BRGame(
            stage_name=stage,
            team_one=team,
            team_two=all_games[second_team_index][0],
            team_one_points=int(game.split(":")[0]),
            team_two_points=int(game.split(":")[1]),
        )
        for second_team_index, game in enumerate(
            takewhile(lambda x: game_format.fullmatch(x), row)
        )
    )


def read_single_game(line: str, stage: str) -> BRGame:
    first, second, game = line.split(" - ")
    team_one = first.split("(")[0].strip()
    team_two = second.split("(")[0].strip()
    if "," in game:
        main_str, shootout_str = game.split(",")
        team_one_points = int(main_str.split(":")[0])
        team_two_points = int(main_str.split(":")[1])
        if "1:0" in shootout_str:
            team_one_shootout, team_two_shootout = 1, 0
        elif "0:1" in shootout_str:
            team_one_shootout, team_two_shootout = 0, 1
        else:
            raise ValueError(f"Weird: {line}")

    else:
        team_one_points = int(game.split(":")[0])
        team_two_points = int(game.split(":")[1])
        team_one_shootout, team_two_shootout = None, None

    return BRGame(
        stage_name=stage,
        team_one=team_one,
        team_two=team_two,
        team_one_points=team_one_points,
        team_two_points=team_two_points,
        team_one_shootout_points=team_one_shootout,
        team_two_shootout_points=team_two_shootout,
    )


def read_final(line) -> List[BRGame]:
    first, second, game = line.split(" - ")
    delimiter = ";" if ";" in game else ","
    subgames = game.split(delimiter)
    return [
        read_single_game(f"{first} - {second} - {subgame}", old_br_stages[4])
        for subgame in subgames
    ]


def read_group(lines: List, stage: str) -> Tuple[List[BRGame], List[BRGroupTeamResult]]:
    if not lines[0].startswith("Группа"):
        pprint(lines[0])
        raise ValueError

    group_name = lines[0].upper().strip("ГРУППА").replace('"', "").strip()
    assert len(group_name) == 1
    teams_count = len(lines[2:])
    team_results = []
    games = []
    for team_num, line in enumerate(lines[2:]):
        vals = list(reversed(line.split()))
        team_name = " ".join(reversed(vals[7 + teams_count :]))
        games.append((team_name, vals[5 + teams_count : 5 : -1]))
        try:
            vals[2].split("-")[0]
        except IndexError:
            pprint(vals)
            raise
        tr = BRGroupTeamResult(
            stage_name=stage,
            group_name=group_name,
            team_name=team_name,
            place=vals[0],
            points=vals[1],
            plus=vals[2].split("-")[0],
            minus=vals[2].split("-")[1],
            losses=vals[3],
            draws=vals[4],
            wins=vals[5],
        )
        team_results.append(tr)

    parsed_games = [
        game
        for team, row in games
        for game in process_games_row(row, team, games, stage)
    ]

    try:
        assert len(parsed_games) == teams_count * (teams_count - 1) / 2
    except AssertionError:
        pprint(parsed_games)
        raise
    return parsed_games, team_results


def is_junk_line(line: str):
    if line.strip() == "":
        return True
    if line == "\n":
        return True
    if "Кубок Европы" in line:
        return True
    if line.startswith("На главную страницу"):
        return True
    return False


def read_old_year(year: int) -> Tuple[List[BRGroupTeamResult], List[BRGame]]:
    with open(f"./txt/{year}/br.txt") as year_file:
        lines = [l for l in year_file.readlines() if not is_junk_line(l)]

    if year == 2009:
        group_lengths = [5, 5, 6, 6]
    elif year == 2006:
        group_lengths = [6, 7, 7, 7]
    else:
        group_lengths = [6, 6, 6, 6]

    prelims = []
    last_line = 1
    for gl in group_lengths:
        prelims.append(
            read_group(lines[last_line : last_line + gl + 2], old_br_stages[0])
        )
        last_line = last_line + gl + 2

    last_line += 1
    second_stage = (
        read_group(lines[last_line : last_line + 6], old_br_stages[1]),
        read_group(lines[last_line + 6 : last_line + 12], old_br_stages[1]),
    )

    last_line += 13
    if year > 2006:
        playoffs = [
            read_single_game(lines[last_line], old_br_stages[2]),
            read_single_game(lines[last_line + 1], old_br_stages[2]),
            read_single_game(lines[last_line + 3], old_br_stages[3]),
            read_final(lines[last_line + 5]),
        ]
    else:
        playoffs = [
            read_single_game(lines[last_line], old_br_stages[3]),
            read_final(lines[last_line + 2]),
        ]

    groups = [p[1] for p in prelims] + [p[1] for p in second_stage]
    group_games = flatten([p[0] for p in prelims] + [p[0] for p in second_stage])
    games = group_games + playoffs[:-1] + playoffs[-1]
    return flatten(groups), games


def read_2005() -> Tuple[List[BRGroupTeamResult], List[BRGame]]:
    with open(f"./txt/2005/br.txt") as year_file:
        lines = [line for line in year_file.readlines() if not is_junk_line(line)]

    group_lengths = [4, 4, 4, 4, 4, 4]

    prelims = []
    last_line = 1
    for gl in group_lengths:
        prelims.append(
            read_group(lines[last_line : last_line + gl + 2], br_stages_2005[0])
        )
        last_line = last_line + gl + 2

    last_line += 1
    second_stage = (
        read_group(lines[last_line : last_line + 5], br_stages_2005[1]),
        read_group(lines[last_line + 5 : last_line + 10], br_stages_2005[1]),
    )

    last_line += 11
    top_eight = (
        read_group(lines[last_line : last_line + 6], br_stages_2005[2]),
        read_group(lines[last_line + 6 : last_line + 12], br_stages_2005[2]),
    )

    last_line += 13
    playoffs = [
        read_single_game(lines[last_line], old_br_stages[3]),
        read_final(lines[last_line + 2]),
    ]

    groups = (
        [p[1] for p in prelims]
        + [p[1] for p in second_stage]
        + [p[1] for p in top_eight]
    )
    group_games = flatten(
        [p[0] for p in prelims]
        + [p[0] for p in second_stage]
        + [p[0] for p in top_eight]
    )
    games = group_games + playoffs[:-1] + playoffs[-1]
    return flatten(groups), games


def load_old_br_results():
    newer = {year: read_old_year(year) for year in old_years}
    return {2005: read_2005(), **newer}


if __name__ == '__main__':
    results = load_old_br_results()
    print(results)