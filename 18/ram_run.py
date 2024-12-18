#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import bisect_left, insort_right
from collections import deque
from collections.abc import Iterable, Iterator
from itertools import islice
from typing import NamedTuple, Optional


########################################################################################################################
# Computer two: electric boogaloo
########################################################################################################################

MEMORY_SPACE_WIDTH = 71
MEMORY_SPACE_HEIGHT = 71


class Coordinate(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f'{self.x},{self.y}'


def init_memory_space(width: int, height: int) -> list[list[bool]]:
    assert (width > 1) and (height > 1)
    return [([False] * width) for _ in range(height)]


def parse_bytefall(lines: Iterable[str]) -> Iterator[Coordinate]:
    for line in lines:
        yield Coordinate(*map(int, line.split(',')))


def corrupt(memory_space: list[list[bool]], bytefall: Iterable[Coordinate]) -> None:
    for (x, y) in bytefall:
        memory_space[y][x] = True


def count_shortest_path_length(memory_space: list[list[bool]]) -> Optional[int]:
    assert (max_y := len(memory_space) - 1) >= 0
    assert (max_x := len(memory_space[0]) - 1) >= 0
    end_position = Coordinate(max_x, max_y)

    start_position = Coordinate(0, 0)
    start_h_score = manhattan_distance(start_position, end_position)

    g_scores: dict[Coordinate, int] = {start_position: 0}
    f_scores: dict[Coordinate, int] = {start_position: start_h_score}
    queue: deque[tuple[int, Coordinate]] = deque([(start_h_score, start_position)])
    while queue:
        # 에이스타, 에이스타
        # 에이스타, 에이스타
        # 에이스타, 에이스타
        # Uh, uh-huh uh-huh
        (_, position) = queue.popleft()

        if position == end_position:
            return g_scores[position]

        g_score = g_scores[position]
        for next_position in uncorrupted_neighbours(memory_space, position):
            next_g_score = g_score + 1
            if (next_position not in g_scores) or (next_g_score < g_scores[next_position]):
                g_scores[next_position] = next_g_score
                if next_position in f_scores:
                    expected_queue_item = (f_scores[next_position], next_position)
                    i = bisect_left(queue, expected_queue_item)
                    assert queue[i] == expected_queue_item
                    del queue[i]
                next_f_score = next_g_score + manhattan_distance(next_position, end_position)
                f_scores[next_position] = next_f_score
                insort_right(queue, (next_f_score, next_position))
    return None


def uncorrupted_neighbours(memory_space: list[list[bool]], position: Coordinate) -> Iterator[Coordinate]:
    assert (max_y := len(memory_space) - 1) >= 0
    assert (max_x := len(memory_space[0]) - 1) >= 0
    (x, y) = position
    if (y > 0) and not memory_space[y - 1][x]:
        yield Coordinate(x, y - 1)
    if (y < max_y) and not memory_space[y + 1][x]:
        yield Coordinate(x, y + 1)
    if (x > 0) and not memory_space[y][x - 1]:
        yield Coordinate(x - 1, y)
    if (x < max_x) and not memory_space[y][x + 1]:
        yield Coordinate(x + 1, y)


def manhattan_distance(start_position: Coordinate, end_position: Coordinate) -> int:
    return abs(end_position.x - start_position.x) + abs(end_position.y - start_position.y)


########################################################################################################################
# Part 1
########################################################################################################################

def count_shortest_path_length_after_some_ns(width: int, height: int, lines: Iterable[str], time: int) -> int:
    """
    >>> count_shortest_path_length_after_some_ns(7, 7, [
    ...     '5,4',
    ...     '4,2',
    ...     '4,5',
    ...     '3,0',
    ...     '2,1',
    ...     '6,3',
    ...     '2,4',
    ...     '1,5',
    ...     '0,6',
    ...     '3,3',
    ...     '2,6',
    ...     '5,1',
    ...     '1,2',
    ...     '5,5',
    ...     '2,5',
    ...     '6,5',
    ...     '1,4',
    ...     '0,4',
    ...     '6,4',
    ...     '1,1',
    ...     '6,1',
    ...     '1,0',
    ...     '0,5',
    ...     '1,6',
    ...     '2,0',
    ... ], 12)
    22
    """
    memory_space = init_memory_space(width, height)
    bytefall = parse_bytefall(lines)
    corrupt(memory_space, islice(bytefall, time))
    assert (shortest_path_length := count_shortest_path_length(memory_space)) is not None
    return shortest_path_length


def count_shortest_path_length_after_1024_ns(lines: Iterable[str]) -> int:
    return count_shortest_path_length_after_some_ns(MEMORY_SPACE_WIDTH, MEMORY_SPACE_HEIGHT, lines, 1024)


########################################################################################################################
# Part 2
########################################################################################################################

def find_entrapping_bytefall_position_from_some_ns(width: int, height: int, lines: Iterable[str], time: int) -> Optional[Coordinate]:
    """
    >>> find_entrapping_bytefall_position_from_some_ns(7, 7, [
    ...     '5,4',
    ...     '4,2',
    ...     '4,5',
    ...     '3,0',
    ...     '2,1',
    ...     '6,3',
    ...     '2,4',
    ...     '1,5',
    ...     '0,6',
    ...     '3,3',
    ...     '2,6',
    ...     '5,1',
    ...     '1,2',
    ...     '5,5',
    ...     '2,5',
    ...     '6,5',
    ...     '1,4',
    ...     '0,4',
    ...     '6,4',
    ...     '1,1',
    ...     '6,1',
    ...     '1,0',
    ...     '0,5',
    ...     '1,6',
    ...     '2,0',
    ... ], 12)
    Coordinate(x=6, y=1)
    """
    memory_space = init_memory_space(width, height)
    bytefall_iter = iter(parse_bytefall(lines))
    corrupt(memory_space, islice(bytefall_iter, time))
    for position in bytefall_iter:
        corrupt(memory_space, (position,))
        if count_shortest_path_length(memory_space) is None:
            return position
    return None


def find_entrapping_bytefall_position(lines: Iterable[str]) -> str:
    assert (position := find_entrapping_bytefall_position_from_some_ns(MEMORY_SPACE_WIDTH, MEMORY_SPACE_HEIGHT, lines, 1024)) is not None
    return str(position)


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
        print(count_shortest_path_length_after_1024_ns(lines))
    elif args.part == 2:
        print(find_entrapping_bytefall_position(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
