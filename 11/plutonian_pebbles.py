#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from functools import cache


########################################################################################################################
# Part 1
########################################################################################################################

def parse_stones(line: str) -> tuple[int, ...]:
    return tuple(map(int, line.split()))


def transform_stone(stone: int) -> tuple[int, ...]:
    """
    >>> transform_stone(0)
    (1,)
    >>> transform_stone(10)
    (1, 0)
    >>> transform_stone(99)
    (9, 9)
    >>> transform_stone(1000)
    (10, 0)
    >>> transform_stone(1)
    (2024,)
    >>> transform_stone(999)
    (2021976,)
    """
    if stone == 0:
        return (1,)

    stone_digits = str(stone)
    (half_num_stone_digits, remainder) = divmod(len(stone_digits), 2)
    if remainder == 0:
        left_stone = int(stone_digits[:half_num_stone_digits])
        right_stone = int(stone_digits[half_num_stone_digits:])
        return (left_stone, right_stone)

    return (stone * 2024,)


@cache
def count_stones_after_blinks(stones: tuple[int, ...], blinks: int) -> int:
    """
    >>> count_stones_after_blinks((0, 1, 10, 99, 999), 1)
    7
    >>> count_stones_after_blinks((125, 17), 1)
    3
    >>> count_stones_after_blinks((125, 17), 2)
    4
    >>> count_stones_after_blinks((125, 17), 3)
    5
    >>> count_stones_after_blinks((125, 17), 4)
    9
    >>> count_stones_after_blinks((125, 17), 5)
    13
    >>> count_stones_after_blinks((125, 17), 6)
    22
    >>> count_stones_after_blinks((125, 17), 25)
    55312
    """
    assert blinks >= 0
    if blinks == 0:
        return len(stones)
    return sum(count_stones_after_blinks(transform_stone(stone), blinks - 1) for stone in stones)


def count_stones_after_25_blinks(lines: Iterable[str]) -> int:
    """
    >>> count_stones_after_25_blinks(['125 17'])
    55312
    """
    stones = parse_stones(next(iter(lines)))
    return count_stones_after_blinks(stones, 25)


########################################################################################################################
# Part 2
########################################################################################################################

def count_stones_after_75_blinks(lines: Iterable[str]) -> int:
    stones = parse_stones(next(iter(lines)))
    return count_stones_after_blinks(stones, 75)


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
        print(count_stones_after_25_blinks(lines))
    elif args.part == 2:
        print(count_stones_after_75_blinks(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
