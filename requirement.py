import json
import re
from typing import List

from util import listToJson

if __name__ == '__main__':
    sections: List[dict] = json.load(open('_pawsSection.raw.json', 'r'))

    requirements = set()
    for section in sections:
        description: str = section['title'][1]

        try:
            # Search for header
            startIndex = re.search(
                r'\(Requirement[s]?: ', description
            ).end()   # AttributeError

            # We could simply search for ')'
            # But there could be nesting prentices, so a nesting counter is required
            # For example: 'Background knowledge in Fortran, C/C++ or other programming language (other than MATLAB or similar), and partial differential equations.'
            nestingLevel = 1
            for offset, char in enumerate(description[startIndex:]):
                if char == '(':
                    nestingLevel += 1
                elif char == ')':
                    nestingLevel -= 1

                if nestingLevel == 0:
                    endIndex = startIndex + offset
                    break

            requirements.add(description[startIndex:endIndex])
        except AttributeError:  # 'NoneType' object has no attribute 'end'
            pass

    requirements = list(requirements)

    listToJson(requirements, 'requirement')
