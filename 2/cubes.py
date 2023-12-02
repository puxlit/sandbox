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
COLOURS = {'red', 'green', 'blue'}


class CubeCollection(NamedTuple):
    red: int
    green: int
    blue: int

    @classmethod
    def from_colour_counts(cls, colour_counts: str) -> 'CubeCollection':
        """
        >>> CubeCollection.from_colour_counts('1 red')
        CubeCollection(red=1, green=0, blue=0)
        >>> CubeCollection.from_colour_counts('001 red')
        CubeCollection(red=1, green=0, blue=0)
        >>> CubeCollection.from_colour_counts('0 green')
        CubeCollection(red=0, green=0, blue=0)
        >>> CubeCollection.from_colour_counts('-1 blue')
        Traceback (most recent call last):
            ...
        ValueError: '-1' is not a valid count for the colour 'blue'
        >>> CubeCollection.from_colour_counts('1 purple')
        Traceback (most recent call last):
            ...
        ValueError: 'purple' is not a valid colour
        >>> CubeCollection.from_colour_counts('1 red, 2 green, 3 blue')
        CubeCollection(red=1, green=2, blue=3)
        >>> CubeCollection.from_colour_counts('2 green, 1 red, 3 blue')
        CubeCollection(red=1, green=2, blue=3)
        >>> CubeCollection.from_colour_counts('2 green, 1 red, 3 blue, 4 red')
        Traceback (most recent call last):
            ...
        ValueError: count for colour 'red' was specified multiple times (1 and 4)
        """
        counts: dict[str, int] = {}
        for colour_count in colour_counts.split(COLOUR_COUNTS_DELIMITER):
            (count, colour) = colour_count.split(COLOUR_COUNT_DELIMITER)
            if not count.isdigit():
                raise ValueError(f'{count!r} is not a valid count for the colour {colour!r}')
            if colour not in COLOURS:
                raise ValueError(f'{colour!r} is not a valid colour')
            if colour in counts:
                raise ValueError(f'count for colour {colour!r} was specified multiple times '
                                 f'({counts[colour]} and {int(count)})')
            counts[colour] = int(count)
        return CubeCollection(**{colour: counts.get(colour, 0) for colour in COLOURS})


GAME_ID_COLOUR_COUNTS_SET_DELIMITER = ': '
GAME_ID_PREFIX = 'Game '
COLOUR_COUNTS_SET_DELIMITER = '; '


class Game(NamedTuple):
    id_: int
    witnessed_cube_collections: tuple[CubeCollection, ...]
    minimal_cube_collection: CubeCollection

    @classmethod
    def from_line(cls, line: str) -> 'Game':
        """
        >>> Game.from_line('Game 1: 1 red, 2 green; 3 blue, 3 red; 3 green')
        Game(id_=1, witnessed_cube_collections=(CubeCollection(red=1, green=2, blue=0), CubeCollection(red=3, green=0, blue=3), CubeCollection(red=0, green=3, blue=0)), minimal_cube_collection=CubeCollection(red=3, green=3, blue=3))
        >>> Game.from_line('Juego 1: 1 red, 2 green')
        Traceback (most recent call last):
            ...
        ValueError: Game ID fragment 'Juego 1' does not start with expected prefix 'Game '
        >>> Game.from_line('Game -1: 1 red, 2 green')
        Traceback (most recent call last):
            ...
        ValueError: '-1' is not a valid game ID
        """
        (game_fragment, colour_counts_set) = line.split(GAME_ID_COLOUR_COUNTS_SET_DELIMITER)

        if not game_fragment.startswith(GAME_ID_PREFIX):
            raise ValueError(f'Game ID fragment {game_fragment!r} does not start with '
                             f'expected prefix {GAME_ID_PREFIX!r}')
        game_fragment = game_fragment.removeprefix(GAME_ID_PREFIX)
        if not game_fragment.isdigit():
            raise ValueError(f'{game_fragment!r} is not a valid game ID')
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
        """
        >>> list(Game.from_lines([
        ...     'Game 1: 1 red',
        ...     'Game 2: 1 green',
        ...     'Game 1: 1 blue',
        ... ]))
        Traceback (most recent call last):
            ...
        ValueError: game ID 1 was specified multiple times (Game(id_=1, witnessed_cube_collections=(CubeCollection(red=1, green=0, blue=0),), minimal_cube_collection=CubeCollection(red=1, green=0, blue=0)) and Game(id_=1, witnessed_cube_collections=(CubeCollection(red=0, green=0, blue=1),), minimal_cube_collection=CubeCollection(red=0, green=0, blue=1)))
        """
        witnessed_game_ids: dict[int, Game] = {}
        for line in lines:
            game = Game.from_line(line)
            if game.id_ in witnessed_game_ids:
                raise ValueError(f'game ID {game.id_} was specified multiple times '
                                 f'({witnessed_game_ids[game.id_]} and {game})')
            witnessed_game_ids[game.id_] = game
            yield game


def is_relevant_game(game: Game) -> bool:
    """
    >>> is_relevant_game(Game.from_line('Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green'))
    True
    >>> is_relevant_game(Game.from_line('Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue'))
    True
    >>> is_relevant_game(Game.from_line('Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red'))
    False
    >>> is_relevant_game(Game.from_line('Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red'))
    False
    >>> is_relevant_game(Game.from_line('Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green'))
    True
    """
    (red, green, blue) = game.minimal_cube_collection
    return (red <= 12) and (green <= 13) and (blue <= 14)


def sum_relevant_game_ids(lines: Iterable[str]) -> int:
    """
    >>> sum_relevant_game_ids([
    ...     'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green',
    ...     'Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue',
    ...     'Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red',
    ...     'Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red',
    ...     'Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green',
    ... ])
    8
    """
    relevant_games = filter(is_relevant_game, Game.from_lines(lines))
    return sum(map(lambda game: game.id_, relevant_games))


########################################################################################################################
# Part 2
########################################################################################################################

def calculate_game_power(game: Game) -> int:
    """
    >>> calculate_game_power(Game.from_line('Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green'))
    48
    >>> calculate_game_power(Game.from_line('Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue'))
    12
    >>> calculate_game_power(Game.from_line('Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red'))
    1560
    >>> calculate_game_power(Game.from_line('Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red'))
    630
    >>> calculate_game_power(Game.from_line('Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green'))
    36
    """
    (red, green, blue) = game.minimal_cube_collection
    return red * green * blue


def sum_game_powers(lines: Iterable[str]) -> int:
    """
    >>> sum_game_powers([
    ...     'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green',
    ...     'Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue',
    ...     'Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red',
    ...     'Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red',
    ...     'Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green',
    ... ])
    2286
    """
    games = Game.from_lines(lines)
    return sum(map(calculate_game_power, games))


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

    if (args.part == 1):
        print(sum_relevant_game_ids(lines))
    elif (args.part == 2):
        print(sum_game_powers(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
