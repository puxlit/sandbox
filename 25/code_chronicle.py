#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from typing import NamedTuple


########################################################################################################################
# Keys and keyholes
########################################################################################################################

WIDTH = 5
MAX_HEIGHT = 5
START_OF_KEY_LINE = END_OF_LOCK_LINE = '.' * WIDTH
START_OF_LOCK_LINE = END_OF_KEY_LINE = '#' * WIDTH


class Schematics(NamedTuple):
    keys: tuple[tuple[int, int, int, int, int], ...]
    locks: tuple[tuple[int, int, int, int, int], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Schematics':
        """
        >>> Schematics.from_lines([
        ...     '#####',
        ...     '.####',
        ...     '.####',
        ...     '.####',
        ...     '.#.#.',
        ...     '.#...',
        ...     '.....',
        ...     '',
        ...     '#####',
        ...     '##.##',
        ...     '.#.##',
        ...     '...##',
        ...     '...#.',
        ...     '...#.',
        ...     '.....',
        ...     '',
        ...     '.....',
        ...     '#....',
        ...     '#....',
        ...     '#...#',
        ...     '#.#.#',
        ...     '#.###',
        ...     '#####',
        ...     '',
        ...     '.....',
        ...     '.....',
        ...     '#.#..',
        ...     '###..',
        ...     '###.#',
        ...     '###.#',
        ...     '#####',
        ...     '',
        ...     '.....',
        ...     '.....',
        ...     '.....',
        ...     '#....',
        ...     '#.#..',
        ...     '#.#.#',
        ...     '#####',
        ... ])
        Schematics(keys=((5, 0, 2, 1, 3), (4, 3, 4, 0, 2), (3, 0, 2, 0, 1)), locks=((0, 5, 3, 4, 3), (1, 2, 0, 5, 3)))
        """
        keys: list[tuple[int, int, int, int, int]] = []
        locks: list[tuple[int, int, int, int, int]] = []
        lines_iter = iter(enumerate(lines))
        while True:
            try:
                while True:
                    (line_number, line) = next(lines_iter)
                    if line != '':
                        break
            except StopIteration:
                break
            if line == START_OF_KEY_LINE:
                is_key = True
                schematic = 'key'
                void_mapping = {'.': True, '#': False}
                columns = [0] * WIDTH
                expected_end_of_schematic_line = END_OF_KEY_LINE
            elif line == START_OF_LOCK_LINE:
                is_key = False
                schematic = 'lock'
                void_mapping = {'#': True, '.': False}
                columns = [MAX_HEIGHT] * WIDTH
                expected_end_of_schematic_line = END_OF_LOCK_LINE
            else:
                raise ValueError(f'Line {line_number + 1} does not look like the start of a key or lock: {line!r}')
            for y in range(MAX_HEIGHT):
                (line_number, line) = next(lines_iter)
                if len(line) != WIDTH:
                    raise ValueError(f'Line {line_number + 1} does not have the expected {schematic} width of {WIDTH}: {line!r}')
                for x in range(WIDTH):
                    if void_mapping[line[x]]:
                        if not columns[x] == (0 if is_key else MAX_HEIGHT):
                            raise ValueError(f'Line {line_number + 1} column {x + 1} has discontinuity in {schematic} {"bit" if is_key else "pin"}: {line!r}')
                    else:
                        columns[x] += (1 if is_key else -1)
            (line_number, line) = next(lines_iter)
            if line != expected_end_of_schematic_line:
                raise ValueError(f'Line {line_number + 1} does not look like the end of a {schematic}: {line!r}')
            (keys if is_key else locks).append((columns[0], columns[1], columns[2], columns[3], columns[4]))
        return Schematics(tuple(keys), tuple(locks))

    def count_fitting_key_lock_pairs(self) -> int:
        count = 0
        for lock in self.locks:
            for key in self.keys:
                if all(((pin_height + bit_height) <= MAX_HEIGHT) for (pin_height, bit_height) in zip(lock, key)):
                    count += 1
        return count


########################################################################################################################
# Part 1
########################################################################################################################

def count_fitting_key_lock_pairs(lines: Iterable[str]) -> int:
    """
    >>> count_fitting_key_lock_pairs([
    ...     '#####',
    ...     '.####',
    ...     '.####',
    ...     '.####',
    ...     '.#.#.',
    ...     '.#...',
    ...     '.....',
    ...     '',
    ...     '#####',
    ...     '##.##',
    ...     '.#.##',
    ...     '...##',
    ...     '...#.',
    ...     '...#.',
    ...     '.....',
    ...     '',
    ...     '.....',
    ...     '#....',
    ...     '#....',
    ...     '#...#',
    ...     '#.#.#',
    ...     '#.###',
    ...     '#####',
    ...     '',
    ...     '.....',
    ...     '.....',
    ...     '#.#..',
    ...     '###..',
    ...     '###.#',
    ...     '###.#',
    ...     '#####',
    ...     '',
    ...     '.....',
    ...     '.....',
    ...     '.....',
    ...     '#....',
    ...     '#.#..',
    ...     '#.#.#',
    ...     '#####',
    ... ])
    3
    """
    schematics = Schematics.from_lines(lines)
    return schematics.count_fitting_key_lock_pairs()


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
        print(count_fitting_key_lock_pairs(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
