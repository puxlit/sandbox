#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
from typing import NamedTuple

from typing_extensions import assert_never


########################################################################################################################
# Map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'


class Direction(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Edge(NamedTuple):
    start: Coordinate
    direction: Direction

    @property
    def end(self) -> Coordinate:
        if self.direction == Direction.HORIZONTAL:
            return Coordinate(self.start.x + 1, self.start.y)
        elif self.direction == Direction.VERTICAL:
            return Coordinate(self.start.x, self.start.y + 1)
        assert_never(self.direction)


class Region(NamedTuple):
    id_: Coordinate
    area: int
    perimeter: int
    sides: int


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
        [('A', Region(id_=Coordinate(x=0, y=0), area=4, perimeter=10, sides=4)), ('B', Region(id_=Coordinate(x=0, y=1), area=4, perimeter=8, sides=4)), ('C', Region(id_=Coordinate(x=2, y=1), area=4, perimeter=10, sides=8)), ('D', Region(id_=Coordinate(x=3, y=1), area=1, perimeter=4, sides=4)), ('E', Region(id_=Coordinate(x=0, y=3), area=3, perimeter=8, sides=4))]
        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'OOOOO',
        ...     'OXOXO',
        ...     'OOOOO',
        ...     'OXOXO',
        ...     'OOOOO',
        ... ]).regions.items() for region in regions)
        [('O', Region(id_=Coordinate(x=0, y=0), area=21, perimeter=36, sides=20)), ('X', Region(id_=Coordinate(x=1, y=1), area=1, perimeter=4, sides=4)), ('X', Region(id_=Coordinate(x=1, y=3), area=1, perimeter=4, sides=4)), ('X', Region(id_=Coordinate(x=3, y=1), area=1, perimeter=4, sides=4)), ('X', Region(id_=Coordinate(x=3, y=3), area=1, perimeter=4, sides=4))]
        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'EEEEE',
        ...     'EXXXX',
        ...     'EEEEE',
        ...     'EXXXX',
        ...     'EEEEE',
        ... ]).regions.items() for region in regions)
        [('E', Region(id_=Coordinate(x=0, y=0), area=17, perimeter=36, sides=12)), ('X', Region(id_=Coordinate(x=1, y=1), area=4, perimeter=10, sides=4)), ('X', Region(id_=Coordinate(x=1, y=3), area=4, perimeter=10, sides=4))]
        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'AAAAAA',
        ...     'AAABBA',
        ...     'AAABBA',
        ...     'ABBAAA',
        ...     'ABBAAA',
        ...     'AAAAAA',
        ... ]).regions.items() for region in regions)
        [('A', Region(id_=Coordinate(x=0, y=0), area=28, perimeter=40, sides=12)), ('B', Region(id_=Coordinate(x=1, y=3), area=4, perimeter=8, sides=4)), ('B', Region(id_=Coordinate(x=3, y=1), area=4, perimeter=8, sides=4))]
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
        [('C', Region(id_=Coordinate(x=3, y=3), area=14, perimeter=28, sides=22)), ('C', Region(id_=Coordinate(x=7, y=4), area=1, perimeter=4, sides=4)), ('E', Region(id_=Coordinate(x=7, y=8), area=13, perimeter=18, sides=8)), ('F', Region(id_=Coordinate(x=7, y=2), area=10, perimeter=18, sides=12)), ('I', Region(id_=Coordinate(x=1, y=7), area=14, perimeter=22, sides=16)), ('I', Region(id_=Coordinate(x=4, y=0), area=4, perimeter=8, sides=4)), ('J', Region(id_=Coordinate(x=5, y=4), area=11, perimeter=20, sides=12)), ('M', Region(id_=Coordinate(x=0, y=7), area=5, perimeter=12, sides=6)), ('R', Region(id_=Coordinate(x=0, y=0), area=12, perimeter=18, sides=10)), ('S', Region(id_=Coordinate(x=4, y=8), area=3, perimeter=8, sides=6)), ('V', Region(id_=Coordinate(x=0, y=2), area=13, perimeter=20, sides=10))]

        >>> sorted((plant, region) for (plant, regions) in Map.from_lines([
        ...     'ASSASSA',
        ...     'ASSASSA',
        ...     'AAAAAAA',
        ... ]).regions.items() for region in regions)
        [('A', Region(id_=Coordinate(x=0, y=0), area=13, perimeter=28, sides=12)), ('S', Region(id_=Coordinate(x=1, y=0), area=4, perimeter=8, sides=4)), ('S', Region(id_=Coordinate(x=4, y=0), area=4, perimeter=8, sides=4))]
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
                    Edge(Coordinate(x, y), Direction.HORIZONTAL),
                    # Right edge.
                    Edge(Coordinate(x + 1, y), Direction.VERTICAL),
                    # Bottom edge.
                    Edge(Coordinate(x, y + 1), Direction.HORIZONTAL),
                    # Left edge.
                    Edge(Coordinate(x, y), Direction.VERTICAL),
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

        simplified_regions: dict[str, set[Region]] = {}
        for (plant, plant_regions) in regions.items():
            simplified_plant_regions: set[Region] = set()
            for (id_, area, edges) in plant_regions:
                # Coalesce edges into sides. This is equivalent to finding vertices, which we can do by finding edge
                # coordinates belonging to perpendicular edges.
                edge_coordinates: dict[Coordinate, tuple[int, int]] = {}
                for edge in edges:
                    if edge.direction == Direction.HORIZONTAL:
                        (horizontal_count, vertical_count) = edge_coordinates.get(edge.start, (0, 0))
                        edge_coordinates[edge.start] = (horizontal_count + 1, vertical_count)
                        (horizontal_count, vertical_count) = edge_coordinates.get(edge.end, (0, 0))
                        edge_coordinates[edge.end] = (horizontal_count + 1, vertical_count)
                    elif edge.direction == Direction.VERTICAL:
                        (horizontal_count, vertical_count) = edge_coordinates.get(edge.start, (0, 0))
                        edge_coordinates[edge.start] = (horizontal_count, vertical_count + 1)
                        (horizontal_count, vertical_count) = edge_coordinates.get(edge.end, (0, 0))
                        edge_coordinates[edge.end] = (horizontal_count, vertical_count + 1)
                    else:
                        assert_never(edge.direction)
                sides = sum(
                    horizontal_count
                    for (horizontal_count, vertical_count) in edge_coordinates.values()
                    if (horizontal_count == vertical_count)
                )
                simplified_plant_regions.add(Region(id_, area, len(edges), sides))
            simplified_regions[plant] = simplified_plant_regions

        return Map(width, height, tuple(rows), simplified_regions)


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
# Part 2
########################################################################################################################

