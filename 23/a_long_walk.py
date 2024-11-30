#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
from io import StringIO
from operator import itemgetter
from typing import NamedTuple, Optional


########################################################################################################################
# Bit manipulation
########################################################################################################################

def decompose(bitmask: int) -> Iterator[int]:
    """
    >>> list(decompose(0b1000101))
    [1, 4, 64]
    """
    i = 0
    while bitmask:
        if bitmask & 1:
            yield 1 << i
        bitmask >>= 1
        i += 1


########################################################################################################################
# Map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int


class CardinalDirection(Enum):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'

    @property
    def reverse(self) -> 'CardinalDirection':
        if self == CardinalDirection.NORTH:
            return CardinalDirection.SOUTH
        elif self == CardinalDirection.SOUTH:
            return CardinalDirection.NORTH
        elif self == CardinalDirection.EAST:
            return CardinalDirection.WEST
        elif self == CardinalDirection.WEST:
            return CardinalDirection.EAST
        else:
            raise ValueError(f'Unexpected direction: {self!r}')


def translate(width: int, height: int, coord: Coordinate, direction: CardinalDirection) -> Optional[Coordinate]:
    (x, y) = coord
    assert 0 <= x < width
    assert 0 <= y < height
    if direction == CardinalDirection.NORTH:
        if y > 0:
            return Coordinate(x, y - 1)
    elif direction == CardinalDirection.SOUTH:
        if y < height - 1:
            return Coordinate(x, y + 1)
    elif direction == CardinalDirection.EAST:
        if x < width - 1:
            return Coordinate(x + 1, y)
    elif direction == CardinalDirection.WEST:
        if x > 0:
            return Coordinate(x - 1, y)
    else:
        raise ValueError(f'Unexpected direction: {direction!r}')
    return None


class Tile(Enum):
    PATH = '.'
    FOREST = '#'
    NORTH_FACING_SLOPE = '^'
    EAST_FACING_SLOPE = '>'
    SOUTH_FACING_SLOPE = 'v'
    WEST_FACING_SLOPE = '<'


SLOPE_TO_CARDINAL_DIRECTION = {
    Tile.NORTH_FACING_SLOPE: CardinalDirection.NORTH,
    Tile.EAST_FACING_SLOPE: CardinalDirection.EAST,
    Tile.SOUTH_FACING_SLOPE: CardinalDirection.SOUTH,
    Tile.WEST_FACING_SLOPE: CardinalDirection.WEST,
}


