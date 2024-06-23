#!/usr/bin/env python3


from collections import defaultdict
import json
import re
from typing import TextIO


CATEGORY_PATTERN = re.compile(r'^[a-z]+$')
NAME_PATTERN = re.compile(r"^['0-9?A-Z_a-z]+$")


def generate_index(output_file: TextIO, challenges_file: TextIO) -> None:
    challenges = json.load(challenges_file)['data']
    # Default ordering for categories and challenges is intrinsic.
    challenges_by_category = defaultdict(list)
    for challenge in challenges:
        assert CATEGORY_PATTERN.fullmatch(challenge['category'])
        assert NAME_PATTERN.fullmatch(challenge['name'])
        assert isinstance(challenge['value'], int)
        challenges_by_category[challenge['category']].append(challenge)

    output_file.write('# jellyCTF 2024\n\n')
    for (category, category_challenges) in challenges_by_category.items():
        output_file.write(f'  - {category}\n')
        for challenge in category_challenges:
            name = challenge['name']
            value = challenge['value']
            output_file.write(f'      - [{name}](./challenges/{category}/{name}/README.md) ({value} pts)\n')


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default=sys.stdout, type=argparse.FileType('xt'))
    parser.add_argument('challenges', type=argparse.FileType('rt'))
    args = parser.parse_args()

    generate_index(args.output, args.challenges)


if __name__ == '__main__':
    main()
