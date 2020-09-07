import json
from typing import List

from util import listToJson

if __name__ == '__main__':
    sections: List[dict] = json.load(open('_pawsSection.raw.json', 'r'))

    campuses = set()
    for section in sections:
        campuses.add(section['location'])

    campuses = list(campuses)

    listToJson(campuses, 'campus')
