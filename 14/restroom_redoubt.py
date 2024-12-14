#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from math import prod
import re
from typing import NamedTuple


########################################################################################################################
# Bathroom security
########################################################################################################################

ROBOT_CONFIG_PATTERN = re.compile(r'^p=(\d+),(\d+) v=(-?\d+),(-?\d+)$')
VESTIBULE_WIDTH = 101
VESTIBULE_HEIGHT = 103


class Robot(NamedTuple):
    x0: int
    y0: int
    dx: int
    dy: int

    @classmethod
    def from_line(cls, line: str) -> 'Robot':
        assert (match := ROBOT_CONFIG_PATTERN.fullmatch(line)) is not None
        return Robot(*map(int, match.groups()))

    def simulate(self, duration: int) -> tuple[int, int]:
        return (
            self.x0 + (self.dx * duration),
            self.y0 + (self.dy * duration),
        )


class Vestibule(NamedTuple):
    width: int
    height: int
    robots: tuple[Robot, ...]

    @classmethod
    def from_lines(cls, width: int, height: int, lines: Iterable[str]) -> 'Vestibule':
        assert (width % 2) == (height % 2) == 1
        robots = tuple(map(Robot.from_line, lines))
        return Vestibule(width, height, robots)

    def calculate_safety_factor(self, duration: int) -> int:
        """
        >>> Vestibule.from_lines(11, 7, [
        ...     'p=0,4 v=3,-3',
        ...     'p=6,3 v=-1,-3',
        ...     'p=10,3 v=-1,2',
        ...     'p=2,0 v=2,-1',
        ...     'p=0,0 v=1,3',
        ...     'p=3,0 v=-2,-2',
        ...     'p=7,6 v=-1,-3',
        ...     'p=3,0 v=-1,-2',
        ...     'p=9,3 v=2,3',
        ...     'p=7,3 v=-1,2',
        ...     'p=2,4 v=2,-3',
        ...     'p=9,5 v=-3,-3',
        ... ]).calculate_safety_factor(100)
        12
        """
        vertical_divider = self.width // 2
        horizontal_divider = self.height // 2
        quadrant_counts = [0, 0, 0, 0]
        for robot in self.robots:
            (x, y) = robot.simulate(duration)
            x %= self.width
            y %= self.height
            if (x == vertical_divider) or (y == horizontal_divider):
                continue
            quadrant_counts[((y > horizontal_divider) * 2) + (x > vertical_divider)] += 1
        return prod(quadrant_counts)


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_safety_factor_after_100_seconds(lines: Iterable[str]) -> int:
    vestibule = Vestibule.from_lines(VESTIBULE_WIDTH, VESTIBULE_HEIGHT, lines)
    return vestibule.calculate_safety_factor(100)


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
        print(calculate_safety_factor_after_100_seconds(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
