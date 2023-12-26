#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import Counter
from collections.abc import Iterable
from math import ceil, comb, log
from random import randrange
import re
from typing import NamedTuple, Optional


########################################################################################################################
# Part 1
########################################################################################################################

VERTEX_ADJACENCIES_LINE_PATTERN = re.compile(r'^([a-z]+): *([ a-z]+)$')
MIN_CUT_STAGE_ONE_FAILURE_PROBABILITY = 0.01


class UndirectedGraph(NamedTuple):
    vertex_adjacencies: dict[str, set[str]]
    edges: set[tuple[str, str]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'UndirectedGraph':
        vertex_adjacencies: dict[str, set[str]] = {}
        edges: set[tuple[str, str]] = set()
        for (i, line) in enumerate(lines):
            match = VERTEX_ADJACENCIES_LINE_PATTERN.fullmatch(line)
            if not match:
                raise ValueError(f'Invalid vertex adjacencies on line {i + 1}: {line!r}')
            (vertex, raw_adjacent_vertices) = match.groups()
            adjacent_vertices = set(raw_adjacent_vertices.split())
            if vertex not in vertex_adjacencies:
                vertex_adjacencies[vertex] = adjacent_vertices
            else:
                vertex_adjacencies[vertex] |= adjacent_vertices
            for adjacent_vertex in adjacent_vertices:
                assert adjacent_vertex != vertex  # Assume no self-loops.
                if adjacent_vertex not in vertex_adjacencies:
                    vertex_adjacencies[adjacent_vertex] = {vertex}
                else:
                    vertex_adjacencies[adjacent_vertex].add(vertex)
                edges.add((vertex, adjacent_vertex) if vertex < adjacent_vertex else (adjacent_vertex, vertex))
        return UndirectedGraph(vertex_adjacencies, edges)

    def calculate_min_cut(self, expected_min_cut_size: int) -> tuple[set[str], set[str]]:
        """
        This is a simplified implementation of Karger's random contraction algorithm for computing the minimum cut of a
        graph.

        >>> (first_disjoint_subset, second_disjoint_subset) = UndirectedGraph.from_lines([
        ...     'jqt: rhn xhk nvd',
        ...     'rsh: frs pzl lsr',
        ...     'xhk: hfx',
        ...     'cmg: qnr nvd lhk bvb',
        ...     'rhn: xhk bvb hfx',
        ...     'bvb: xhk hfx',
        ...     'pzl: lsr hfx nvd',
        ...     'qnr: nvd',
        ...     'ntq: jqt hfx bvb xhk',
        ...     'nvd: lhk',
        ...     'lsr: lhk',
        ...     'rzs: qnr cmg lsr rsh',
        ...     'frs: qnr lhk lsr',
        ... ]).calculate_min_cut(3)
        >>> sorted(first_disjoint_subset)
        ['bvb', 'hfx', 'jqt', 'ntq', 'rhn', 'xhk']
        >>> sorted(second_disjoint_subset)
        ['cmg', 'frs', 'lhk', 'lsr', 'nvd', 'pzl', 'qnr', 'rsh', 'rzs']
        """
        stage_one_min_vertices = ceil(2 / MIN_CUT_STAGE_ONE_FAILURE_PROBABILITY)
        stage_one_results: Optional[tuple[dict[str, Counter], list[tuple[str, str]], set[tuple[str, str]], dict[str, set[str]]]] = None
        stage_two_iterations = 1
        stage_two_max_iterations = ceil(comb(stage_one_min_vertices, 2) * log(stage_one_min_vertices))
        while True:
            if stage_one_results is not None:
                vertex_adjacencies = {vertex: vertices.copy() for (vertex, vertices) in stage_one_results[0].items()}
                edges_list = stage_one_results[1].copy()
                edges_set = stage_one_results[2].copy()
                vertex_contractions = {vertex: vertices.copy() for (vertex, vertices) in stage_one_results[3].items()}
            else:
                vertex_adjacencies = {vertex: Counter(adjacent_vertices) for (vertex, adjacent_vertices) in self.vertex_adjacencies.items()}
                edges_list = list(self.edges)
                edges_set = self.edges.copy()
                vertex_contractions = {vertex: {vertex} for vertex in self.vertex_adjacencies.keys()}
            while len(edges_list) > 1:
                # Optimise for large numbers of vertices.
                if len(vertex_adjacencies) == stage_one_min_vertices:
                    if stage_one_results is not None:
                        stage_two_iterations += 1
                    else:
                        stage_one_results = (
                            {vertex: vertices.copy() for (vertex, vertices) in vertex_adjacencies.items()},
                            edges_list.copy(),
                            edges_set.copy(),
                            {vertex: vertices.copy() for (vertex, vertices) in vertex_contractions.items()},
                        )
                        stage_two_iterations = 1
                if stage_two_iterations >= stage_two_max_iterations:
                    stage_one_results = None
                # Pick a random edge to contract.
                (supernode, subnode) = edges_list.pop(randrange(len(edges_list)))
                edges_set.remove((supernode, subnode))
                # No self-loops.
                del vertex_adjacencies[supernode][subnode]
                del vertex_adjacencies[subnode][supernode]
                # Update adjacency list.
                for adjacent_vertex in vertex_adjacencies[subnode]:
                    assert adjacent_vertex != supernode
                    assert vertex_adjacencies[subnode][adjacent_vertex] == vertex_adjacencies[adjacent_vertex][subnode]
                    vertex_adjacencies[supernode][adjacent_vertex] += vertex_adjacencies[adjacent_vertex][subnode]
                    vertex_adjacencies[adjacent_vertex][supernode] += vertex_adjacencies[adjacent_vertex][subnode]
                    del vertex_adjacencies[adjacent_vertex][subnode]
                    old_edge = (subnode, adjacent_vertex) if (subnode < adjacent_vertex) else (adjacent_vertex, subnode)
                    new_edge = (supernode, adjacent_vertex) if (supernode < adjacent_vertex) else (adjacent_vertex, supernode)
                    edges_list.remove(old_edge)
                    edges_set.remove(old_edge)
                    if new_edge not in edges_set:
                        edges_list.append(new_edge)
                        edges_set.add(new_edge)
                del vertex_adjacencies[subnode]
                # Update bookkeeping for node contractions.
                vertex_contractions[supernode] |= vertex_contractions[subnode]
                del vertex_contractions[subnode]
            assert len(vertex_adjacencies) == 2
            assert len(vertex_contractions) == 2
            (first_node, second_node) = edges_list.pop()
            assert vertex_adjacencies[first_node][second_node] == vertex_adjacencies[second_node][first_node]
            assert first_node in vertex_contractions
            assert second_node in vertex_contractions
            if vertex_adjacencies[first_node][second_node] == expected_min_cut_size:
                return (vertex_contractions[first_node], vertex_contractions[second_node]) if (first_node < second_node) else (vertex_contractions[second_node], vertex_contractions[first_node])


def calculate_product_of_disjoint_subset_sizes_with_cut_size_three(lines: Iterable[str]) -> int:
    """
    >>> calculate_product_of_disjoint_subset_sizes_with_cut_size_three([
    ...     'jqt: rhn xhk nvd',
    ...     'rsh: frs pzl lsr',
    ...     'xhk: hfx',
    ...     'cmg: qnr nvd lhk bvb',
    ...     'rhn: xhk bvb hfx',
    ...     'bvb: xhk hfx',
    ...     'pzl: lsr hfx nvd',
    ...     'qnr: nvd',
    ...     'ntq: jqt hfx bvb xhk',
    ...     'nvd: lhk',
    ...     'lsr: lhk',
    ...     'rzs: qnr cmg lsr rsh',
    ...     'frs: qnr lhk lsr',
    ... ])
    54
    """
    graph = UndirectedGraph.from_lines(lines)
    (first_disjoint_subset, second_disjoint_subset) = graph.calculate_min_cut(3)
    return len(first_disjoint_subset) * len(second_disjoint_subset)


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
        print(calculate_product_of_disjoint_subset_sizes_with_cut_size_three(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
