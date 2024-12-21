#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from functools import cache
from typing import NamedTuple


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


@cache
def numeric_to_directional_keypad_button_press(from_button_press: str, to_button_press: str) -> str:
    if to_button_press == from_button_press:
        return 'A'
    (from_button_row, from_button_column) = NUMERIC_KEYPAD_BUTTON_COORDINATES[from_button_press]
    (to_button_row, to_button_column) = NUMERIC_KEYPAD_BUTTON_COORDINATES[to_button_press]
    # To minimise button presses the next layer up, we want to consolidate movements along each axis. Prefer moving
    # horizontally first (except when that'd take us over the empty gap) because that's what the examples prefer.
    horizontal_button_presses = ('>' if (to_button_column > from_button_column) else '<') * abs(to_button_column - from_button_column)
    vertical_button_presses = ('^' if (to_button_row > from_button_row) else 'v') * abs(to_button_row - from_button_row)
    if (from_button_row == 0) and (to_button_column == 0):
        return vertical_button_presses + horizontal_button_presses + 'A'
    else:
        return horizontal_button_presses + vertical_button_presses + 'A'


def numeric_to_directional_keypad_button_presses(button_presses: str) -> str:
    """
    >>> numeric_to_directional_keypad_button_presses('029A')
    '<A^A>^^AvvvA'
    >>> numeric_to_directional_keypad_button_presses('980A')
    '^^^A<AvvvA>A'
    >>> numeric_to_directional_keypad_button_presses('179A')
    '^<<A^^A>>AvvvA'
    >>> numeric_to_directional_keypad_button_presses('456A')
    '^^<<A>A>AvvA'
    >>> numeric_to_directional_keypad_button_presses('379A')
    '^A<<^^A>>AvvvA'
    """
    translated_button_presses: list[str] = []
    prev_button_press = 'A'
    for button_press in button_presses:
        translated_button_presses.append(numeric_to_directional_keypad_button_press(prev_button_press, button_press))
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
def directional_to_directional_keypad_button_press(from_button_press: str, to_button_press: str) -> str:
    if to_button_press == from_button_press:
        return 'A'
    (from_button_row, from_button_column) = DIRECTIONAL_KEYPAD_BUTTON_COORDINATES[from_button_press]
    (to_button_row, to_button_column) = DIRECTIONAL_KEYPAD_BUTTON_COORDINATES[to_button_press]
    # To minimise button presses the next layer up, we want to consolidate movements along each axis. Prefer moving
    # horizontally first (except when that'd take us over the empty gap) because that's what the examples prefer.
    horizontal_button_presses = ('>' if (to_button_column > from_button_column) else '<') * abs(to_button_column - from_button_column)
    vertical_button_presses = ('v' if (to_button_row > from_button_row) else '^') * abs(to_button_row - from_button_row)
    if (from_button_row == 0) and (to_button_column == 0):
        return vertical_button_presses + horizontal_button_presses + 'A'
    else:
        return horizontal_button_presses + vertical_button_presses + 'A'


def directional_to_directional_keypad_button_presses(button_presses: str) -> str:
    """
    >>> directional_to_directional_keypad_button_presses('<A^A>^^AvvvA')  # 029A
    'v<<A>>^A<A>AvA<^AA>A<vAAA>^A'
    >>> # directional_to_directional_keypad_button_presses('v<<A>>^A<A>AvA<^AA>A<vAAA>^A')
    >>> # expected (from example): '<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A'
    >>> # what we produce        : '<vA<AA>>^AvAA<^A>Av<<A>>^AvA^A<vA>^Av<<A>^A>AAvA^Av<<A>A>^AAAvA<^A>A'
    >>> directional_to_directional_keypad_button_presses('^^^A<AvvvA>A')  # 980A
    '<AAA>Av<<A>>^A<vAAA>^AvA^A'
    >>> # directional_to_directional_keypad_button_presses('<AAA>Av<<A>>^A<vAAA>^AvA^A')
    >>> # expected (from example): '<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A'
    >>> # what we produce        : 'v<<A>>^AAAvA^A<vA<AA>>^AvAA<^A>Av<<A>A>^AAAvA<^A>A<vA>^A<A>A'
    >>> directional_to_directional_keypad_button_presses('^<<A^^A>>AvvvA')  # 179A
    '<Av<AA>>^A<AA>AvAA^A<vAAA>^A'
    >>> # directional_to_directional_keypad_button_presses('<Av<AA>>^A<AA>AvAA^A<vAAA>^A')  # 179A
    >>> # expected (from example): '<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A'
    >>> # what we produce        : 'v<<A>>^A<vA<A>>^AAvAA<^A>Av<<A>>^AAvA^A<vA>^AA<A>Av<<A>A>^AAAvA<^A>A'
    >>> directional_to_directional_keypad_button_presses('^^<<A>A>AvvA')  # 456A
    '<AAv<AA>>^AvA^AvA^A<vAA>^A'
    >>> # directional_to_directional_keypad_button_presses('<AAv<AA>>^AvA^AvA^A<vAA>^A')
    >>> # expected (from example): '<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A'
    >>> # what we produce        : 'v<<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>Av<<A>A>^AAvA<^A>A'
    >>> directional_to_directional_keypad_button_presses('^A<<^^A>>AvvvA')  # 379A
    '<A>Av<<AA>^AA>AvAA^A<vAAA>^A'
    >>> # directional_to_directional_keypad_button_presses('<A>Av<<AA>^AA>AvAA^A<vAAA>^A')
    >>> # expected (from example): '<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A'
    >>> # what we produce        : 'v<<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>Av<<A>A>^AAAvA<^A>A'
    """
    translated_button_presses: list[str] = []
    prev_button_press = 'A'
    for button_press in button_presses:
        translated_button_presses.append(directional_to_directional_keypad_button_press(prev_button_press, button_press))
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
    first_robot_remote_button_presses = numeric_to_directional_keypad_button_presses(code.button_presses)
    second_robot_remote_button_presses = directional_to_directional_keypad_button_presses(first_robot_remote_button_presses)
    third_robot_remote_button_presses = directional_to_directional_keypad_button_presses(second_robot_remote_button_presses)
    return len(third_robot_remote_button_presses) * code.number


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
