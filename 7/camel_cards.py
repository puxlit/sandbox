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
# Cards
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
    JOKER = 'j'
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
    Card.JOKER: -1,
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


HAND_LINE_PATTERN = re.compile(r'^([2-9AJKQTj]{5}) ([1-9][0-9]*)$')


@dataclass(order=True, frozen=True)
class Hand:
    type_: HandType
    cards: tuple[Card, Card, Card, Card, Card]
    # The bid amount isn't supposed to factor into hand strength. Note this _does_ make equality comparisons weird.
    bid_amount: int = field(compare=False)

    @classmethod
    def from_line(cls, line: str) -> 'Hand':
        """
        >>> assert Hand.from_line('AAAAA 1').type_ == HandType.FIVE_OF_A_KIND
        >>> assert Hand.from_line('AA8AA 1').type_ == HandType.FOUR_OF_A_KIND
        >>> assert Hand.from_line('23332 1').type_ == HandType.FULL_HOUSE
        >>> assert Hand.from_line('TTT98 1').type_ == HandType.THREE_OF_A_KIND
        >>> assert Hand.from_line('23432 1').type_ == HandType.TWO_PAIR
        >>> assert Hand.from_line('A23A4 1').type_ == HandType.ONE_PAIR
        >>> assert Hand.from_line('23456 1').type_ == HandType.HIGH_CARD

        >>> (a, b) = (Hand.from_line('33332 1'), Hand.from_line('2AAAA 1'))
        >>> assert a.type_ == b.type_ == HandType.FOUR_OF_A_KIND
        >>> assert a > b
        >>> (a, b) = (Hand.from_line('77888 1'), Hand.from_line('77788 1'))
        >>> assert a.type_ == b.type_ == HandType.FULL_HOUSE
        >>> assert a > b

        >>> assert Hand.from_line('32T3K 765').type_ == HandType.ONE_PAIR
        >>> (a, b) = (Hand.from_line('KK677 28'), Hand.from_line('KTJJT 220'))
        >>> assert a.type_ == b.type_ == HandType.TWO_PAIR
        >>> assert a > b
        >>> (a, b) = (Hand.from_line('T55J5 684'), Hand.from_line('QQQJA 483'))
        >>> assert a.type_ == b.type_ == HandType.THREE_OF_A_KIND
        >>> assert a < b

        >>> assert Hand.from_line('QjjQ2 1').type_ == HandType.FOUR_OF_A_KIND
        >>> (a, b) = (Hand.from_line('jKKK2 1'), Hand.from_line('QQQQ2 1'))
        >>> assert a.type_ == b.type_ == HandType.FOUR_OF_A_KIND
        >>> assert a < b

        >>> (a, b, c) = (Hand.from_line('T55j5 684'), Hand.from_line('KTjjT 220'), Hand.from_line('QQQjA 483'))
        >>> assert a.type_ == b.type_ == c.type_ == HandType.FOUR_OF_A_KIND
        >>> assert a < c < b
        """
        match = HAND_LINE_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Hand line {line!r} does not match '
                             f'expected pattern /{HAND_LINE_PATTERN.pattern}/')
        (raw_cards, raw_bid_amount) = match.groups()
        assert len(raw_cards) == 5
        cards = cast(tuple[Card, Card, Card, Card, Card], tuple(Card(card) for card in raw_cards))
        bid_amount = int(raw_bid_amount)

        counter = Counter(cards)
        joker_count = counter.get(Card.JOKER, 0)
        del counter[Card.JOKER]
        cards_by_frequency = counter.most_common()
        mode_count = cards_by_frequency[0][1] if cards_by_frequency else 0
        # Jokers should always be allocated to whatever's the most frequent card.
        mode_count += joker_count
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


########################################################################################################################
# Part 1
########################################################################################################################

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
# Part 2
########################################################################################################################

def calculate_total_winnings_with_joker_rule(lines: Iterable[str]) -> int:
    """
    >>> calculate_total_winnings_with_joker_rule([
    ...     '32T3K 765',
    ...     'T55J5 684',
    ...     'KK677 28',
    ...     'KTJJT 220',
    ...     'QQQJA 483',
    ... ])
    5905
    """
    hands = list(Hand.from_line(line.replace(Card.JACK.value, Card.JOKER.value)) for line in lines)
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
    elif args.part == 2:
        print(calculate_total_winnings_with_joker_rule(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
