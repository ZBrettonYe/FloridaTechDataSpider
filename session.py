import json
from typing import List

from util import listToJson

if __name__ == '__main__':
    sections: List[dict] = json.load(open('_pawsSection.raw.json', 'r'))

    sessions = set()
    for section in sections:
        session: str = section['session']
        if session is not None:
            sessions.add(session)

    sessions = list(sessions)

    listToJson(sessions, 'session')
