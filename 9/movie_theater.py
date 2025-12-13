#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import insort
from collections.abc import Iterable, Iterator
from heapq import heappop, heappush
from itertools import combinations, groupby
from operator import attrgetter
from typing import NamedTuple


########################################################################################################################
# Tile floor
########################################################################################################################

COORDINATE_DELIMITER = ','


class RedTile(NamedTuple):
    x: int
    y: int

    @classmethod
    def from_line(cls, line: str) -> 'RedTile':
        (raw_x, raw_y) = line.split(COORDINATE_DELIMITER)
        return RedTile(int(raw_x), int(raw_y))


def calculate_area(a: RedTile, b: RedTile) -> int:
    return (abs(a.x - b.x) + 1) * (abs(a.y - b.y) + 1)


def pairs_by_largest_area(red_tiles: Iterable[RedTile]) -> Iterator[tuple[int, RedTile, RedTile]]:
    # A complete graph of n vertices has n(n-1)÷2 edges. So 496 vertices would have 122,760 edges.
    pairs: list[tuple[int, RedTile, RedTile]] = []
    for (a, b) in combinations(red_tiles, 2):
        area = calculate_area(a, b)
        # If we were on Python 3.14, we could use `heappush_max`.
        heappush(pairs, (-area, a, b))
    while pairs:
        # If we were on Python 3.14, we could use `heappop_max`.
        (negative_area, a, b) = heappop(pairs)
        yield (-negative_area, a, b)


def collect_tiles_and_spans_by_row(red_tiles: tuple[RedTile, ...]) -> tuple[tuple[int, tuple[tuple[RedTile, ...], tuple[tuple[int, int], ...]]], ...]:
    """
    >>> collect_tiles_and_spans_by_row(tuple(parse_red_tiles([
    ...     '13,1',  # The coordinates plot the following points.
    ...     '9,1',   # ```
    ...     '9,3',   # ...................
    ...     '9,5',   # .........#...#...#.
    ...     '6,5',   # ...................
    ...     '1,5',   # .........#.........
    ...     '1,9',   # .................#.
    ...     '3,9',   # .#...#...#.........
    ...     '3,7',   # ...................
    ...     '7,7',   # ...#...#...........
    ...     '7,9',   # ...................
    ...     '17,9',  # .#.#...#.........#.
    ...     '17,4',  # ...................
    ...     '17,1',  # ```
    ... ])))
    ((1, ((RedTile(x=9, y=1), RedTile(x=13, y=1), RedTile(x=17, y=1)), ((9, 17),))), (3, ((RedTile(x=9, y=3),), ())), (4, ((RedTile(x=17, y=4),), ())), (5, ((RedTile(x=1, y=5), RedTile(x=6, y=5), RedTile(x=9, y=5)), ((1, 9),))), (7, ((RedTile(x=3, y=7), RedTile(x=7, y=7)), ((3, 7),))), (9, ((RedTile(x=1, y=9), RedTile(x=3, y=9), RedTile(x=7, y=9), RedTile(x=17, y=9)), ((1, 3), (7, 17)))))
    """
    # Verify we have at least enough tiles to form one rectangle.
    assert len(red_tiles) >= 4
    # Verify adjacent tiles are on the same row or column.
    has_columns = has_rows = False
    prev_tile = red_tiles[-1]
    for tile in red_tiles:
        has_columns |= (is_column := tile.x == prev_tile.x)
        has_rows |= (is_row := tile.y == prev_tile.y)
        assert is_column ^ is_row
        prev_tile = tile
    assert has_columns and has_rows

    # To make our life easier, we'll shift the tiles around to ensure that a run of tiles on the same row do not
    # straddle the ends of the list. Given the above checks, this _should_ terminate (outside of some edge cases that
    # I'm going to ignore).
    while red_tiles[0].y == red_tiles[-1].y:
        red_tiles = (*red_tiles[1:], red_tiles[0])

    tiles_and_spans_by_row: dict[int, tuple[dict[int, RedTile], list[tuple[int, int]]]] = {}
    for (y, run_tiles_iter) in groupby(red_tiles, key=attrgetter('y')):
        run_tiles = tuple(run_tiles_iter)
        (row_tiles, row_spans) = tiles_and_spans_by_row.setdefault(y, ({}, []))
        for run_tile in run_tiles:
            assert run_tile.x not in row_tiles
            row_tiles[run_tile.x] = run_tile
        if len(run_tiles) == 1:
            # This lonesome tile is part of a vertical run, so we don't need to update `row_spans`.
            continue
        run_abscissas = tuple(run_tile.x for run_tile in run_tiles)
        span_start = min(run_abscissas)
        span_end = max(run_abscissas)
        insort(row_spans, (span_start, span_end))

    return tuple(
        (y, (tuple(sorted(row_tiles.values())), tuple(row_spans)))
        for (y, (row_tiles, row_spans))
        in sorted(tiles_and_spans_by_row.items())
    )


