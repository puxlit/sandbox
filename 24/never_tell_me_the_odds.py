#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from itertools import combinations, islice
from math import isclose
import re
from typing import NamedTuple, Optional


########################################################################################################################
# Hailstones
########################################################################################################################

class Vec3(NamedTuple):
    x: int
    y: int
    z: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z})'


class Vec4(NamedTuple):
    x: int
    y: int
    z: int
    t: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z}, {self.t})'

    def __sub__(self, other: 'Vec4') -> 'Vec4':
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        t = self.t - other.t
        return Vec4(x, y, z, t)


class Projectile(NamedTuple):
    position: Vec3
    velocity: Vec3

    @classmethod
    def from_points(cls, p0: Vec4, p1: Vec4) -> 'Projectile':
        assert p0 != p1
        assert (t_delta := p1.t - p0.t) != 0
        (dx, remainder) = divmod(p1.x - p0.x, t_delta)
        assert remainder == 0
        x0 = p0.x - (dx * p0.t)
        (dy, remainder) = divmod(p1.y - p0.y, t_delta)
        assert remainder == 0
        y0 = p0.y - (dy * p0.t)
        (dz, remainder) = divmod(p1.z - p0.z, t_delta)
        assert remainder == 0
        z0 = p0.z - (dz * p0.t)
        return Projectile(Vec3(x0, y0, z0), Vec3(dx, dy, dz))

    def __call__(self, t: int) -> Vec4:
        x = self.position.x + (self.velocity.x * t)
        y = self.position.y + (self.velocity.y * t)
        z = self.position.z + (self.velocity.z * t)
        return Vec4(x, y, z, t)

    def get_collision(self, other: 'Projectile') -> Optional[Vec4]:
        assert self != other  # Trajectories mustn't be coincident.
        if self.velocity.x != other.velocity.x:
            (t, remainder) = divmod(other.position.x - self.position.x, self.velocity.x - other.velocity.x)
        elif self.velocity.y != other.velocity.y:
            (t, remainder) = divmod(other.position.y - self.position.y, self.velocity.y - other.velocity.y)
        elif self.velocity.z != other.velocity.z:
            (t, remainder) = divmod(other.position.z - self.position.z, self.velocity.z - other.velocity.z)
        else:
            return None  # Trajectories are parallel.
        if remainder != 0:
            return None  # No integer solution.
        if t <= 0:
            return None  # Potential collision occurs before the start of time.
        if (collision := self(t)) != other(t):
            return None  # Trajectories intersect when projected onto at least one coordinate plane, but not all.
        return collision


class Hyperplane(NamedTuple):
    normal: Vec4
    constant: int

    @classmethod
    def from_projectiles(cls, h0: Projectile, h1: Projectile) -> 'Hyperplane':
        assert h0 != h1  # Trajectories mustn't be coincident.
        (p0, p1, u0, u1) = (h0(0), h0(1), h1(0), h1(1))
        (u, v, w) = (p1 - p0, u0 - p0, u1 - p0)
        assert u != v != w
        # Calculate the normal from the above three vectors. For a refresher, see the following.
        #
        #   - [Laplace expansion for computing determinants | Lecture 29 | Matrix Algebra for Engineers](https://www.youtube.com/watch?v=cAARX18-74g)
        #
        # First, compute the second minors.
        minor_34_12 = (v.x * w.y) - (v.y * w.x)
        minor_34_13 = (v.x * w.z) - (v.z * w.x)
        minor_34_14 = (v.x * w.t) - (v.t * w.x)
        minor_34_23 = (v.y * w.z) - (v.z * w.y)
        minor_34_24 = (v.y * w.t) - (v.t * w.y)
        minor_34_34 = (v.z * w.t) - (v.t * w.z)
        # Next, compute the first minors.
        minor_1_1 = (u.y * minor_34_34) - (u.z * minor_34_24) + (u.t * minor_34_23)
        minor_1_2 = (u.x * minor_34_34) - (u.z * minor_34_14) + (u.t * minor_34_13)
        minor_1_3 = (u.x * minor_34_24) - (u.y * minor_34_14) + (u.t * minor_34_12)
        minor_1_4 = (u.x * minor_34_23) - (u.y * minor_34_13) + (u.z * minor_34_12)
        # Finally, compute the normal vector.
        nx = minor_1_1
        ny = -minor_1_2
        nz = minor_1_3
        nt = -minor_1_4
        constant = (nx * p0.x) + (ny * p0.y) + (nz * p0.z) + (nt * p0.t)
        return Hyperplane(Vec4(nx, ny, nz, nt), constant)

    def get_intersection(self, h: Projectile) -> Optional[Vec4]:
        numerator = self.constant - (self.normal.x * h.position.x) - (self.normal.y * h.position.y) - (self.normal.z * h.position.z)
        denominator = (self.normal.x * h.velocity.x) + (self.normal.y * h.velocity.y) + (self.normal.z * h.velocity.z) + self.normal.t
        if denominator == 0:
            return None
        (t, remainder) = divmod(numerator, denominator)
        if remainder != 0:
            return None
        if t <= 0:
            return None
        return h(t)


