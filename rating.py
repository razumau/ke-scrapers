import csv
from pprint import pprint
from subprocess import call
import os
from typing import List, Optional, Iterable, Dict, NamedTuple

import requests

from utils import Team, Player, TeamQuestions, flatten

tournament_ids = {
    2143: 2005,
    2144: 2006,
    2241: 2007,
    2240: 2008,
    1692: 2009,
    1929: 2010,
    1930: 2011,
    2234: 2012,
    2760: 2013,
    3118: 2014,
    3563: 2015,
    3999: 2016,
    4411: 2017,
    5015: 2018,
    5773: 2019,
}


class RatingData(NamedTuple):
    teams: Iterable[Team]
    players: Iterable[Player]
    results: Iterable[TeamQuestions]


def reverse_dict(dict_: Dict):
    return {value: key for key, value in dict_}


def write_urls_to_file(tournaments, filename):
    with open(filename, "w") as file:
        for t_id in tournaments:
            file.write(
                f"http://rating.chgk.info/tournaments.php?"
                f"tournament_id={t_id}"
                f"&download_data=export_tournament_with_players\n"
            )


def download_csvs(filename):
    print("Downloading CSV files with players")
    call(["wget", "-q", "--show-progress", "--content-disposition", "-i", filename])


def rename_csvs(ids: Iterable[int]):
    print("Renaming CSV files")
    for id_ in ids:
        os.rename(f"tournament-with-players-{id_}.csv", f"{tournament_ids[id_]}.csv")


def read_csv(year: int) -> List[Dict]:
    with open(f"{year}.csv", encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        return list(dict(row) for row in reader)


def process_csv(year: int) -> List[Player]:
    print(f"Processing {year}")
    dicts = read_csv(year)
    return [
        Player(
            id=int(d["IDplayer"]),
            team=Team(
                id=int(d["Team ID"]), name=d["Название"], city=d["Город"], year=year
            ),
            first_name=d["Имя"],
            middle_name=d["Отчество"],
            last_name=d["Фамилия"],
        )
        for d in dicts
    ]


def read_rating_data() -> RatingData:
    ids = tournament_ids.keys()
    write_urls_to_file(ids, "urls.txt")
    download_csvs("urls.txt")
    rename_csvs(ids)
    players = flatten(process_csv(year) for year in tournament_ids.values())
    teams = set(player.team for player in players)
    results = get_results()
    return RatingData(teams, players, results)


def process_team_result(team_result: Dict) -> Optional[List]:
    questions = [int(i) for i in team_result["mask"]]
    mask_sum = sum(questions)
    if mask_sum == 0 or mask_sum != int(team_result["questions_total"]):
        return None
    return questions


def fetch_results(tournament_id: int) -> List[TeamQuestions]:
    print(f"Fetching results for {tournament_id}")
    res = requests.get(
        f"http://rating.chgk.info/api/tournaments/{tournament_id}/list.json"
    )

    return [
        TeamQuestions(
            team_id=int(team_result["idteam"]),
            year=tournament_ids[tournament_id],
            questions=process_team_result(team_result),
        )
        for team_result in res.json()
    ]


def get_results() -> List[TeamQuestions]:
    print("Getting results from rating.chgk.info")
    results = (fetch_results(id_) for id_ in tournament_ids)
    return flatten(results)


if __name__ == "__main__":
    data = read_rating_data()
    pprint(data.teams)
