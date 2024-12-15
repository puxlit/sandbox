#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
from io import StringIO
from typing import NamedTuple, Optional

from typing_extensions import assert_never


########################################################################################################################
# Warehouse
########################################################################################################################

class Tile(Enum):
    EMPTY_SPACE = '.'
    WALL = '#'
    BOX = 'O'
    ROBOT = '@'


class Direction(Enum):
    UP = '^'
    DOWN = 'v'
    LEFT = '<'
    RIGHT = '>'


class Warehouse(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[Tile, ...], ...]
    robot_movements: tuple[Direction, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Warehouse':
        lines_iter = iter(lines)
        width = -1
        rows: list[tuple[Tile, ...]] = []
        for (y, line) in enumerate(lines_iter):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif line == '':
                y -= 1
                break
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            rows.append(tuple(Tile(char) for char in line))
        height = y + 1
        robot_movements = tuple(Direction(char) for line in lines_iter for char in line)
        return Warehouse(width, height, tuple(rows), robot_movements)

    def rasterise(self) -> str:
        rasterisation = StringIO()
        for y in range(self.height):
            leading_newline = '\n' if y > 0 else ''
            line = ''.join(tile.value for tile in self.rows[y])
            rasterisation.write(leading_newline + line)
        return rasterisation.getvalue()

    def simulate_robot_movements(self) -> 'Warehouse':
        """
        >>> print(Warehouse.from_lines([
        ...     '########',
        ...     '#..O.O.#',
        ...     '##@.O..#',
        ...     '#...O..#',
        ...     '#.#.O..#',
        ...     '#...O..#',
        ...     '#......#',
        ...     '########',
        ...     '',
        ...     '<^^>>>vv<v>>v<<',
        ... ]).simulate_robot_movements().rasterise())
        ########
        #....OO#
        ##.....#
        #.....O#
        #.#O@..#
        #...O..#
        #...O..#
        ########
        >>> print(Warehouse.from_lines([
        ...     '##########',
        ...     '#..O..O.O#',
        ...     '#......O.#',
        ...     '#.OO..O.O#',
        ...     '#..O@..O.#',
        ...     '#O#..O...#',
        ...     '#O..O..O.#',
        ...     '#.OO.O.OO#',
        ...     '#....O...#',
        ...     '##########',
        ...     '',
        ...     '<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^',
        ...     'vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v',
        ...     '><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<',
        ...     '<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^',
        ...     '^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><',
        ...     '^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^',
        ...     '>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^',
        ...     '<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>',
        ...     '^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>',
        ...     'v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^',
        ... ]).simulate_robot_movements().rasterise())
        ##########
        #.O.O.OOO#
        #........#
        #OO......#
        #OO@.....#
        #O#.....O#
        #O.....OO#
        #O.....OO#
        #OO....OO#
        ##########
        """
        robot_position: Optional[tuple[int, int]] = None
        rows = []
        for (y, immutable_row) in enumerate(self.rows):
            row = []
            for (x, tile) in enumerate(immutable_row):
                if tile == Tile.ROBOT:
                    assert robot_position is None
                    robot_position = (x, y)
                    row.append(Tile.EMPTY_SPACE)
                    continue
                row.append(tile)
            rows.append(row)
        assert robot_position is not None
        (robot_x, robot_y) = robot_position
        (max_x, max_y) = (self.width - 1, self.height - 1)

        for robot_movement in self.robot_movements:
            (next_robot_x, next_robot_y) = (robot_x, robot_y)
            if robot_movement == Direction.UP:
                if robot_y == 0:
                    continue
                next_robot_y -= 1
            elif robot_movement == Direction.DOWN:
                if robot_y == max_y:
                    continue
                next_robot_y += 1
            elif robot_movement == Direction.LEFT:
                if robot_x == 0:
                    continue
                next_robot_x -= 1
            elif robot_movement == Direction.RIGHT:
                if robot_y == max_x:
                    continue
                next_robot_x += 1
            else:
                assert_never(robot_movement)

            next_tile = rows[next_robot_y][next_robot_x]
            if next_tile == Tile.EMPTY_SPACE:
                (robot_x, robot_y) = (next_robot_x, next_robot_y)
                continue
            elif next_tile == Tile.WALL:
                continue
            assert next_tile == Tile.BOX

            if robot_movement == Direction.UP:
                tiles_ahead = [rows[y][robot_x] for y in range(next_robot_y, -1, -1)]
            elif robot_movement == Direction.DOWN:
                tiles_ahead = [rows[y][robot_x] for y in range(next_robot_y, self.height)]
            elif robot_movement == Direction.LEFT:
                tiles_ahead = [rows[robot_y][x] for x in range(next_robot_x, -1, -1)]
            elif robot_movement == Direction.RIGHT:
                tiles_ahead = [rows[robot_y][x] for x in range(next_robot_x, self.width)]
            else:
                assert_never(robot_movement)
            try:
                first_empty_space = tiles_ahead.index(Tile.EMPTY_SPACE)
            except ValueError:
                # No empty spaces ahead; we can't move in this direction. >:(
                continue
            try:
                first_wall = tiles_ahead.index(Tile.WALL)
            except ValueError:
                first_wall = len(tiles_ahead)
            if first_wall < first_empty_space:
                assert all(tile == Tile.BOX for tile in tiles_ahead[:first_wall])
                continue
            assert all(tile == Tile.BOX for tile in tiles_ahead[:first_empty_space])
            tiles_ahead[1:(first_empty_space + 1)] = tiles_ahead[:first_empty_space]
            tiles_ahead[0] = Tile.EMPTY_SPACE
            if robot_movement == Direction.UP:
                for (i, y) in enumerate(range(next_robot_y, -1, -1)):
                    rows[y][robot_x] = tiles_ahead[i]
            elif robot_movement == Direction.DOWN:
                for (i, y) in enumerate(range(next_robot_y, self.height)):
                    rows[y][robot_x] = tiles_ahead[i]
            elif robot_movement == Direction.LEFT:
                for (i, x) in enumerate(range(next_robot_x, -1, -1)):
                    rows[robot_y][x] = tiles_ahead[i]
            elif robot_movement == Direction.RIGHT:
                for (i, x) in enumerate(range(next_robot_x, self.width)):
                    rows[robot_y][x] = tiles_ahead[i]
            else:
                assert_never(robot_movement)
            (robot_x, robot_y) = (next_robot_x, next_robot_y)
        assert rows[robot_y][robot_x] == Tile.EMPTY_SPACE
        rows[robot_y][robot_x] = Tile.ROBOT

        return Warehouse(self.width, self.height, tuple(tuple(row) for row in rows), ())

    def box_gps_coordinates(self) -> Iterator[int]:
        """
        >>> tuple(Warehouse.from_lines([
        ...     '#######',
        ...     '#...O..',
        ...     '#......',
        ... ]).box_gps_coordinates())
        (104,)
        >>> sum(Warehouse.from_lines([
        ...     '########',
        ...     '#....OO#',
        ...     '##.....#',
        ...     '#.....O#',
        ...     '#.#O@..#',
        ...     '#...O..#',
        ...     '#...O..#',
        ...     '########',
        ... ]).box_gps_coordinates())
        2028
        >>> sum(Warehouse.from_lines([
        ...     '##########',
        ...     '#.O.O.OOO#',
        ...     '#........#',
        ...     '#OO......#',
        ...     '#OO@.....#',
        ...     '#O#.....O#',
        ...     '#O.....OO#',
        ...     '#O.....OO#',
        ...     '#OO....OO#',
        ...     '##########',
        ... ]).box_gps_coordinates())
        10092
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.rows[y][x] == Tile.BOX:
                    yield (100 * y) + x


########################################################################################################################
# Part 1
########################################################################################################################

def sum_box_gps_coordinates_after_robot_rampage(lines: Iterable[str]) -> int:
    """
    >>> sum_box_gps_coordinates_after_robot_rampage([
    ...     '########',
    ...     '#..O.O.#',
    ...     '##@.O..#',
    ...     '#...O..#',
    ...     '#.#.O..#',
    ...     '#...O..#',
    ...     '#......#',
    ...     '########',
    ...     '',
    ...     '<^^>>>vv<v>>v<<',
    ... ])
    2028
    >>> sum_box_gps_coordinates_after_robot_rampage([
    ...     '##########',
    ...     '#..O..O.O#',
    ...     '#......O.#',
    ...     '#.OO..O.O#',
    ...     '#..O@..O.#',
    ...     '#O#..O...#',
    ...     '#O..O..O.#',
    ...     '#.OO.O.OO#',
    ...     '#....O...#',
    ...     '##########',
    ...     '',
    ...     '<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^',
    ...     'vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v',
    ...     '><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<',
    ...     '<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^',
    ...     '^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><',
    ...     '^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^',
    ...     '>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^',
    ...     '<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>',
    ...     '^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>',
    ...     'v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^',
    ... ])
    10092
    """
    warehouse = Warehouse.from_lines(lines).simulate_robot_movements()
    return sum(warehouse.box_gps_coordinates())


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
        print(sum_box_gps_coordinates_after_robot_rampage(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
