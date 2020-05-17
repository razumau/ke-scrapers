from pprint import pprint

from chgk import load_year_results_html, load_chgk_results
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
    save_br_results, save_old_chgk_results,
)
from models import Base
from process import build_base_teams, unique_players
from rating import read_rating_data, tournament_ids, get_results
from si import load_si_results
from old_br import load_old_br_results
from new_br import load_new_br_results
from utils import flatten


def recreate_schema():
    Base.metadata.drop_all(engine())
    Base.metadata.create_all(engine())
    create_tournaments()
    create_stages()


def save_teams_and_tournaments():
    rating_data = read_rating_data()
    #
    teams = build_base_teams(rating_data.teams)
    save_teams(teams)
    save_players(unique_players(rating_data.players))
    save_team_tournaments(rating_data.teams)
    save_team_tournament_player(rating_data.players)
    # save_chgk_results(rating_data.results)

def main():
    # recreate_schema()
    # save_teams_and_tournaments()


    rating_data = read_rating_data()
    save_rating_chgk_results(rating_data.results)

    # old_chgk_results = load_year_results_html(2014)
    # old_chgk_results = load_chgk_results()
    # save_old_chgk_results(old_chgk_results)

    # years = tournament_ids.values()

    # old_br = load_old_br_results()
    # new_br = load_new_br_results()
    # all_br = {**old_br, **new_br}
    # save_br_results(all_br)


if __name__ == "__main__":
    main()
