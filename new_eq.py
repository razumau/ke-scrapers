from pprint import pprint
from typing import List
from string import ascii_uppercase

from utils import EQGame, EQGameTeamResult

eq_stages_2017 = ["1/8 финала", "1/4 финала", "Полуфинал", "Финал"]
eq_stages = ["Первый бой", "Второй бой", "1/4 финала", "Полуфинал", "Финал"]


class Letters:
    def __init__(self):
        self.letters = ascii_uppercase
        self.pos = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.pos += 1
        return self.letters[self.pos]


def read_single_game(
    stage: str, name: str, lines: List[str], shootout_col=False, first_col=True
) -> EQGame:

    game = EQGame(stage, name, [])

    for line in lines:
        line_split = line.strip("\n").split("\t")
        if first_col:
            team_name = line_split[1]
        else:
            team_name = line_split[0]

        place = float(line_split[-1])

        if shootout_col:
            points = int(line_split[-4])
            shootout = int(line_split[-3])
        elif "(" in line_split[-2]:
            points_str, shootout_str = line_split[-2].split("(")
            points = int(points_str)
            shootout = int(shootout_str[:-1])
        else:
            shootout = 0
            points = int(line_split[-2])

        game.teams.append(
            EQGameTeamResult(
                stage, name, team_name, place=place, points=points, shootout=shootout,
            )
        )

    return game


def read_2017() -> List[EQGame]:
    letters = Letters()

    with open(f"./txt/2017/eq.txt") as year_file:
        lines = year_file.readlines()

    eighth_games = [
        read_single_game(
            eq_stages_2017[0],
            next(letters),
            lines[7 * k + 3 : 7 * k + 7],
            first_col=False,
        )
        for k in range(8)
    ]

    quarters = [
        read_single_game(
            eq_stages_2017[1], next(letters), lines[7 * k + 60 : 7 * k + 64]
        )
        for k in range(4)
    ]
    semis = [
        read_single_game(
            eq_stages_2017[2], next(letters), lines[7 * k + 89 : 7 * k + 93]
        )
        for k in range(2)
    ]
    finals = [read_single_game(eq_stages_2017[3], next(letters), lines[102:106])]
    return eighth_games + quarters + semis + finals


def read_year(year: int) -> List[EQGame]:
    letters = Letters()

    with open(f"./txt/{year}/eq.txt") as year_file:
        lines = year_file.readlines()

    first = [
        read_single_game(
            eq_stages[0], next(letters), lines[7 * k + 3 : 7 * k + 7], first_col=False,
        )
        for k in range(8)
    ]

    second = [
        read_single_game(eq_stages[1], next(letters), lines[7 * k + 60 : 7 * k + 64])
        for k in range(8)
    ]

    quarters = [
        read_single_game(
            eq_stages[2],
            next(letters),
            lines[7 * k + 117 : 7 * k + 121],
            shootout_col=True,
        )
        for k in range(4)
    ]
    semis = [
        read_single_game(
            eq_stages[3],
            next(letters),
            lines[7 * k + 146 : 7 * k + 150],
            shootout_col=True,
        )
        for k in range(2)
    ]
    finals = [
        read_single_game(eq_stages[4], next(letters), lines[159:163], first_col=False)
    ]
    return first + second + quarters + semis + finals


def load_new_eq_results():
    new_years = [2018, 2019]
    newer = {year: read_year(year) for year in new_years}
    return {2017: read_2017(), **newer}


if __name__ == "__main__":
    results = load_new_eq_results()
    pprint(results)
