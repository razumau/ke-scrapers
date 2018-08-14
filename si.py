from pprint import pprint

from itertools import tee, groupby, chain
from typing import Iterable, List

from utils import SIPlayer, SIGame, flatten

from requests_html import HTMLSession

OLD_URL = "http://localhost:8000/ke"


def load_si_results(year: int):
    all_rows = fetch_page(year)
    split = split_into_stages(all_rows)
    games = [split_into_games(stage, rows) for stage, rows in split.items()]
    final = split_into_games("Финал", all_rows[-4:])
    return flatten(games).extend(final)


def fetch_page(year: int) -> List[str]:
    session = HTMLSession()
    r = session.get(f"{OLD_URL}/{year}/results/svoyak.html")
    r.encoding = "cp1251"
    r.html.encoding = r.encoding
    results_table = r.html.find("table")[0]
    return [row.text.split("\n") for row in results_table.find("tr")]


def pairwise(iterable: Iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def split_into_stages(rows):
    stages = [
        "Квалификационный этап",
        "1/27 финала",
        "1/9 финала",
        "1/3 финала",
        "Финал",
    ]

    indices = [i for stage in stages for i, row in enumerate(rows) if row[0] == stage]

    return {rows[i][0]: rows[i + 1 : j] for i, j in pairwise(indices)}


def split_into_games(stage_name: str, rows: List):
    result = []
    name = rows[0][0]  # if stage_name != 'Финал' else 'Финал'
    for row in rows[1:]:
        if row[0].startswith("Бой"):
            name = row[0]
            continue

        if not row[0]:
            continue

        result.append((stage_name, name, process_score_row(row)))

    data = sorted(result, key=lambda r: r[1])
    groups = [list(g) for _, g in groupby(data, lambda r: r[1])]
    games = [
        SIGame(
            stage_name=group[0][0], game_name=group[0][1], players=[g[2] for g in group]
        )
        for group in groups
    ]
    return games


def process_score_row(row) -> SIPlayer:
    player, team, score = row[0], row[1], row[2]
    split = team.split("(")
    return SIPlayer(
        team=split[0][:-1],
        city=None if not split[1:] else split[1][:-1],
        first_name=player.split(" ")[1],
        last_name=player.split(" ")[0],
        points=score,
        shootout=None if not row[3:] else sum(int(r) for r in row[3:]),
    )


if __name__ == "__main__":
    load_si_results(2015)
