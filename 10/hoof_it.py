#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import deque
from collections.abc import Iterable, Iterator
from typing import NamedTuple


########################################################################################################################
# Topographic map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int


class TopographicMap(NamedTuple):
    max_x: int
    max_y: int
    rows: tuple[tuple[int, ...], ...]
    trailheads: set[Coordinate]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'TopographicMap':
        width = -1
        rows: list[tuple[int, ...]] = []
        trailheads: set[Coordinate] = set()
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row = tuple((int(height) if height != '.' else -1) for height in line)
            rows.append(row)
            for (x, height) in enumerate(row):
                if height == 0:
                    trailheads.add(Coordinate(x, y))
        return TopographicMap(width - 1, y, tuple(rows), trailheads)

    def neighbours(self, position: Coordinate, expected_height: int) -> Iterator[Coordinate]:
        if (position.y > 0) and (self.rows[position.y - 1][position.x] == expected_height):
            yield Coordinate(position.x, position.y - 1)
        if (position.y < self.max_y) and (self.rows[position.y + 1][position.x] == expected_height):
            yield Coordinate(position.x, position.y + 1)
        if (position.x > 0) and (self.rows[position.y][position.x - 1] == expected_height):
            yield Coordinate(position.x - 1, position.y)
        if (position.x < self.max_x) and (self.rows[position.y][position.x + 1] == expected_height):
            yield Coordinate(position.x + 1, position.y)

    def score_trailheads(self) -> dict[Coordinate, int]:
        """
        >>> sorted(TopographicMap.from_lines([
        ...     '0123',
        ...     '1234',
        ...     '8765',
        ...     '9876',
        ... ]).score_trailheads().items())
        [(Coordinate(x=0, y=0), 1)]
        >>> sorted(TopographicMap.from_lines([
        ...     '...0...',
        ...     '...1...',
        ...     '...2...',
        ...     '6543456',
        ...     '7.....7',
        ...     '8.....8',
        ...     '9.....9',
        ... ]).score_trailheads().items())
        [(Coordinate(x=3, y=0), 2)]
        >>> sorted(TopographicMap.from_lines([
        ...     '..90..9',
        ...     '...1.98',
        ...     '...2..7',
        ...     '6543456',
        ...     '765.987',
        ...     '876....',
        ...     '987....',
        ... ]).score_trailheads().items())
        [(Coordinate(x=3, y=0), 4)]
        >>> sorted(TopographicMap.from_lines([
        ...     '10..9..',
        ...     '2...8..',
        ...     '3...7..',
        ...     '4567654',
        ...     '...8..3',
        ...     '...9..2',
        ...     '.....01',
        ... ]).score_trailheads().items())
        [(Coordinate(x=1, y=0), 1), (Coordinate(x=5, y=6), 2)]
        >>> sorted(TopographicMap.from_lines([
        ...     '89010123',
        ...     '78121874',
        ...     '87430965',
        ...     '96549874',
        ...     '45678903',
        ...     '32019012',
        ...     '01329801',
        ...     '10456732',
        ... ]).score_trailheads().items())
        [(Coordinate(x=0, y=6), 5), (Coordinate(x=1, y=7), 5), (Coordinate(x=2, y=0), 5), (Coordinate(x=2, y=5), 1), (Coordinate(x=4, y=0), 6), (Coordinate(x=4, y=2), 5), (Coordinate(x=5, y=5), 3), (Coordinate(x=6, y=4), 3), (Coordinate(x=6, y=6), 3)]
        """
        scores = {}
        # As a slight optimisation, we could also iterate through peaks, if there are fewer peaks than trailheads.
        for trailhead in self.trailheads:
            score = 0
            visited = {trailhead}
            to_visit = deque([trailhead])
            while to_visit:
                position = to_visit.popleft()
                height = self.rows[position.y][position.x]
                if height == 9:
                    score += 1
                    continue
                for next_position in self.neighbours(position, height + 1):
                    if next_position not in visited:
                        visited.add(next_position)
                        to_visit.append(next_position)
            scores[trailhead] = score
        return scores

    def rate_trailheads(self) -> dict[Coordinate, int]:
        """
        >>> sorted(TopographicMap.from_lines([
        ...     '.....0.',
        ...     '..4321.',
        ...     '..5..2.',
        ...     '..6543.',
        ...     '..7..4.',
        ...     '..8765.',
        ...     '..9....',
        ... ]).rate_trailheads().items())
        [(Coordinate(x=5, y=0), 3)]
        >>> sorted(TopographicMap.from_lines([
        ...     '..90..9',
        ...     '...1.98',
        ...     '...2..7',
        ...     '6543456',
        ...     '765.987',
        ...     '876....',
        ...     '987....',
        ... ]).rate_trailheads().items())
        [(Coordinate(x=3, y=0), 13)]
        >>> sorted(TopographicMap.from_lines([
        ...     '012345',
        ...     '123456',
        ...     '234567',
        ...     '345678',
        ...     '4.6789',
        ...     '56789.',
        ... ]).rate_trailheads().items())
        [(Coordinate(x=0, y=0), 227)]
        >>> sorted(TopographicMap.from_lines([
        ...     '89010123',
        ...     '78121874',
        ...     '87430965',
        ...     '96549874',
        ...     '45678903',
        ...     '32019012',
        ...     '01329801',
        ...     '10456732',
        ... ]).rate_trailheads().items())
        [(Coordinate(x=0, y=6), 5), (Coordinate(x=1, y=7), 5), (Coordinate(x=2, y=0), 20), (Coordinate(x=2, y=5), 1), (Coordinate(x=4, y=0), 24), (Coordinate(x=4, y=2), 10), (Coordinate(x=5, y=5), 4), (Coordinate(x=6, y=4), 4), (Coordinate(x=6, y=6), 8)]
        """
        ratings = {}
        for trailhead in self.trailheads:
            rating = 0
            distinct_trails = {trailhead: 1}
            to_visit = deque([(0, trailhead)])
            while to_visit:
                (height, position) = to_visit.popleft()
                distinct_trails_to_position = distinct_trails[position]
                if height == 9:
                    rating += distinct_trails_to_position
                    continue
                next_height = height + 1
                for next_position in self.neighbours(position, next_height):
                    if next_position not in distinct_trails:
                        distinct_trails[next_position] = distinct_trails_to_position
                        to_visit.append((next_height, next_position))
                    else:
                        distinct_trails[next_position] += distinct_trails_to_position
            ratings[trailhead] = rating
        return ratings


