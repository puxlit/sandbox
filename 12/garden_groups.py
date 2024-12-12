#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from typing import NamedTuple


########################################################################################################################
# Map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'


class Edge(NamedTuple):
    start: Coordinate
    end: Coordinate


class Region(NamedTuple):
    id_: Coordinate
    area: int
    perimeter: int


class Map(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[str, ...], ...]
    regions: dict[str, set[Region]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        """
        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'AAAA',
        ...     'BBCD',
        ...     'BBCC',
        ...     'EEEC',
        ... ]).regions.items() for region in regions)
        [('A', Region(id_=Coordinate(x=0, y=0), area=4, perimeter=10)), ('B', Region(id_=Coordinate(x=0, y=1), area=4, perimeter=8)), ('C', Region(id_=Coordinate(x=2, y=1), area=4, perimeter=10)), ('D', Region(id_=Coordinate(x=3, y=1), area=1, perimeter=4)), ('E', Region(id_=Coordinate(x=0, y=3), area=3, perimeter=8))]
        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'OOOOO',
        ...     'OXOXO',
        ...     'OOOOO',
        ...     'OXOXO',
        ...     'OOOOO',
        ... ]).regions.items() for region in regions)
        [('O', Region(id_=Coordinate(x=0, y=0), area=21, perimeter=36)), ('X', Region(id_=Coordinate(x=1, y=1), area=1, perimeter=4)), ('X', Region(id_=Coordinate(x=1, y=3), area=1, perimeter=4)), ('X', Region(id_=Coordinate(x=3, y=1), area=1, perimeter=4)), ('X', Region(id_=Coordinate(x=3, y=3), area=1, perimeter=4))]
        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'RRRRIICCFF',
        ...     'RRRRIICCCF',
        ...     'VVRRRCCFFF',
        ...     'VVRCCCJFFF',
        ...     'VVVVCJJCFE',
        ...     'VVIVCCJJEE',
        ...     'VVIIICJJEE',
        ...     'MIIIIIJJEE',
        ...     'MIIISIJEEE',
        ...     'MMMISSJEEE',
        ... ]).regions.items() for region in regions)
        [('C', Region(id_=Coordinate(x=3, y=3), area=14, perimeter=28)), ('C', Region(id_=Coordinate(x=7, y=4), area=1, perimeter=4)), ('E', Region(id_=Coordinate(x=7, y=8), area=13, perimeter=18)), ('F', Region(id_=Coordinate(x=7, y=2), area=10, perimeter=18)), ('I', Region(id_=Coordinate(x=1, y=7), area=14, perimeter=22)), ('I', Region(id_=Coordinate(x=4, y=0), area=4, perimeter=8)), ('J', Region(id_=Coordinate(x=5, y=4), area=11, perimeter=20)), ('M', Region(id_=Coordinate(x=0, y=7), area=5, perimeter=12)), ('R', Region(id_=Coordinate(x=0, y=0), area=12, perimeter=18)), ('S', Region(id_=Coordinate(x=4, y=8), area=3, perimeter=8)), ('V', Region(id_=Coordinate(x=0, y=2), area=13, perimeter=20))]

        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'ASSASSA',
        ...     'ASSASSA',
        ...     'AAAAAAA',
        ... ]).regions.items() for region in regions)
        [('A', Region(id_=Coordinate(x=0, y=0), area=13, perimeter=28)), ('S', Region(id_=Coordinate(x=1, y=0), area=4, perimeter=8)), ('S', Region(id_=Coordinate(x=4, y=0), area=4, perimeter=8))]
        """
        width = -1
        rows: list[tuple[str, ...]] = []
        regions: dict[str, list[tuple[Coordinate, int, set[Edge]]]] = {}
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row: list[str] = []
            for (x, plant) in enumerate(line):
                row.append(plant)
                id_ = Coordinate(x, y)
                area = 1
                edges = {
                    # Top edge.
                    Edge(Coordinate(x, y), Coordinate(x + 1, y)),
                    # Right edge.
                    Edge(Coordinate(x + 1, y), Coordinate(x + 1, y + 1)),
                    # Bottom edge.
                    Edge(Coordinate(x, y + 1), Coordinate(x + 1, y + 1)),
                    # Left edge.
                    Edge(Coordinate(x, y), Coordinate(x, y + 1)),
                }
                if plant not in regions:
                    regions[plant] = [(id_, area, edges)]
                    continue
                # Merge with other plant regions that share edges.
                for i in range(len(regions[plant]) - 1, -1, -1):
                    (other_id, other_area, other_edges) = regions[plant][i]
                    shared_edges = edges & other_edges
                    if not shared_edges:
                        continue
                    del regions[plant][i]
                    if other_id < id_:
                        id_ = other_id
                    area += other_area
                    edges = edges ^ other_edges
                regions[plant].append((id_, area, edges))
            rows.append(tuple(row))
        height = y + 1
        return Map(width, height, tuple(rows), {
            plant: {Region(id_, area, len(edges)) for (id_, area, edges) in plant_regions}
            for (plant, plant_regions) in regions.items()
        })


########################################################################################################################
# Part 1
########################################################################################################################

def sum_price_for_fencing_all_regions(lines: Iterable[str]) -> int:
    """
    >>> sum_price_for_fencing_all_regions([
    ...     'AAAA',
    ...     'BBCD',
    ...     'BBCC',
    ...     'EEEC',
    ... ])
    140
    >>> sum_price_for_fencing_all_regions([
    ...     'OOOOO',
    ...     'OXOXO',
    ...     'OOOOO',
    ...     'OXOXO',
    ...     'OOOOO',
    ... ])
    772
    >>> sum_price_for_fencing_all_regions([
    ...     'RRRRIICCFF',
    ...     'RRRRIICCCF',
    ...     'VVRRRCCFFF',
    ...     'VVRCCCJFFF',
    ...     'VVVVCJJCFE',
    ...     'VVIVCCJJEE',
    ...     'VVIIICJJEE',
    ...     'MIIIIIJJEE',
    ...     'MIIISIJEEE',
    ...     'MMMISSJEEE',
    ... ])
    1930
    """
    map_ = Map.from_lines(lines)
    return sum(
        region.area * region.perimeter
        for regions in map_.regions.values()
        for region in regions
    )


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
        print(sum_price_for_fencing_all_regions(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
