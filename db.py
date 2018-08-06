from typing import Tuple, List

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from models import Team


def engine() -> Engine:
    return create_engine("postgresql://localhost:5433/ke", echo=False)


def session() -> Session:
    return sessionmaker(engine())()


def save_teams(teams: List[Tuple]):
    s = session()
    s.query(Team).delete()
    for team in teams:
        if not team[3]:
            print(team)
        s.add(
            Team(
                base_rating_id=team[0], base_name=team[1], city=team[2], country=team[3]
            )
        )
    s.commit()
