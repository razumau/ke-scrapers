from typing import Tuple, List
from itertools import takewhile
import re

from old_br import is_junk_line
from utils import BRGame, BRGroupTeamResult, flatten

new_br_stages = [
    "Предварительный этап",
    "Топ-16",
    "Топ-8",
    "Полуфинал",
    "Бой за третье место",
    "Финал",
]

new_years = list(range(2017, 2020))
game_format = re.compile(r"[\d]+:[\d]+")


def check_group_is_mirrored(games: List[List[str]]):
    for sum_ in range(6):
        for i in range(sum_):
            j = sum_ - i
            if i >= 4 or j >= 4:
                continue
            assert games[i][j][::-1] == games[j][i]


def read_group(lines: List[str], stage: str) -> Tuple:
    group_name = lines[0][7]
    raw_games: List[Tuple[str, List[str]]] = []
    team_results = {}
    order = [i - 1 for i in map(int, lines[1].split()[1:5])]

    for team_num, line in enumerate(lines[2:]):
        vals = line.split()
        team_games = [v for v in vals if game_format.fullmatch(v) or v == "×"]
        team_name = " ".join(takewhile(lambda v: v not in team_games, vals[1:]))
        place = float(vals[-1])
        raw_games.append((team_name, team_games))
        team_results[team_name] = BRGroupTeamResult(
            stage_name=stage, group_name=group_name, team_name=team_name, place=place
        )

    games: List[BRGame] = []

    # check_group_is_mirrored([rg[1] for rg in raw_games])

    for team, team_games in raw_games:
        for index, game in enumerate(team_games):
            if game == "×":
                break

            first, second = map(int, game.split(":"))
            second_team = raw_games[order[index]][0]

            games.append(
                BRGame(
                    stage_name=stage,
                    team_one=team,
                    team_two=second_team,
                    team_one_points=first,
                    team_two_points=second,
                )
            )

            update_team_result(team_results[team], first, second)
            update_team_result(team_results[second_team], second, first)

    assert len(games) == 6
    assert len(team_results.values()) == 4
    return games, list(team_results.values())


def update_team_result(tr: BRGroupTeamResult, first: int, second: int):
    tr.plus += first
    tr.minus += second
    if first > second:
        tr.points += 3
        tr.wins += 1
    elif first < second:
        if first > 0:
            tr.points += 1
        tr.losses += 1
    else:
        if first > 0:
            tr.points += 2
        tr.draws += 1


def read_game(lines: List[str], stage) -> BRGame:
    first_name, first_score = lines[0].split("\t")
    second_name, second_score = lines[1].split("\t")
    return BRGame(
        stage_name=stage,
        team_one=first_name,
        team_two=second_name,
        team_one_points=int(first_score),
        team_two_points=int(second_score),
    )


def read_final(lines: List[str]) -> List[BRGame]:
    first_name, first_scores_str = lines[0].split("\t")
    first_scores = first_scores_str.split()
    second_name, second_scores_str = lines[1].split("\t")
    second_scores = second_scores_str.split()
    return [
        read_game(
            [f"{first_name}\t{first_scores[i]}", f"{second_name}\t{second_scores[i]}"],
            new_br_stages[-1],
        )
        for i in range(len(first_scores))
    ]


def read_year(year: int) -> Tuple[List[BRGroupTeamResult], List[BRGame]]:
    with open(f"./txt/{year}/br.txt") as year_file:
        lines = [line for line in year_file.readlines() if not is_junk_line(line)]

    first_stage_first_lines = [6 * i + 1 for i in range(8)]
    first_stage = [
        read_group(lines[first : first + 6], new_br_stages[0])
        for first in first_stage_first_lines
    ]

    second_stage_first_lines = [6 * i + 50 for i in range(4)]
    second_stage = [
        read_group(lines[first : first + 6], new_br_stages[1])
        for first in second_stage_first_lines
    ]

    third_stage_first_lines = [75, 81]
    third_stage = [
        read_group(lines[first : first + 6], new_br_stages[2])
        for first in third_stage_first_lines
    ]

    playoffs = [
        read_game(lines[88:90], new_br_stages[3]),
        read_game(lines[91:93], new_br_stages[3]),
        read_game(lines[94:96], new_br_stages[4]),
        *read_final(lines[97:]),
    ]

    games = (
        flatten(
            [
                group[0]
                for stage in (first_stage, second_stage, third_stage)
                for group in stage
            ]
        )
        + playoffs
    )

    team_results = flatten(
        [
            group[1]
            for stage in (first_stage, second_stage, third_stage)
            for group in stage
        ]
    )

    return team_results, games


def load_new_br_results():
    return {year: read_year(year) for year in new_years}
