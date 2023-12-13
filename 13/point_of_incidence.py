#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterator
from itertools import chain
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

ASH = '.'
ROCKS = '#'

COLUMN_REFLECTION_SUMMARY_FACTOR = 1
ROW_REFLECTION_SUMMARY_FACTOR = 100


class Pattern(NamedTuple):
    width: int
    height: int
    columns: tuple[int, ...] = ()
    rows: tuple[int, ...] = ()

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> 'Pattern':
        width = -1
        height = 0
        columns: list[int] = []
        rows: list[int] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                assert not columns
                columns = [0] * width
            elif len(line) == 0:
                break
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')

            height += 1
            row = 0
            for (x, char) in enumerate(line):
                assert char in {ASH, ROCKS}
                bit = char == ROCKS
                columns[x] = (columns[x] << 1) | bit
                row = (row << 1) | bit
            rows.append(row)
        return Pattern(width, height, tuple(columns), tuple(rows))

    def summarise(self) -> int:
        """
        >>> Pattern.from_lines(iter([
        ...     '#.##..##.',
        ...     '..#.##.#.',
        ...     '##......#',
        ...     '##......#',
        ...     '..#.##.#.',
        ...     '..##..##.',
        ...     '#.#.##.#.',
        ... ])).summarise()
        5
        >>> Pattern.from_lines(iter([
        ...     '#...##..#',
        ...     '#....#..#',
        ...     '..##..###',
        ...     '#####.##.',
        ...     '#####.##.',
        ...     '..##..###',
        ...     '#....#..#',
        ... ])).summarise()
        400

        >>> Pattern.from_lines(iter([
        ...     '#..###.##.#.#...#',
        ...     '#.##.....#.###.#.',
        ...     '#.##..#.###.#.#.#',
        ...     '##........#..###.',
        ...     '#..##.#.###..#.#.',
        ...     '#..#.#...#....##.',
        ...     '#..#.#...#....##.',
        ...     '#..##.#.###..#.#.',
        ...     '##........#..###.',
        ...     '#.##..#.###.#.#.#',
        ...     '#.##.....#.###.#.',
        ...     '#..###.##...#...#',
        ...     '.##...##..#..##..',
        ...     '####.#...#...##..',
        ...     '..##.#..#..#.#.#.',
        ...     '##.##.#.#..#.#..#',
        ...     '##.##.#.#..#.#..#',
        ... ])).summarise()
        1600
        """
        best_reflection_length = 0
        best_summary = 0
        for x in range(0, self.width - 1):
            if self.columns[x] != self.columns[x + 1]:
                continue
            reflection_length = min(x + 1, self.width - x - 1)
            if reflection_length <= best_reflection_length:
                continue
            if tuple(reversed(self.columns[x + 1 - reflection_length:x + 1])) != self.columns[x + 1:x + 1 + reflection_length]:
                continue
            best_reflection_length = reflection_length
            best_summary = COLUMN_REFLECTION_SUMMARY_FACTOR * (x + 1)
        for y in range(0, self.height - 1):
            if self.rows[y] != self.rows[y + 1]:
                continue
            reflection_length = min(y + 1, self.height - y - 1)
            if reflection_length <= best_reflection_length:
                continue
            if tuple(reversed(self.rows[y + 1 - reflection_length:y + 1])) != self.rows[y + 1:y + 1 + reflection_length]:
                continue
            best_reflection_length = reflection_length
            best_summary = ROW_REFLECTION_SUMMARY_FACTOR * (y + 1)
        return best_summary


def patterns_from_lines(lines: Iterator[str]) -> Iterator[Pattern]:
    while True:
        try:
            line = next(lines)
        except StopIteration:
            return
        yield Pattern.from_lines(chain.from_iterable(((line,), lines)))


def summarise_notes(lines: Iterator[str]) -> int:
    """
    >>> summarise_notes(iter([
    ...     '#.##..##.',
    ...     '..#.##.#.',
    ...     '##......#',
    ...     '##......#',
    ...     '..#.##.#.',
    ...     '..##..##.',
    ...     '#.#.##.#.',
    ...     '',
    ...     '#...##..#',
    ...     '#....#..#',
    ...     '..##..###',
    ...     '#####.##.',
    ...     '#####.##.',
    ...     '..##..###',
    ...     '#....#..#',
    ... ]))
    405
    """
    patterns = patterns_from_lines(lines)
    return sum(pattern.summarise() for pattern in patterns)


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=argparse.FileType('rt'))
    args = parser.parse_args()
    lines = (line.rstrip('\n') for line in args.input)

    if args.part == 1:
        print(summarise_notes(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
