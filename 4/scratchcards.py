#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

CARD_HEADER_DELIMITER = ': '
CARD_HEADER_PREFIX = 'Card '
NUMBER_LIST_DELIMITER = ' | '
NUMBER_DELIMITER = ' '


class Card(NamedTuple):
    id_: int
    # We're preserving order in case it's important for part 2.
    winning_numbers: tuple[int, ...]
    numbers: tuple[int, ...]
    # These appear in the same order as the winning numbers, because that's how they're listed in almost all of the
    # examples.
    matching_numbers: tuple[int, ...]
    points: int

    @classmethod
    def from_line(cls, line: str) -> 'Card':
        """
        >>> Card.from_line('Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53')
        Card(id_=1, winning_numbers=(41, 48, 83, 86, 17), numbers=(83, 86, 6, 31, 17, 9, 48, 53), matching_numbers=(48, 83, 86, 17), points=8)
        >>> Card.from_line('Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19')
        Card(id_=2, winning_numbers=(13, 32, 20, 16, 61), numbers=(61, 30, 68, 82, 17, 32, 24, 19), matching_numbers=(32, 61), points=2)
        >>> Card.from_line('Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1')
        Card(id_=3, winning_numbers=(1, 21, 53, 59, 44), numbers=(69, 82, 63, 72, 16, 21, 14, 1), matching_numbers=(1, 21), points=2)
        >>> Card.from_line('Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83')
        Card(id_=4, winning_numbers=(41, 92, 73, 84, 69), numbers=(59, 84, 76, 51, 58, 5, 54, 83), matching_numbers=(84,), points=1)
        >>> Card.from_line('Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36')
        Card(id_=5, winning_numbers=(87, 83, 26, 28, 32), numbers=(88, 30, 70, 12, 93, 22, 82, 36), matching_numbers=(), points=0)
        >>> Card.from_line('Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11')
        Card(id_=6, winning_numbers=(31, 18, 13, 56, 72), numbers=(74, 77, 10, 23, 35, 67, 36, 11), matching_numbers=(), points=0)

        >>> Card.from_line('Tarjeta 1: 1 | 1')
        Traceback (most recent call last):
            ...
        ValueError: Card header 'Tarjeta 1' does not start with expected prefix 'Card '
        >>> Card.from_line('Card -1: 1 | 1')
        Traceback (most recent call last):
            ...
        ValueError: '-1' is not a valid card ID
        """
        (header, body) = line.split(CARD_HEADER_DELIMITER)

        if not header.startswith(CARD_HEADER_PREFIX):
            raise ValueError(f'Card header {header!r} does not start with '
                             f'expected prefix {CARD_HEADER_PREFIX!r}')
        header = header.removeprefix(CARD_HEADER_PREFIX).lstrip()
        if not header.isdigit():
            raise ValueError(f'{header!r} is not a valid card ID')
        id_ = int(header)

        (winning_numbers_list, numbers_you_have_list) = body.split(NUMBER_LIST_DELIMITER)
        winning_numbers = tuple(int(number) for number in winning_numbers_list.split(NUMBER_DELIMITER) if number)
        numbers = tuple(int(number) for number in numbers_you_have_list.split(NUMBER_DELIMITER) if number)
        matching_numbers = tuple(number for number in winning_numbers if number in set(numbers))
        points = (2 ** (len(matching_numbers) - 1)) if matching_numbers else 0

        return Card(id_, winning_numbers, numbers, matching_numbers, points)

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Iterator['Card']:
        """
        >>> list(Card.from_lines([
        ...     'Card 1: 1 | 1',
        ...     'Card 2: 2 | 2',
        ...     'Card 1: 3 | 3',
        ... ]))
        Traceback (most recent call last):
            ...
        ValueError: card ID 1 was specified multiple times (Card(id_=1, winning_numbers=(1,), numbers=(1,), matching_numbers=(1,), points=1) and Card(id_=1, winning_numbers=(3,), numbers=(3,), matching_numbers=(3,), points=1))
        """
        witnessed_card_ids: dict[int, Card] = {}
        for line in lines:
            card = Card.from_line(line)
            if card.id_ in witnessed_card_ids:
                raise ValueError(f'card ID {card.id_} was specified multiple times '
                                 f'({witnessed_card_ids[card.id_]} and {card})')
            witnessed_card_ids[card.id_] = card
            yield card


def sum_points(lines: Iterable[str]) -> int:
    """
    >>> sum_points([
    ...     'Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53',
    ...     'Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19',
    ...     'Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1',
    ...     'Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83',
    ...     'Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36',
    ...     'Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11',
    ... ])
    13
    """
    cards = Card.from_lines(lines)
    return sum(map(lambda card: card.points, cards))


########################################################################################################################
# Part 2
########################################################################################################################

def count_total_cards(lines: Iterable[str]) -> int:
    """
    >>> count_total_cards([
    ...     'Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53',
    ...     'Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19',
    ...     'Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1',
    ...     'Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83',
    ...     'Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36',
    ...     'Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11',
    ... ])
    30
    >>> count_total_cards([
    ...     'Card 1: 1 | 1',
    ... ])
    Traceback (most recent call last):
        ...
    ValueError: Ran out of cards to copy when processing Card(id_=1, winning_numbers=(1,), numbers=(1,), matching_numbers=(1,), points=1); needed 1 more card(s)
    """
    cards = list(Card.from_lines(lines))
    total_original_cards = len(cards)
    copied_card_counts = [0] * total_original_cards
    for (i, card) in enumerate(cards):
        num_matching_numbers = len(card.matching_numbers)
        num_missing_cards = (i + num_matching_numbers) - (total_original_cards - 1)
        if num_missing_cards > 0:
            raise ValueError(f'Ran out of cards to copy when processing {card}; '
                             f'needed {num_missing_cards} more card(s)')
        card_count = 1 + copied_card_counts[i]
        for j in range(i + 1, i + 1 + num_matching_numbers):
            copied_card_counts[j] += card_count
    total_copied_cards = sum(copied_card_counts)
    return total_original_cards + total_copied_cards


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
        print(sum_points(lines))
    elif args.part == 2:
        print(count_total_cards(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
