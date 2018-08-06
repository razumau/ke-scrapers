from db import save_teams, engine
from models import Base
from process import build_base_teams
from rating import read_rating_data


def main():
    Base.metadata.drop_all(engine())
    Base.metadata.create_all(engine())
    rating_data = read_rating_data()
    teams = build_base_teams(rating_data.teams)
    save_teams(teams)


if __name__ == "__main__":
    main()
