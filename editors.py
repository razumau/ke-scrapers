import csv
from pprint import pprint
from typing import Dict, List


def load_editors() -> List[Dict]:
    with open("editors.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        editors = [row for row in reader]
    return editors


if __name__ == '__main__':
    pprint(load_editors())
