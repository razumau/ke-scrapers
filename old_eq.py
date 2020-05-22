from itertools import takewhile
from pprint import pprint
from typing import List
from string import ascii_uppercase

from utils import EQGame, EQGameTeamResult

old_eq_stages = ["Предварительный этап", "Полуфинал", "Финал"]


class Letters:
    def __init__(self):
        self.letters = ascii_uppercase
        self.pos = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.pos += 1
        return self.letters[self.pos]


def read_2005() -> List[EQGame]:
    game = stage = old_eq_stages[-1]
    teams = [
        EQGameTeamResult(stage, game, "Дальше некуда", 1),
        EQGameTeamResult(stage, game, "Бандерлоги", 2),
        EQGameTeamResult(stage, game, "Absent", 3),
        EQGameTeamResult(stage, game, "Солнышко", 4),
    ]
    return [EQGame(stage, game, teams)]


def read_single_game(stage: str, name: str, lines: List[str]) -> EQGame:
    game = EQGame(stage, name, [])

    for index, line in enumerate(lines):
        line_split = line.strip("\n").split("\t")
        team_name = line_split[0]
        if len(line_split) == 6:
            shootout = int(line_split[-1])
            points = int(line_split[-3])
        else:
            shootout = 0
            points = int(line_split[-1])

        game.teams.append(
            EQGameTeamResult(
                stage,
                name,
                team_name,
                place=index + 1,
                points=points,
                shootout=shootout,
            )
        )

    return game


def read_old_year(year: int) -> List[EQGame]:
    letters = Letters()

    with open(f"./txt/{year}/eq.txt") as year_file:
        lines = year_file.readlines()[2:]

    prelim_lines = list(takewhile(lambda l: not l.startswith("Полуфинал"), lines))
    prelims = []
    current_lines = []

    read_single_game(old_eq_stages[-1], old_eq_stages[-1], lines[-6:-2])

    for line in prelim_lines:
        if line.strip():
            current_lines.append(line)
            continue
        if current_lines:
            prelims.append(
                read_single_game(old_eq_stages[0], next(letters), current_lines)
            )
            current_lines = []

    semis_line = len(prelim_lines) + 1
    playoffs = [
        read_single_game(
            old_eq_stages[1], next(letters), lines[semis_line : semis_line + 4]
        ),
        read_single_game(
            old_eq_stages[1], next(letters), lines[semis_line + 5 : semis_line + 9]
        ),
        read_single_game(old_eq_stages[-1], old_eq_stages[-1], lines[-6:-2]),
    ]

    return prelims + playoffs


def load_old_eq_results():
    old_years = range(2006, 2017)
    newer = {year: read_old_year(year) for year in old_years}
    return {2005: read_2005(), **newer}


if __name__ == "__main__":
    year = 2014
    results = load_old_eq_results()
    pprint(results)
