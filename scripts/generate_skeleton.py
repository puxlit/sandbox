#!/usr/bin/env python3


import json
import re
from typing import TextIO
from urllib.parse import urlparse


AUTHOR_PATTERN = re.compile(r'(\n+)?(?:^Author: +)([ 0-9A-Z_a-z]+)$(\n+)?', flags=re.MULTILINE)
CATEGORY_PATTERN = re.compile(r'^[a-z]+$')
FILE_PATTERN = re.compile(r'(?<=^/files/[0-9a-f]{32}/)[.0-9_a-z]+(?=\?token=[-0-9A-Z_a-z]+\.[-0-9A-Z_a-z]+\.[-0-9A-Z_a-z]+$)')
NAME_PATTERN = re.compile(r"^['0-9?A-Z_a-z]+$")
TAG_PATTERN = re.compile(r'^[a-z]+$')


def generate_skeleton(output_file: TextIO, challenge_file: TextIO) -> None:
    challenge = json.load(challenge_file)['data']

    name = challenge['name']
    assert NAME_PATTERN.fullmatch(name)

    value = challenge['value']
    assert isinstance(value, int)

    # We're going to trust this is non-malicious Markdown. 🫣
    description_md = challenge['description'].replace('\r\n', '\n').replace('\n\n\n', '\n\n').strip()
    author = ''
    match = AUTHOR_PATTERN.search(description_md)
    if match:
        author = match.group(2)
        if not match.group(3):
            assert description_md.endswith(match.group(0))
            description_md = description_md[:match.start(0)]
        else:
            description_md = description_md[:match.start(0)] + '\n\n' + description_md[match.end(0):]

    connection_info_html = ''
    if challenge['connection_info']:
        assert all(special_char not in challenge['connection_info'] for special_char in {'&', '<', '>'})
        parse_result = urlparse(challenge['connection_info'])
        if parse_result.scheme and parse_result.netloc:
            connection_info_html = f"""<a href="{challenge['connection_info']}">{challenge['connection_info']}</a>"""
        else:
            connection_info_html = f"<code>{challenge['connection_info']}</code>"

    category = challenge['category']
    assert CATEGORY_PATTERN.fullmatch(category)

    files_html = ''
    if challenge['files']:
        for filepath in challenge['files']:
            match = FILE_PATTERN.search(filepath)
            assert match
            filename = match.group(0)
            if files_html:
                files_html += ' · '
            files_html += f'<a href="./files/{filename}">{filename}</a>'

    assert all(TAG_PATTERN.fullmatch(tag) for tag in challenge['tags'])
    tags_html = ' · '.join(f'<code>{tag}</code>' for tag in challenge['tags'])

    output_file.write(f"""\
# [{category}] {name}

<table><tbody>
<tr><th>Value</th><td>{value} pts</td></tr>
""")
    if tags_html:
        output_file.write(f'<tr><th>Tags</th><td>{tags_html}</td></tr>\n')
    if author:
        output_file.write(f'<tr><th>Author</th><td>{author}</td></tr>\n')
    if connection_info_html:
        output_file.write(f'<tr><th>Connection info</th><td>{connection_info_html}</td></tr>\n')
    if files_html:
        output_file.write(f'<tr><th>Files</th><td>{files_html}</td></tr>\n')
    output_file.write('</tbody></table>\n\n')
    if description_md:
        output_file.write(f'{description_md}\n\n')
    output_file.write('---\n')


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default=sys.stdout, type=argparse.FileType('xt'))
    parser.add_argument('challenge', type=argparse.FileType('rt'))
    args = parser.parse_args()

    generate_skeleton(args.output, args.challenge)


if __name__ == '__main__':
    main()
