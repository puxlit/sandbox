#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

COLOUR_COUNTS_DELIMITER = ', '
COLOUR_COUNT_DELIMITER = ' '


class CubeCollection(NamedTuple):
    red: int
    green: int
    blue: int

    @classmethod
    def from_colour_counts(cls, colour_counts: str) -> 'CubeCollection':
        (red, green, blue) = (None, None, None)
        for colour_count in colour_counts.split(COLOUR_COUNTS_DELIMITER):
            (count, colour) = colour_count.split(COLOUR_COUNT_DELIMITER)
            assert count.isdigit()
            if colour == 'red':
                # Ensure the count for this colour has not been previously set.
                assert red is None
                red = int(count)
            elif colour == 'green':
                assert green is None
                green = int(count)
            elif colour == 'blue':
                assert blue is None
                blue = int(count)
            else:
                raise ValueError()
        return CubeCollection(red or 0, green or 0, blue or 0)


GAME_ID_COLOUR_COUNTS_SET_DELIMITER = ': '
GAME_ID_PREFIX = 'Game '
COLOUR_COUNTS_SET_DELIMITER = '; '


class Game(NamedTuple):
    id_: int
    witnessed_cube_collections: tuple[CubeCollection, ...]
    minimal_cube_collection: CubeCollection

    @classmethod
    def from_line(cls, line: str) -> 'Game':
        (game_fragment, colour_counts_set) = line.rstrip('\n').split(GAME_ID_COLOUR_COUNTS_SET_DELIMITER)

        assert game_fragment.startswith(GAME_ID_PREFIX)
        game_fragment = game_fragment.removeprefix(GAME_ID_PREFIX)
        assert game_fragment.isdigit()
        id_ = int(game_fragment)

        witnessed_cube_collections = []
        (minimal_red, minimal_green, minimal_blue) = (0, 0, 0)
        for colour_counts in colour_counts_set.split(COLOUR_COUNTS_SET_DELIMITER):
            witnessed_cube_collection = CubeCollection.from_colour_counts(colour_counts)
            witnessed_cube_collections.append(witnessed_cube_collection)
            minimal_red = max(witnessed_cube_collection.red, minimal_red)
            minimal_green = max(witnessed_cube_collection.green, minimal_green)
            minimal_blue = max(witnessed_cube_collection.blue, minimal_blue)
        minimal_cube_collection = CubeCollection(minimal_red, minimal_green, minimal_blue)

        return Game(id_, tuple(witnessed_cube_collections), minimal_cube_collection)

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Iterator['Game']:
        witnessed_game_ids = set()
        for line in lines:
            game = Game.from_line(line)
            assert game.id_ not in witnessed_game_ids
            witnessed_game_ids.add(game.id_)
            yield game


def is_relevant_game(game: Game) -> bool:
    (red, green, blue) = game.minimal_cube_collection
    return (red <= 12) and (green <= 13) and (blue <= 14)


def sum_relevant_game_ids(lines: Iterable[str]) -> int:
    r"""
    >>> sum_relevant_game_ids([
    ...     'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green\n',
    ...     'Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue\n',
    ...     'Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red\n',
    ...     'Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red\n',
    ...     'Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green\n',
    ... ])
    8
    """
    relevant_games = filter(is_relevant_game, Game.from_lines(lines))
    return sum(map(lambda game: game.id_, relevant_games))


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1,))
    parser.add_argument('input', type=argparse.FileType('rt'))
    args = parser.parse_args()

    if (args.part == 1):
        print(sum_relevant_game_ids(args.input))
    else:
        raise ValueError()


if __name__ == '__main__':
    main()
