import json

from util import listToJson

if __name__ == '__main__':
    courses: list = json.load(open('_pawsCourse.raw.json', 'r'))

    levels = set()
    for course in courses:
        level: str = course['level']
        if level is not None:
            levels.add(level)

    levels = list(levels)

    listToJson(levels, 'level')
