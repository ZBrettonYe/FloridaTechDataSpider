import json
from util import listToJson

if __name__ == '__main__':
    courses: list = json.load(open('_pawsCourse.raw.json', 'r'))
    sections: list = json.load(open('_pawsSection.raw.json', 'r'))

    prerequisites = set()

    for course in courses:
        prerequisite: str = course['prerequisite']
        if prerequisite is not None:
            prerequisites.add(prerequisite)

    for section in sections:
        prerequisite: str = section['prerequisite']
        if prerequisite is not None:
            prerequisites.add(prerequisite)

    prerequisites = list(prerequisites)

    listToJson(prerequisites, 'prerequisite')
