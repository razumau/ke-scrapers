from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship


class Base:
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)


Base = declarative_base(cls=Base)


class Tournament(Base):
    city = Column(String)
    year = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)


class Team(Base):
    base_name = Column(String, nullable=False)
    base_rating_id = Column(Integer)
    city = Column(String)
    country = Column(String)


class Player(Base):
    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    last_name = Column(String, nullable=False)
    rating_id = Column(Integer)


class TeamTournament(Base):
    __tablename__ = "team_tournament"
    tournament_id = Column(Integer, ForeignKey("tournament.id"), index=True)
    team_id = Column(Integer, ForeignKey("team.id"), index=True)
    rating_id = Column(Integer)
    name = Column(String)

    tournament = relationship("Tournament", backref="teams")
    team = relationship("Team", backref="tournaments")


class TeamTournamentPlayer(Base):
    __tablename__ = "team_tournament_player"
    player_id = Column(Integer, ForeignKey("player.id"), index=True)
    team_tournament_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)

    team_tournament = relationship("TeamTournament", backref="players")
    player = relationship("Player", backref="tournaments")


class CHGKTeamResults(Base):
    __tablename__ = "chgk_results"

    team_tournament_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)
    sum = Column(Integer)
    shootout = Column(Integer)
    tour_1 = Column(Integer)
    tour_2 = Column(Integer)
    tour_3 = Column(Integer)
    tour_4 = Column(Integer)
    tour_5 = Column(Integer)

    tournament = relationship("TeamTournament", backref="chgk_results")


class CHGKTeamDetails(Base):
    __tablename__ = "chgk_details"

    team_tournament_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)
    question_number = Column(Integer)
    result = Column(Integer)

    tournament = relationship("TeamTournament", backref="chgk_details")


class Stage(Base):
    tournament_id = Column(Integer, ForeignKey("tournament.id"), index=True)
    game = Column(String)
    name = Column(String)

    tournament = relationship("Tournament", backref="stages")


class EQGame(Base):
    __tablename__ = "eq_game"
    tournament_id = Column(Integer, ForeignKey("tournament.id"), index=True)
    stage_id = Column(Integer, ForeignKey("stage.id"), index=True)
    name = Column(String)

    tournament = relationship("Tournament", backref="eq_games")
    stage = relationship("Stage", backref="eq_games")


class EQGameTeamResult(Base):
    __tablename__ = "eq_game_team_result"

    team_tournament_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)
    game_id = Column(Integer, ForeignKey("eq_game.id"), index=True)
    points = Column(Integer)
    shootout = Column(Integer)

    tournament = relationship("TeamTournament", backref="eq_game_team_results")
    game = relationship("EQGame", backref="team_results")


class SIGame(Base):
    __tablename__ = "si_game"
    tournament_id = Column(Integer, ForeignKey("tournament.id"), index=True)
    stage_id = Column(Integer, ForeignKey("stage.id"), index=True)
    name = Column(String)

    tournament = relationship("Tournament", backref="si_games")
    stage = relationship("Stage", backref="si_games")


class SIGamePlayerResult(Base):
    __tablename__ = "si_game_player_result"

    player_id = Column(Integer, ForeignKey("player.id"), index=True)
    game_id = Column(Integer, ForeignKey("si_game.id"), index=True)
    points = Column(Integer)
    shootout = Column(Integer)

    game = relationship("SIGame", backref="players")
    player = relationship("Player", backref="si_games")


class BRGame(Base):
    __tablename__ = "br_game"

    stage_id = Column(Integer, ForeignKey("stage.id"), index=True)
    team_one_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)
    team_two_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)
    team_one_points = Column(Integer)
    team_two_points = Column(Integer)

    tournament = relationship(
        "TeamTournament",
        foreign_keys=[team_one_id, team_two_id],
        primaryjoin="or_(BRGame.team_one_id==TeamTournament.team_id,"
        "BRGame.team_two_id==TeamTournament.team_id)",
    )
    stage = relationship("Stage", backref="br_games")


class BRGroupTeamResult(Base):
    __tablename__ = "br_group_team_result"

    team_tournament_id = Column(Integer, ForeignKey("team_tournament.id"), index=True)
    stage_id = Column(Integer, ForeignKey("stage.id"), index=True)
    wins = Column(Integer)
    losses = Column(Integer)
    draws = Column(Integer)
    plus = Column(Integer)
    minus = Column(Integer)
    points = Column(Integer)
    place = Column(Float)

    tournament = relationship("TeamTournament", backref="br_group_team_results")
    stage = relationship("Stage", backref="br_group_team_results")