def update_mask_spans(mask_spans: tuple[tuple[int, int], ...], row_spans: tuple[tuple[int, int], ...]) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    """
    >>> update_mask_spans((), ((9, 17),))
    (((9, 17),), ((9, 17),))
    >>> update_mask_spans(((9, 17),), ())
    (((9, 17),), ((9, 17),))
    >>> update_mask_spans(((9, 17),), ((1, 9),))
    (((1, 17),), ((1, 17),))
    >>> update_mask_spans(((1, 17),), ((3, 7),))
    (((1, 17),), ((1, 3), (7, 17)))
    >>> update_mask_spans(((1, 3), (7, 17)), ((1, 3), (7, 17)))
    (((1, 3), (7, 17)), ())
    """
    if not row_spans:
        return (mask_spans, mask_spans)
    if not mask_spans:
        return (row_spans, row_spans)
    union_mask_spans: list[tuple[int, int]] = list(mask_spans)
    row_spans_to_subtract: list[tuple[int, int]] = []
    for row_span in row_spans:
        (row_span_start, row_span_end) = row_span
        for (i, mask_span) in enumerate(union_mask_spans):
            (mask_span_start, mask_span_end) = mask_span
            if row_span_end < mask_span_start:
                # Row span is disjoint, strictly to the left of the mask span. Add to mask spans.
                union_mask_spans.insert(i, row_span)
                break
            elif row_span_end == mask_span_start:
                # Row span's right side touches mask span's left side. Extend mask span.
                union_mask_spans[i] = (row_span_start, mask_span_end)
                break
            elif mask_span_start <= row_span_start and row_span_end <= mask_span_end:
                # Row span is covered by mask span. We'll deal with these later.
                row_spans_to_subtract.append(row_span)
                break
            elif mask_span_end == row_span_start:
                # Row span's left side touches mask span's right side. Extend mask span.
                union_mask_spans[i] = (mask_span_start, row_span_end)
                break
            elif i == len(union_mask_spans) - 1:
                # We've exhausted all mask spans. Row span must be disjoint, strictly to the right of the mask span. Add
                # to mask spans.
                union_mask_spans.append(row_span)
                break
        # Compaction pass.
        i = 0
        while i < (len(union_mask_spans) - 1):
            (mask_span_start, mask_span_end) = union_mask_spans[i]
            (next_mask_span_start, next_mask_span_end) = union_mask_spans[i + 1]
            if next_mask_span_start == mask_span_end:
                union_mask_spans.pop(i)
                union_mask_spans.pop(i)
                union_mask_spans.insert(i, (mask_span_start, next_mask_span_end))
            i += 1
    intersection_mask_spans: list[tuple[int, int]] = list(union_mask_spans)
    for row_span in row_spans_to_subtract:
        (row_span_start, row_span_end) = row_span
        for (i, mask_span) in enumerate(intersection_mask_spans):
            (mask_span_start, mask_span_end) = mask_span
            if mask_span_start <= row_span_start and row_span_end <= mask_span_end:
                # Row span is covered by mask span. Subtract mask span.
                intersection_mask_spans.pop(i)
                if row_span_end != mask_span_end:
                    intersection_mask_spans.insert(i, (row_span_end, mask_span_end))
                if mask_span_start != row_span_start:
                    intersection_mask_spans.insert(i, (mask_span_start, row_span_start))
                break
    return (tuple(union_mask_spans), tuple(intersection_mask_spans))


