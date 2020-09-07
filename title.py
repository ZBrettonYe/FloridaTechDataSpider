import json
from typing import List

from util import listToJson

if __name__ == '__main__':
    sections: List[dict] = json.load(open('_pawsSection.raw.json', 'r'))

    titles = set()
    for section in sections:
        titles.add(section['title'][0])

    titles = list(titles)

    listToJson(titles, 'title')
