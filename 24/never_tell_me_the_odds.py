#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from itertools import combinations
from math import isclose
import re
from typing import NamedTuple


########################################################################################################################
# Hailstones
########################################################################################################################

class Vec3(NamedTuple):
    x: int
    y: int
    z: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z})'


class Hailstone(NamedTuple):
    position: Vec3
    velocity: Vec3


HAILSTONE_SNAPSHOT_PATTERN = re.compile(r'^(-?\d+), *(-?\d+), *(-?\d+) *@ *(-?\d+), *(-?\d+), *(-?\d+)$')


class Snapshot(NamedTuple):
    hailstones: set[Hailstone]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Snapshot':
        hailstones: set[Hailstone] = set()
        for line in lines:
            match = HAILSTONE_SNAPSHOT_PATTERN.fullmatch(line)
            if not match:
                raise ValueError(f'Invalid hailstone snapshot: {line!r} '
                                 f'does not match expected pattern /{HAILSTONE_SNAPSHOT_PATTERN.pattern}/')
            (px, py, pz, vx, vy, vz) = (int(raw_number) for raw_number in match.groups())
            position = Vec3(px, py, pz)
            velocity = Vec3(vx, vy, vz)
            hailstones.add(Hailstone(position, velocity))
        return Snapshot(hailstones)

    def count_intersections_within_test_area(self, min_xy: int, max_xy: int) -> int:
        """
        >>> Snapshot.from_lines([
        ...     '19, 13, 30 @ -2,  1, -2',
        ...     '18, 19, 22 @ -1, -1, -2',
        ...     '20, 25, 34 @ -2, -2, -4',
        ...     '12, 31, 28 @ -1, -2, -1',
        ...     '20, 19, 15 @  1, -5, -3',
        ... ]).count_intersections_within_test_area(7, 27)
        2
        """
        intersections = 0
        for (a, b) in combinations(self.hailstones, 2):
            # <https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment>
            (x1, y1, _) = a.position
            (x2, y2) = (a.position.x + a.velocity.x, a.position.y + a.velocity.y)
            (x3, y3, _) = b.position
            (x4, y4) = (b.position.x + b.velocity.x, b.position.y + b.velocity.y)
            denominator = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
            try:
                t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / denominator
                u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / denominator
            except ZeroDivisionError:
                # Paths were parallel.
                continue
            if t < 0 or u < 0:
                # Intersection occurred in the path for at least one path.
                continue
            px = x1 + (t * a.velocity.x)
            assert isclose(px, x3 + (u * b.velocity.x))
            py = y1 + (t * a.velocity.y)
            assert isclose(py, y3 + (u * b.velocity.y))
            if (min_xy <= px <= max_xy) and (min_xy <= py <= max_xy):
                intersections += 1
        return intersections


########################################################################################################################
# Part 1
########################################################################################################################

def count_intersections_within_test_area(lines: Iterable[str]) -> int:
    snapshot = Snapshot.from_lines(lines)
    return snapshot.count_intersections_within_test_area(200_000_000_000_000, 400_000_000_000_000)


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
        print(count_intersections_within_test_area(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