def pairs_by_largest_red_or_green_area(tiles_and_spans_by_row: tuple[tuple[int, tuple[tuple[RedTile, ...], tuple[tuple[int, int], ...]]], ...]) -> Iterator[tuple[int, RedTile, RedTile]]:
    pairs: list[tuple[int, RedTile, RedTile]] = []

    mask_spans: tuple[tuple[int, int], ...] = ()
    tiles_by_column: dict[int, list[RedTile]] = {}
    for (_, (row_tiles, row_spans)) in tiles_and_spans_by_row:
        (union_mask_spans, intersection_mask_spans) = update_mask_spans(mask_spans, row_spans)
        # Extend `tiles_by_columns`.
        for row_tile in row_tiles:
            tiles_by_column.setdefault(row_tile.x, []).append(row_tile)
        # Add all combinations of valid areas.
        for row_tile in row_tiles:
            for (mask_span_start, mask_span_end) in union_mask_spans:
                if mask_span_end < row_tile.x:
                    continue
                if mask_span_start > row_tile.x:
                    break
                assert mask_span_start <= row_tile.x <= mask_span_end
                # Scan to the right (inclusive of the current column), ratcheting down the height.
                max_x = mask_span_end
                min_y = 0
                for (x, column_tiles) in sorted(tiles_by_column.items()):
                    if x < row_tile.x:
                        continue
                    if x > max_x:
                        break
                    assert row_tile.x <= x <= max_x
                    has_ratched_vertical_bound = False
                    for column_tile in column_tiles:
                        if column_tile.y < min_y:
                            continue
                        if not has_ratched_vertical_bound:
                            min_y = column_tile.y
                            has_ratched_vertical_bound = True
                        if row_tile == column_tile:
                            continue
                        area = calculate_area(row_tile, column_tile)
                        # If we were on Python 3.14, we could use `heappush_max`.
                        heappush(pairs, (-area, row_tile, column_tile))
                    if not has_ratched_vertical_bound:
                        break
                # Scan to the left (exclusive of the current column), ratcheting down the height.
                min_x = mask_span_start
                min_y = 0
                for (x, column_tiles) in sorted(tiles_by_column.items(), reverse=True):
                    if x >= row_tile.x:
                        continue
                    if x < min_x:
                        break
                    assert min_x <= x < row_tile.x
                    has_ratched_vertical_bound = False
                    for column_tile in column_tiles:
                        if column_tile.y < min_y:
                            continue
                        if not has_ratched_vertical_bound:
                            min_y = column_tile.y
                            has_ratched_vertical_bound = True
                        area = calculate_area(row_tile, column_tile)
                        # If we were on Python 3.14, we could use `heappush_max`.
                        heappush(pairs, (-area, row_tile, column_tile))
                    if not has_ratched_vertical_bound:
                        break
        # Prune `tiles_by_columns`.
        for x in tuple(tiles_by_column.keys()):
            if not any((mask_span_start <= x <= mask_span_end) for (mask_span_start, mask_span_end) in intersection_mask_spans):
                del tiles_by_column[x]
        mask_spans = intersection_mask_spans
    # We should wind up with an empty mask at the very end.
    assert not mask_spans

    while pairs:
        # If we were on Python 3.14, we could use `heappop_max`.
        (negative_area, a, b) = heappop(pairs)
        yield (-negative_area, a, b)


def parse_red_tiles(lines: Iterable[str]) -> Iterator[RedTile]:
    for line in lines:
        yield RedTile.from_line(line)


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_largest_area(lines: Iterable[str]) -> int:
    """
    >>> calculate_largest_area([
    ...     '7,1',
    ...     '11,1',
    ...     '11,7',
    ...     '9,7',
    ...     '9,5',
    ...     '2,5',
    ...     '2,3',
    ...     '7,3',
    ... ])
    50
    """
    red_tiles = parse_red_tiles(lines)
    (area, _, _) = next(pairs_by_largest_area(red_tiles))
    return area


########################################################################################################################
# Part 2
########################################################################################################################

def calculate_largest_red_or_green_area(lines: Iterable[str]) -> int:
    """
    >>> calculate_largest_red_or_green_area([
    ...     '7,1',
    ...     '11,1',
    ...     '11,7',
    ...     '9,7',
    ...     '9,5',
    ...     '2,5',
    ...     '2,3',
    ...     '7,3',
    ... ])
    24
    """
    red_tiles = tuple(parse_red_tiles(lines))
    # The following is similar in spirit to Pipe Maze (from day 10 of 2023) or Lavaduct Lagoon (from day 18 of 2023).
    tiles_and_spans_by_row = collect_tiles_and_spans_by_row(red_tiles)
    (area, _, _) = next(pairs_by_largest_red_or_green_area(tiles_and_spans_by_row))
    return area


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
        print(calculate_largest_area(lines))
    elif args.part == 2:
        print(calculate_largest_red_or_green_area(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
