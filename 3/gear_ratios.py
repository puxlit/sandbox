#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import NamedTuple, Optional, Union


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
# Engine schematic
########################################################################################################################

BLANK_SPACE = '.'
GEAR_SYMBOL = '*'
# Derived valid symbols via `cat input.txt | tr -d $'\n.0123456789' | fold -bw1 | LC_ALL=C sort -u`.
VALID_SYMBOLS = {'#', '$', '%', '&', GEAR_SYMBOL, '+', '-', '/', '=', '@'}


@dataclass
class Number:
    value: int
    aabb: AABB
    is_part_number: bool = False
    is_yielded: bool = False

    def flag_as_part_number(self) -> None:
        assert not self.is_part_number
        self.is_part_number = True

    def flag_as_yielded(self) -> None:
        assert self.is_part_number
        assert not self.is_yielded
        self.is_yielded = True


@dataclass
class Symbol:
    value: str
    point: Point
    num_adjacent_part_numbers: int = 0
    gear_ratio: int = 1

    def intersects(self, number: Number) -> bool:
        return self.point.intersects(number.aabb)

    def is_before(self, number: Number) -> bool:
        return self.point.is_before(number.aabb)

    def is_after(self, number: Number) -> bool:
        return self.point.is_after(number.aabb)

    def is_gear(self) -> bool:
        return (self.value == GEAR_SYMBOL) and (self.num_adjacent_part_numbers == 2)

    def associate_with_part_number(self, number: Number) -> None:
        self.num_adjacent_part_numbers += 1
        self.gear_ratio *= number.value


class PartNumber(NamedTuple):
    value: int


class GearRatio(NamedTuple):
    value: int


def parse_schematic(lines: Iterable[str]) -> Iterator[Union[PartNumber, GearRatio]]:
    candidate_numbers: list[Number] = []
    candidate_symbols: list[Symbol] = []

    def handle_new_number(number: Number) -> Iterator[Union[PartNumber, GearRatio]]:
        i = 0
        while i < len(candidate_symbols):
            symbol = candidate_symbols[i]
            if symbol.is_before(number):
                # The new number's AABB is well after this symbol, so this symbol cannot possibly intersect with any
                # future number's AABB.
                assert i == 0
                if symbol.is_gear():
                    yield GearRatio(symbol.gear_ratio)
                del candidate_symbols[i]
                continue
            if symbol.intersects(number):
                if not number.is_part_number:
                    number.flag_as_part_number()
                    if not candidate_numbers:
                        yield PartNumber(number.value)
                        number.flag_as_yielded()
                symbol.associate_with_part_number(number)
            else:
                assert not symbol.is_after(number)
            i += 1
        candidate_numbers.append(number)

    def handle_new_symbol(symbol: Symbol) -> Iterator[Union[PartNumber, GearRatio]]:
        i = 0
        while i < len(candidate_numbers):
            number = candidate_numbers[i]
            if symbol.is_after(number):
                # This number's AABB is well before the new symbol, and cannot possibly be a part number anymore.
                assert i == 0
                if number.is_part_number and not number.is_yielded:
                    yield PartNumber(number.value)
                del candidate_numbers[i]
                continue
            if symbol.intersects(number):
                if not number.is_part_number:
                    number.flag_as_part_number()
                    if i == 0:
                        yield PartNumber(number.value)
                        number.flag_as_yielded()
                symbol.associate_with_part_number(number)
            else:
                assert not symbol.is_before(number)
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

    def finish_number(exclusive_end_pos: Point) -> Iterator[Union[PartNumber, GearRatio]]:
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
        yield from handle_new_number(Number(number, AABB(min_, max_)))
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
    # Hack to flush out any remaining part numbers and symbols.
    # TODO: Add unit test.
    yield from handle_new_symbol(Symbol('#', Point(x + 2, y + 2)))
    assert not candidate_numbers
    yield from handle_new_number(Number(0, AABB(Point(x + 2, y + 3), Point(x + 4, y + 5))))
    assert not candidate_symbols


########################################################################################################################
# Part 1
########################################################################################################################

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
    >>> list(extract_part_numbers([
    ...     '1.2.3',
    ...     '4#.$5',
    ...     '6.7.8'
    ... ]))
    [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(extract_part_numbers([
    ...     '#.$',
    ...     '.1.',
    ... ]))
    [1]
    """
    part_numbers = filter(lambda x: isinstance(x, PartNumber), parse_schematic(lines))
    return map(lambda x: x.value, part_numbers)


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
# Part 2
########################################################################################################################

def extract_gear_ratios(lines: Iterable[str]) -> Iterator[int]:
    """
    >>> list(extract_gear_ratios([
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
    [16345, 451490]
    >>> list(extract_gear_ratios([
    ...     '..2..#...3.#...11',
    ...     '..*..#..*..#.7*..',
    ...     '.....#.5...#...13',
    ... ]))
    [15]
    >>> list(extract_gear_ratios([
    ...     '.2',
    ...     '3*',
    ... ]))
    [6]
    >>> list(extract_gear_ratios([
    ...     '*2',
    ...     '3.',
    ... ]))
    [6]
    """
    gear_ratios = filter(lambda x: isinstance(x, GearRatio), parse_schematic(lines))
    return map(lambda x: x.value, gear_ratios)


def sum_gear_ratios(lines: Iterable[str]) -> int:
    """
    >>> sum_gear_ratios([
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
    467835
    """
    return sum(extract_gear_ratios(lines))


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
    elif args.part == 2:
        print(sum_gear_ratios(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
