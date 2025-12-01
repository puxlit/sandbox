#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator


########################################################################################################################
# Part 1
########################################################################################################################

LEFT_ROTATION_PREFIX = 'L'
RIGHT_ROTATION_PREFIX = 'R'

DIAL_SIZE = 100
DIAL_STARTING_POSITION = 50
DIAL_KEY_POSITION = 0


def parse_rotations(lines: Iterable[str]) -> Iterator[int]:
    """
    >>> list(parse_rotations([
    ...     'L68',
    ...     'L30',
    ...     'R48',
    ...     'L5',
    ...     'R60',
    ...     'L55',
    ...     'L1',
    ...     'L99',
    ...     'R14',
    ...     'L82',
    ... ]))
    [-68, -30, 48, -5, 60, -55, -1, -99, 14, -82]
    """
    for line in lines:
        if line.startswith(LEFT_ROTATION_PREFIX):
            raw_magnitude = line.removeprefix(LEFT_ROTATION_PREFIX)
            direction = -1
        elif line.startswith(RIGHT_ROTATION_PREFIX):
            raw_magnitude = line.removeprefix(RIGHT_ROTATION_PREFIX)
            direction = 1
        else:
            raise ValueError(f'Unexpected rotation prefix: {line!r}')
        magnitude = int(raw_magnitude)
        yield direction * magnitude


def execute_rotations(dial_size: int, dial_starting_position: int, rotations: Iterable[int]) -> Iterator[int]:
    """
    >>> list(execute_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, [-68, -30, 48, -5, 60, -55, -1, -99, 14, -82]))
    [82, 52, 0, 95, 55, 0, 99, 0, 14, 32]
    """
    assert dial_size > 0
    assert 0 <= dial_starting_position < dial_size
    dial_position = dial_starting_position
    for rotation in rotations:
        dial_position = (dial_position + rotation) % dial_size
        yield dial_position


def derive_password(lines: Iterable[str]) -> int:
    """
    >>> derive_password([
    ...     'L68',
    ...     'L30',
    ...     'R48',
    ...     'L5',
    ...     'R60',
    ...     'L55',
    ...     'L1',
    ...     'L99',
    ...     'R14',
    ...     'L82',
    ... ])
    3
    """
    rotations = parse_rotations(lines)
    return sum(
        1 if dial_position == DIAL_KEY_POSITION else 0
        for dial_position
        in execute_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, rotations)
    )


########################################################################################################################
# Part 2
########################################################################################################################

def execute_click_rotations(dial_size: int, dial_starting_position: int, rotations: Iterable[int]) -> Iterator[tuple[int, int]]:
    """
    >>> list(execute_click_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, [-68, -30, 48, -5, 60, -55, -1, -99, 14, -82]))
    [(1, 82), (0, 52), (1, 0), (0, 95), (1, 55), (1, 0), (0, 99), (1, 0), (0, 14), (1, 32)]
    >>> list(execute_click_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, [1000]))
    [(10, 50)]
    >>> list(execute_click_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, [-50, -1]))
    [(1, 0), (0, 99)]
    >>> list(execute_click_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, [-50, -101]))
    [(1, 0), (1, 99)]
    """
    assert dial_size > 0
    assert 0 <= dial_starting_position < dial_size
    dial_position = dial_starting_position
    for rotation in rotations:
        raw_new_dial_position = dial_position + rotation
        (signed_clicks, new_dial_position) = divmod(raw_new_dial_position, dial_size)
        clicks = abs(signed_clicks)
        # If we turn left from zero, then `divmod(-1, 100) == (-1, 99)`, which we need to adjust for.
        if (dial_position == 0) and (rotation < 0) and (new_dial_position != 0):
            clicks -= 1
        # If we turn left from anywhere to zero, then `divmod(0, 100) == (0, 0)`, which we need to adjust for.
        elif (rotation < 0) and (raw_new_dial_position == 0):
            clicks += 1
        dial_position = new_dial_position
        yield (clicks, dial_position)


def derive_click_password(lines: Iterable[str]) -> int:
    """
    >>> derive_click_password([
    ...     'L68',
    ...     'L30',
    ...     'R48',
    ...     'L5',
    ...     'R60',
    ...     'L55',
    ...     'L1',
    ...     'L99',
    ...     'R14',
    ...     'L82',
    ... ])
    6
    >>> derive_click_password([
    ...     'R1000',
    ... ])
    10
    """
    rotations = parse_rotations(lines)
    return sum(clicks for (clicks, _) in execute_click_rotations(DIAL_SIZE, DIAL_STARTING_POSITION, rotations))


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
        print(derive_password(lines))
    elif args.part == 2:
        print(derive_click_password(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