def sum_discounted_price_for_fencing_all_regions(lines: Iterable[str]) -> int:
    """
    >>> sum_discounted_price_for_fencing_all_regions([
    ...     'AAAA',
    ...     'BBCD',
    ...     'BBCC',
    ...     'EEEC',
    ... ])
    80
    >>> sum_discounted_price_for_fencing_all_regions([
    ...     'OOOOO',
    ...     'OXOXO',
    ...     'OOOOO',
    ...     'OXOXO',
    ...     'OOOOO',
    ... ])
    436
    >>> sum_discounted_price_for_fencing_all_regions([
    ...     'EEEEE',
    ...     'EXXXX',
    ...     'EEEEE',
    ...     'EXXXX',
    ...     'EEEEE',
    ... ])
    236
    >>> sum_discounted_price_for_fencing_all_regions([
    ...     'AAAAAA',
    ...     'AAABBA',
    ...     'AAABBA',
    ...     'ABBAAA',
    ...     'ABBAAA',
    ...     'AAAAAA',
    ... ])
    368
    >>> sum_discounted_price_for_fencing_all_regions([
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
    1206
    """
    map_ = Map.from_lines(lines)
    return sum(
        region.area * region.sides
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
    elif args.part == 2:
        print(sum_discounted_price_for_fencing_all_regions(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
