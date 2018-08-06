from pprint import pprint

from db import (
    save_teams,
    engine,
    save_players,
    save_team_tournaments,
    create_tournaments,
    save_team_tournament_player,
    save_chgk_results,
)
from models import Base
from process import build_base_teams, unique_players
from rating import read_rating_data


def main():
    Base.metadata.drop_all(engine())
    Base.metadata.create_all(engine())
    create_tournaments()
    rating_data = read_rating_data()
    teams = build_base_teams(rating_data.teams)
    save_teams(teams)
    save_players(unique_players(rating_data.players))
    pprint(rating_data.results)
    save_chgk_results(rating_data.results)
    save_team_tournament_player(rating_data.players)
    save_team_tournaments(rating_data.teams)


if __name__ == "__main__":
    main()
