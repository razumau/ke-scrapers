from pprint import pprint
from typing import List

from utils import SIGame, SIPlayer

new_si_stages = ["1/16 финала", "1/8 финала", "1/4 финала", "1/2 финала", "Финал"]


class Numbers:
    def __init__(self):
        self.numbers = list(range(1, 100))
        self.pos = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.pos += 1
        return f"Бой {self.numbers[self.pos]}"


def read_single_game(stage: str, name: str, lines: List[str], place_col) -> SIGame:
    game = SIGame(stage, name, [])

    for line in lines:
        line_split = line.strip("\n").split("\t")

        place = float(line_split[place_col])

        if place_col == 3:
            first_name, last_name = line_split[1].split(" ")
            points_str = line_split[2]
            if "(" in points_str:
                points = int(points_str.split("(")[0])
                shootout = int(points_str.split("(")[1][:-1])
            else:
                points = int(points_str)
                shootout = None

        elif place_col == 1:
            first_name, last_name = line_split[2].split(" ")
            points = int(line_split[3])
            shootout = None
        else:
            raise ValueError

        game.players.append(
            SIPlayer(
                team=None,
                city=None,
                first_name=first_name,
                last_name=last_name,
                place=place,
                points=points,
                shootout=shootout,
            )
        )

    return game


def read_2017() -> List[SIGame]:
    numbers = Numbers()

    with open(f"./txt/2017/si.txt") as year_file:
        lines = year_file.readlines()

    sixteenth_games = [
        read_single_game(
            new_si_stages[0], next(numbers), lines[6 * k + 3 : 6 * k + 7], place_col=3,
        )
        for k in range(16)
    ]

    eighth_games = [
        read_single_game(
            new_si_stages[1], next(numbers), lines[6 * k + 101 : 6 * k + 105], place_col=3,
        )
        for k in range(8)
    ]

    quarters = [
        read_single_game(
            new_si_stages[2], next(numbers), lines[6 * k + 151 : 6 * k + 155], place_col=3
        )
        for k in range(4)
    ]

    semis = [
        read_single_game(
            new_si_stages[3], next(numbers), lines[6 * k + 177 : 6 * k + 181], place_col=3
        )
        for k in range(2)
    ]

    finals = [
        read_single_game(new_si_stages[4], next(numbers), lines[189:193], place_col=3)
    ]

    return sixteenth_games + eighth_games + quarters + semis + finals


def read_year(year: int) -> List[SIGame]:
    numbers = Numbers()

    with open(f"./txt/{year}/si.txt") as year_file:
        lines = year_file.readlines()

    sixteenth_games = [
        read_single_game(
            new_si_stages[0], next(numbers), lines[9 * k + 4: 9 * k + 8], place_col=1,
        )
        for k in range(16)
    ]

    eighth_games = [
        read_single_game(
            new_si_stages[1], next(numbers), lines[9 * k + 149: 9 * k + 153], place_col=1,
        )
        for k in range(8)
    ]

    quarters = [
        read_single_game(
            new_si_stages[2], next(numbers), lines[9 * k + 222: 9 * k + 226], place_col=1
        )
        for k in range(4)
    ]

    semis = [
        read_single_game(
            new_si_stages[3], next(numbers), lines[9 * k + 259: 9 * k + 263], place_col=1
        )
        for k in range(2)
    ]

    finals = [
        read_single_game(new_si_stages[4], next(numbers), lines[275:279], place_col=1)
    ]

    return sixteenth_games + eighth_games + quarters + semis + finals


def load_new_si_results():
    new_years = [2018, 2019]
    newer = {year: read_year(year) for year in new_years}
    return {2017: read_2017(), **newer}


if __name__ == "__main__":
    results = load_new_si_results()
    pprint(results)
