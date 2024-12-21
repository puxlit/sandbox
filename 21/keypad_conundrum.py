#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from functools import cache, partial
from itertools import permutations
from typing import NamedTuple, Optional


########################################################################################################################
# The hardest button to button
########################################################################################################################

# (0, 0) is the empty gap, rows count upwards, columns count rightwards.
NUMPAD_BUTTON_COORDINATES = {
    '7': (3, 0),
    '8': (3, 1),
    '9': (3, 2),
    '4': (2, 0),
    '5': (2, 1),
    '6': (2, 2),
    '1': (1, 0),
    '2': (1, 1),
    '3': (1, 2),
    '0': (0, 1),
    'A': (0, 2),
}
NUMPAD_COORDINATE_BUTTONS = {coordinate: button for (button, coordinate) in NUMPAD_BUTTON_COORDINATES.items()}

# (0, 0) is the empty gap, rows count downwards, columns count rightwards.
DPAD_BUTTON_COORDINATES = {
    '^': (0, 1),
    'A': (0, 2),
    '<': (1, 0),
    'v': (1, 1),
    '>': (1, 2),
}
DPAD_COORDINATE_BUTTONS = {coordinate: button for (button, coordinate) in DPAD_BUTTON_COORDINATES.items()}


class Code(NamedTuple):
    button_presses: str
    number: int

    @classmethod
    def from_line(cls, line: str) -> 'Code':
        assert len(line) == 4
        assert (digits := line[:3]).isdigit()
        assert line[3] == 'A'
        return Code(line, int(digits))


def parse_codes(lines: Iterable[str]) -> Iterator[Code]:
    for line in lines:
        yield Code.from_line(line)


# Some general observations on "complexity" follow.
#
#   - At first blush, to minimise button presses the next layer up, it seems sufficient to consolidate movements along
#     each axis. (For example, `>^^A` translates to `vA<^AA>A`, whereas `^>^A` translates to the longer `<A>vA<^A>A`.)
#   - However, between directional keypad layers, the shortest sequence of button presses may produce a longer sequence
#     of button presses the next layer up compared to a slightly longer sequence of button presses.


@cache
def min_translated_button_presses_for_numpad_button_press(from_button_press: str, to_button_press: str, depth: int) -> int:
    assert depth >= 0
    if to_button_press == from_button_press:
        # At the end of each button press, actors higher up the stack should be poised over the activate button.
        return 1

    (from_button_row, from_button_column) = NUMPAD_BUTTON_COORDINATES[from_button_press]
    (to_button_row, to_button_column) = NUMPAD_BUTTON_COORDINATES[to_button_press]
    horizontal_button_presses = ('>' if (to_button_column > from_button_column) else '<') * abs(to_button_column - from_button_column)
    vertical_button_presses = ('^' if (to_button_row > from_button_row) else 'v') * abs(to_button_row - from_button_row)
    routes = set(''.join(permutation) for permutation in permutations(horizontal_button_presses + vertical_button_presses))
    # Remove permutation that takes us over the empty gap.
    if (from_button_row == to_button_column == 0):
        routes.remove(horizontal_button_presses + vertical_button_presses)
    elif (from_button_column == to_button_row == 0):
        routes.remove(vertical_button_presses + horizontal_button_presses)

    best_num_translated_button_presses: Optional[int] = None
    for route in sorted(routes):
        button_presses = route + 'A'
        num_translated_button_presses = len(button_presses) if (depth == 0) else min_translated_button_presses_for_dpad_button_presses(button_presses, depth - 1)
        if (best_num_translated_button_presses is None) or num_translated_button_presses < best_num_translated_button_presses:
            best_num_translated_button_presses = num_translated_button_presses
    assert best_num_translated_button_presses is not None
    return best_num_translated_button_presses


def min_translated_button_presses_for_numpad_button_presses(button_presses: str, depth: int) -> int:
    """
    >>> min_translated_button_presses_for_numpad_button_presses('029A', 0)
    12
    >>> min_translated_button_presses_for_numpad_button_presses('029A', 1)
    28
    >>> min_translated_button_presses_for_numpad_button_presses('029A', 2)
    68
    >>> min_translated_button_presses_for_numpad_button_presses('980A', 0)
    12
    >>> min_translated_button_presses_for_numpad_button_presses('980A', 1)
    26
    >>> min_translated_button_presses_for_numpad_button_presses('980A', 2)
    60
    >>> min_translated_button_presses_for_numpad_button_presses('179A', 0)
    14
    >>> min_translated_button_presses_for_numpad_button_presses('179A', 1)
    28
    >>> min_translated_button_presses_for_numpad_button_presses('179A', 2)
    68
    >>> min_translated_button_presses_for_numpad_button_presses('456A', 0)
    12
    >>> min_translated_button_presses_for_numpad_button_presses('456A', 1)
    26
    >>> min_translated_button_presses_for_numpad_button_presses('456A', 2)
    64
    >>> min_translated_button_presses_for_numpad_button_presses('379A', 0)
    14
    >>> min_translated_button_presses_for_numpad_button_presses('379A', 1)
    28
    >>> min_translated_button_presses_for_numpad_button_presses('379A', 2)
    64
    """
    assert depth >= 0
    num_translated_button_presses = 0
    prev_button_press = 'A'
    for button_press in button_presses:
        num_translated_button_presses += min_translated_button_presses_for_numpad_button_press(prev_button_press, button_press, depth)
        prev_button_press = button_press
    return num_translated_button_presses


