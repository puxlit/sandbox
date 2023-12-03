#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from typing import NamedTuple, Optional


########################################################################################################################
# 2D geometry
########################################################################################################################

class Point(NamedTuple):
    x: int
    y: int

    def intersects(self, aabb: 'AABB') -> bool:
        (x, y) = self
        ((x0, y0), (x1, y1)) = aabb
        return (x0 <= x <= x1) and (y0 <= y <= y1)

    def is_before(self, aabb: 'AABB') -> bool:
        (x, y) = self
        (x0, y0) = aabb.min_
        return (y < y0) or ((y == y0) and (x < x0))

    def is_after(self, aabb: 'AABB') -> bool:
        (x, y) = self
        (x1, y1) = aabb.max_
        return (y1 < y) or ((y1 == y) and (x1 < x))


class AABB(NamedTuple):
    min_: Point
    max_: Point


########################################################################################################################
# Part 1
########################################################################################################################

BLANK_SPACE = '.'
# Derived valid symbols via `cat input.txt | tr -d $'\n.0123456789' | fold -bw1 | LC_ALL=C sort -u`.
VALID_SYMBOLS = {'#', '$', '%', '&', '*', '+', '-', '/', '=', '@'}


class Number(NamedTuple):
    value: int
    aabb: AABB
    is_part_number: bool

    def as_part_number(self) -> 'Number':
        assert not self.is_part_number
        return Number(self.value, self.aabb, True)


class Symbol(NamedTuple):
    value: str
    point: Point


def extract_part_numbers(lines: Iterable[str]) -> Iterator[int]:
    """
    >>> list(extract_part_numbers([
    ...     '467..114..',
    ...     '...*......',
    ...     '..35..633.',
    ...     '......#...',
    ...     '617*......',
    ...     '.....+.58.',
    ...     '..592.....',
    ...     '......755.',
    ...     '...$.*....',
    ...     '.664.598..',
    ... ]))
    [467, 35, 633, 617, 592, 755, 664, 598]
    >>> list(extract_part_numbers([
    ...     '.........',
    ...     '......',
    ... ]))
    Traceback (most recent call last):
        ...
    ValueError: Width of line 2 differs from line 1 (6 ≠ 9)
    >>> list(extract_part_numbers([
    ...     '.....',
    ...     '..!..',
    ...     '.....',
    ... ]))
    Traceback (most recent call last):
        ...
    ValueError: Unexpected character '!' at line 2, column 3
    >>> list(extract_part_numbers([
    ...     '12..34#',
    ...     '..$.56.',
    ... ]))
    [12, 34, 56]
    """
    candidate_numbers: list[Number] = []
    candidate_symbols: list[Symbol] = []

    def handle_new_number(y: int, number: Number) -> Iterator[int]:
        i = 0
        while i < len(candidate_symbols):
            symbol = candidate_symbols[i]
            if symbol.point.is_before(number.aabb):
                # The new number's AABB is well after this symbol, so this symbol cannot possibly intersect with any
                # future number's AABB.
                del candidate_symbols[i]
            elif symbol.point.intersects(number.aabb):
                if not candidate_numbers:
                    yield number.value
                else:
                    candidate_numbers.append(number.as_part_number())
                return
            else:
                i += 1
        candidate_numbers.append(number)

    def handle_new_symbol(symbol: Symbol) -> Iterator[int]:
        i = 0
        while i < len(candidate_numbers):
            number = candidate_numbers[i]
            if number.is_part_number:
                if i == 0:
                    yield number.value
                    del candidate_numbers[i]
                else:
                    i += 1
            elif symbol.point.is_after(number.aabb):
                # This number's AABB is well before the new symbol, and cannot possibly be a part number anymore.
                assert i == 0
                del candidate_numbers[i]
            elif symbol.point.intersects(number.aabb):
                if i == 0:
                    yield number.value
                    del candidate_numbers[i]
                else:
                    candidate_numbers[i] = number.as_part_number()
                    i += 1
            else:
                i += 1
        # Save this symbol for any future numbers' AABB it might intersect with.
        candidate_symbols.append(symbol)

    partial_number: Optional[tuple[int, Point]] = None

    def build_number(pos: Point, digit: int) -> None:
        assert 0 <= digit <= 9, f'`build_number` called with non-digit {digit}'

        nonlocal partial_number
        if partial_number is None:
            partial_number = (digit, pos)
            return

        (number, start_pos) = partial_number
        assert pos.y == start_pos.y, (
            f'Cannot build number across multiple lines; parsed {number} '
            f'starting on line {start_pos.y + 1}, column {start_pos.x + 1} and '
            f'continuing on line {pos.y + 1}, column {pos.x + 1} (inclusive)'
        )
        assert pos.x > start_pos.x, (
            f'Cannot build number backwards; parsed {number} on line {start_pos.y + 1} '
            f'starting on column {start_pos.x + 1} and '
            f'continuing on column {pos.x + 1} (inclusive)'
        )
        partial_number = ((number * 10) + digit, start_pos)

    def finish_number(exclusive_end_pos: Point) -> Iterator[int]:
        nonlocal partial_number
        if partial_number is None:
            return

        (number, start_pos) = partial_number
        # We must always call `finish_number` at the end of a line.
        assert exclusive_end_pos.y == start_pos.y, (
            f'Cannot build number across multiple lines; parsed {number} '
            f'starting on line {start_pos.y + 1}, column {start_pos.x + 1} and '
            f'ending on line {exclusive_end_pos.y + 1}, column {exclusive_end_pos.x} (inclusive)'
        )
        assert exclusive_end_pos.x > start_pos.x, (
            f'Cannot build number backwards; parsed {number} on line {start_pos.y + 1} '
            f'starting on column {start_pos.x + 1} and '
            f'ending on column {exclusive_end_pos.x} (inclusive)'
        )
        # For intersecton testing purposes, it doesn't matter if these coordinates are outside of the dimensions of the
        # schematic.
        min_ = Point(start_pos.x - 1, start_pos.y - 1)
        max_ = Point(exclusive_end_pos.x, exclusive_end_pos.y + 1)
        yield from handle_new_number(exclusive_end_pos.y, Number(number, AABB(min_, max_), False))
        partial_number = None

    for (y, line) in enumerate(lines):
        # Ensure width is consistent across lines.
        if y == 0:
            width = len(line)
        elif len(line) != width:
            raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')

        for (x, char) in enumerate(line):
            pos = Point(x, y)
            if char == BLANK_SPACE:
                yield from finish_number(pos)
            elif char.isdigit():
                build_number(pos, int(char))
            elif char in VALID_SYMBOLS:
                yield from finish_number(pos)
                yield from handle_new_symbol(Symbol(char, pos))
            else:
                raise ValueError(f'Unexpected character {char!r} at line {y + 1}, column {x + 1}')
        yield from finish_number(Point(x + 1, y))


def sum_part_numbers(lines: Iterable[str]) -> int:
    """
    >>> sum_part_numbers([
    ...     '467..114..',
    ...     '...*......',
    ...     '..35..633.',
    ...     '......#...',
    ...     '617*......',
    ...     '.....+.58.',
    ...     '..592.....',
    ...     '......755.',
    ...     '...$.*....',
    ...     '.664.598..',
    ... ])
    4361
    """
    return sum(extract_part_numbers(lines))


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
        print(sum_part_numbers(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
