from chgk import load_chgk_results
from db import (
    save_teams,
    engine,
    save_players,
    save_team_tournaments,
    create_tournaments,
    save_team_tournament_player,
    save_rating_chgk_results,
    save_si_results,
    create_stages,
    save_br_results,
    save_old_chgk_results,
    save_eq_results,
    save_editors, save_written_si_results,
)
from models import Base
from new_eq import load_new_eq_results
from old_eq import load_old_eq_results
from process import build_base_teams, unique_players
from rating import read_rating_data
from old_si import load_old_si_results
from new_si import load_new_si_results
from old_br import load_old_br_results
from new_br import load_new_br_results
from si_written import read_written_si_results


def recreate_schema():
    print("recreating db schema")
    Base.metadata.drop_all(engine())
    print("dropped tables")
    Base.metadata.create_all(engine())
    print("created tables")
    create_tournaments()
    print("created tournaments")
    create_stages()
    print("created stages")


def save_teams_and_tournaments():
    rating_data = read_rating_data()
    teams = build_base_teams(rating_data.teams)
    save_teams(teams)
    save_players(unique_players(rating_data.players))
    save_team_tournaments(rating_data.teams)
    save_team_tournament_player(rating_data.players)


def save_chgk():
    rating_data = read_rating_data()
    save_rating_chgk_results(rating_data.results)

    old_chgk_results = load_chgk_results()
    save_old_chgk_results(old_chgk_results)


def save_br():
    old_br = load_old_br_results()
    new_br = load_new_br_results()
    all_br = {**old_br, **new_br}
    save_br_results(all_br)


def save_eq():
    old_eq = load_old_eq_results()
    new_eq = load_new_eq_results()
    all_eq = {**old_eq, **new_eq}
    save_eq_results(all_eq)


def save_si():
    old_si = load_old_si_results()
    new_si = load_new_si_results()
    all_si = {**old_si, **new_si}
    save_si_results(all_si)


def save_written_si():
    results = read_written_si_results()
    save_written_si_results(results)


def main():
    recreate_schema()
    save_teams_and_tournaments()
    save_chgk()
    save_si()
    save_eq()
    save_br()
    save_editors()
    save_written_si()


if __name__ == "__main__":
    main()
