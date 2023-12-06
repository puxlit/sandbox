#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from math import ceil, floor, prod, sqrt
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

CHARGING_MM_PER_MS_PER_MS = 1


class RaceInfo(NamedTuple):
    time_allowed_ms: int
    best_distance_mm: int

    def calculate_margin_of_error(self) -> int:
        """
        Calculate the number of ways we could beat the record.

        TIME_ALLOWED = time_charging + time_moving
        BEST_DISTANCE < CHARGING_MM_PER_MS_PER_MS * time_charging * time_moving

        time_charging = TIME_ALLOWED - time_moving
        BEST_DISTANCE < CHARGING_MM_PER_MS_PER_MS * (TIME_ALLOWED - time_moving) * time_moving
        BEST_DISTANCE < CHARGING_MM_PER_MS_PER_MS * ((TIME_ALLOWED * time_moving) - time_moving^2)
        BEST_DISTANCE / CHARGING_MM_PER_MS_PER_MS < (TIME_ALLOWED * time_moving) - time_moving^2
        time_moving^2 - (TIME_ALLOWED * time_moving) + (BEST_DISTANCE / CHARGING_MM_PER_MS_PER_MS) < 0

        Using the quadratic formula, our roots are as follows.

        (TIME_ALLOWED ± sqrt(TIME_ALLOWED^2 - (4 * (BEST_DISTANCE / CHARGING_MM_PER_MS_PER_MS)))) / 2

        As the `a` coefficient is positive, the parabola opens up. Thus, the integer solutions to the original
        inequality lie in the interval (smaller_root, larger_root).

        >>> RaceInfo(7, 9).calculate_margin_of_error()
        4
        >>> RaceInfo(15, 40).calculate_margin_of_error()
        8
        >>> RaceInfo(30, 200).calculate_margin_of_error()
        9
        """
        discriminant = self.time_allowed_ms**2 - (4 * (self.best_distance_mm / CHARGING_MM_PER_MS_PER_MS))
        assert discriminant >= 0  # There should be one or two real solutions.
        sqrt_discriminant = sqrt(discriminant)
        smaller_root = (self.time_allowed_ms - sqrt_discriminant) / 2
        larger_root = (self.time_allowed_ms + sqrt_discriminant) / 2
        smaller_solution = ceil(smaller_root) if smaller_root != int(smaller_root) else int(smaller_root) + 1
        larger_solution = floor(larger_root) if larger_root != int(larger_root) else int(larger_root) - 1
        assert smaller_solution <= larger_solution
        return larger_solution - smaller_solution + 1


TIMES_ALLOWED_MS_HEADER_PREFIX = 'Time:'
BEST_DISTANCES_MM_HEADER_PREFIX = 'Distance:'


def parse_race_infos(lines: Iterator[str]) -> Iterator[RaceInfo]:
    """
    >>> list(parse_race_infos(iter([
    ...     'Time:      7  15   30',
    ...     'Distance:  9  40  200',
    ... ])))
    [RaceInfo(time_allowed_ms=7, best_distance_mm=9), RaceInfo(time_allowed_ms=15, best_distance_mm=40), RaceInfo(time_allowed_ms=30, best_distance_mm=200)]
    """
    line = next(lines)
    if not line.startswith(TIMES_ALLOWED_MS_HEADER_PREFIX):
        raise ValueError(f'Times allowed (ms) line {line!r} does not start with '
                         f'expected prefix {TIMES_ALLOWED_MS_HEADER_PREFIX!r}')
    times_allowed_ms = (int(x) for x in line.removeprefix(TIMES_ALLOWED_MS_HEADER_PREFIX).split())
    line = next(lines)
    if not line.startswith(BEST_DISTANCES_MM_HEADER_PREFIX):
        raise ValueError(f'Best distances (mm) line {line!r} does not start with '
                         f'expected prefix {BEST_DISTANCES_MM_HEADER_PREFIX!r}')
    best_distances_mm = (int(x) for x in line.removeprefix(BEST_DISTANCES_MM_HEADER_PREFIX).split())
    try:
        line = next(lines)
        raise ValueError(f'Unexpected line {line!r}')
    except StopIteration:
        pass
    # TODO: Raise exception if iterables are of unequal length.
    return (RaceInfo(*args) for args in zip(times_allowed_ms, best_distances_mm))


def calculate_product_of_margins_of_error(lines: Iterable[str]) -> int:
    """
    >>> calculate_product_of_margins_of_error([
    ...     'Time:      7  15   30',
    ...     'Distance:  9  40  200',
    ... ])
    288
    """
    race_infos = parse_race_infos(iter(lines))
    return prod(map(lambda race_info: race_info.calculate_margin_of_error(), race_infos))


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
        print(calculate_product_of_margins_of_error(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
