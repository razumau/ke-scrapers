from typing import Tuple, List, Iterable, Set, Callable, Dict

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

import utils
from models import (
    Team,
    Player,
    TeamTournament,
    Tournament,
    TeamTournamentPlayer,
    CHGKTeamDetails,
    CHGKTeamResults,
)


def engine() -> Engine:
    return create_engine("postgresql://localhost:5433/ke", echo=False)


def session() -> Session:
    return sessionmaker(engine())()


def create_tournaments():
    s = session()
    query = open("tournaments.sql").read()
    s.execute(query)
    s.commit()


def save_teams(teams: List[Tuple]):
    def create_team(team: Tuple):
        return Team(
            base_rating_id=team[0], base_name=team[1], city=team[2], country=team[3]
        )

    return save(Team, create_team, teams)


def save_players(players: Set[Tuple]):
    def create_player(player: Tuple):
        return Player(
            first_name=player[0],
            middle_name=player[1],
            last_name=player[2],
            rating_id=player[3],
        )

    return save(Player, create_player, players)


def fetch_tournament_year_map() -> Dict:
    tournaments = session().query(Tournament.year, Tournament.id)
    return {t.year: t.id for t in tournaments}


def find_team_id(rating_id: int) -> int:
    s = session()
    team_id = s.query(Team.id).filter_by(base_rating_id=rating_id).first()[0]
    s.close()
    return team_id


def save_team_tournaments(teams: Iterable[utils.Team]):
    tournament_year = fetch_tournament_year_map()

    def create_team_tournament(team: utils.Team):
        return TeamTournament(
            tournament_id=tournament_year[team.year],
            team_id=find_team_id(team.id),
            rating_id=team.id,
        )

    return save(TeamTournament, create_team_tournament, teams)


def save_team_tournament_player(players: Iterable[utils.Player]):
    s = session()
    for player in players:
        tt = s.query(TeamTournament).filter_by(rating_id=player.team.id).one()
        player_id = s.query(Player.id).filter_by(rating_id=player.id).one()[0]
        ttp = TeamTournamentPlayer(player_id=player_id)
        tt.players.append(ttp)
    s.commit()


def save_chgk_results(results: Iterable[utils.TeamQuestions]):
    s = session()
    s.query(CHGKTeamDetails).delete()
    s.query(CHGKTeamResults).delete()
    for res in results:
        if not res.questions:
            continue
        tt = s.query(TeamTournament).filter_by(rating_id=res.team_id).one()
        questions = [
            CHGKTeamDetails(question_number=q_number, result=q_result)
            for q_number, q_result in enumerate(res.questions, 1)
        ]
        aggregated_results = CHGKTeamResults(
            sum=sum(res.questions),
            tour_1=sum(res.questions[:15]),
            tour_2=sum(res.questions[15:30]),
            tour_3=sum(res.questions[30:45]),
            tour_4=sum(res.questions[45:60]),
            tour_5=sum(res.questions[60:75]),
        )
        tt.chgk_details.extend(questions)
        tt.chgk_results.append(aggregated_results)
    s.commit()


def save(entity_type, entity_factory: Callable, entities_data: Iterable):
    s = session()
    s.query(entity_type).delete()

    for entity in entities_data:
        s.add(entity_factory(entity))

    s.commit()