class Map(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[Tile, ...], ...]
    starting_position: Coordinate
    ending_position: Coordinate
    paths: dict[Coordinate, set[tuple[Coordinate, Coordinate, bool, tuple[Coordinate, ...]]]]
    are_slopes_slippery: bool

    @classmethod
    def from_lines(cls, lines: Iterable[str], are_slopes_slippery: bool) -> 'Map':
        width = -1
        rows: list[tuple[Tile, ...]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                assert width >= 3
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            if are_slopes_slippery:
                row = tuple(Tile(char) for char in line)
            else:
                row = tuple({
                    Tile.PATH: Tile.PATH,
                    Tile.FOREST: Tile.FOREST,
                    Tile.NORTH_FACING_SLOPE: Tile.PATH,
                    Tile.EAST_FACING_SLOPE: Tile.PATH,
                    Tile.SOUTH_FACING_SLOPE: Tile.PATH,
                    Tile.WEST_FACING_SLOPE: Tile.PATH,
                }[Tile(char)] for char in line)
            if y == 0:
                assert row == (Tile.FOREST, Tile.PATH) + ((Tile.FOREST,) * (width - 2))
            else:
                assert row[0] == row[-1] == Tile.FOREST
            rows.append(row)
        height = y + 1
        starting_position = Coordinate(1, 0)
        assert row == ((Tile.FOREST,) * (width - 2)) + (Tile.PATH, Tile.FOREST)
        ending_position = Coordinate(width - 2, y)

        paths: dict[Coordinate, set[tuple[Coordinate, Coordinate, bool, tuple[Coordinate, ...]]]] = {}
        explored_paths: set[tuple[Coordinate, CardinalDirection]] = set()
        paths_to_explore: list[tuple[Coordinate, CardinalDirection]] = [(starting_position, CardinalDirection.SOUTH)]
        while paths_to_explore:
            (starting_path_position, prev_path_direction) = paths_to_explore.pop(0)
            if (starting_path_position, prev_path_direction) in explored_paths:
                continue
            explored_paths.add((starting_path_position, prev_path_direction))
            prev_path_position = starting_path_position
            is_bidirectional = starting_path_position != starting_position
            path_positions: list[Coordinate] = []
            while True:
                path_position = translate(width, height, prev_path_position, prev_path_direction)
                assert path_position is not None
                path_positions.append(path_position)
                path_tile = rows[path_position.y][path_position.x]
                assert path_tile in {Tile.PATH, Tile.NORTH_FACING_SLOPE, Tile.EAST_FACING_SLOPE, Tile.SOUTH_FACING_SLOPE, Tile.WEST_FACING_SLOPE}

                if path_position == ending_position:
                    paths.setdefault(starting_path_position, set()).add((starting_path_position, path_position, False, tuple(path_positions)))
                    break

                path_directions = set(CardinalDirection) - {prev_path_direction.reverse}
                for path_direction in list(path_directions):
                    next_path_position = translate(width, height, path_position, path_direction)
                    if next_path_position is None:
                        path_directions.remove(path_direction)
                        continue
                    next_path_tile = rows[next_path_position.y][next_path_position.x]
                    if next_path_tile == Tile.FOREST:
                        path_directions.remove(path_direction)
                        continue
                    if next_path_tile in {Tile.NORTH_FACING_SLOPE, Tile.EAST_FACING_SLOPE, Tile.SOUTH_FACING_SLOPE, Tile.WEST_FACING_SLOPE}:
                        if SLOPE_TO_CARDINAL_DIRECTION[next_path_tile] == path_direction.reverse:
                            # This path is about to have us walk backwards. As an optimisation, we _could_ finish
                            # following the path and just remember the polarity.
                            path_directions.remove(path_direction)
                            continue
                        is_bidirectional = False
                    else:
                        assert next_path_tile == Tile.PATH
                if len(path_directions) == 0:
                    # We have no valid ways forward. Abandon this path.
                    break
                if len(path_directions) > 1:
                    # We're at a junction. Time to finish this path segment, and start some new paths to explore.
                    paths.setdefault(starting_path_position, set()).add((starting_path_position, path_position, is_bidirectional, tuple(path_positions)))
                    for path_direction in path_directions:
                        paths_to_explore.append((path_position, path_direction))
                    break
                assert len(path_directions) == 1
                prev_path_position = path_position
                prev_path_direction = path_directions.pop()

        if are_slopes_slippery:
            # Verify we have a DAG.
            path_positions_to_incoming_path_positions: dict[Coordinate, set[Coordinate]] = {}
            for starting_path_position in paths:
                for (_, ending_path_position, is_bidirectional, _) in paths[starting_path_position]:
                    assert not is_bidirectional
                    path_positions_to_incoming_path_positions.setdefault(ending_path_position, set()).add(starting_path_position)
            visited_path_positions: set[Coordinate] = set()
            path_positions_to_visit: set[Coordinate] = {starting_position}
            while path_positions_to_visit:
                starting_path_position = path_positions_to_visit.pop()
                visited_path_positions.add(starting_path_position)
                if starting_path_position in paths:
                    for ending_path_position in set(ending_path_position for (_, ending_path_position, _, _) in paths[starting_path_position]):
                        path_positions_to_incoming_path_positions[ending_path_position].remove(starting_path_position)
                        if not path_positions_to_incoming_path_positions[ending_path_position]:
                            del path_positions_to_incoming_path_positions[ending_path_position]
                            path_positions_to_visit.add(ending_path_position)
                else:
                    assert starting_path_position == ending_position
            assert not path_positions_to_incoming_path_positions
        else:
            # Verify we have an undirected graph.
            for starting_path_position in paths:
                for (_, ending_path_position, is_bidirectional, _) in paths[starting_path_position]:
                    assert is_bidirectional or (starting_path_position == starting_position) or (ending_path_position == ending_position)
                    assert (ending_path_position in paths) or (ending_path_position == ending_position)

        return Map(width, height, tuple(rows), starting_position, ending_position, paths, are_slopes_slippery)

    def to_dot_graph(self) -> str:
        output = StringIO()
        output.write('digraph {\n  node [shape=box]\n')

        visited_path_positions: set[Coordinate] = set()
        for starting_path_position in sorted(self.paths):
            visited_path_positions.add(starting_path_position)

            (x, y) = starting_path_position
            starting_node_id = f'node_{x}_{y}'
            attrs = f'label="({x}, {y})"'
            if starting_path_position == self.starting_position:
                attrs += ', style=filled, fillcolor=red, fontcolor=white'
            output.write(f'  {starting_node_id} [{attrs}]\n')

            for (_, ending_path_position, is_bidirectional, path_positions_sequence) in sorted(self.paths[starting_path_position], key=itemgetter(1)):
                (x, y) = ending_path_position
                weight = len(path_positions_sequence) - 1
                attrs = f'label="{weight}", '
                if is_bidirectional and ending_path_position in visited_path_positions:
                    continue
                attrs += 'dir=both' if is_bidirectional else 'style=dashed'
                output.write(f'  {starting_node_id} -> node_{x}_{y} [{attrs}]\n')

        (x, y) = self.ending_position
        output.write(f'  node_{x}_{y} [label="({x}, {y})", style=filled, fillcolor=red, fontcolor=white]\n')

        output.write('}')
        return output.getvalue()

    def count_steps_for_longest_hiking_trail(self) -> int:
        # The trails can be represented as a graph, where each vertex represents a junction and each edge represents a
        # path. By definition, each vertex (with the exception of the starting and ending vertices) is adjacent to three
        # or four other vertices. (We ignore dead end paths, and a vertex that's only adjacent to two vertices wouldn't
        # be a junction so much as part of the path between those two vertices.)
        #
        # When the slopes are slippery, it so happens that we get a directed acyclic graph (DAG) that's amenable to
        # brute forcing (i.e., enumerating all possible paths via depth-first search [DFS]).
        #
        # However, when the slopes are dry, this graph becomes undirected and full of cycles, and thus impractical to
        # brute force. Because all vertices (except for the starting and ending vertices) have degree three or four, we
        # can't cut the graph into subgraphs that are more amenable to brute forcing.
        if self.are_slopes_slippery:
            return self.__count_longest_path_for_dag_by_brute_force()
        else:
            return self.__count_longest_path_for_undirected_graph_by_dp()

    def __count_longest_path_for_dag_by_brute_force(self) -> int:
        def explore(visited_path_positions: set[Coordinate], starting_path_position: Coordinate) -> Iterator[set[Coordinate]]:
            assert starting_path_position in self.paths
            for (_, ending_path_position, _, path_positions_sequence) in self.paths[starting_path_position]:
                path_positions = set(path_positions_sequence)
                if visited_path_positions & path_positions:
                    # New path traverses previously visited tiles; abandon.
                    continue
                combined_path_positions = visited_path_positions | path_positions
                if ending_path_position == self.ending_position:
                    yield combined_path_positions
                if ending_path_position not in self.paths:
                    continue
                yield from explore(combined_path_positions, ending_path_position)
        return max(len(positions) for positions in explore(set(), self.starting_position))

    def __count_longest_path_for_undirected_graph_by_dp(self) -> int:
        # There should only be one directed edge from the starting position to the first junction.
        assert len(self.paths[self.starting_position]) == 1
        (_, ending_path_position, is_bidirectional, path_positions_sequence) = next(iter(self.paths[self.starting_position]))
        assert not is_bidirectional
        starting_vertex_coordinate = ending_path_position
        onramp_edge_length = len(path_positions_sequence)

        # There should only be one directed path from the last junction to the ending position.
        ending_vertex_coordinate: Optional[Coordinate] = None
        offramp_edge_length: Optional[int] = None
        for starting_path_position in self.paths:
            for (_, ending_path_position, is_bidirectional, path_positions_sequence) in self.paths[starting_path_position]:
                if ending_path_position == self.ending_position:
                    assert not is_bidirectional
                    assert ending_vertex_coordinate is None
                    ending_vertex_coordinate = starting_path_position
                    offramp_edge_length = len(path_positions_sequence)
        assert ending_vertex_coordinate is not None
        assert offramp_edge_length is not None

        # Use bitmasks to more efficiently encode sets of vertices. We don't care about the starting or ending
        # positions, since they're excluded from our permutations.
        vertex_bitmasks: dict[Coordinate, int] = {}
        vertex_bitmask = 1
        for starting_path_position in sorted(self.paths):
            if starting_path_position == self.starting_position:
                continue
            vertex_bitmasks[starting_path_position] = vertex_bitmask
            vertex_bitmask <<= 1
        assert len(vertex_bitmasks) > 0
        starting_vertex_bitmask = vertex_bitmasks[starting_vertex_coordinate]
        ending_vertex_bitmask = vertex_bitmasks[ending_vertex_coordinate]
        all_vertices_bitmask = vertex_bitmask - 1

        # Prepare some additional tables for faster lookups. (The sorted iteration is just to make debugging easier,
        # since dicts preserve insertion order.)
        vertex_neighbours: dict[int, int] = {}
        edge_lengths: dict[int, int] = {}
        for starting_path_position in sorted(self.paths):
            if starting_path_position == self.starting_position:
                continue
            vertex_i_bitmask = vertex_bitmasks[starting_path_position]
            neighbours_bitmask = 0
            for (_, ending_path_position, is_bidirectional, path_positions_sequence) in sorted(self.paths[starting_path_position], key=itemgetter(1)):
                if not is_bidirectional:
                    continue
                vertex_j_bitmask = vertex_bitmasks[ending_path_position]
                neighbours_bitmask |= vertex_j_bitmask
                edge_bitmask = vertex_i_bitmask | vertex_j_bitmask
                if edge_bitmask not in edge_lengths:
                    edge_lengths[edge_bitmask] = len(path_positions_sequence)
                else:
                    assert edge_lengths[edge_bitmask] == len(path_positions_sequence)
            vertex_neighbours[vertex_i_bitmask] = neighbours_bitmask

        # Prepare traversal order.
        bfs_visited_vertices = starting_vertex_bitmask
        bfs_vertices_order = [starting_vertex_bitmask]
        for vertex_i_bitmask in bfs_vertices_order:
            for vertex_j_bitmask in decompose(vertex_neighbours[vertex_i_bitmask]):
                if vertex_j_bitmask & bfs_visited_vertices:
                    continue
                bfs_visited_vertices |= vertex_j_bitmask
                bfs_vertices_order.append(vertex_j_bitmask)
        assert bfs_visited_vertices == all_vertices_bitmask

        # Track the longest path (that's the inner dict's value) from `starting_vertex_coordinate` to some path position
        # (that's the outer dict's key) visiting some subset of path positions (that's the inner dict's key). Space
        # complexity is O(n * 2^n).
        vertex_longest_paths: dict[int, dict[int, int]] = {}
        visited_vertices = 0
        for vertex_j in range(len(bfs_vertices_order)):
            vertex_j_bitmask = bfs_vertices_order[vertex_j]
            visited_vertices |= vertex_j_bitmask
            if vertex_j_bitmask == starting_vertex_bitmask:
                vertex_longest_paths[vertex_j_bitmask] = {
                    vertex_j_bitmask: 0,
                }
                continue
            # Teach new vertex about longest path to it.
            vertex_j_longest_paths: dict[int, int] = {}
            for vertex_i_bitmask in decompose(vertex_neighbours[vertex_j_bitmask] & visited_vertices):
                edge_length = edge_lengths[vertex_i_bitmask | vertex_j_bitmask]
                for (old_vertices_bitmask, old_edge_length) in vertex_longest_paths[vertex_i_bitmask].items():
                    new_vertices_bitmask = old_vertices_bitmask | vertex_j_bitmask
                    new_edge_length = old_edge_length + edge_length
                    if (new_vertices_bitmask not in vertex_j_longest_paths) or (vertex_j_longest_paths[new_vertices_bitmask] < new_edge_length):
                        vertex_j_longest_paths[new_vertices_bitmask] = new_edge_length
            vertex_longest_paths[vertex_j_bitmask] = vertex_j_longest_paths
            # Teach other vertices about longest path via new vertex.
            reverse_bfs_visited_vertices = vertex_j_bitmask
            reverse_bfs_vertices_order = [vertex_j_bitmask]
            for vertex_h_bitmask in reverse_bfs_vertices_order:
                vertex_h_longest_paths = vertex_longest_paths[vertex_h_bitmask]
                needs_repropagation = False
                for vertex_g_bitmask in decompose(vertex_neighbours[vertex_h_bitmask] & visited_vertices):
                    if not (vertex_g_bitmask & reverse_bfs_visited_vertices):
                        reverse_bfs_visited_vertices |= vertex_g_bitmask
                        reverse_bfs_vertices_order.append(vertex_g_bitmask)
                    edge_length = edge_lengths[vertex_g_bitmask | vertex_h_bitmask]
                    for (old_vertices_bitmask, old_edge_length) in vertex_longest_paths[vertex_g_bitmask].items():
                        if old_vertices_bitmask & vertex_h_bitmask:
                            continue
                        new_vertices_bitmask = old_vertices_bitmask | vertex_h_bitmask
                        new_edge_length = old_edge_length + edge_length
                        if (new_vertices_bitmask not in vertex_h_longest_paths) or (vertex_h_longest_paths[new_vertices_bitmask] < new_edge_length):
                            vertex_h_longest_paths[new_vertices_bitmask] = new_edge_length
                            # We may have learned a new path that's of interest to vertices we've already covered. (This
                            # criteria could probably be improved.)
                            needs_repropagation = True
                if needs_repropagation:
                    for vertex_g_bitmask in decompose(vertex_neighbours[vertex_h_bitmask] & visited_vertices):
                        # This criteria could probably be improved.
                        if vertex_g_bitmask & reverse_bfs_visited_vertices:
                            reverse_bfs_vertices_order.insert(0, vertex_g_bitmask)

        # Reconstruct longest path.
        # import sys
        # reverse_vertex_bitmasks = {value: key for (key, value) in vertex_bitmasks.items()}
        # print(reverse_vertex_bitmasks[ending_vertex_bitmask], file=sys.stderr)
        # (_, length) = max(vertex_longest_paths[ending_vertex_bitmask].items(), key=itemgetter(1))
        # vertex_j_bitmask = visited_vertices = ending_vertex_bitmask
        # while vertex_j_bitmask != starting_vertex_bitmask:
        #     possibilities: list[tuple[int, int]] = []
        #     for vertex_i_bitmask in decompose(vertex_neighbours[vertex_j_bitmask]):
        #         for (vertices_bitmask, prev_length) in vertex_longest_paths[vertex_i_bitmask].items():
        #             if vertices_bitmask & visited_vertices:
        #                 continue
        #             if prev_length + edge_lengths[vertex_i_bitmask | vertex_j_bitmask] == length:
        #                 possibilities.append((vertex_i_bitmask, prev_length))
        #     assert len(possibilities) == 1
        #     (vertex_j_bitmask, length) = possibilities[0]
        #     visited_vertices |= vertex_j_bitmask
        #     print(reverse_vertex_bitmasks[vertex_j_bitmask], file=sys.stderr)

        return onramp_edge_length + max(vertex_longest_paths[ending_vertex_bitmask].values()) + offramp_edge_length


########################################################################################################################
# Part 1
########################################################################################################################

def count_steps_for_longest_wet_hiking_trail(lines: Iterable[str]) -> int:
    """
    >>> count_steps_for_longest_wet_hiking_trail([
    ...     '#.#####################',
    ...     '#.......#########...###',
    ...     '#######.#########.#.###',
    ...     '###.....#.>.>.###.#.###',
    ...     '###v#####.#v#.###.#.###',
    ...     '###.>...#.#.#.....#...#',
    ...     '###v###.#.#.#########.#',
    ...     '###...#.#.#.......#...#',
    ...     '#####.#.#.#######.#.###',
    ...     '#.....#.#.#.......#...#',
    ...     '#.#####.#.#.#########v#',
    ...     '#.#...#...#...###...>.#',
    ...     '#.#.#v#######v###.###v#',
    ...     '#...#.>.#...>.>.#.###.#',
    ...     '#####v#.#.###v#.#.###.#',
    ...     '#.....#...#...#.#.#...#',
    ...     '#.#########.###.#.#.###',
    ...     '#...###...#...#...#.###',
    ...     '###.###.#.###v#####v###',
    ...     '#...#...#.#.>.>.#.>.###',
    ...     '#.###.###.#.###.#.#v###',
    ...     '#.....###...###...#...#',
    ...     '#####################.#',
    ... ])
    94
    """
    map_ = Map.from_lines(lines, True)
    return map_.count_steps_for_longest_hiking_trail()


def visualise_wet_hiking_trail(lines: Iterable[str]) -> str:
    map_ = Map.from_lines(lines, True)
    return map_.to_dot_graph()


########################################################################################################################
# Part 2
########################################################################################################################

def count_steps_for_longest_dry_hiking_trail(lines: Iterable[str]) -> int:
    """
    >>> count_steps_for_longest_dry_hiking_trail([
    ...     '#.#####################',
    ...     '#.......#########...###',
    ...     '#######.#########.#.###',
    ...     '###.....#.>.>.###.#.###',
    ...     '###v#####.#v#.###.#.###',
    ...     '###.>...#.#.#.....#...#',
    ...     '###v###.#.#.#########.#',
    ...     '###...#.#.#.......#...#',
    ...     '#####.#.#.#######.#.###',
    ...     '#.....#.#.#.......#...#',
    ...     '#.#####.#.#.#########v#',
    ...     '#.#...#...#...###...>.#',
    ...     '#.#.#v#######v###.###v#',
    ...     '#...#.>.#...>.>.#.###.#',
    ...     '#####v#.#.###v#.#.###.#',
    ...     '#.....#...#...#.#.#...#',
    ...     '#.#########.###.#.#.###',
    ...     '#...###...#...#...#.###',
    ...     '###.###.#.###v#####v###',
    ...     '#...#...#.#.>.>.#.>.###',
    ...     '#.###.###.#.###.#.#v###',
    ...     '#.....###...###...#...#',
    ...     '#####################.#',
    ... ])
    154
    """
    map_ = Map.from_lines(lines, False)
    return map_.count_steps_for_longest_hiking_trail()


def visualise_dry_hiking_trail(lines: Iterable[str]) -> str:
    map_ = Map.from_lines(lines, False)
    return map_.to_dot_graph()


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--visualise', action='store_true')
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=argparse.FileType('rt'))
    args = parser.parse_args()
    lines = (line.rstrip('\n') for line in args.input)

    if args.part == 1:
        if args.visualise:
            print(visualise_wet_hiking_trail(lines))
        else:
            print(count_steps_for_longest_wet_hiking_trail(lines))
    elif args.part == 2:
        if args.visualise:
            print(visualise_dry_hiking_trail(lines))
        else:
            print(count_steps_for_longest_dry_hiking_trail(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
