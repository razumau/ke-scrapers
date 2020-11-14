from pprint import pprint
from typing import List, Dict

from utils import SIWrittenPlayer


def read_row(row_str: str) -> SIWrittenPlayer:
    row = row_str.split("\t")
    points = [10 * int(p) for p in row[3:]]
    if sum(points) != 0 and int(row[2]) != sum(points):
        print(row_str)
        raise ValueError
    if sum(points) == 0 and int(row[2]) != 0:
        points = [None] * 15

    return SIWrittenPlayer(name=row[1],
                           sum=int(row[2]),
                           place=float(row[0]),
                           points=points)


def read_year(year: int) -> List[SIWrittenPlayer]:
    with open(f"txt/{year}/written.txt") as txtfile:
        rows = txtfile.readlines()

    return [read_row(row) for row in rows[1:]]


def read_written_si_results() -> Dict[int, List[SIWrittenPlayer]]:
    return {year: read_year(year) for year in range(2017, 2020)}


if __name__ == '__main__':
    year = 2019
    pprint(read_year(year))