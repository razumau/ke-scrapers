from dataclasses import dataclass
from itertools import chain
from typing import List, Optional, Iterable


def is_junk_line(line: str):
    if line.strip() == "":
        return True
    if line == "\n":
        return True
    if "Кубок Европы" in line:
        return True
    if line.startswith("На главную страницу"):
        return True
    return False


def flatten(list_of_lists: Iterable) -> List:
    return list(chain.from_iterable(list_of_lists))


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


@dataclass(frozen=True)
class TeamNameQuestions:
    name: str
    city: str
    country: str
    year: int
    questions: List[int]


@dataclass(frozen=False)
class SIPlayer:
    team: str
    city: str
    first_name: str
    last_name: str
    points: int = None
    shootout: int = None
    place: float = None


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


@dataclass(frozen=True)
class EQGameTeamResult:
    stage_name: str
    game_name: str
    team_name: str
    place: float
    points: int = None
    shootout: int = None


@dataclass(frozen=False)
class EQGame:
    stage_name: str
    game_name: str
    teams: List[EQGameTeamResult]


@dataclass(frozen=False)
class SIWrittenPlayer:
    name: str
    sum: int
    place: float
    points: List[int]
