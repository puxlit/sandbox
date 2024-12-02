#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator


########################################################################################################################
# Part 1
########################################################################################################################

def parse_reports(lines: Iterable[str]) -> Iterator[tuple[int, ...]]:
    for line in lines:
        yield tuple(int(level) for level in line.split())


def is_report_safe(levels: tuple[int, ...]) -> bool:
    """
    >>> is_report_safe((7, 6, 4, 2, 1))
    True
    >>> is_report_safe((1, 2, 7, 8, 9))
    False
    >>> is_report_safe((9, 7, 6, 2, 1))
    False
    >>> is_report_safe((1, 3, 2, 4, 5))
    False
    >>> is_report_safe((8, 6, 4, 4, 1))
    False
    >>> is_report_safe((1, 3, 6, 7, 9))
    True
    """
    assert len(levels) >= 2
    expect_increasing_levels = levels[1] > levels[0]
    for i in range(1, len(levels)):
        delta = levels[i] - levels[i - 1]
        if expect_increasing_levels != (delta > 0):
            return False
        abs_delta = abs(delta)
        if abs_delta < 1 or abs_delta > 3:
            return False
    return True


def count_safe_reports(lines: Iterable[str]) -> int:
    """
    >>> count_safe_reports([
    ...     '7 6 4 2 1',
    ...     '1 2 7 8 9',
    ...     '9 7 6 2 1',
    ...     '1 3 2 4 5',
    ...     '8 6 4 4 1',
    ...     '1 3 6 7 9',
    ... ])
    2
    """
    reports = parse_reports(lines)
    return sum(map(is_report_safe, reports))


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
        print(count_safe_reports(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
