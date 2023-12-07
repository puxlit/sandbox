#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering
import re
from typing import Any, cast


########################################################################################################################
# Part 1
########################################################################################################################

@total_ordering
class Card(Enum):
    ACE = 'A'
    KING = 'K'
    QUEEN = 'Q'
    JACK = 'J'
    TEN = 'T'
    NINE = '9'
    EIGHT = '8'
    SEVEN = '7'
    SIX = '6'
    FIVE = '5'
    FOUR = '4'
    THREE = '3'
    TWO = '2'
    _ignore_ = ['_STRENGTH']
    _STRENGTH: dict['Card', int]

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Card):
            return Card._STRENGTH[self] < Card._STRENGTH[other]
        raise TypeError(f'Cannot evaluate `{self!r} < {other!r}`')


Card._STRENGTH = {
    Card.ACE: 12,
    Card.KING: 11,
    Card.QUEEN: 10,
    Card.JACK: 9,
    Card.TEN: 8,
    Card.NINE: 7,
    Card.EIGHT: 6,
    Card.SEVEN: 5,
    Card.SIX: 4,
    Card.FIVE: 3,
    Card.FOUR: 2,
    Card.THREE: 1,
    Card.TWO: 0,
}


@total_ordering
class HandType(Enum):
    FIVE_OF_A_KIND = 6
    FOUR_OF_A_KIND = 5
    FULL_HOUSE = 4
    THREE_OF_A_KIND = 3
    TWO_PAIR = 2
    ONE_PAIR = 1
    HIGH_CARD = 0

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, HandType):
            return self.value < other.value
        raise TypeError(f'Cannot evaluate `{self!r} < {other!r}`')


HAND_LINE_PATTERN = re.compile(r'^([2-9AJKQT]{5}) ([1-9][0-9]*)$')


@dataclass(order=True, frozen=True)
class Hand:
    type_: HandType
    cards: tuple[Card, Card, Card, Card, Card]
    # The bid amount isn't supposed to factor into hand strength. Note this _does_ make equality comparisons weird.
    bid_amount: int = field(compare=False)

    @classmethod
    def from_line(cls, line: str) -> 'Hand':
        """
        >>> Hand.from_line('AAAAA 1').type_.name
        'FIVE_OF_A_KIND'
        >>> Hand.from_line('AA8AA 1').type_.name
        'FOUR_OF_A_KIND'
        >>> Hand.from_line('23332 1').type_.name
        'FULL_HOUSE'
        >>> Hand.from_line('TTT98 1').type_.name
        'THREE_OF_A_KIND'
        >>> Hand.from_line('23432 1').type_.name
        'TWO_PAIR'
        >>> Hand.from_line('A23A4 1').type_.name
        'ONE_PAIR'
        >>> Hand.from_line('23456 1').type_.name
        'HIGH_CARD'
        """
        match = HAND_LINE_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Hand line {line!r} does not match '
                             f'expected pattern /{HAND_LINE_PATTERN.pattern}/')
        (raw_cards, raw_bid_amount) = match.groups()
        assert len(raw_cards) == 5
        cards = cast(tuple[Card, Card, Card, Card, Card], tuple(Card(card) for card in raw_cards))
        bid_amount = int(raw_bid_amount)

        cards_by_frequency = Counter(cards).most_common()
        assert len(cards_by_frequency) >= 1
        mode_count = cards_by_frequency[0][1]
        if mode_count == 5:
            type_ = HandType.FIVE_OF_A_KIND
        elif mode_count == 4:
            type_ = HandType.FOUR_OF_A_KIND
        else:
            assert len(cards_by_frequency) >= 2
            if mode_count == 3:
                if cards_by_frequency[1][1] == 2:
                    type_ = HandType.FULL_HOUSE
                else:
                    type_ = HandType.THREE_OF_A_KIND
            elif mode_count == 2:
                if cards_by_frequency[1][1] == 2:
                    type_ = HandType.TWO_PAIR
                else:
                    type_ = HandType.ONE_PAIR
            else:
                type_ = HandType.HIGH_CARD

        return Hand(type_, cards, bid_amount)


def calculate_total_winnings(lines: Iterable[str]) -> int:
    """
    >>> calculate_total_winnings([
    ...     '32T3K 765',
    ...     'T55J5 684',
    ...     'KK677 28',
    ...     'KTJJT 220',
    ...     'QQQJA 483',
    ... ])
    6440
    """
    hands = list(Hand.from_line(line) for line in lines)
    ranked_hands = sorted(hands)  # We'll assume there are no ties.
    return sum(hand.bid_amount * (i + 1) for (i, hand) in enumerate(ranked_hands))


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
        print(calculate_total_winnings(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
