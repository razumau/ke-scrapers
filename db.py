from contextlib import contextmanager
from functools import lru_cache
from typing import Tuple, List, Iterable, Set, Callable, Dict

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import sqlalchemy.orm as orm

import utils
from models import (
    Team,
    Player,
    TeamTournament,
    Tournament,
    TeamTournamentPlayer,
    CHGKTeamDetails,
    CHGKTeamResults,
    Stage,
    SIGame,
    SIGamePlayerResult,
)
from si import old_si_stages, new_si_stages
from br import old_br_stages, new_br_stages
from eq import old_eq_stages, new_eq_stages


def engine() -> Engine:
    return create_engine("postgresql://localhost:5433/ke", echo=False)


@contextmanager
def session() -> orm.Session:
    s = orm.sessionmaker(engine())()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()


def create_tournaments():
    with session() as s:
        query = open("tournaments.sql").read()
        s.execute(query)


def generate_stages(years: Iterable[int], stages: Iterable, game: str):
    years_map = fetch_tournament_year_map()

    return [(years_map[year], game, stage) for stage in stages for year in years]


def create_stages():
    def create_stage(stage):
        return Stage(tournament_id=stage[0], game=stage[1], name=stage[2])

    old_range = list(range(2005, 2017))
    new_range = list(range(2017, 2018))

    stages = [
        *generate_stages(old_range, old_si_stages, "СИ"),
        *generate_stages(new_range, new_si_stages, "СИ"),
        *generate_stages(old_range, old_eq_stages, "ЭК"),
        *generate_stages(new_range, new_eq_stages, "ЭК"),
        *generate_stages(old_range, old_br_stages, "БР"),
        *generate_stages(new_range, new_br_stages, "БР"),
    ]

    save(Stage, create_stage, stages)


def save_teams(teams: List[Tuple]):
    def create_team(team: Tuple):
        return Team(
            base_rating_id=team[0], base_name=team[1], city=team[2], country=team[3]
        )

    print("Saving teams")
    return save(Team, create_team, teams)


def save_players(players: Set[Tuple]):
    def create_player(player: Tuple):
        return Player(
            first_name=player[0],
            middle_name=player[1],
            last_name=player[2],
            rating_id=player[3],
        )

    print("Saving players")
    return save(Player, create_player, players)


@lru_cache(1)
def fetch_tournament_year_map() -> Dict:
    with session() as s:
        tournaments = s.query(Tournament.year, Tournament.id)
    return {t.year: t.id for t in tournaments}


def find_team_id(rating_id: int) -> int:
    with session() as s:
        team_id = s.query(Team.id).filter_by(base_rating_id=rating_id).first()[0]
    return team_id


def find_player_id(
    first_name: str, last_name: str, team_name: str = None, team_city: str = None
):
    with session() as s:
        ids = (
            s.query(Player.id)
            .filter_by(first_name=first_name, last_name=last_name)
            .all()
        )

        if len(ids) == 1:
            return ids[0][0]

        if team_name is None:
            raise ValueError(f"More than one player with name {first_name} {last_name}")

        try:
            player_id = (
                s.query(TeamTournamentPlayer.player_id)
                .join(TeamTournament)
                .join(Player)
                .filter(
                    TeamTournament.name == team_name,
                    Player.first_name == first_name,
                    Player.last_name == last_name
                )
                .one()
            )
        except Exception:
            print(first_name, last_name, team_name)
            raise
        return player_id


def save_si_results(si_results: Dict[int, List[utils.SIGame]]):
    print("Saving SI results")
    year_map = fetch_tournament_year_map()
    with session() as s:
        # s.execute("TRUNCATE si_game CASCADE")
        s.execute("TRUNCATE si_game_player_result CASCADE")

    # for year, games in si_results.items():
    #     print(f"Saving SI games for {year}")
    #     t_id = year_map[year]
    #     save_single_year_si_games(t_id, games)

    for year, games in si_results.items():
        print(f"Saving SI results for {year}")
        t_id = year_map[year]
        save_single_year_si_results(t_id, games)


def save_single_year_si_games(t_id: int, games: List[utils.SIGame]):
    def create_si_game(game: utils.SIGame):
        with session() as s:
            stage_id = (
                s.query(Stage.id)
                .filter_by(tournament_id=t_id, name=game.stage_name, game="СИ")
                .one()[0]
            )
        return SIGame(tournament_id=t_id, stage_id=stage_id, name=game.game_name)

    save(SIGame, create_si_game, games, truncate=False)


def save_single_year_si_results(t_id: int, games: List[utils.SIGame]):
    with session() as s:
        for game in games:
            saved_game = (
                s.query(SIGame)
                .join(Stage)
                .filter(
                    Stage.tournament_id == t_id,
                    Stage.name == game.stage_name,
                    Stage.game == "СИ",
                    SIGame.name == game.game_name,
                )
                .one()
            )

            for player in game.players:
                player_id = find_player_id(
                    player.first_name, player.last_name, player.team
                )
                saved_game.players.append(
                    SIGamePlayerResult(
                        player_id=player_id,
                        points=player.points,
                        shootout=player.shootout,
                    )
                )


def save_team_tournaments(teams: Iterable[utils.Team]):
    tournament_year = fetch_tournament_year_map()

    def create_team_tournament(team: utils.Team):
        return TeamTournament(
            tournament_id=tournament_year[team.year],
            team_id=find_team_id(team.id),
            name=team.name,
            rating_id=team.id,
        )

    print("Saving team-tournament links")
    return save(TeamTournament, create_team_tournament, teams)


def save_team_tournament_player(players: Iterable[utils.Player]):
    print("Saving team-tournament-player links")
    with session() as s:
        for player in players:
            t_id = fetch_tournament_year_map()[player.team.year]
            tt = (
                s.query(TeamTournament)
                .filter_by(rating_id=player.team.id, tournament_id=t_id)
                .one()
            )
            player_id = s.query(Player.id).filter_by(rating_id=player.id).one()[0]
            ttp = TeamTournamentPlayer(player_id=player_id)
            tt.players.append(ttp)


def save_chgk_results(results: Iterable[utils.TeamQuestions]):
    print("Saving chgk results")
    with session() as s:
        s.query(CHGKTeamDetails).delete()
        s.query(CHGKTeamResults).delete()
        for res in results:
            if not res.questions:
                continue

            t_id = fetch_tournament_year_map()[res.year]
            tt = (
                s.query(TeamTournament)
                .filter_by(rating_id=res.team_id, tournament_id=t_id)
                .one()
            )
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


def save(entity_type, entity_factory: Callable, entities_data: Iterable,
         truncate: bool = True):
    with session() as s:
        if truncate:
            s.query(entity_type).delete()

        for entity in entities_data:
            s.add(entity_factory(entity))
