#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import deque
from collections.abc import Iterable, Iterator, Sequence
from enum import Enum
from io import StringIO
from typing import Literal, NamedTuple, Optional, TypeVar

from typing_extensions import assert_never


########################################################################################################################
# Utilities
########################################################################################################################

T = TypeVar('T')


def maybe_index_of(s: Sequence[T], x: T) -> Optional[int]:
    try:
        return s.index(x)
    except ValueError:
        return None


########################################################################################################################
# Warehouse
########################################################################################################################

class Tile(Enum):
    EMPTY_SPACE = '.'
    WALL = '#'
    BOX = 'O'
    ROBOT = '@'


class WideTile(Enum):
    EMPTY_SPACE = '.'
    WALL = '#'
    BOX_LEFT = '['
    BOX_RIGHT = ']'
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
        rows: list[list[Tile]] = []
        for (y, immutable_row) in enumerate(self.rows):
            row: list[Tile] = []
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
            next_robot_position = translate(robot_x, robot_y, robot_movement, max_x, max_y)
            if next_robot_position is None:
                continue
            (next_robot_x, next_robot_y) = next_robot_position

            next_tile = rows[next_robot_y][next_robot_x]
            if next_tile == Tile.EMPTY_SPACE:
                (robot_x, robot_y) = (next_robot_x, next_robot_y)
                continue
            elif next_tile == Tile.WALL:
                continue
            assert next_tile == Tile.BOX

            tiles_ahead = scan_ahead(rows, next_robot_x, next_robot_y, robot_movement)
            if (first_empty_space := maybe_index_of(tiles_ahead, Tile.EMPTY_SPACE)) is None:
                # No empty spaces ahead; we can't move in this direction. >:(
                continue
            if (first_wall := maybe_index_of(tiles_ahead, Tile.WALL)) is None:
                first_wall = len(tiles_ahead)
            if first_wall < first_empty_space:
                assert all(tile == Tile.BOX for tile in tiles_ahead[:first_wall])
                continue
            assert all(tile == Tile.BOX for tile in tiles_ahead[:first_empty_space])
            tiles_ahead[1:(first_empty_space + 1)] = tiles_ahead[:first_empty_space]
            tiles_ahead[0] = Tile.EMPTY_SPACE
            commit_ahead(rows, next_robot_x, next_robot_y, robot_movement, tiles_ahead)
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


