#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
from itertools import chain
import re
from typing import NamedTuple, Optional


########################################################################################################################
# Snapshot
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int
    z: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z})'


class Axis(Enum):
    X = 'x'
    Y = 'y'
    Z = 'z'


class Brick(NamedTuple):
    from_end: Coordinate
    to_end: Coordinate
    extending_direction: Optional[Axis]


BRICK_SNAPSHOT_PATTERN = re.compile(r'^(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)$')


class Snapshot(NamedTuple):
    settled_bricks: tuple[Brick, ...]
    voxels: tuple[tuple[tuple[Optional[Brick], ...], ...], ...]
    support_bricks: dict[Brick, set[Brick]]
    bricks_supported: dict[Brick, set[Brick]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Snapshot':
        falling_bricks: list[Brick] = []
        max_x = 0
        max_y = 0
        for line in lines:
            match = BRICK_SNAPSHOT_PATTERN.fullmatch(line)
            if not match:
                raise ValueError(f'Invalid brick snapshot: {line!r} '
                                 f'does not match expected pattern /{BRICK_SNAPSHOT_PATTERN.pattern}/')
            (from_x, from_y, from_z, to_x, to_y, to_z) = (int(raw_number) for raw_number in match.groups())
            from_end = Coordinate(from_x, from_y, from_z)
            to_end = Coordinate(to_x, to_y, to_z)
            if not all(number >= 0 for number in (from_x, from_y, to_x, to_y)):
                raise ValueError(f'All x/y coordinates should be ≥ 0 in {from_end} → {to_end}')
            if not to_z >= from_z >= 1:
                raise ValueError(f'All z coordinates should be ≥ 1 in {from_end} → {to_end}')
            if not sum((from_x != to_x, from_y != to_y, from_z != to_z)) <= 1:
                raise ValueError(f'Coordinates should vary in at most one axis in {from_end} → {to_end}')
            if not from_end <= to_end:
                raise ValueError(f'Smaller coordinates should appear first, but {from_end} ≰ {to_end}')
            brick = Brick(from_end, to_end, (
                Axis.X if from_x != to_x else
                Axis.Y if from_y != to_y else
                Axis.Z if from_z != to_z else
                None
            ))
            falling_bricks.append(brick)
            if to_x > max_x:
                max_x = to_x
            if to_y > max_y:
                max_y = to_y
        falling_bricks.sort(key=lambda brick: brick.from_end.z)

        settled_bricks: list[Brick] = []
        # Prepare the first layer, representing z=1.
        voxels: list[list[list[Optional[Brick]]]] = [[([None] * (max_x + 1)) for _ in range(max_y + 1)]]
        support_bricks: dict[Brick, set[Brick]] = {}
        bricks_supported: dict[Brick, set[Brick]] = {}
        while falling_bricks:
            brick = falling_bricks.pop(0)
            if brick.extending_direction == Axis.X:
                assert (brick.from_end.y, brick.from_end.z) == (brick.to_end.y, brick.to_end.z)
                new_from_z = max(chain.from_iterable(((-1,), (
                    z
                    for x in range(brick.from_end.x, brick.to_end.x + 1)
                    for z in range(len(voxels))
                    if voxels[z][brick.from_end.y][x] is not None
                )))) + 2
            elif brick.extending_direction == Axis.Y:
                assert (brick.from_end.x, brick.from_end.z) == (brick.to_end.x, brick.to_end.z)
                new_from_z = max(chain.from_iterable(((-1,), (
                    z
                    for y in range(brick.from_end.y, brick.to_end.y + 1)
                    for z in range(len(voxels))
                    if voxels[z][y][brick.from_end.x] is not None
                )))) + 2
            else:
                assert (brick.extending_direction == Axis.Z) or (brick.extending_direction is None)
                assert (brick.from_end.x, brick.from_end.y) == (brick.to_end.x, brick.to_end.y)
                new_from_z = max(chain.from_iterable(((-1,), (
                    z
                    for z in range(len(voxels))
                    if voxels[z][brick.from_end.y][brick.from_end.x] is not None
                )))) + 2
            new_to_z = new_from_z + (brick.to_end.z - brick.from_end.z)
            new_brick = Brick(Coordinate(brick.from_end.x, brick.from_end.y, new_from_z), Coordinate(brick.to_end.x, brick.to_end.y, new_to_z), brick.extending_direction)
            settled_bricks.append(new_brick)

            layers_to_add = new_to_z - len(voxels)  # No off-by-one error here; outermost array starts at z=1.
            if layers_to_add > 0:
                voxels += [[([None] * (max_x + 1)) for _ in range(max_y + 1)] for _ in range(layers_to_add)]
            supporting_bricks: set[Brick] = set()
            for z in range(new_brick.from_end.z - 1, new_brick.to_end.z):
                for y in range(new_brick.from_end.y, new_brick.to_end.y + 1):
                    for x in range(new_brick.from_end.x, new_brick.to_end.x + 1):
                        voxels[z][y][x] = new_brick
                        if (z == new_brick.from_end.z - 1) and (new_brick.from_end.z - 2 >= 0):
                            supporting_brick = voxels[z - 1][y][x]
                            if supporting_brick is not None:
                                supporting_bricks.add(supporting_brick)
                                bricks_supported[supporting_brick].add(new_brick)
            support_bricks[new_brick] = supporting_bricks
            bricks_supported[new_brick] = set()

        return Snapshot(tuple(settled_bricks), tuple(tuple(tuple(row) for row in plane) for plane in voxels), support_bricks, bricks_supported)

    def count_safely_disintegrable_bricks(self) -> int:
        safely_disintegrable_bricks = 0
        for brick in self.settled_bricks:
            if len(self.bricks_supported[brick]) == 0:
                # This brick doesn't support any other bricks; it's safely disintegrable.
                safely_disintegrable_bricks += 1
                continue
            if all(len(self.support_bricks[supported_brick]) > 1 for supported_brick in self.bricks_supported[brick]):
                # This brick supports other bricks, all of which have at least one different brick also supporting them.
                safely_disintegrable_bricks += 1
                continue
        return safely_disintegrable_bricks


########################################################################################################################
# Part 1
########################################################################################################################

def count_safely_disintegrable_bricks(lines: Iterable[str]) -> int:
    """
    >>> count_safely_disintegrable_bricks([
    ...     '1,0,1~1,2,1',
    ...     '0,0,2~2,0,2',
    ...     '0,2,3~2,2,3',
    ...     '0,0,4~0,2,4',
    ...     '2,0,5~2,2,5',
    ...     '0,1,6~2,1,6',
    ...     '1,1,8~1,1,9',
    ... ])
    5
    """
    snapshot = Snapshot.from_lines(lines)
    return snapshot.count_safely_disintegrable_bricks()


########################################################################################################################
# Part 2
########################################################################################################################

def sum_chain_reaction_falling_bricks(lines: Iterable[str]) -> int:
    """
    >>> sum_chain_reaction_falling_bricks([
    ...     '1,0,1~1,2,1',
    ...     '0,0,2~2,0,2',
    ...     '0,2,3~2,2,3',
    ...     '0,0,4~0,2,4',
    ...     '2,0,5~2,2,5',
    ...     '0,1,6~2,1,6',
    ...     '1,1,8~1,1,9',
    ... ])
    7
    """
    snapshot = Snapshot.from_lines(lines)
    chain_reaction_falling_bricks = 0
    cumulative_bricks_supported: dict[Brick, set[Brick]] = {}
    for brick in reversed(snapshot.settled_bricks):
        cumulative_bricks_supported[brick] = snapshot.bricks_supported[brick].copy()
        for supported_brick in snapshot.bricks_supported[brick]:
            cumulative_bricks_supported[brick] |= cumulative_bricks_supported[supported_brick]
        if len(snapshot.bricks_supported[brick]) == 0:
            # This brick doesn't support any other bricks; disintegrating it won't cause any other bricks to fall.
            continue
        potential_falling_bricks = cumulative_bricks_supported[brick].copy()
        not_falling_bricks: set[Brick] = set()
        for potential_falling_brick in potential_falling_bricks:
            if not snapshot.support_bricks[potential_falling_brick] <= potential_falling_bricks | {brick}:
                # This brick is supported by other bricks that aren't part of the chain reaction. Exclude 'em.
                not_falling_bricks.add(potential_falling_brick)
                not_falling_bricks |= cumulative_bricks_supported[potential_falling_brick]
        not_falling_bricks -= {brick}
        assert len(potential_falling_bricks) >= len(not_falling_bricks)
        chain_reaction_falling_bricks += len(potential_falling_bricks) - len(not_falling_bricks)
    return chain_reaction_falling_bricks


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
        print(count_safely_disintegrable_bricks(lines))
    elif args.part == 2:
        print(sum_chain_reaction_falling_bricks(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
