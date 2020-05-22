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
    BRGame,
    BRGroupTeamResult, EQGame, EQGameTeamResult,
)
from renames import rename_team
from si import old_si_stages, new_si_stages
from old_br import old_br_stages, br_stages_2005
from new_br import new_br_stages
from old_eq import old_eq_stages
from new_eq import eq_stages_2017, eq_stages


def engine() -> Engine:
    return create_engine("sqlite+pysqlite:///db.db")


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

    old_range = list(range(2006, 2017))
    new_range = list(range(2017, 2020))

    stages = [
        *generate_stages(old_range, old_si_stages, "СИ"),
        *generate_stages(new_range, new_si_stages, "СИ"),
        *generate_stages([2005], ["Финал"], "ЭК"),
        *generate_stages(old_range, old_eq_stages, "ЭК"),
        *generate_stages([2017], eq_stages_2017, "ЭК"),
        *generate_stages([2018, 2019], eq_stages, "ЭК"),
        *generate_stages([2005], br_stages_2005, "БР"),
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


def find_team_tournament_id(session, tournament_id: int, team_name: str) -> int:
    print(f"finding id for {team_name} in {tournament_id}")
    return (
        session.query(TeamTournament.id)
        .filter_by(tournament_id=tournament_id, name=team_name)
        .one()[0]
    )


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
                    Player.last_name == last_name,
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

    for year, games in si_results.items():
        print(f"Saving SI results for {year}")
        t_id = year_map[year]
        save_single_year_si_results(t_id, games)


def save_br_results(
    br_results: Dict[int, Tuple[List[utils.BRGroupTeamResult], List[utils.BRGame]]]
):
    print("Saving BR results")
    year_map = fetch_tournament_year_map()
    with session() as s:
        s.execute("delete from br_group_team_result")
        # s.execute("delete from br_game")

    for year, (group_results, games) in br_results.items():
        print(f"Saving BR results for {year}")
        t_id = year_map[year]
        # save_single_year_br_games(t_id, games)
        save_single_year_br_group_results(t_id, group_results)


def save_single_year_br_games(t_id: int, games: List[utils.BRGame]):
    def create_br_game(game: utils.BRGame):
        with session() as s:
            stage_id = (
                s.query(Stage.id)
                .filter_by(tournament_id=t_id, name=game.stage_name, game="БР")
                .one()[0]
            )

            team_one_id = find_team_tournament_id(s, t_id, game.team_one)
            team_two_id = find_team_tournament_id(s, t_id, game.team_two)

            s.add(
                BRGame(
                    stage_id=stage_id,
                    team_one_id=team_one_id,
                    team_two_id=team_two_id,
                    team_one_points=game.team_one_points,
                    team_two_points=game.team_two_points,
                    team_one_shootout=game.team_one_shootout_points,
                    team_two_shootout=game.team_two_shootout_points,
                )
            )

    for game in games:
        print(game.stage_name, game.team_one, game.team_two)
        create_br_game(game)


def save_single_year_br_group_results(
    t_id: int, group_results: List[utils.BRGroupTeamResult]
):
    for gr in group_results:
        with session() as s:
            stage_id = (
                s.query(Stage.id)
                .filter_by(tournament_id=t_id, name=gr.stage_name, game="БР")
                .one()[0]
            )
            team_id = find_team_tournament_id(s, t_id, gr.team_name)
            print(f"found team_id for {gr.team_name}")
            s.add(
                BRGroupTeamResult(
                    team_tournament_id=team_id,
                    stage_id=stage_id,
                    wins=gr.wins,
                    losses=gr.losses,
                    draws=gr.draws,
                    plus=gr.plus,
                    minus=gr.minus,
                    points=gr.points,
                    place=gr.place,
                    group=gr.group_name,
                )
            )


def save_eq_results(
    eq_results: Dict[int, List[utils.EQGame]]
):
    print("Saving EQ results")
    year_map = fetch_tournament_year_map()
    with session() as s:
        s.execute("delete from eq_game")
        s.execute("delete from eq_game_team_result")

    for year, games in eq_results.items():
        print(f"Saving EQ results for {year}")
        t_id = year_map[year]
        save_single_year_eq_games(t_id, games)
        save_single_year_eq_results(t_id, games)


def save_single_year_eq_games(t_id: int, games: List[utils.EQGame]):
    print(f'creating games for {t_id}')

    def create_eq_game(game: utils.SIGame):
        with session() as s:
            stage_id = (
                s.query(Stage.id)
                .filter_by(tournament_id=t_id, name=game.stage_name, game="ЭК")
                .one()[0]
            )
        return EQGame(tournament_id=t_id, stage_id=stage_id, name=game.game_name)

    save(EQGame, create_eq_game, games, truncate=False)
    print(f'created games for {t_id}')


def save_single_year_eq_results(t_id: int, games: List[utils.EQGame]):
    with session() as s:
        for game in games:
            print(f"finding {game}")
            saved_game = (
                s.query(EQGame)
                .join(Stage)
                .filter(
                    Stage.tournament_id == t_id,
                    Stage.name == game.stage_name,
                    Stage.game == "ЭК",
                    EQGame.name == game.game_name,
                )
                .one()
            )

            for team in game.teams:
                tt_id = find_team_tournament_id(s, t_id, team.team_name)
                saved_game.team_results.append(
                    EQGameTeamResult(
                        team_tournament_id=tt_id,
                        points=team.points,
                        shootout=team.shootout,
                        place=team.place,
                    )
                )


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
            name=rename_team(team.name),
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


def save_old_chgk_results(results: Iterable[utils.TeamNameQuestions]):
    print("Saving old chgk results")
    with session() as s:
        # s.query(CHGKTeamDetails).delete()
        # s.query(CHGKTeamResults).delete()
        for res in results:
            t_id = fetch_tournament_year_map()[res.year]
            tt_id = find_team_tournament_id(s, t_id, res.name)

            for q_number, q_result in enumerate(res.questions, 1):
                s.add(
                    CHGKTeamDetails(
                        team_tournament_id=tt_id,
                        question_number=q_number,
                        result=q_result,
                    )
                )

            s.add(
                CHGKTeamResults(
                    team_tournament_id=tt_id,
                    sum=sum(res.questions),
                    tour_1=sum(res.questions[:15]),
                    tour_2=sum(res.questions[15:30]),
                    tour_3=sum(res.questions[30:45]),
                    tour_4=sum(res.questions[45:60]),
                    tour_5=sum(res.questions[60:75]),
                    unofficial=False,
                )
            )


def save_rating_chgk_results(results: Iterable[utils.TeamQuestions]):
    print("Saving rating chgk results")
    with session() as s:
        # s.query(CHGKTeamDetails).delete()
        # s.query(CHGKTeamResults).delete()
        for res in results:
            if not res.questions:
                continue

            t_id = fetch_tournament_year_map()[res.year]
            tt_id = (
                s.query(TeamTournament.id)
                .filter_by(rating_id=res.team_id, tournament_id=t_id)
                .one()[0]
            )

            for q_number, q_result in enumerate(res.questions, 1):
                s.add(
                    CHGKTeamDetails(
                        team_tournament_id=tt_id,
                        question_number=q_number,
                        result=q_result,
                    )
                )

            s.add(
                CHGKTeamResults(
                    team_tournament_id=tt_id,
                    sum=sum(res.questions),
                    tour_1=sum(res.questions[:15]),
                    tour_2=sum(res.questions[15:30]),
                    tour_3=sum(res.questions[30:45]),
                    tour_4=sum(res.questions[45:60]),
                    tour_5=sum(res.questions[60:75]),
                    unofficial=False,
                )
            )


def save(
    entity_type,
    entity_factory: Callable,
    entities_data: Iterable,
    truncate: bool = True,
):
    with session() as s:
        if truncate:
            s.query(entity_type).delete()

        for entity in entities_data:
            s.add(entity_factory(entity))
