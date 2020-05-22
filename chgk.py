from pprint import pprint
from typing import List, Any
from collections import defaultdict

from requests_html import HTMLSession

from utils import flatten, TeamNameQuestions
from renames import rename_team, rename_city


def safe_int(value: Any) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def rename(team: str, year: int) -> str:
    if year == 2013 and team == "Мишки-Плутишки":
        return "Мишки-Плутишки: возрождение легенды"
    return rename_team(team)


def load_year_results_html(year: int) -> List[TeamNameQuestions]:
    print(f"Loading results for {year}")
    session = HTMLSession()
    r = session.get(f"http://windflower.spb.ru/ke/{year}/results/chgk.html")
    r.html.encoding = r.encoding
    results_table = r.html.find("table")[2]

    all_rows = [row.text.split("\n") for row in results_table.find("tr")]
    results_rows = [row[:-2] for row in all_rows if len(row) > 1 and row[-1] != "М"]
    teams_results = defaultdict(list)
    for res in results_rows:
        teams_results[res[0]].extend(safe_int(r) for r in res[1:])

    teams_table = r.html.find("table")[0]
    teams = [row.text.split("\n")[:3] for row in teams_table.find("tr")[1:]]

    return [
        TeamNameQuestions(
            name=rename(team[0], year),
            city=rename_city(team[1]),
            country=team[2],
            year=year,
            questions=teams_results[team[0]],
        )
        for team in teams
    ]


def load_chgk_results():
    return flatten(load_year_results_html(year) for year in range(2005, 2015))


if __name__ == "__main__":
    pprint(load_chgk_results())