class WideWarehouse(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[WideTile, ...], ...]
    robot_movements: tuple[Direction, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'WideWarehouse':
        lines_iter = iter(lines)
        width = -1
        rows: list[tuple[WideTile, ...]] = []
        for (y, line) in enumerate(lines_iter):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif line == '':
                y -= 1
                break
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row: list[WideTile] = []
            expect_box_right = False
            for char in line:
                tile = WideTile(char)
                if tile == WideTile.BOX_RIGHT:
                    assert expect_box_right
                    expect_box_right = False
                else:
                    assert not expect_box_right
                    if tile == WideTile.BOX_LEFT:
                        expect_box_right = True
                row.append(tile)
            rows.append(tuple(row))
        height = y + 1
        robot_movements = tuple(Direction(char) for line in lines_iter for char in line)
        return WideWarehouse(width, height, tuple(rows), robot_movements)

    @classmethod
    def from_warehouse(cls, warehouse: Warehouse) -> 'WideWarehouse':
        width = warehouse.width * 2
        height = warehouse.height
        rows = tuple(tuple(new_tile for old_tile in row for new_tile in {
            Tile.EMPTY_SPACE: (WideTile.EMPTY_SPACE, WideTile.EMPTY_SPACE),
            Tile.WALL: (WideTile.WALL, WideTile.WALL),
            Tile.BOX: (WideTile.BOX_LEFT, WideTile.BOX_RIGHT),
            Tile.ROBOT: (WideTile.ROBOT, WideTile.EMPTY_SPACE),
        }[old_tile]) for row in warehouse.rows)
        robot_movements = warehouse.robot_movements
        return WideWarehouse(width, height, rows, robot_movements)

    def rasterise(self) -> str:
        rasterisation = StringIO()
        for y in range(self.height):
            leading_newline = '\n' if y > 0 else ''
            line = ''.join(tile.value for tile in self.rows[y])
            rasterisation.write(leading_newline + line)
        return rasterisation.getvalue()

    def simulate_robot_movements(self) -> 'WideWarehouse':
        """
        >>> print(WideWarehouse.from_warehouse(Warehouse.from_lines([
        ...     '#######',
        ...     '#...#.#',
        ...     '#.....#',
        ...     '#..OO@#',
        ...     '#..O..#',
        ...     '#.....#',
        ...     '#######',
        ...     '',
        ...     '<vv<<^^<<^^',
        ... ])).simulate_robot_movements().rasterise())
        ##############
        ##...[].##..##
        ##...@.[]...##
        ##....[]....##
        ##..........##
        ##..........##
        ##############
        >>> print(WideWarehouse.from_warehouse(Warehouse.from_lines([
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
        ... ])).simulate_robot_movements().rasterise())
        ####################
        ##[].......[].[][]##
        ##[]...........[].##
        ##[]........[][][]##
        ##[]......[]....[]##
        ##..##......[]....##
        ##..[]............##
        ##..@......[].[][]##
        ##......[][]..[]..##
        ####################

        >>> print(WideWarehouse.from_lines([
        ...     '############',
        ...     '#..........#',
        ...     '#...[].....#',
        ...     '#..[][][]@.#',
        ...     '#.....[]...#',
        ...     '#..........#',
        ...     '############',
        ...     '',
        ...     '<',
        ... ]).simulate_robot_movements().rasterise())
        ############
        #..........#
        #...[].....#
        #.[][][]@..#
        #.....[]...#
        #..........#
        ############
        >>> print(WideWarehouse.from_lines([
        ...     '############',
        ...     '#..........#',
        ...     '#...[].....#',
        ...     '#.@[][][]..#',
        ...     '#.....[]...#',
        ...     '#..........#',
        ...     '############',
        ...     '',
        ...     '>',
        ... ]).simulate_robot_movements().rasterise())
        ############
        #..........#
        #...[].....#
        #..@[][][].#
        #.....[]...#
        #..........#
        ############
        >>> print(WideWarehouse.from_lines([
        ...     '############',
        ...     '#......#...#',
        ...     '#...[]...#.#',
        ...     '#..[][][]..#',
        ...     '#....#[]...#',
        ...     '#.....@....#',
        ...     '############',
        ...     '',
        ...     '^',
        ... ]).simulate_robot_movements().rasterise())
        ############
        #...[].#...#
        #....[][]#.#
        #..[].[]...#
        #....#@....#
        #..........#
        ############
        >>> print(WideWarehouse.from_lines([
        ...     '############',
        ...     '#...@......#',
        ...     '#..#[]#....#',
        ...     '#..[][][]..#',
        ...     '#.....[]#..#',
        ...     '#....#.....#',
        ...     '############',
        ...     '',
        ...     'v',
        ... ]).simulate_robot_movements().rasterise())
        ############
        #..........#
        #..#@.#....#
        #...[].[]..#
        #..[][].#..#
        #....#[]...#
        ############

        >>> print(WideWarehouse.from_lines([
        ...     '#######',
        ...     '#.....#',
        ...     '#..[].#',
        ...     '#.##..#',
        ...     '#.....#',
        ...     '#.[]..#',
        ...     '#..@..#',
        ...     '#######',
        ...     '',
        ...     '^',
        ... ]).simulate_robot_movements().rasterise())
        #######
        #.....#
        #..[].#
        #.##..#
        #.[]..#
        #..@..#
        #.....#
        #######
        >>> print(WideWarehouse.from_lines([
        ...     '########',
        ...     '#......#',
        ...     '#.@....#',
        ...     '#.[]...#',
        ...     '#..[]..#',
        ...     '#......#',
        ...     '#...[].#',
        ...     '#...[].#',
        ...     '#......#',
        ...     '########',
        ...     '',
        ...     'v',
        ... ]).simulate_robot_movements().rasterise())
        ########
        #......#
        #......#
        #.@....#
        #.[]...#
        #..[]..#
        #...[].#
        #...[].#
        #......#
        ########
        >>> print(WideWarehouse.from_lines([
        ...     '########',
        ...     '#......#',
        ...     '#.[][].#',
        ...     '#.[]...#',
        ...     '#.[][].#',
        ...     '#..[]..#',
        ...     '#.[]...#',
        ...     '#.@....#',
        ...     '#......#',
        ...     '########',
        ...     '',
        ...     '^',
        ... ]).simulate_robot_movements().rasterise())
        ########
        #.[]...#
        #.[][].#
        #.[][].#
        #..[]..#
        #.[]...#
        #.@....#
        #......#
        #......#
        ########
        >>> print(WideWarehouse.from_lines([
        ...     '############',
        ...     '#..........#',
        ...     '#.[].......#',
        ...     '#....[]....#',
        ...     '#.[][].....#',
        ...     '#..[]......#',
        ...     '#.[][]..[].#',
        ...     '#....[]....#',
        ...     '#.....[][].#',
        ...     '#......[]..#',
        ...     '#.....[][].#',
        ...     '#....[]....#',
        ...     '#....@.....#',
        ...     '#..........#',
        ...     '############',
        ...     '',
        ...     '^',
        ... ]).simulate_robot_movements().rasterise())
        ############
        #..........#
        #.[].[]....#
        #.[][].....#
        #..[]......#
        #...[].....#
        #.[].[].[].#
        #.....[][].#
        #......[]..#
        #.....[]...#
        #....[].[].#
        #....@.....#
        #..........#
        #..........#
        ############
        """
        robot_position: Optional[tuple[int, int]] = None
        rows: list[list[WideTile]] = []
        for (y, immutable_row) in enumerate(self.rows):
            row: list[WideTile] = []
            for (x, tile) in enumerate(immutable_row):
                if tile == WideTile.ROBOT:
                    assert robot_position is None
                    robot_position = (x, y)
                    row.append(WideTile.EMPTY_SPACE)
                    continue
                row.append(tile)
            rows.append(row)
        assert robot_position is not None
        (robot_x, robot_y) = robot_position
        (max_x, max_y) = (self.width - 1, self.height - 1)

        for robot_movement in self.robot_movements:
            next_robot_position = translate(robot_x, robot_y, robot_movement, max_x, max_y)
            if next_robot_position is None:
                continue
            (next_robot_x, next_robot_y) = next_robot_position

            next_tile = rows[next_robot_y][next_robot_x]
            if next_tile == WideTile.EMPTY_SPACE:
                (robot_x, robot_y) = (next_robot_x, next_robot_y)
                continue
            elif next_tile == WideTile.WALL:
                continue
            assert next_tile in (WideTile.BOX_LEFT, WideTile.BOX_RIGHT)

            if (robot_movement == Direction.LEFT) or (robot_movement == Direction.RIGHT):
                expected_box_sequence = (WideTile.BOX_LEFT, WideTile.BOX_RIGHT) if (robot_movement == Direction.RIGHT) else (WideTile.BOX_RIGHT, WideTile.BOX_LEFT)
                tiles_ahead = scan_ahead(rows, next_robot_x, next_robot_y, robot_movement)
                if (first_empty_space := maybe_index_of(tiles_ahead, WideTile.EMPTY_SPACE)) is None:
                    continue
                if (first_wall := maybe_index_of(tiles_ahead, WideTile.WALL)) is None:
                    first_wall = len(tiles_ahead)
                if first_wall < first_empty_space:
                    assert (first_wall % 2 == 0) and all(tuple(tiles_ahead[i:(i + 2)]) == expected_box_sequence for i in range(0, first_wall, 2))
                    continue
                assert (first_empty_space % 2 == 0) and all(tuple(tiles_ahead[i:(i + 2)]) == expected_box_sequence for i in range(0, first_empty_space, 2))
                tiles_ahead[1:(first_empty_space + 1)] = tiles_ahead[:first_empty_space]
                tiles_ahead[0] = WideTile.EMPTY_SPACE
                commit_ahead(rows, next_robot_x, next_robot_y, robot_movement, tiles_ahead)
            else:
                assert (robot_movement == Direction.UP) or (robot_movement == Direction.DOWN)
                (robot_index, wide_tiles_ahead) = wide_scan_ahead(rows, next_robot_x, next_robot_y, robot_movement)
                if not maybe_wide_shift_ahead(wide_tiles_ahead, robot_movement, 0, robot_index, WideTile.EMPTY_SPACE):
                    continue
                wide_commit_ahead(rows, next_robot_x, next_robot_y, robot_movement, robot_index, wide_tiles_ahead)
            (robot_x, robot_y) = (next_robot_x, next_robot_y)
        assert rows[robot_y][robot_x] == WideTile.EMPTY_SPACE
        rows[robot_y][robot_x] = WideTile.ROBOT

        return WideWarehouse(self.width, self.height, tuple(tuple(row) for row in rows), ())

    def box_gps_coordinates(self) -> Iterator[int]:
        """
        >>> tuple(WideWarehouse.from_lines([
        ...     '##########',
        ...     '##...[]...',
        ...     '##........',
        ... ]).box_gps_coordinates())
        (105,)
        >>> sum(WideWarehouse.from_lines([
        ...     '####################',
        ...     '##[].......[].[][]##',
        ...     '##[]...........[].##',
        ...     '##[]........[][][]##',
        ...     '##[]......[]....[]##',
        ...     '##..##......[]....##',
        ...     '##..[]............##',
        ...     '##..@......[].[][]##',
        ...     '##......[][]..[]..##',
        ...     '####################',
        ... ]).box_gps_coordinates())
        9021
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.rows[y][x] == WideTile.BOX_LEFT:
                    yield (100 * y) + x


def translate(x: int, y: int, direction: Direction, max_x: int, max_y: int) -> Optional[tuple[int, int]]:
    if direction == Direction.UP:
        if y == 0:
            return None
        return (x, y - 1)
    elif direction == Direction.DOWN:
        if y == max_y:
            return None
        return (x, y + 1)
    elif direction == Direction.LEFT:
        if x == 0:
            return None
        return (x - 1, y)
    elif direction == Direction.RIGHT:
        if y == max_x:
            return None
        return (x + 1, y)
    assert_never(direction)


def scan_ahead(rows: list[list[T]], x: int, y: int, direction: Direction) -> list[T]:
    if direction == Direction.UP:
        return [rows[i][x] for i in range(y, -1, -1)]
    elif direction == Direction.DOWN:
        return [rows[i][x] for i in range(y, len(rows))]
    elif direction == Direction.LEFT:
        return rows[y][x::-1]
    elif direction == Direction.RIGHT:
        return rows[y][x:]
    assert_never(direction)


def commit_ahead(rows: list[list[T]], x: int, y: int, direction: Direction, tiles_ahead: list[T]) -> None:
    if direction == Direction.UP:
        for i in range(len(tiles_ahead)):
            rows[y - i][x] = tiles_ahead[i]
    elif direction == Direction.DOWN:
        for (i) in range(len(tiles_ahead)):
            rows[y + i][x] = tiles_ahead[i]
    elif direction == Direction.LEFT:
        rows[y][x::-1] = tiles_ahead
    elif direction == Direction.RIGHT:
        rows[y][x:] = tiles_ahead
    else:
        assert_never(direction)


def wide_scan_ahead(rows: list[list[WideTile]], x: int, y: int, direction: Literal[Direction.UP, Direction.DOWN]) -> tuple[int, tuple[tuple[int, list[WideTile]], ...]]:
    wide_tiles_ahead: deque[tuple[int, list[WideTile]]] = deque([(0, [])])
    x_start = x
    robot_index = 0
    if direction == Direction.UP:
        for i in range(y + 1):
            j = 0
            while j < len(wide_tiles_ahead):
                tile = rows[y - i][x_start + j]
                wide_tiles_ahead[j][1].append(tile)
                # Only consider extending columns if a box in the previous row is going to push on us.
                if (i == 0) or (rows[y - i + 1][x_start + j] in (WideTile.BOX_LEFT, WideTile.BOX_RIGHT)):
                    if (j == 0) and (tile == WideTile.BOX_RIGHT):
                        assert rows[y - i][x_start - 1] == WideTile.BOX_LEFT
                        wide_tiles_ahead.appendleft((i, [WideTile.BOX_LEFT]))
                        x_start -= 1
                        robot_index += 1
                        j += 1
                    elif (j == len(wide_tiles_ahead) - 1) and (tile == WideTile.BOX_LEFT):
                        assert rows[y - i][x_start + j + 1] == WideTile.BOX_RIGHT
                        wide_tiles_ahead.append((i, [WideTile.BOX_RIGHT]))
                        j += 1
                j += 1
        return (robot_index, tuple(wide_tiles_ahead))
    elif direction == Direction.DOWN:
        for i in range(len(rows) - y):
            j = 0
            while j < len(wide_tiles_ahead):
                tile = rows[y + i][x_start - j]
                wide_tiles_ahead[j][1].append(tile)
                # Only consider extending columns if a box in the previous row is going to push on us.
                if (i == 0) or (rows[y + i - 1][x_start - j] in (WideTile.BOX_LEFT, WideTile.BOX_RIGHT)):
                    if (j == 0) and (tile == WideTile.BOX_LEFT):
                        assert rows[y + i][x_start + 1] == WideTile.BOX_RIGHT
                        wide_tiles_ahead.appendleft((i, [WideTile.BOX_RIGHT]))
                        x_start += 1
                        robot_index += 1
                        j += 1
                    elif (j == len(wide_tiles_ahead) - 1) and (tile == WideTile.BOX_RIGHT):
                        assert rows[y + i][x_start - j - 1] == WideTile.BOX_LEFT
                        wide_tiles_ahead.append((i, [WideTile.BOX_LEFT]))
                        j += 1
                j += 1
        return (robot_index, tuple(wide_tiles_ahead))
    assert_never(direction)


def maybe_wide_shift_ahead(wide_tiles_ahead: tuple[tuple[int, list[WideTile]], ...], direction: Literal[Direction.UP, Direction.DOWN], i: int, j: int, prev_tile: WideTile) -> bool:
    (i_offset, tiles_ahead) = wide_tiles_ahead[j]
    tile = tiles_ahead[i - i_offset]
    if tile == WideTile.EMPTY_SPACE:
        tiles_ahead[i - i_offset] = prev_tile
        return True
    elif tile == WideTile.WALL:
        return False

    next_tile_free = maybe_wide_shift_ahead(wide_tiles_ahead, direction, i + 1, j, tile)
    if not next_tile_free:
        return False
    if tile == WideTile.BOX_RIGHT:
        adjacent_j = (j - 1) if direction == Direction.UP else (j + 1)
        (adjacent_i_offset, adjacent_tiles_ahead) = wide_tiles_ahead[adjacent_j]
        assert (adjacent_tile := adjacent_tiles_ahead[i - adjacent_i_offset]) == WideTile.BOX_LEFT
        adjacent_next_tile_free = maybe_wide_shift_ahead(wide_tiles_ahead, direction, i + 1, adjacent_j, adjacent_tile)
    else:
        assert tile == WideTile.BOX_LEFT
        adjacent_j = (j + 1) if direction == Direction.UP else (j - 1)
        (adjacent_i_offset, adjacent_tiles_ahead) = wide_tiles_ahead[adjacent_j]
        assert (adjacent_tile := adjacent_tiles_ahead[i - adjacent_i_offset]) == WideTile.BOX_RIGHT
        adjacent_next_tile_free = maybe_wide_shift_ahead(wide_tiles_ahead, direction, i + 1, adjacent_j, adjacent_tile)
    if not adjacent_next_tile_free:
        return False
    tiles_ahead[i - i_offset] = prev_tile
    adjacent_tiles_ahead[i - adjacent_i_offset] = WideTile.EMPTY_SPACE
    return True


def wide_commit_ahead(rows: list[list[WideTile]], x: int, y: int, direction: Literal[Direction.UP, Direction.DOWN], robot_index: int, wide_tiles_ahead: tuple[tuple[int, list[WideTile]], ...]) -> None:
    if direction == Direction.UP:
        x_start = x - robot_index
        for i in range(y + 1):
            for j in range(len(wide_tiles_ahead)):
                (i_offset, tiles_ahead) = wide_tiles_ahead[j]
                if i < i_offset:
                    continue
                rows[y - i][x_start + j] = tiles_ahead[i - i_offset]
        return
    elif direction == Direction.DOWN:
        x_start = x + robot_index
        for i in range(len(rows) - y):
            for j in range(len(wide_tiles_ahead)):
                (i_offset, tiles_ahead) = wide_tiles_ahead[j]
                if i < i_offset:
                    continue
                rows[y + i][x_start - j] = tiles_ahead[i - i_offset]
        return
    assert_never(direction)


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
# Part 2
########################################################################################################################

def sum_box_gps_coordinates_after_second_robot_rampage(lines: Iterable[str]) -> int:
    """
    >>> sum_box_gps_coordinates_after_second_robot_rampage([
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
    9021
    """
    warehouse = Warehouse.from_lines(lines)
    wide_warehouse = WideWarehouse.from_warehouse(warehouse).simulate_robot_movements()
    return sum(wide_warehouse.box_gps_coordinates())


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
    elif args.part == 2:
        print(sum_box_gps_coordinates_after_second_robot_rampage(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
