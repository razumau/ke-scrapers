from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from db import engine


class Base:
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class Tournament(Base):
    city = Column(String)
    year = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)


class Team(Base):
    base_name = Column(String, nullable=False)
    city = Column(String)
    country = Column(String)


class Player(Base):
    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    last_name = Column(String, nullable=False)
    rating_id = Column(Integer)


class TeamTournament(Base):
    __tablename__ = "team_tournament"
    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    rating_id = Column(Integer)

    tournament = relationship("Tournament", backref="teams")
    team = relationship("Team", backref="tournaments")


class TeamTournamentPlayer(Base):
    __tablename__ = "team_tournament_player"
    player_id = Column(Integer, ForeignKey("player.id"))
    team_tournament_id = Column(Integer, ForeignKey("team_tournament.id"))

    team_tournament = relationship("TeamTournament", backref="players")


class CHGKTeamResults(Base):
    __tablename__ = "chgk_results"

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    sum = Column(Integer)
    shootout = Column(Integer)
    tour_1 = Column(Integer)
    tour_2 = Column(Integer)
    tour_3 = Column(Integer)
    tour_4 = Column(Integer)
    tour_5 = Column(Integer)

    tournament = relationship("Tournament", backref="chgk_results")


class CHGKTeamDetails(Base):
    __tablename__ = "chgk_details"

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    question_number = Column(Integer)
    result = Column(Integer)

    tournament = relationship("Tournament", backref="chgk_details")


class Stage(Base):
    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    game = Column(String)
    name = Column(String)

    tournament = relationship("Tournament", backref="stages")


class EQGameTeamResult(Base):
    __tablename__ = "eq_game_team_result"

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    stage_id = Column(Integer, ForeignKey("stage.id"))
    points = Column(Integer)
    shootout = Column(Integer)

    tournament = relationship("Tournament", backref="eq_game_team_results")
    stage = relationship("Stage", backref="eq_game_team_results")
    team = relationship("Team", backref="eq_game_team_results")


class BRGame(Base):
    __tablename__ = "br_game"

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    stage_id = Column(Integer, ForeignKey("stage.id"))
    team_one_id = Column(Integer, ForeignKey("team.id"))
    team_two_id = Column(Integer, ForeignKey("team.id"))
    team_one_points = Column(Integer)
    team_two_points = Column(Integer)

    tournament = relationship("Tournament", backref="br_games")
    stage = relationship("Stage", backref="br_games")
    team = relationship("Team", backref="br_games")


class BRGroupTeamResult(Base):
    __tablename__ = "br_group_team_result"

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    stage_id = Column(Integer, ForeignKey("stage.id"))
    wins = Column(Integer)
    losses = Column(Integer)
    draws = Column(Integer)
    plus = Column(Integer)
    minus = Column(Integer)
    points = Column(Integer)
    place = Column(Float)

    tournament = relationship("Tournament", backref="br_group_team_results")
    stage = relationship("Stage", backref="br_group_team_results")
    team = relationship("Team", backref="br_group_team_results")


class SIGame(Base):
    __tablename__ = "si_game"

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    player_id = Column(Integer, ForeignKey("player.id"))
    stage_id = Column(Integer, ForeignKey("stage.id"))
    points = Column(Integer)
    shootout = Column(Integer)

    tournament = relationship("Tournament", backref="si_games")
    stage = relationship("Stage", backref="si_games")
    player = relationship("Player", backref="si_games")


Base.metadata.create_all(engine())