def execute_dpad_to_numpad_button_presses(button_presses: str) -> str:
    """
    >>> execute_dpad_to_numpad_button_presses('<A^A>^^AvvvA')
    '029A'
    """
    executed_button_presses: list[str] = []
    (row, column) = NUMPAD_BUTTON_COORDINATES['A']
    for button_press in button_presses:
        if button_press == 'v':
            row -= 1
        elif button_press == '^':
            row += 1
        elif button_press == '<':
            column -= 1
        elif button_press == '>':
            column += 1
        elif button_press == 'A':
            executed_button_presses.append(NUMPAD_COORDINATE_BUTTONS[(row, column)])
        else:
            assert False
        assert (0 <= row <= 3) and (0 <= column <= 2) and ((row, column) != (0, 0))
    return ''.join(executed_button_presses)


@cache
def min_translated_button_presses_for_dpad_button_press(from_button_press: str, to_button_press: str, depth: int) -> int:
    assert depth >= 0
    if to_button_press == from_button_press:
        # At the end of each button press, actors higher up the stack should be poised over the activate button.
        return 1

    (from_button_row, from_button_column) = DPAD_BUTTON_COORDINATES[from_button_press]
    (to_button_row, to_button_column) = DPAD_BUTTON_COORDINATES[to_button_press]
    horizontal_button_presses = ('>' if (to_button_column > from_button_column) else '<') * abs(to_button_column - from_button_column)
    vertical_button_presses = ('v' if (to_button_row > from_button_row) else '^') * abs(to_button_row - from_button_row)
    routes = set(''.join(permutation) for permutation in permutations(horizontal_button_presses + vertical_button_presses))
    # Remove permutation that takes us over the empty gap.
    if (from_button_row == to_button_column == 0):
        routes.remove(horizontal_button_presses + vertical_button_presses)
    elif (from_button_column == to_button_row == 0):
        routes.remove(vertical_button_presses + horizontal_button_presses)

    best_num_translated_button_presses: Optional[int] = None
    for route in sorted(routes):
        button_presses = route + 'A'
        num_translated_button_presses = len(button_presses) if (depth == 0) else min_translated_button_presses_for_dpad_button_presses(button_presses, depth - 1)
        if (best_num_translated_button_presses is None) or num_translated_button_presses < best_num_translated_button_presses:
            best_num_translated_button_presses = num_translated_button_presses
    assert best_num_translated_button_presses is not None
    return best_num_translated_button_presses


@cache
def min_translated_button_presses_for_dpad_button_presses(button_presses: str, depth: int) -> int:
    assert depth >= 0
    num_translated_button_presses = 0
    prev_button_press = 'A'
    for button_press in button_presses:
        num_translated_button_presses += min_translated_button_presses_for_dpad_button_press(prev_button_press, button_press, depth)
        prev_button_press = button_press
    return num_translated_button_presses


def execute_dpad_to_dpad_button_presses(button_presses: str) -> str:
    """
    >>> execute_dpad_to_dpad_button_presses('<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A')
    'v<<A>>^A<A>AvA<^AA>A<vAAA>^A'
    >>> execute_dpad_to_dpad_button_presses('v<<A>>^A<A>AvA<^AA>A<vAAA>^A')
    '<A^A>^^AvvvA'
    """
    executed_button_presses: list[str] = []
    (row, column) = DPAD_BUTTON_COORDINATES['A']
    for button_press in button_presses:
        if button_press == '^':
            row -= 1
        elif button_press == 'v':
            row += 1
        elif button_press == '<':
            column -= 1
        elif button_press == '>':
            column += 1
        elif button_press == 'A':
            executed_button_presses.append(DPAD_COORDINATE_BUTTONS[(row, column)])
        else:
            assert False
        assert (0 <= row <= 1) and (0 <= column <= 2) and ((row, column) != (0, 0))
    return ''.join(executed_button_presses)


def calculate_code_complexity(code: Code, num_robots: int) -> int:
    """
    >>> calculate_code_complexity(Code.from_line('029A'), 2)
    1972
    >>> calculate_code_complexity(Code.from_line('980A'), 2)
    58800
    >>> calculate_code_complexity(Code.from_line('179A'), 2)
    12172
    >>> calculate_code_complexity(Code.from_line('456A'), 2)
    29184
    >>> calculate_code_complexity(Code.from_line('379A'), 2)
    24256
    """
    num_button_presses = min_translated_button_presses_for_numpad_button_presses(code.button_presses, num_robots)
    return num_button_presses * code.number


########################################################################################################################
# Part 1
########################################################################################################################

def sum_code_complexities_with_two_robots(lines: Iterable[str]) -> int:
    """
    >>> sum_code_complexities_with_two_robots([
    ...     '029A',
    ...     '980A',
    ...     '179A',
    ...     '456A',
    ...     '379A',
    ... ])
    126384
    """
    codes = parse_codes(lines)
    return sum(map(partial(calculate_code_complexity, num_robots=2), codes))


########################################################################################################################
# Part 2 (of a copy of a copy of a copy of a)
########################################################################################################################

def sum_code_complexities_with_twenty_five_robots(lines: Iterable[str]) -> int:
    codes = parse_codes(lines)
    return sum(map(partial(calculate_code_complexity, num_robots=25), codes))


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
        print(sum_code_complexities_with_two_robots(lines))
    elif args.part == 2:
        print(sum_code_complexities_with_twenty_five_robots(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
