import json
from typing import List

from util import listToJson

if __name__ == '__main__':
    sections: List[dict] = json.load(open('_pawsSection.raw.json', 'r'))

    notes = set()
    for section in sections:
        for note in section['notes']:
            notes.add(note)

    notes = list(notes)

    listToJson(notes, 'note')
