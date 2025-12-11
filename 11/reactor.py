#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
import re
from typing import NamedTuple


########################################################################################################################
# Server rack
########################################################################################################################

VERTEX_ADJACENCIES_LINE_PATTERN = re.compile(r'^([a-z]+): *([ a-z]+)$')


class DirectedGraph(NamedTuple):
    vertices: set[str]
    vertex_adjacencies: dict[str, set[str]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'DirectedGraph':
        vertices: set[str] = set()
        vertex_adjacencies: dict[str, set[str]] = {}
        for (i, line) in enumerate(lines):
            match = VERTEX_ADJACENCIES_LINE_PATTERN.fullmatch(line)
            if not match:
                raise ValueError(f'Invalid vertex adjacencies on line {i + 1}: {line!r}')
            (vertex, raw_adjacent_vertices) = match.groups()
            adjacent_vertices = set(raw_adjacent_vertices.split())
            assert vertex not in adjacent_vertices  # Assume no self-loops.
            vertices.add(vertex)
            vertices.update(adjacent_vertices)
            if vertex not in vertex_adjacencies:
                vertex_adjacencies[vertex] = adjacent_vertices
            else:
                vertex_adjacencies[vertex] |= adjacent_vertices
        return DirectedGraph(set(vertices), vertex_adjacencies)

    def count_paths(self, from_vertex: str, to_vertex: str) -> int:
        assert from_vertex in self.vertices
        assert to_vertex in self.vertices

        if from_vertex == to_vertex:
            return 1

        if from_vertex not in self.vertex_adjacencies:
            return 0

        return sum(self.count_paths(adjacent_vertex, to_vertex) for adjacent_vertex in self.vertex_adjacencies[from_vertex])


########################################################################################################################
# Part 1
########################################################################################################################

def count_paths_from_you_to_out(lines: Iterable[str]) -> int:
    """
    >>> count_paths_from_you_to_out([
    ...     'aaa: you hhh',
    ...     'you: bbb ccc',
    ...     'bbb: ddd eee',
    ...     'ccc: ddd eee fff',
    ...     'ddd: ggg',
    ...     'eee: out',
    ...     'fff: out',
    ...     'ggg: out',
    ...     'hhh: ccc fff iii',
    ...     'iii: out',
    ... ])
    5
    """
    rack = DirectedGraph.from_lines(lines)
    return rack.count_paths('you', 'out')


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
        print(count_paths_from_you_to_out(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