########################################################################################################################
# Part 1
########################################################################################################################

def sum_trailhead_scores(lines: Iterable[str]) -> int:
    """
    >>> sum_trailhead_scores([
    ...     '0123',
    ...     '1234',
    ...     '8765',
    ...     '9876',
    ... ])
    1
    >>> sum_trailhead_scores([
    ...     '89010123',
    ...     '78121874',
    ...     '87430965',
    ...     '96549874',
    ...     '45678903',
    ...     '32019012',
    ...     '01329801',
    ...     '10456732',
    ... ])
    36
    """
    map_ = TopographicMap.from_lines(lines)
    return sum(map_.score_trailheads().values())


########################################################################################################################
# Part 2
########################################################################################################################

def sum_trailhead_ratings(lines: Iterable[str]) -> int:
    """
    >>> sum_trailhead_ratings([
    ...     '89010123',
    ...     '78121874',
    ...     '87430965',
    ...     '96549874',
    ...     '45678903',
    ...     '32019012',
    ...     '01329801',
    ...     '10456732',
    ... ])
    81
    """
    map_ = TopographicMap.from_lines(lines)
    return sum(map_.rate_trailheads().values())


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
        print(sum_trailhead_scores(lines))
    elif args.part == 2:
        print(sum_trailhead_ratings(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
