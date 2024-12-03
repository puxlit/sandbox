#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator


########################################################################################################################
# Arithmetic
########################################################################################################################

def shrink(x: int) -> int:
    if x > 0:
        return x - 1
    elif x < 0:
        return x + 1
    else:
        return 0


########################################################################################################################
# Reports and levels
########################################################################################################################

def parse_reports(lines: Iterable[str]) -> Iterator[tuple[int, ...]]:
    for line in lines:
        yield tuple(int(level) for level in line.split())


def is_report_safe(levels: tuple[int, ...], tolerance: int = 0, intertia: int = 0) -> bool:
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

    >>> is_report_safe((1, 1, 2, 4, 7), tolerance=1)  # leading plateau, recoverable by removing one level
    True
    >>> is_report_safe((1, 1, 1, 2, 4), tolerance=1)  # leading plateau, irrecoverable by removing one level
    False
    >>> is_report_safe((1, 1, 1, 2, 4), tolerance=2)  # leading plateau, recoverable by removing two levels
    True
    >>> is_report_safe((1, 2, 4, 7, 7), tolerance=1)  # trailing plateau, recoverable by removing one level
    True
    >>> is_report_safe((1, 2, 4, 4, 4), tolerance=1)  # trailing plateau, irrecoverable by removing one level
    False
    >>> is_report_safe((1, 2, 4, 4, 4), tolerance=2)  # trailing plateau, recoverable by removing two levels
    True
    >>> is_report_safe((1, 2, 2, 4, 7), tolerance=1)  # intermediate plateau, recoverable by removing one level
    True
    >>> is_report_safe((1, 2, 2, 2, 4), tolerance=1)  # intermediate plateau, irrecoverable by removing one level
    False
    >>> is_report_safe((1, 2, 2, 2, 4), tolerance=2)  # intermediate plateau, recoverable by removing two levels
    True

    >>> is_report_safe((7, 9, 7, 6, 4), tolerance=1)  # leading maxima, recoverable by removing level preceding pair of levels
    True
    >>> is_report_safe((7, 9, 4, 2, 1), tolerance=1)  # leading maxima, recoverable by removing first of pair of levels
    True
    >>> is_report_safe((1, 4, 2, 7, 8), tolerance=1)  # leading maxima/minima, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((3, 0, 1, 2, 4), tolerance=1)  # leading minima, recoverable by removing level preceding pair of levels
    True
    >>> is_report_safe((3, 0, 4, 7, 9), tolerance=1)  # leading minima, recoverable by removing first of pair of levels
    True
    >>> is_report_safe((8, 6, 9, 4, 2), tolerance=1)  # leading minima/maxima, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((4, 6, 7, 9, 8), tolerance=1)  # trailing maxima, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((4, 2, 1, 0, 3), tolerance=1)  # trailing minima, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((2, 4, 7, 6, 9), tolerance=1)  # intermediate maxima/minima, recoverable by removing first of pair of levels
    True
    >>> is_report_safe((2, 4, 5, 3, 7), tolerance=1)  # intermediate maxima/minima, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((9, 7, 5, 6, 5), tolerance=1)  # intermediate minima/maxima, recoverable by removing first of pair of levels
    True
    >>> is_report_safe((9, 7, 4, 6, 3), tolerance=1)  # intermediate minima/maxima, recoverable by removing second of pair of levels
    True

    >>> is_report_safe((1, 6, 7, 8, 9), tolerance=1)  # leading magnitude deviation, recoverable by removing first of pair of levels
    True
    >>> is_report_safe((4, 9, 5, 6, 7), tolerance=1)  # leading magnitude deviation, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((9, 8, 7, 6, 2), tolerance=1)  # trailing magnitude deviation, recoverable by removing second of pair of levels
    True
    >>> is_report_safe((2, 3, 9, 4, 5), tolerance=1)  # intermediate magnitude deviation, recoverable by removing second of pair of levels
    True
    """
    assert tolerance >= 0

    num_levels = len(levels)
    if num_levels < 2:
        return True

    i = 1
    while i < num_levels:
        delta = levels[i] - levels[i - 1]

        # Handle plateau.
        if delta == 0:
            if tolerance == 0:
                return False
            tolerance -= 1
            # Since the pair of levels are identical, it makes no difference which one we remove. In the report
            # "abcXXdef" where we're evaluating the pair "XX", we've validated "abcX" as safe and will try the subreport
            # "Xdef".
            return is_report_safe(levels[i:], tolerance=tolerance, intertia=intertia)

        # Handle change in direction.
        positive_delta = delta > 0
        if (intertia != 0) and (positive_delta != (intertia > 0)):
            if tolerance == 0:
                return False
            tolerance -= 1
            # Try removing either of the pair of levels. For example, in the report "abcXYdef" where we're evaluating
            # the pair "XY", we've validated "abcX" as safe and will try the subreports "cYdef" and "Xdef".
            #
            # If we have limited intertia (e.g. "aXYbcd"), we also need to try the subreport "YZbcd".
            #
            # If we're at the end of the report, we only need to remove the second of the pair of levels.
            limited_inertia = abs(intertia) == 1
            if limited_inertia:
                assert i == 2
            return (
                limited_inertia and is_report_safe(levels[1:], tolerance=tolerance, intertia=0)
            ) or (
                (i >= 2) and (i + 1 < num_levels) and is_report_safe((levels[i - 2],) + levels[i:], tolerance=tolerance, intertia=shrink(intertia))
            ) or (
                is_report_safe((levels[i - 1],) + levels[i + 1:], tolerance=tolerance, intertia=intertia)
            )
        next_intertia = intertia + (1 if positive_delta else -1)

        # Handle magnitude deviations.
        abs_delta = abs(delta)
        if abs_delta < 1 or abs_delta > 3:
            if tolerance == 0:
                return False
            tolerance -= 1
            # Try removing the second of the pair of levels. (Because we've validated that levels are monotonic at this
            # point, removing the first of the pair of levels would only increase the delta between the preceding level
            # and the second of the pair of levels.) For example, in the report "abcXYdef" where we're evaluating the
            # pair "XY", we've validated "abcX" as safe and will try the subreport "Xdef".
            #
            # If we have no intertia (e.g. "XYdef"), we can also try the subreport "Ydef".
            no_inertia = intertia == 0
            if no_inertia:
                assert i == 1
            return (
                no_inertia and is_report_safe(levels[i:], tolerance=tolerance, intertia=intertia)
            ) or (
                is_report_safe((levels[i - 1],) + levels[i + 1:], tolerance=tolerance, intertia=intertia)
            )

        intertia = next_intertia
        i += 1
    return True


########################################################################################################################
# Part 1
########################################################################################################################

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
# Part 2
########################################################################################################################

def is_report_tolerable(levels: tuple[int, ...]) -> bool:
    """
    >>> is_report_tolerable((7, 6, 4, 2, 1))
    True
    >>> is_report_tolerable((1, 2, 7, 8, 9))
    False
    >>> is_report_tolerable((9, 7, 6, 2, 1))
    False
    >>> is_report_tolerable((1, 3, 2, 4, 5))
    True
    >>> is_report_tolerable((8, 6, 4, 4, 1))
    True
    >>> is_report_tolerable((1, 3, 6, 7, 9))
    True
    """
    return is_report_safe(levels, tolerance=1)


def count_tolerable_reports(lines: Iterable[str]) -> int:
    """
    >>> count_tolerable_reports([
    ...     '7 6 4 2 1',
    ...     '1 2 7 8 9',
    ...     '9 7 6 2 1',
    ...     '1 3 2 4 5',
    ...     '8 6 4 4 1',
    ...     '1 3 6 7 9',
    ... ])
    4
    """
    reports = parse_reports(lines)
    return sum(map(is_report_tolerable, reports))


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
    elif args.part == 2:
        print(count_tolerable_reports(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
