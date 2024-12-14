#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import Counter, deque
from collections.abc import Iterable
from enum import Enum
from itertools import chain, cycle
from typing import NamedTuple, Optional


########################################################################################################################
# Map
########################################################################################################################

MAX_STEPS_MATRIX_SIZE = 1000


class Tile(Enum):
    STARTING_POSITION = 'S'
    GARDEN_PLOT = '.'
    ROCKS = '#'


class Map(NamedTuple):
    size: int
    origin_chunk_steps: tuple[int, ...]
    origin_chunk_even_steps: int
    origin_chunk_odd_steps: int
    expanded_chunks_steps: tuple[int, ...]
    expanded_chunks_radius: int
    edge_cardinal_chunks_steps: tuple[int, ...]
    edge_cardinal_chunks_even_steps: int
    edge_cardinal_chunks_odd_steps: int
    edge_diagonal_chunks_steps: tuple[int, ...]
    edge_diagonal_chunks_even_steps: int
    edge_diagonal_chunks_odd_steps: int

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        """
        >>> Map.from_lines([
        ...     '.',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected map with odd side length greater than 3 × 3, but got width of 1 tile on line 1
        >>> Map.from_lines([
        ...     '....',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected map with odd side length greater than 3 × 3, but got width of 4 tiles on line 1
        >>> Map.from_lines([
        ...     '...',
        ...     '.S.',
        ...     '...',
        ...     '...',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected a 3 × 3 map, but encountered an extra line
        >>> Map.from_lines([
        ...     '...',
        ...     '..',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Width of line 2 differs from line 1 (2 ≠ 3)
        >>> Map.from_lines([
        ...     '...',
        ...     '.#.',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected an 'S' tile at (1, 1), but parsed a '#' tile instead
        >>> Map.from_lines([
        ...     '...',
        ...     '.S.',
        ...     '..S',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Parsed an unexpected 'S' tile at (2, 2)
        >>> Map.from_lines([
        ...     '##.',
        ...     '.S.',
        ...     '...',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected edges of map to be rock-free, but parsed 2 rocks on top edge
        >>> Map.from_lines([
        ...     '...',
        ...     '.S.',
        ...     '.#.',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected edges of map to be rock-free, but parsed 1 rock on bottom edge
        >>> Map.from_lines([
        ...     '.....',
        ...     '#....',
        ...     '..S..',
        ...     '.....',
        ...     '.....',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected edges of map to be rock-free, but parsed a rock on left edge of line 2
        >>> Map.from_lines([
        ...     '.....',
        ...     '.....',
        ...     '..S..',
        ...     '....#',
        ...     '.....',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected edges of map to be rock-free, but parsed a rock on right edge of line 4
        >>> Map.from_lines([
        ...     '...',
        ...     '.S.',
        ... ])
        Traceback (most recent call last):
            ...
        ValueError: Expected a 3 × 3 map, but parsed 1 fewer line
        """
        size = -1
        midpoint: Optional[int] = None
        rows: list[tuple[Optional[int], ...]] = []
        for (y, line) in enumerate(lines):
            if y == 0:
                size = len(line)
                if (size <= 2) or (size % 2 != 1):
                    raise ValueError(f'Expected map with odd side length greater than 3 × 3, but got width of {size} tile{"s" if size != 1 else ""} on line 1')
                midpoint = size // 2
            elif y >= size:
                raise ValueError(f'Expected a {size} × {size} map, but encountered an extra line')
            elif len(line) != size:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {size})')
            row: list[Optional[int]] = []
            for (x, char) in enumerate(line):
                tile = Tile(char)
                if (y == midpoint == x):
                    if tile != Tile.STARTING_POSITION:
                        raise ValueError(f"Expected an 'S' tile at {(midpoint, midpoint)}, but parsed a {repr(tile.value)} tile instead")
                    tile = Tile.GARDEN_PLOT
                elif tile == Tile.STARTING_POSITION:
                    raise ValueError(f"Parsed an unexpected 'S' tile at {(x, y)}")
                if tile == Tile.GARDEN_PLOT:
                    row.append(-1)
                else:
                    assert tile == Tile.ROCKS
                    row.append(None)
            if ((y == 0) or (y == (size - 1))) and (num_unexpected_rocks := sum(tile is None for tile in row)):
                raise ValueError(f'Expected edges of map to be rock-free, but parsed {num_unexpected_rocks} rock{"" if num_unexpected_rocks == 1 else "s"} on {"top" if y == 0 else "bottom"} edge')
            elif (unexpected_left_rock := (row[0] is None)) or (row[-1] is None):
                raise ValueError(f'Expected edges of map to be rock-free, but parsed a rock on {"left" if unexpected_left_rock else "right"} edge of line {y + 1}')
            rows.append(tuple(row))
        missing_lines = size - y - 1
        if missing_lines != 0:
            raise ValueError(f'Expected a {size} × {size} map, but parsed {missing_lines} fewer line{"s" if missing_lines != 1 else ""}')
        assert midpoint is not None
        template_steps_matrix = tuple(rows)

        # Verify that the frontier follows a pattern across wraparound boundaries.
        #
        # First, expand the map twice in each direction, so we get 5 × 5 chunks.
        assert size * 5 <= MAX_STEPS_MATRIX_SIZE
        steps_matrix = deque(deque(template_row * 5) for template_row in template_steps_matrix)
        for _ in range(4):
            for i in range(size):
                steps_matrix.append(steps_matrix[i].copy())
        # Next, flood fill garden plots with the number of steps it takes to reach them from the starting position.
        expanded_midpoint = len(steps_matrix) // 2
        to_visit = {(expanded_midpoint, expanded_midpoint): 0}
        while True:
            unreachable_to_visit = fill_steps_matrix(steps_matrix, to_visit)

            # Finally, for each cardinal direction, verify that the difference in steps beween garden plots in the
            # outermost and inner chunks is `size`.
            result = verify_steps_matrix(steps_matrix, size)
            if result is not None:
                break

            # If that's not the case, try again after expanding the steps matrix.
            expand_steps_matrix(steps_matrix, template_steps_matrix)
            to_visit = {(x + size, y + size): steps for ((x, y), steps) in unreachable_to_visit.items()}
        return Map(size, *result)

    def count_reachable_garden_plots(self, total_steps: int) -> int:
        """
        >>> map_ = Map.from_lines([
        ...     '...........',
        ...     '.....###.#.',
        ...     '.###.##..#.',
        ...     '..#.#...#..',
        ...     '....#.#....',
        ...     '.##..S####.',
        ...     '.##..#...#.',
        ...     '.......##..',
        ...     '.##.#.####.',
        ...     '.##..##.##.',
        ...     '...........',
        ... ])
        >>> map_.count_reachable_garden_plots(0)
        1
        >>> map_.count_reachable_garden_plots(1)
        2
        >>> map_.count_reachable_garden_plots(2)
        4
        >>> map_.count_reachable_garden_plots(3)
        6
        >>> map_.count_reachable_garden_plots(6)
        16
        """
        assert total_steps >= 0
        adjusted_total_steps = min(total_steps, len(self.origin_chunk_steps) - 1)
        # Match parity.
        if (adjusted_total_steps % 2) != (total_steps % 2):
            adjusted_total_steps -= 1
        return sum(self.origin_chunk_steps[i] for i in range(adjusted_total_steps, -1, -2))

    def count_reachable_garden_plots_with_wraparound(self, total_steps: int) -> int:
        r"""
        First, let's lay out the invariants we can surmise from the provided inputs.

          - Maps are square with odd side lengths.
          - The starting position is always in the centre of the map.
          - The edges of the map are rock-free; they're just garden plots.
          - The edges of the map are reachable from the starting position.
          - However, not all garden plots are reachable; some are enclosed in all four cardinal directions by rocks.

        Let's consider a simple case without rocks.

        Here's the first three steps.

           s=0       s=1       s=2       s=3
          (t=1)     (t=5)     (t=13)    (t=25)
           r=1       r=4       r=9       r=16
        ......... ......... ......... .........
        ......... ......... ......... ....O....
        ......... ......... ....O.... ...O.O...
        ......... ....O.... ...O.O... ..O.O.O..
        ....O.... ...OSO... ..O.O.O.. .O.OSO.O.
        ......... ....O.... ...O.O... ..O.O.O..
        ......... ......... ....O.... ...O.O...
        ......... ......... ......... ....O....
        ......... ......... ......... .........

        For step 0, we reach one garden plot: the starting position.

        For step 1, note we can't move diagonally. Note also that we can't reach the tile from the previous step. The
        total number of garden plots that we've covered: (i) after step 1 is 5; and (ii) after step 0 is 1. The total
        number of _reachable_ garden plots is 5 - 1 = 4.

        By step 2, we've covered 13 garden plots, but because we walked from the 4 tiles reachable in the previous step,
        they need to be subtracted, leaving us with 9 _reachable_ garden plots. By now, we can see both a visual pattern
        and a formulaic pattern: the number of reachable garden plots at step n might be (n + 1)^2.

        For step 3, (n + 1)^2 = 4^2 = 16, which is the number of reachable garden plots. As the frontier expands,
        everything contained within the wavefront oscillates: for one step, they're reachable, but for the next, they're
        not.

        So for 26,501,365 steps, we can surmise that the upper bound is 702,322,399,865,956 garden plots.

        Alternatively, we could precompute the shortest number of steps it takes to reach each garden plot. Then, to
        determine how many garden plots are reachable after n steps, we count the number of garden plots whose shortest
        number of steps is less than or equal to n _and_ has the same parity as n.

        876545678
        765434567
        654323456
        543212345
        432101234
        543212345
        654323456
        765434567
        876545678

        For example, the number of garden plots reachable after 4 steps is 16 (the number of garden plots whose shortest
        distance from the starting position is 4) + 8 (the number of garden plots whose shortest distance from the
        starting position is 2) + 1 (the number of garden plots whose shortest distance from the starting position is
        0), which equals 25. This agrees with our initial formulation: (n + 1)^2 = 5^2 = 25.

        Now let's talk about rocks. If we play around with different configurations of rocks, we'll see that their
        presence perturbs the frontier. However, at a macroscopic level across chunks, the frontier eventually settles
        into a pattern, where the difference in steps for each garden plot between two adjacent chunks along a cardinal
        direction is equal to the (map/)chunk's side length. (I haven't thought too deeply into why this is the case. I
        suspect it has to do with the rock-free edges acting as gutters that eventually help the frontier expand
        consistently.)

        We can take advantage of this pattern by transforming the number of steps taken into the number of complete
        chunks filled plus the number of partial edge chunks filled (and by how much).

        A couple things to note follow.

          - A garden plot in the origin chunk whose shortest distance is _even_ will become _odd_ in the next chunk. In
            other words, the parity flips between adjacent chunks. (This is probably due to the odd side lengths.)

        >>> map_ = Map.from_lines([
        ...     '...........',
        ...     '.....###.#.',
        ...     '.###.##..#.',
        ...     '..#.#...#..',
        ...     '....#.#....',
        ...     '.##..S####.',
        ...     '.##..#...#.',
        ...     '.......##..',
        ...     '.##.#.####.',
        ...     '.##..##.##.',
        ...     '...........',
        ... ])
        >>> map_.count_reachable_garden_plots_with_wraparound(6)
        16
        >>> map_.count_reachable_garden_plots_with_wraparound(10)
        50
        >>> map_.count_reachable_garden_plots_with_wraparound(50)
        1594
        >>> map_.count_reachable_garden_plots_with_wraparound(100)
        6536
        >>> map_.count_reachable_garden_plots_with_wraparound(500)
        167004
        >>> map_.count_reachable_garden_plots_with_wraparound(1000)
        668697
        >>> map_.count_reachable_garden_plots_with_wraparound(5000)
        16733044

        >>> map_.count_reachable_garden_plots_with_wraparound(54)  # "edge" case
        1853
        >>> map_.count_reachable_garden_plots_with_wraparound(55)
        1914
        >>> map_.count_reachable_garden_plots_with_wraparound(56)
        1988
        >>> map_.count_reachable_garden_plots_with_wraparound(57)
        2072
        >>> map_.count_reachable_garden_plots_with_wraparound(58)
        2145
        >>> map_.count_reachable_garden_plots_with_wraparound(59)
        2244
        >>> map_.count_reachable_garden_plots_with_wraparound(60)
        2324
        >>> map_.count_reachable_garden_plots_with_wraparound(61)
        2406
        >>> map_.count_reachable_garden_plots_with_wraparound(62)
        2479
        >>> map_.count_reachable_garden_plots_with_wraparound(63)
        2579
        >>> map_.count_reachable_garden_plots_with_wraparound(64)
        2665
        >>> map_.count_reachable_garden_plots_with_wraparound(65)  # "edge" case
        2722
        >>> map_.count_reachable_garden_plots_with_wraparound(66)
        2794
        >>> map_.count_reachable_garden_plots_with_wraparound(67)
        2882
        >>> map_.count_reachable_garden_plots_with_wraparound(68)
        2982
        >>> map_.count_reachable_garden_plots_with_wraparound(69)
        3069
        >>> map_.count_reachable_garden_plots_with_wraparound(70)
        3186
        >>> map_.count_reachable_garden_plots_with_wraparound(71)
        3282
        >>> map_.count_reachable_garden_plots_with_wraparound(72)
        3380
        >>> map_.count_reachable_garden_plots_with_wraparound(73)
        3467
        >>> map_.count_reachable_garden_plots_with_wraparound(74)
        3585
        >>> map_.count_reachable_garden_plots_with_wraparound(75)
        3687
        >>> map_.count_reachable_garden_plots_with_wraparound(76)  # "edge" case
        3753

        >>> with open('input.txt', mode='rt') as input_file:
        ...     map_ = Map.from_lines(line.rstrip('\n') for line in input_file)
        ...
        >>> map_.count_reachable_garden_plots_with_wraparound(327)  # "edge" case
        95144
        >>> map_.count_reachable_garden_plots_with_wraparound(360)
        115459
        >>> map_.count_reachable_garden_plots_with_wraparound(421)
        157480
        >>> map_.count_reachable_garden_plots_with_wraparound(458)  # "edge" case
        186350
        >>> map_.count_reachable_garden_plots_with_wraparound(459)
        187556
        >>> map_.count_reachable_garden_plots_with_wraparound(588)
        307118
        >>> map_.count_reachable_garden_plots_with_wraparound(589)  # "edge" case
        307928
        """
        assert total_steps >= 0
        safe_precomputed_steps = len(self.expanded_chunks_steps) - 1
        if total_steps <= safe_precomputed_steps:
            return sum(self.expanded_chunks_steps[i] for i in range(total_steps, -1, -2))

        reachable_garden_plots = 0
        chunks_radius = self.expanded_chunks_radius + ((total_steps - safe_precomputed_steps + (self.size - 1)) // self.size)
        assert chunks_radius > self.expanded_chunks_radius >= 2
        delta_steps = (total_steps - safe_precomputed_steps) % self.size

        filled_chunks_radius = chunks_radius - (2 if delta_steps > 0 else 1)
        if filled_chunks_radius % 2 == 0:
            # Outermost layer of completely filled chunks have the same parity as the origin chunk.
            filled_even_chunks = (filled_chunks_radius + 1) ** 2
            filled_odd_chunks = filled_chunks_radius ** 2
        else:
            # Outermost layer of completely filled chunks have the opposite parity from the origin chunk.
            filled_odd_chunks = (filled_chunks_radius + 1) ** 2
            filled_even_chunks = filled_chunks_radius ** 2
        if total_steps % 2 == 0:
            reachable_garden_plots += (self.origin_chunk_even_steps * filled_even_chunks)
            reachable_garden_plots += (self.origin_chunk_odd_steps * filled_odd_chunks)
        else:
            reachable_garden_plots += (self.origin_chunk_odd_steps * filled_even_chunks)
            reachable_garden_plots += (self.origin_chunk_even_steps * filled_odd_chunks)

        if delta_steps > 0:
            # This is the length of the (n - 1)th chunk diagonals.
            diagonal_length = chunks_radius - 2
            if ((chunks_radius - 1) % 2) == (self.expanded_chunks_radius % 2):
                if total_steps % 2 == 0:
                    reachable_garden_plots += self.edge_cardinal_chunks_even_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_even_steps * diagonal_length
                else:
                    reachable_garden_plots += self.edge_cardinal_chunks_odd_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_odd_steps * diagonal_length
            else:
                if total_steps % 2 == 0:
                    reachable_garden_plots += self.edge_cardinal_chunks_odd_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_odd_steps * diagonal_length
                else:
                    reachable_garden_plots += self.edge_cardinal_chunks_even_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_even_steps * diagonal_length
            reachable_garden_plots += sum(self.edge_cardinal_chunks_steps[i] for i in range(delta_steps - 1, -1, -2))
            reachable_garden_plots += sum(self.edge_diagonal_chunks_steps[i] for i in range(delta_steps - 1, -1, -2)) * diagonal_length
        else:
            diagonal_length = chunks_radius - 1
            if (chunks_radius % 2) == (self.expanded_chunks_radius % 2):
                if total_steps % 2 == 0:
                    reachable_garden_plots += self.edge_cardinal_chunks_even_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_even_steps * diagonal_length
                else:
                    reachable_garden_plots += self.edge_cardinal_chunks_odd_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_odd_steps * diagonal_length
            else:
                if total_steps % 2 == 0:
                    reachable_garden_plots += self.edge_cardinal_chunks_odd_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_odd_steps * diagonal_length
                else:
                    reachable_garden_plots += self.edge_cardinal_chunks_even_steps
                    reachable_garden_plots += self.edge_diagonal_chunks_even_steps * diagonal_length

        return reachable_garden_plots


def expand_steps_matrix(matrix: deque[deque[Optional[int]]], template_matrix: tuple[tuple[Optional[int], ...], ...]) -> None:
    """
    >>> steps_matrix = deque([
    ...     deque([None, 1, 2]),
    ...     deque([1, 0, 1]),
    ...     deque([2, 1, 2]),
    ... ])
    >>> template_steps_matrix = (
    ...     (None, -1, -1),
    ...     (-1, -1, -1),
    ...     (-1, -1, -1),
    ... )
    >>> expand_steps_matrix(steps_matrix, template_steps_matrix)
    >>> steps_matrix
    deque([deque([None, -1, -1, None, -1, -1, None, -1, -1]), deque([-1, -1, -1, -1, -1, -1, -1, -1, -1]), deque([-1, -1, -1, -1, -1, -1, -1, -1, -1]), deque([None, -1, -1, None, 1, 2, None, -1, -1]), deque([-1, -1, -1, 1, 0, 1, -1, -1, -1]), deque([-1, -1, -1, 2, 1, 2, -1, -1, -1]), deque([None, -1, -1, None, -1, -1, None, -1, -1]), deque([-1, -1, -1, -1, -1, -1, -1, -1, -1]), deque([-1, -1, -1, -1, -1, -1, -1, -1, -1])])
    """
    old_size = len(matrix)
    template_size = len(template_matrix)
    (old_expansion_factor, remainder) = divmod(old_size, template_size)
    assert remainder == 0
    new_expansion_factor = old_expansion_factor + 2
    new_size = template_size * new_expansion_factor
    assert new_size <= MAX_STEPS_MATRIX_SIZE
    for (row, template_row) in zip(matrix, cycle(template_matrix)):
        assert (len(row) == old_size) and (len(template_row) == template_size)
        row.extendleft(reversed(template_row))
        row.extend(template_row)
    matrix.extendleft(deque(template_row * new_expansion_factor) for template_row in reversed(template_matrix))
    matrix.extend(deque(template_row * new_expansion_factor) for template_row in template_matrix)


def fill_steps_matrix(matrix: deque[deque[Optional[int]]], to_visit: dict[tuple[int, int], int]) -> dict[tuple[int, int], int]:
    """
    >>> steps_matrix = deque([
    ...     deque([-1, -1, -1, -1, -1]),
    ...     deque([-1, None, -1, -1, -1]),
    ...     deque([-1, -1, -1, -1, -1]),
    ...     deque([-1, -1, -1, -1, -1]),
    ...     deque([-1, -1, -1, -1, -1]),
    ... ])
    >>> unreachable_to_visit = fill_steps_matrix(steps_matrix, {(2, 2): 0})
    >>> sorted((x, y, steps) for ((x, y), steps) in unreachable_to_visit.items())
    [(-1, 0, 5), (-1, 1, 4), (-1, 2, 3), (-1, 3, 4), (-1, 4, 5), (0, -1, 5), (0, 5, 5), (1, -1, 4), (1, 5, 4), (2, -1, 3), (2, 5, 3), (3, -1, 4), (3, 5, 4), (4, -1, 5), (4, 5, 5), (5, 0, 5), (5, 1, 4), (5, 2, 3), (5, 3, 4), (5, 4, 5)]
    >>> steps_matrix
    deque([deque([4, 3, 2, 3, 4]), deque([3, None, 1, 2, 3]), deque([2, 1, 0, 1, 2]), deque([3, 2, 1, 2, 3]), deque([4, 3, 2, 3, 4])])
    """
    to_visit_queue: deque[tuple[int, int]] = deque()
    for ((x, y), steps) in to_visit.items():
        assert matrix[y][x] == -1
        matrix[y][x] = steps
        to_visit_queue.append((x, y))
    max_dim = len(matrix) - 1
    unreachable_to_visit: dict[tuple[int, int], int] = {}
    while to_visit_queue:
        (x, y) = to_visit_queue.popleft()
        assert (curr_steps := matrix[y][x]) is not None
        next_steps = curr_steps + 1
        y_north = y - 1
        if (y > 0):
            # If we were flood-filling once, we would only need to test for -1. However, to support resuming
            # flood-filling after expansion, we need to account for potentially discovering shorter paths (because they
            # were originally unreachable and thus weren't queued).
            if ((existing_steps := matrix[y_north][x]) is not None) and ((existing_steps == -1) or (existing_steps > next_steps)):
                matrix[y_north][x] = next_steps
                to_visit_queue.append((x, y_north))
        elif ((x, y_north) not in unreachable_to_visit) or (unreachable_to_visit[(x, y_north)] > next_steps):
            # Unreachable tile would be an edge tile, which is guaranteed to be rock-free.
            unreachable_to_visit[(x, y_north)] = next_steps
        y_south = y + 1
        if (y < max_dim):
            if ((existing_steps := matrix[y_south][x]) is not None) and ((existing_steps == -1) or (existing_steps > next_steps)):
                matrix[y_south][x] = next_steps
                to_visit_queue.append((x, y_south))
        elif ((x, y_south) not in unreachable_to_visit) or (unreachable_to_visit[(x, y_south)] > next_steps):
            unreachable_to_visit[(x, y_south)] = next_steps
        x_west = x - 1
        if (x > 0):
            if ((existing_steps := matrix[y][x_west]) is not None) and ((existing_steps == -1) or (existing_steps > next_steps)):
                matrix[y][x_west] = next_steps
                to_visit_queue.append((x_west, y))
        elif ((x_west, y) not in unreachable_to_visit) or (unreachable_to_visit[(x_west, y)] > next_steps):
            unreachable_to_visit[(x_west, y)] = next_steps
        x_east = x + 1
        if (x < max_dim):
            if ((existing_steps := matrix[y][x_east]) is not None) and ((existing_steps == -1) or (existing_steps > next_steps)):
                matrix[y][x_east] = next_steps
                to_visit_queue.append((x_east, y))
        elif ((x_east, y) not in unreachable_to_visit) or (unreachable_to_visit[(x_east, y)] > next_steps):
            unreachable_to_visit[(x_east, y)] = next_steps
    return unreachable_to_visit


def verify_steps_matrix(matrix: deque[deque[Optional[int]]], size: int) -> Optional[tuple[tuple[int, ...], int, int, tuple[int, ...], int, tuple[int, ...], int, int, tuple[int, ...], int, int]]:
    expanded_size = len(matrix)
    (expansion_factor, remainder) = divmod(expanded_size, size)
    assert (expansion_factor >= 3) and (expansion_factor % 2 == 1) and (remainder == 0)
    low_outer_chunk_end = (low_outer_chunk_start := 0) + size
    origin_chunk_end = (origin_chunk_start := size * (expansion_factor // 2)) + size
    high_inner_chunk_end = (high_inner_chunk_start := expanded_size - (size * 2)) + size
    # Check north.
    if not all(
        (outer_steps - inner_steps == size)
        for y in range(low_outer_chunk_start, low_outer_chunk_end)
        for x in range(origin_chunk_start, origin_chunk_end)
        if ((inner_steps := matrix[y + size][x]) is not None) and ((outer_steps := matrix[y][x]) is not None) and not (inner_steps == outer_steps == -1)
    ):
        return None
    # Check south.
    if not all(
        (outer_steps - inner_steps == size)
        for y in range(high_inner_chunk_start, high_inner_chunk_end)
        for x in range(origin_chunk_start, origin_chunk_end)
        if ((inner_steps := matrix[y][x]) is not None) and ((outer_steps := matrix[y + size][x]) is not None) and not (inner_steps == outer_steps == -1)
    ):
        return None
    # Check east.
    if not all(
        (outer_steps - inner_steps == size)
        for y in range(origin_chunk_start, origin_chunk_end)
        for x in range(high_inner_chunk_start, high_inner_chunk_end)
        if ((inner_steps := matrix[y][x]) is not None) and ((outer_steps := matrix[y][x + size]) is not None) and not (inner_steps == outer_steps == -1)
    ):
        return None
    # Check west.
    if not all(
        (outer_steps - inner_steps == size)
        for y in range(origin_chunk_start, origin_chunk_end)
        for x in range(low_outer_chunk_start, low_outer_chunk_end)
        if ((inner_steps := matrix[y][x + size]) is not None) and ((outer_steps := matrix[y][x]) is not None) and not (inner_steps == outer_steps == -1)
    ):
        return None

    # So far, so good. Next, verify the diagonal chunks.
    #
    # Ensure the chunk to the east of the northernmost chunk is the same as the chunk to the north of the easternmost
    # chunk.
    assert all(steps_ne == steps_en for (steps_ne, steps_en) in zip((
        matrix[y][x]
        for y in range(0, size)
        for x in range(origin_chunk_end, origin_chunk_end + size)
    ), (
        matrix[y][x]
        for y in range(origin_chunk_start - size, origin_chunk_start)
        for x in range(expanded_size - size, expanded_size)
    )))
    # Ensure the chunk to the west of the northernmost chunk is the same as the chunk to the north of the westernmost
    # chunk.
    assert all(steps_nw == steps_wn for (steps_nw, steps_wn) in zip((
        matrix[y][x]
        for y in range(0, size)
        for x in range(origin_chunk_start - size, origin_chunk_start)
    ), (
        matrix[y][x]
        for y in range(origin_chunk_start - size, origin_chunk_start)
        for x in range(0, size)
    )))
    # Ensure the chunk to the east of the southernmost chunk is the same as the chunk to the south of the easternmost
    # chunk.
    assert all(steps_se == steps_es for (steps_se, steps_es) in zip((
        matrix[y][x]
        for y in range(expanded_size - size, expanded_size)
        for x in range(origin_chunk_end, origin_chunk_end + size)
    ), (
        matrix[y][x]
        for y in range(origin_chunk_end, origin_chunk_end + size)
        for x in range(expanded_size - size, expanded_size)
    )))
    # Ensure the chunk to the west of the southernmost chunk is the same as the chunk to the south of the westernmost
    # chunk.
    assert all(steps_sw == steps_ws for (steps_sw, steps_ws) in zip((
        matrix[y][x]
        for y in range(expanded_size - size, expanded_size)
        for x in range(origin_chunk_start - size, origin_chunk_start)
    ), (
        matrix[y][x]
        for y in range(origin_chunk_end, origin_chunk_end + size)
        for x in range(0, size)
    )))

    # Now that we've verified that the frontier expands in a pattern, we can transform the steps matrix into something
    # that's easier to count reachable garden plots with: an array where the element at index i represents the number of
    # new garden plots reachable with that many number of steps.
    #
    # We'll start with just the origin chunk (for the case without wraparound).
    origin_chunk_steps_counter: Counter[int] = Counter()
    origin_chunk_even_steps = 0
    origin_chunk_odd_steps = 0
    for y in range(origin_chunk_start, origin_chunk_end):
        for x in range(origin_chunk_start, origin_chunk_end):
            if ((steps := matrix[y][x]) is None) or (steps == -1):
                continue
            origin_chunk_steps_counter[steps] += 1
            if steps % 2 == 0:
                origin_chunk_even_steps += 1
            else:
                origin_chunk_odd_steps += 1
    # We expect the keys to be contiguous; you can't reach the maximum number of steps without going through all the
    # other steps.
    origin_chunk_steps = tuple(origin_chunk_steps_counter[i] for i in range(max(origin_chunk_steps_counter.keys()) + 1))

    # Next, we'll do the same with the expanded steps matrix, up to a safe number of steps. (The safe number of steps is
    # whatever the smallest number of steps is along the edges of the steps matrix. Beyond that would involve treading
    # into chunks that our steps matrix doesn't cover.)
    safe_precomputed_steps = min(
        # Northern edge.
        *(steps for x in range(expanded_size) if ((steps := matrix[0][x]) is not None) and (steps != -1)),
        # Southern edge.
        *(steps for x in range(expanded_size) if ((steps := matrix[-1][x]) is not None) and (steps != -1)),
        # Eastern edge.
        *(steps for y in range(expanded_size) if ((steps := matrix[y][-1]) is not None) and (steps != -1)),
        # Western edge.
        *(steps for y in range(expanded_size) if ((steps := matrix[y][0]) is not None) and (steps != -1)),
    )
    expanded_chunks_steps_counter: Counter[int] = Counter()
    for y in range(expanded_size):
        for x in range(expanded_size):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps > safe_precomputed_steps):
                continue
            expanded_chunks_steps_counter[steps] += 1
    expanded_chunks_steps = tuple(expanded_chunks_steps_counter[i] for i in range(safe_precomputed_steps + 1))
    expanded_chunks_radius = expansion_factor // 2

    # Finally, we'll compute what we need to derive the partial edge chunks. For (at least one of) the cardinal
    # directions, the first step after the safe number of steps takes us into a new chunk; let's call this the nth chunk
    # (radially speaking from the origin chunk). However, the (n - 1)th chunk may still be partial. The same applies for
    # the diagonals, except we also have to worry about the (n + 1)th chunk, and the (n - 1)th chunk doesn't exist if
    # our steps matrix is only 5 × 5 chunks.
    #
    #       | ..4a1..
    # .4a1. | .4lAi1.
    # 4lAi1 | 4lL.Ii1
    # dDOBb | dD.O.Bb
    # 3kCj2 | 3kK.Jj2
    # .3c2. | .3kCj2.
    #       | ..3c2..
    #
    # In the above examples:
    #   - O is the origin chunk;
    #   - A, B, C, and D are the (n - 1)th chunks in the cardinal directions;
    #   - I, J, K, and L are the (n - 1)th chunks in the diagonal directions;
    #   - a, b, c, and d are the nth chunks in the cardinal directions;
    #   - i, j, k, and l are the nth chunks in the diagonal directions; and
    #   - 1, 2, 3, and 4 are the (n + 1)th chunks in the diagonal directions.
    #
    # We'll prepare two arrays that we can use to calculate steps for the inclusive interval from (safe number of steps
    # + 1) to (safe number of steps + size):
    #   - one combining the nth and (n - 1)th chunks in the cardinal directions (plus eight of the (n + 1)th chunks and
    #     four of the nth chunks in the diagonal directions); and
    #   - one combining the (n + 1)th, nth, and (n - 1)th chunks in the diagonal directions.
    #
    # One thing to note: we're calculating deltas between the nth chunk (which doesn't exist in the steps matrix) and
    # the (n - 1)th chunk using the (n - 1)th and (n - 2)th chunks, so the parities need to be flipped.
    offset_steps = safe_precomputed_steps - size
    edge_cardinal_chunks_steps_counter: Counter[int] = Counter()
    edge_cardinal_chunks_even_steps = 0
    edge_cardinal_chunks_odd_steps = 0
    # Tally nth and (n - 1)th northern chunks using (n - 1)th and (n - 2)th northern chunks.
    for y in range(0, size * 2):
        for x in range(origin_chunk_start, origin_chunk_end):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                continue
            if steps <= offset_steps:
                # Remember the parity is flipped.
                if steps % 2 == 0:
                    edge_cardinal_chunks_odd_steps += 1
                else:
                    edge_cardinal_chunks_even_steps += 1
            else:
                delta_steps = steps - offset_steps
                assert 1 <= delta_steps < size
                edge_cardinal_chunks_steps_counter[delta_steps] += 1
    # Tally nth and (n - 1)th southern chunks using (n - 1)th and (n - 2)th southern chunks.
    for y in range(expanded_size - (size * 2), expanded_size):
        for x in range(origin_chunk_start, origin_chunk_end):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                continue
            if steps <= offset_steps:
                # Remember the parity is flipped.
                if steps % 2 == 0:
                    edge_cardinal_chunks_odd_steps += 1
                else:
                    edge_cardinal_chunks_even_steps += 1
            else:
                delta_steps = steps - offset_steps
                assert 1 <= delta_steps < size
                edge_cardinal_chunks_steps_counter[delta_steps] += 1
    # Tally nth and (n - 1)th eastern chunks using (n - 1)th and (n - 2)th eastern chunks.
    for y in range(origin_chunk_start, origin_chunk_end):
        for x in range(expanded_size - (size * 2), expanded_size):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                continue
            if steps <= offset_steps:
                # Remember the parity is flipped.
                if steps % 2 == 0:
                    edge_cardinal_chunks_odd_steps += 1
                else:
                    edge_cardinal_chunks_even_steps += 1
            else:
                delta_steps = steps - offset_steps
                assert 1 <= delta_steps < size
                edge_cardinal_chunks_steps_counter[delta_steps] += 1
    # Tally nth and (n - 1)th western chunks using (n - 1)th and (n - 2)th western chunks.
    for y in range(origin_chunk_start, origin_chunk_end):
        for x in range(0, size * 2):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                continue
            if steps <= offset_steps:
                # Remember the parity is flipped.
                if steps % 2 == 0:
                    edge_cardinal_chunks_odd_steps += 1
                else:
                    edge_cardinal_chunks_even_steps += 1
            else:
                delta_steps = steps - offset_steps
                assert 1 <= delta_steps < size
                edge_cardinal_chunks_steps_counter[delta_steps] += 1
    edge_diagonal_chunks_steps_counter: Counter[int] = Counter()
    edge_diagonal_chunks_even_steps = 0
    edge_diagonal_chunks_odd_steps = 0
    # Tally (n + 1)th NW/NE/SW/SE chunks using chunks to the west/east of the (n - 1)th northern/southern chunks.
    for y in chain(range(0, size), range(expanded_size - size, expanded_size)):
        for x in chain(range(origin_chunk_start - size, origin_chunk_start), range(origin_chunk_end, origin_chunk_end + size)):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                continue
            if steps <= offset_steps:
                # Remember the parity is flipped.
                if steps % 2 == 0:
                    edge_cardinal_chunks_odd_steps += 2
                    edge_diagonal_chunks_odd_steps += 1
                else:
                    edge_cardinal_chunks_even_steps += 2
                    edge_diagonal_chunks_even_steps += 1
            else:
                delta_steps = steps - offset_steps
                assert 1 <= delta_steps < size
                edge_cardinal_chunks_steps_counter[delta_steps] += 2
                edge_diagonal_chunks_steps_counter[delta_steps] += 1
    # Tally nth NW/NE/SW/SE chunks using chunks to the west/east of the (n - 2)th northern/southern chunks.
    for y in chain(range(size, size * 2), range(expanded_size - (size * 2), expanded_size - size)):
        for x in chain(range(origin_chunk_start - size, origin_chunk_start), range(origin_chunk_end, origin_chunk_end + size)):
            if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                continue
            if steps <= offset_steps:
                # Remember the parity is flipped.
                if steps % 2 == 0:
                    edge_cardinal_chunks_odd_steps += 1
                    edge_diagonal_chunks_odd_steps += 1
                else:
                    edge_cardinal_chunks_even_steps += 1
                    edge_diagonal_chunks_even_steps += 1
            else:
                delta_steps = steps - offset_steps
                assert 1 <= delta_steps < size
                edge_cardinal_chunks_steps_counter[delta_steps] += 1
                edge_diagonal_chunks_steps_counter[delta_steps] += 1
    # Tally (n - 1)th NW/NE/SW/SE chunks using chunks to the west/east of the (n - 3)th northern/southern chunks. If
    # they don't exist, use the chunks to the west/east of the (n - 2)th northern/southern chunk, but with adjusted
    # offsets and parity.
    if expansion_factor >= 7:
        for y in chain(range(size * 2, size * 3), range(expanded_size - (size * 3), expanded_size - (size * 2))):
            for x in chain(range(origin_chunk_start - size, origin_chunk_start), range(origin_chunk_end, origin_chunk_end + size)):
                if ((steps := matrix[y][x]) is None) or (steps == -1) or (steps >= safe_precomputed_steps):
                    continue
                if steps <= offset_steps:
                    # Remember the parity is flipped.
                    if steps % 2 == 0:
                        edge_diagonal_chunks_odd_steps += 1
                    else:
                        edge_diagonal_chunks_even_steps += 1
                else:
                    delta_steps = steps - offset_steps
                    assert 1 <= delta_steps < size
                    edge_diagonal_chunks_steps_counter[delta_steps] += 1
    else:
        for y in chain(range(size, size * 2), range(expanded_size - (size * 2), expanded_size - size)):
            for x in chain(range(origin_chunk_start - size, origin_chunk_start), range(origin_chunk_end, origin_chunk_end + size)):
                if ((steps := matrix[y][x]) is None) or (steps == -1):
                    continue
                if steps <= safe_precomputed_steps:
                    # Remember the parity is double-flipped.
                    if steps % 2 == 0:
                        edge_diagonal_chunks_even_steps += 1
                    else:
                        edge_diagonal_chunks_odd_steps += 1
                else:
                    delta_steps = steps - safe_precomputed_steps
                    assert 1 <= delta_steps < size
                    edge_diagonal_chunks_steps_counter[delta_steps] += 1
    # Compact counters.
    edge_cardinal_chunks_steps = tuple(edge_cardinal_chunks_steps_counter[i] for i in range(1, size))
    edge_diagonal_chunks_steps = tuple(edge_diagonal_chunks_steps_counter[i] for i in range(1, size))

    return (
        origin_chunk_steps, origin_chunk_even_steps, origin_chunk_odd_steps,
        expanded_chunks_steps, expanded_chunks_radius,
        edge_cardinal_chunks_steps, edge_cardinal_chunks_even_steps, edge_cardinal_chunks_odd_steps,
        edge_diagonal_chunks_steps, edge_diagonal_chunks_even_steps, edge_diagonal_chunks_odd_steps,
    )


########################################################################################################################
# Part 1
########################################################################################################################

def count_reachable_garden_plots(lines: Iterable[str]) -> int:
    map_ = Map.from_lines(lines)
    return map_.count_reachable_garden_plots(64)


########################################################################################################################
# Part 2
########################################################################################################################

def count_contrived_reachable_garden_plots(lines: Iterable[str]) -> int:
    map_ = Map.from_lines(lines)
    return map_.count_reachable_garden_plots_with_wraparound(26501365)


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
        print(count_reachable_garden_plots(lines))
    elif args.part == 2:
        print(count_contrived_reachable_garden_plots(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
