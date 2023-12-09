#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable


########################################################################################################################
# Part 1
########################################################################################################################

def parse_oasis_report(lines: Iterable[str]) -> tuple[tuple[int, ...], ...]:
    """
    >>> parse_oasis_report([
    ...     '0 3 6 9 12 15',
    ...     '1 3 6 10 15 21',
    ...     '10 13 16 21 30 45',
    ... ])
    ((0, 3, 6, 9, 12, 15), (1, 3, 6, 10, 15, 21), (10, 13, 16, 21, 30, 45))
    """
    history_length = None
    histories: list[tuple[int, ...]] = []
    for line in lines:
        history = tuple(int(value) for value in line.split())
        if history_length is not None:
            if len(history) != history_length:
                raise ValueError(f'Parsed history with {len(history)} value(s) '
                                 f'instead of expected {history_length} value(s)')
        else:
            history_length = len(history)
        histories.append(history)
    return tuple(histories)


def extrapolate_next_values(values: tuple[int, ...], extrapolation_length: int) -> tuple[int, ...]:
    """
    >>> extrapolate_next_values((0, 3, 6, 9, 12, 15), 1)
    (18,)
    >>> extrapolate_next_values((1, 3, 6, 10, 15, 21), 1)
    (28,)
    >>> extrapolate_next_values((10, 13, 16, 21, 30, 45), 1)
    (68,)
    """
    num_values = len(values)
    assert num_values >= 2
    differences = tuple(values[i] - values[i - 1] for i in range(1, num_values))
    if not all(differences[i] == differences[0] for i in range(1, len(differences))):
        extrapolated_differences = extrapolate_next_values(differences, extrapolation_length)
        assert len(extrapolated_differences) == extrapolation_length
    else:
        extrapolated_differences = (differences[0],) * extrapolation_length
    extrapolated_values = []
    extrapolated_value = values[-1]
    for extrapolated_difference in extrapolated_differences:
        extrapolated_value += extrapolated_difference
        extrapolated_values.append(extrapolated_value)
    return tuple(extrapolated_values)


def sum_extrapolated_next_values(lines: Iterable[str]) -> int:
    """
    >>> sum_extrapolated_next_values([
    ...     '0 3 6 9 12 15',
    ...     '1 3 6 10 15 21',
    ...     '10 13 16 21 30 45',
    ... ])
    114
    """
    histories = parse_oasis_report(lines)
    return sum(extrapolate_next_values(history, 1)[0] for history in histories)


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
        print(sum_extrapolated_next_values(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
