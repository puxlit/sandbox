#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator


########################################################################################################################
# Part 1
########################################################################################################################

ASCII_ZERO = 0x30
ASCII_NINE = 0x39


def extract_naive_first_digit(chars: Iterable[int]) -> int:
    for char in chars:
        if ASCII_ZERO <= char <= ASCII_NINE:
            return char - ASCII_ZERO
    raise ValueError()


def extract_naive_calibration_values(lines: Iterable[bytes]) -> Iterator[int]:
    """
    Extract the calibration value (comprising the first and last digits) from each line.

    >>> list(extract_naive_calibration_values([
    ...     b'1abc2',
    ...     b'pqr3stu8vwx',
    ...     b'a1b2c3d4e5f',
    ...     b'treb7uchet',
    ... ]))
    [12, 38, 15, 77]
    """
    for line in lines:
        first_digit = extract_naive_first_digit(line)
        last_digit = extract_naive_first_digit(reversed(line))
        yield (first_digit * 10) + last_digit


def sum_naive_calibration_values(lines: Iterable[bytes]) -> int:
    return sum(extract_naive_calibration_values(lines))


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1,))
    parser.add_argument('input', type=argparse.FileType('rb'))
    args = parser.parse_args()

    if (args.part == 1):
        print(sum_naive_calibration_values(args.input))
    else:
        raise ValueError()


if __name__ == '__main__':
    main()
