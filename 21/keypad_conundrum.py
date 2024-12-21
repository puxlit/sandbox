#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from functools import cache
from itertools import permutations
from typing import NamedTuple, Optional


########################################################################################################################
# The hardest button to button
########################################################################################################################

# (0, 0) is the empty gap, rows count upwards, columns count rightwards.
NUMERIC_KEYPAD_BUTTON_COORDINATES = {
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
NUMERIC_KEYPAD_COORDINATE_BUTTONS = {coordinate: button for (button, coordinate) in NUMERIC_KEYPAD_BUTTON_COORDINATES.items()}

# (0, 0) is the empty gap, rows count downwards, columns count rightwards.
DIRECTIONAL_KEYPAD_BUTTON_COORDINATES = {
    '^': (0, 1),
    'A': (0, 2),
    '<': (1, 0),
    'v': (1, 1),
    '>': (1, 2),
}
DIRECTIONAL_KEYPAD_COORDINATE_BUTTONS = {coordinate: button for (button, coordinate) in DIRECTIONAL_KEYPAD_BUTTON_COORDINATES.items()}


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
def numeric_to_directional_keypad_button_press(from_button_press: str, to_button_press: str, depth: int) -> str:
    assert depth >= 0
    if to_button_press == from_button_press:
        # At the end of each button press, actors higher up the stack should be poised over the activate button.
        return 'A'

    (from_button_row, from_button_column) = NUMERIC_KEYPAD_BUTTON_COORDINATES[from_button_press]
    (to_button_row, to_button_column) = NUMERIC_KEYPAD_BUTTON_COORDINATES[to_button_press]
    horizontal_button_presses = ('>' if (to_button_column > from_button_column) else '<') * abs(to_button_column - from_button_column)
    vertical_button_presses = ('^' if (to_button_row > from_button_row) else 'v') * abs(to_button_row - from_button_row)
    routes = set(''.join(permutation) for permutation in permutations(horizontal_button_presses + vertical_button_presses))
    # Remove permutation that takes us over the empty gap.
    if (from_button_row == to_button_column == 0):
        routes.remove(horizontal_button_presses + vertical_button_presses)
    elif (from_button_column == to_button_row == 0):
        routes.remove(vertical_button_presses + horizontal_button_presses)

    best_translated_button_presses: Optional[str] = None
    for route in sorted(routes):
        button_presses = route + 'A'
        translated_button_presses = button_presses if (depth == 0) else directional_to_directional_keypad_button_presses(button_presses, depth - 1)
        if (best_translated_button_presses is None) or len(translated_button_presses) < len(best_translated_button_presses):
            best_translated_button_presses = translated_button_presses
    assert best_translated_button_presses is not None
    return best_translated_button_presses


def numeric_to_directional_keypad_button_presses(button_presses: str, depth: int) -> str:
    """
    >>> len(numeric_to_directional_keypad_button_presses('029A', 0))
    12
    >>> len(numeric_to_directional_keypad_button_presses('029A', 1))
    28
    >>> len(numeric_to_directional_keypad_button_presses('029A', 2))
    68
    >>> len(numeric_to_directional_keypad_button_presses('980A', 0))
    12
    >>> len(numeric_to_directional_keypad_button_presses('980A', 1))
    26
    >>> len(numeric_to_directional_keypad_button_presses('980A', 2))
    60
    >>> len(numeric_to_directional_keypad_button_presses('179A', 0))
    14
    >>> len(numeric_to_directional_keypad_button_presses('179A', 1))
    28
    >>> len(numeric_to_directional_keypad_button_presses('179A', 2))
    68
    >>> len(numeric_to_directional_keypad_button_presses('456A', 0))
    12
    >>> len(numeric_to_directional_keypad_button_presses('456A', 1))
    26
    >>> len(numeric_to_directional_keypad_button_presses('456A', 2))
    64
    >>> len(numeric_to_directional_keypad_button_presses('379A', 0))
    14
    >>> len(numeric_to_directional_keypad_button_presses('379A', 1))
    28
    >>> len(numeric_to_directional_keypad_button_presses('379A', 2))
    64
    """
    assert depth >= 0
    translated_button_presses: list[str] = []
    prev_button_press = 'A'
    for button_press in button_presses:
        translated_button_presses.append(numeric_to_directional_keypad_button_press(prev_button_press, button_press, depth))
        prev_button_press = button_press
    return ''.join(translated_button_presses)


def execute_directional_to_numeric_keypad_button_presses(button_presses: str) -> str:
    """
    >>> execute_directional_to_numeric_keypad_button_presses('<A^A>^^AvvvA')
    '029A'
    """
    executed_button_presses: list[str] = []
    (row, column) = NUMERIC_KEYPAD_BUTTON_COORDINATES['A']
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
            executed_button_presses.append(NUMERIC_KEYPAD_COORDINATE_BUTTONS[(row, column)])
        else:
            assert False
        assert (0 <= row <= 3) and (0 <= column <= 2) and ((row, column) != (0, 0))
    return ''.join(executed_button_presses)


@cache
def directional_to_directional_keypad_button_press(from_button_press: str, to_button_press: str, depth: int) -> str:
    assert depth >= 0
    if to_button_press == from_button_press:
        # At the end of each button press, actors higher up the stack should be poised over the activate button.
        return 'A'

    (from_button_row, from_button_column) = DIRECTIONAL_KEYPAD_BUTTON_COORDINATES[from_button_press]
    (to_button_row, to_button_column) = DIRECTIONAL_KEYPAD_BUTTON_COORDINATES[to_button_press]
    horizontal_button_presses = ('>' if (to_button_column > from_button_column) else '<') * abs(to_button_column - from_button_column)
    vertical_button_presses = ('v' if (to_button_row > from_button_row) else '^') * abs(to_button_row - from_button_row)
    routes = set(''.join(permutation) for permutation in permutations(horizontal_button_presses + vertical_button_presses))
    # Remove permutation that takes us over the empty gap.
    if (from_button_row == to_button_column == 0):
        routes.remove(horizontal_button_presses + vertical_button_presses)
    elif (from_button_column == to_button_row == 0):
        routes.remove(vertical_button_presses + horizontal_button_presses)

    best_translated_button_presses: Optional[str] = None
    for route in sorted(routes):
        button_presses = route + 'A'
        translated_button_presses = button_presses if (depth == 0) else directional_to_directional_keypad_button_presses(button_presses, depth - 1)
        if (best_translated_button_presses is None) or len(translated_button_presses) < len(best_translated_button_presses):
            best_translated_button_presses = translated_button_presses
    assert best_translated_button_presses is not None
    return best_translated_button_presses


@cache
def directional_to_directional_keypad_button_presses(button_presses: str, depth: int) -> str:
    assert depth >= 0
    translated_button_presses: list[str] = []
    prev_button_press = 'A'
    for button_press in button_presses:
        translated_button_presses.append(directional_to_directional_keypad_button_press(prev_button_press, button_press, depth))
        prev_button_press = button_press
    return ''.join(translated_button_presses)


def execute_directional_to_directional_keypad_button_presses(button_presses: str) -> str:
    """
    >>> execute_directional_to_directional_keypad_button_presses('<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A')
    'v<<A>>^A<A>AvA<^AA>A<vAAA>^A'
    >>> execute_directional_to_directional_keypad_button_presses('v<<A>>^A<A>AvA<^AA>A<vAAA>^A')
    '<A^A>^^AvvvA'
    """
    executed_button_presses: list[str] = []
    (row, column) = DIRECTIONAL_KEYPAD_BUTTON_COORDINATES['A']
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
            executed_button_presses.append(DIRECTIONAL_KEYPAD_COORDINATE_BUTTONS[(row, column)])
        else:
            assert False
        assert (0 <= row <= 1) and (0 <= column <= 2) and ((row, column) != (0, 0))
    return ''.join(executed_button_presses)


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_code_complexity(code: Code) -> int:
    """
    >>> calculate_code_complexity(Code.from_line('029A'))
    1972
    >>> calculate_code_complexity(Code.from_line('980A'))
    58800
    >>> calculate_code_complexity(Code.from_line('179A'))
    12172
    >>> calculate_code_complexity(Code.from_line('456A'))
    29184
    >>> calculate_code_complexity(Code.from_line('379A'))
    24256
    """
    button_presses = numeric_to_directional_keypad_button_presses(code.button_presses, 2)
    return len(button_presses) * code.number


def sum_code_complexities(lines: Iterable[str]) -> int:
    """
    >>> sum_code_complexities([
    ...     '029A',
    ...     '980A',
    ...     '179A',
    ...     '456A',
    ...     '379A',
    ... ])
    126384
    """
    codes = parse_codes(lines)
    return sum(map(calculate_code_complexity, codes))


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
        print(sum_code_complexities(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
