from dataclasses import dataclass
from itertools import chain
from typing import List, Optional, Iterable

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


def flatten(list_of_lists: Iterable) -> List:
    return list(chain.from_iterable(list_of_lists))


@dataclass(frozen=True)
class SIPlayer:
    team: str
    city: str
    first_name: str
    last_name: str
    points: int
    shootout: int


@dataclass(frozen=True)
class SIGame:
    stage_name: str
    game_name: str
    players: List[SIPlayer]


@dataclass(frozen=True)
class BRGame:
    stage_name: str
    team_one: str
    team_two: str
    team_one_points: int
    team_two_points: int
    team_one_shootout_points: Optional[int] = None
    team_two_shootout_points: Optional[int] = None


@dataclass(frozen=False)
class BRGroupTeamResult:
    stage_name: str
    group_name: str
    team_name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0
    plus: int = 0
    minus: int = 0
    points: int = 0
    place: float = 0
