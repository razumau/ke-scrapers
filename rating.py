from dataclasses import dataclass
from itertools import chain
from typing import List, Optional


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
}


@dataclass(frozen=True)
class Player:
    id: int
    first_name: str
    middle_name: str
    last_name: str


@dataclass(frozen=True)
class Team:
    id: int
    name: str
    city: str
    players: List[Player]
    year: int
    results: Optional[List[int]]


def write_urls_to_file(tournaments, filename):
    with open(filename, "w") as file:
        for t_id in tournaments:
            file.write(
                f"http://rating.chgk.info/tournaments.php?"
                f"tournament_id={t_id}"
                f"&download_data=export_tournament_with_players\n"
            )


def download_csvs(filename):
    pass


def process_csv(tournament_id) -> List[Team]:
    pass


def read_rating_data():
    write_urls_to_file(tournament_ids.keys(), "csv_urls.txt")
    download_csvs("csv_urls.txt")
    lists = [process_csv(t_id) for t_id in tournament_ids.keys()]
    return list(chain.from_iterable(lists))
