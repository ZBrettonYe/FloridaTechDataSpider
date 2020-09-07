import json
import re

from util import listToJson

if __name__ == '__main__':
    sections: list = json.load(open('_pawsSection.raw.json', 'r'))
    requirements: list = json.load(open('requirement.json', 'r'))
    tags: list = json.load(open('tag.json', 'r'))

    descriptions = set()
    for section in sections:
        description: str = section['title'][1]
        if description != '':
            descriptions.add(section['title'][1])

    descriptions = list(descriptions)

    tagPattern = r'\((?:'
    tagPattern += '|'.join([tag['code'] for tag in tags])
    tagPattern += r'|/)+\)'
    # print(tagPattern)
    # \((?:CC|CL|COM|HON|HU|LA|Q|SS|/)+\)
    tagPattern = re.compile(tagPattern, flags=re.IGNORECASE)

    prerequisitesPattern = re.compile(r'(\(Prerequisites: .+?\))')

    for index, description in enumerate(descriptions):
        try:
            startIndex = re.search(r'\(Requirement[s]?: ', description).start()

            nestingLevel = 0
            for offset, char in enumerate(description[startIndex:]):
                if char == '(':
                    nestingLevel += 1
                elif char == ')':
                    nestingLevel -= 1

                if nestingLevel == 0:
                    endIndex = startIndex + offset + 1
                    break

            description = description[:startIndex] + description[endIndex:]
        except AttributeError:
            pass

        description = tagPattern.sub(repl='', string=description)
        description = prerequisitesPattern.sub(repl='', string=description)

        descriptions[index] = description.strip()

    listToJson(descriptions, 'description')