HAILSTONE_SNAPSHOT_PATTERN = re.compile(r'^(-?\d+), *(-?\d+), *(-?\d+) *@ *(-?\d+), *(-?\d+), *(-?\d+)$')


class Snapshot(NamedTuple):
    hailstones: set[Projectile]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Snapshot':
        hailstones: set[Projectile] = set()
        for line in lines:
            match = HAILSTONE_SNAPSHOT_PATTERN.fullmatch(line)
            if not match:
                raise ValueError(f'Invalid hailstone snapshot: {line!r} '
                                 f'does not match expected pattern /{HAILSTONE_SNAPSHOT_PATTERN.pattern}/')
            (px, py, pz, vx, vy, vz) = (int(raw_number) for raw_number in match.groups())
            position = Vec3(px, py, pz)
            velocity = Vec3(vx, vy, vz)
            hailstones.add(Projectile(position, velocity))
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

    def calculate_rock_starting_vector(self) -> tuple[Projectile, dict[Projectile, int]]:
        """
        >>> (rock, collisions) = Snapshot.from_lines([
        ...     '19, 13, 30 @ -2,  1, -2',
        ...     '18, 19, 22 @ -1, -1, -2',
        ...     '20, 25, 34 @ -2, -2, -4',
        ...     '12, 31, 28 @ -1, -2, -1',
        ...     '20, 19, 15 @  1, -5, -3',
        ... ]).calculate_rock_starting_vector()
        >>> rock
        Projectile(position=Vec3(x=24, y=13, z=10), velocity=Vec3(x=-3, y=1, z=2))
        >>> collisions[Projectile(Vec3(19, 13, 30), Vec3(-2,  1, -2))]
        5
        >>> collisions[Projectile(Vec3(18, 19, 22), Vec3(-1, -1, -2))]
        3
        >>> collisions[Projectile(Vec3(20, 25, 34), Vec3(-2, -2, -4))]
        4
        >>> collisions[Projectile(Vec3(12, 31, 28), Vec3(-1, -2, -1))]
        6
        >>> collisions[Projectile(Vec3(20, 19, 15), Vec3( 1, -5, -3))]
        1
        """
        if len(self.hailstones) < 4:
            raise ValueError('Need at least 4 hailstones to calculate a unique solution')

        # Part one: figuring out the rock's starting position and velocity
        (h0, h1, h2, h3) = islice(self.hailstones, 4)
        hyperplane = Hyperplane.from_projectiles(h0, h1)
        assert (p0 := hyperplane.get_intersection(h2)) is not None
        assert (p1 := hyperplane.get_intersection(h3)) is not None
        rock = Projectile.from_points(p0, p1)

        # Part two: verification
        collisions: dict[Projectile, int] = {}
        for hailstone in self.hailstones:
            assert (collision := rock.get_collision(hailstone))
            collisions[hailstone] = collision.t

        return (rock, collisions)


########################################################################################################################
# Part 1
########################################################################################################################

def count_intersections_within_test_area(lines: Iterable[str]) -> int:
    snapshot = Snapshot.from_lines(lines)
    return snapshot.count_intersections_within_test_area(200_000_000_000_000, 400_000_000_000_000)


########################################################################################################################
# Part 2
########################################################################################################################

def sum_coordinates_for_rock_starting_position(lines: Iterable[str]) -> int:
    """
    >>> sum_coordinates_for_rock_starting_position([
    ...     '19, 13, 30 @ -2,  1, -2',
    ...     '18, 19, 22 @ -1, -1, -2',
    ...     '20, 25, 34 @ -2, -2, -4',
    ...     '12, 31, 28 @ -1, -2, -1',
    ...     '20, 19, 15 @  1, -5, -3',
    ... ])
    47
    """
    snapshot = Snapshot.from_lines(lines)
    (rock, _) = snapshot.calculate_rock_starting_vector()
    (x, y, z) = rock.position
    return x + y + z


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
    elif args.part == 2:
        print(sum_coordinates_for_rock_starting_position(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
