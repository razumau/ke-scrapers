from dataclasses import dataclass
from itertools import chain
from typing import List

OLD_URL = "http://localhost:8000/ke"


@dataclass(frozen=True)
class Team:
    id: int
    name: str
    city: str
    year: int


@dataclass(frozen=True)
class Player:
    id: int
    team: Team
    first_name: str
    middle_name: str
    last_name: str


@dataclass(frozen=True)
class TeamQuestions:
    team_id: int
    year: int
    questions: List[int]


def flatten(list_of_lists) -> List:
    return list(chain.from_iterable(list_of_lists))
