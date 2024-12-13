#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
import re
from typing import NamedTuple, Optional


########################################################################################################################
# Arcade claw machines
########################################################################################################################

CONFIG_LINE_ONE_PATTERN = re.compile(r'^Button A: X\+([1-9]\d*), Y\+([1-9]\d*)$')
CONFIG_LINE_TWO_PATTERN = re.compile(r'^Button B: X\+([1-9]\d*), Y\+([1-9]\d*)$')
CONFIG_LINE_THREE_PATTERN = re.compile(r'^Prize: X=([1-9]\d*), Y=([1-9]\d*)$')
A_BUTTON_TOKENS = 3
B_BUTTON_TOKENS = 1
PRIZE_OFFSET = 10000000000000


class Solution(NamedTuple):
    a: int
    b: int
    tokens: int


class ClawMachine(NamedTuple):
    ax: int
    ay: int
    bx: int
    by: int
    px: int
    py: int

    @classmethod
    def from_lines(cls, lines: tuple[str, str, str]) -> 'ClawMachine':
        assert (match := CONFIG_LINE_ONE_PATTERN.fullmatch(lines[0])) is not None
        (ax, ay) = map(int, match.groups())
        assert (match := CONFIG_LINE_TWO_PATTERN.fullmatch(lines[1])) is not None
        (bx, by) = map(int, match.groups())
        assert (match := CONFIG_LINE_THREE_PATTERN.fullmatch(lines[2])) is not None
        (px, py) = map(int, match.groups())
        return ClawMachine(ax, ay, bx, by, px, py)

    def correct_prize_coordinates(self) -> 'ClawMachine':
        return ClawMachine(self.ax, self.ay, self.bx, self.by, self.px + PRIZE_OFFSET, self.py + PRIZE_OFFSET)

    def solve_cheapest_win(self) -> Optional[Solution]:
        """
        >>> ClawMachine.from_lines([
        ...     'Button A: X+94, Y+34',
        ...     'Button B: X+22, Y+67',
        ...     'Prize: X=8400, Y=5400',
        ... ]).solve_cheapest_win()
        Solution(a=80, b=40, tokens=280)
        >>> ClawMachine.from_lines([
        ...     'Button A: X+26, Y+66',
        ...     'Button B: X+67, Y+21',
        ...     'Prize: X=12748, Y=12176',
        ... ]).solve_cheapest_win() is None
        True
        >>> ClawMachine.from_lines([
        ...     'Button A: X+17, Y+86',
        ...     'Button B: X+84, Y+37',
        ...     'Prize: X=7870, Y=6450',
        ... ]).solve_cheapest_win()
        Solution(a=38, b=86, tokens=200)
        >>> ClawMachine.from_lines([
        ...     'Button A: X+69, Y+23',
        ...     'Button B: X+27, Y+71',
        ...     'Prize: X=18641, Y=10279',
        ... ]).solve_cheapest_win() is None
        True

        >>> ClawMachine.from_lines([
        ...     'Button A: X+94, Y+34',
        ...     'Button B: X+22, Y+67',
        ...     'Prize: X=10000000008400, Y=10000000005400',
        ... ]).solve_cheapest_win() is None
        True
        >>> ClawMachine.from_lines([
        ...     'Button A: X+26, Y+66',
        ...     'Button B: X+67, Y+21',
        ...     'Prize: X=10000000012748, Y=10000000012176',
        ... ]).solve_cheapest_win() is not None
        True
        >>> ClawMachine.from_lines([
        ...     'Button A: X+17, Y+86',
        ...     'Button B: X+84, Y+37',
        ...     'Prize: X=10000000007870, Y=10000000006450',
        ... ]).solve_cheapest_win() is None
        True
        >>> ClawMachine.from_lines([
        ...     'Button A: X+69, Y+23',
        ...     'Button B: X+27, Y+71',
        ...     'Prize: X=10000000018641, Y=10000000010279',
        ... ]).solve_cheapest_win() is not None
        True
        """
        # Solve simultaneous equations with Cramer's rule. Assume minimising `3a + b` is a red herring.
        det_coefficient_matrix = (self.ax * self.by) - (self.bx * self.ay)
        if det_coefficient_matrix == 0:
            return None
        det_a = (self.px * self.by) - (self.bx * self.py)
        (a, remainder) = divmod(det_a, det_coefficient_matrix)
        if remainder != 0:
            return None
        det_b = (self.ax * self.py) - (self.px * self.ay)
        (b, remainder) = divmod(det_b, det_coefficient_matrix)
        if remainder != 0:
            return None
        return Solution(a, b, (A_BUTTON_TOKENS * a) + (B_BUTTON_TOKENS * b))


class Arcade(NamedTuple):
    claw_machines: tuple[ClawMachine, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Arcade':
        lines_iter = iter(lines)
        claw_machines: list[ClawMachine] = []
        while True:
            claw_machines.append(ClawMachine.from_lines((next(lines_iter), next(lines_iter), next(lines_iter))))
            try:
                assert next(lines_iter) == ''
            except StopIteration:
                break
        return Arcade(tuple(claw_machines))

    def correct_prize_coordinates(self) -> 'Arcade':
        return Arcade(tuple(claw_machine.correct_prize_coordinates() for claw_machine in self.claw_machines))


########################################################################################################################
# Part 1
########################################################################################################################

def sum_tokens_for_cheapest_wins(lines: Iterable[str]) -> int:
    """
    >>> sum_tokens_for_cheapest_wins([
    ...     'Button A: X+94, Y+34',
    ...     'Button B: X+22, Y+67',
    ...     'Prize: X=8400, Y=5400',
    ...     '',
    ...     'Button A: X+26, Y+66',
    ...     'Button B: X+67, Y+21',
    ...     'Prize: X=12748, Y=12176',
    ...     '',
    ...     'Button A: X+17, Y+86',
    ...     'Button B: X+84, Y+37',
    ...     'Prize: X=7870, Y=6450',
    ...     '',
    ...     'Button A: X+69, Y+23',
    ...     'Button B: X+27, Y+71',
    ...     'Prize: X=18641, Y=10279',
    ... ])
    480
    """
    arcade = Arcade.from_lines(lines)
    return sum(
        solution.tokens
        for claw_machine in arcade.claw_machines
        if (solution := claw_machine.solve_cheapest_win()) is not None
    )


########################################################################################################################
# Part 2
########################################################################################################################

def sum_tokens_for_cheapest_wins_with_corrected_prize_coordinates(lines: Iterable[str]) -> int:
    arcade = Arcade.from_lines(lines).correct_prize_coordinates()
    return sum(
        solution.tokens
        for claw_machine in arcade.claw_machines
        if (solution := claw_machine.solve_cheapest_win()) is not None
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
        print(sum_tokens_for_cheapest_wins(lines))
    elif args.part == 2:
        print(sum_tokens_for_cheapest_wins_with_corrected_prize_coordinates(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
