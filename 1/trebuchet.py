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
    """
    >>> extract_naive_first_digit(b'1abc2')
    1
    >>> extract_naive_first_digit(b'pqr3stu8vwx')
    3
    >>> extract_naive_first_digit(b'a1b2c3d4e5f')
    1
    >>> extract_naive_first_digit(b'treb7uchet')
    7
    >>> extract_naive_first_digit(b'nada')
    Traceback (most recent call last):
        ...
    ValueError: b'nada' contains no digits
    """
    for char in chars:
        if ASCII_ZERO <= char <= ASCII_NINE:
            return char - ASCII_ZERO
    raise ValueError(f'{bytes(chars)!r} contains no digits')


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
    """
    >>> sum_naive_calibration_values([
    ...     b'1abc2',
    ...     b'pqr3stu8vwx',
    ...     b'a1b2c3d4e5f',
    ...     b'treb7uchet',
    ... ])
    142
    """
    return sum(extract_naive_calibration_values(lines))


########################################################################################################################
# Part 2
########################################################################################################################

# Note that "zero" is not mentioned as a valid digit.
SPELLED_DIGITS = {
    1: b'one',
    2: b'two',
    3: b'three',
    4: b'four',
    5: b'five',
    6: b'six',
    7: b'seven',
    8: b'eight',
    9: b'nine',
}


def extract_digits(chars: Iterable[int]) -> Iterator[int]:
    """
    >>> list(extract_digits(b'two1nine'))
    [2, 1, 9]
    >>> list(extract_digits(b'eightwothree'))
    [8, 2, 3]
    >>> list(extract_digits(b'abcone2threexyz'))
    [1, 2, 3]
    >>> list(extract_digits(b'xtwone3four'))
    [2, 1, 3, 4]
    >>> list(extract_digits(b'4nineeightseven2'))
    [4, 9, 8, 7, 2]
    >>> list(extract_digits(b'zoneight234'))
    [1, 8, 2, 3, 4]
    >>> list(extract_digits(b'7pqrstsixteen'))
    [7, 6]
    >>> list(extract_digits(b'twone'))
    [2, 1]
    >>> list(extract_digits(b'ninine'))
    [9]
    >>> list(extract_digits(b'nada'))
    []
    """
    spelled_digits = {digit: [spelling] for (digit, spelling) in SPELLED_DIGITS.items()}
    for char in chars:
        if ASCII_ZERO <= char <= ASCII_NINE:
            yield char - ASCII_ZERO
            spelled_digits = {digit: [spelling] for (digit, spelling) in SPELLED_DIGITS.items()}
        else:
            # It's unclear whether "twone" should yield 2 and 1. I'm assuming it should. Thus, every spelled digit is
            # matched independently.
            for (digit, partial_spellings) in spelled_digits.items():
                full_spelling = SPELLED_DIGITS[digit]
                # We're iterating backwards so we can delete items from `partial_spellings`.
                for i in range(len(partial_spellings) - 1, -1, -1):
                    partial_spelling = partial_spellings[i]
                    # Assume `partial_spelling` will never be an empty (byte) string.
                    if partial_spelling[0] != char:
                        # We didn't match the next expected letter; delete if this is a partial match.
                        if partial_spelling != full_spelling:
                            del partial_spellings[i]
                    elif len(partial_spelling) > 1:
                        # We matched the next expected letter, but still have more letters to go; advance.
                        partial_spellings[i] = partial_spelling[1:]
                    else:
                        # We matched the last expected letter; yield and delete.
                        yield digit
                        del partial_spellings[i]
                if partial_spellings[-1] != full_spelling:
                    # Ensure we can always match from the start of the spelled digit.
                    partial_spellings.append(full_spelling)


def extract_calibration_values(lines: Iterable[bytes]) -> Iterator[int]:
    """
    Extract the calibration value (comprising the first and last digits) from each line.

    >>> list(extract_calibration_values([
    ...     b'two1nine',
    ...     b'eightwothree',
    ...     b'abcone2threexyz',
    ...     b'xtwone3four',
    ...     b'4nineeightseven2',
    ...     b'zoneight234',
    ...     b'7pqrstsixteen',
    ... ]))
    [29, 83, 13, 24, 42, 14, 76]
    >>> list(extract_calibration_values([b'nada']))
    Traceback (most recent call last):
        ...
    ValueError: b'nada' contains no digits
    """
    for line in lines:
        digits = list(extract_digits(line))
        if not digits:
            raise ValueError(f'{line!r} contains no digits')
        first_digit = digits[0]
        last_digit = digits[-1]
        yield (first_digit * 10) + last_digit


def sum_calibration_values(lines: Iterable[bytes]) -> int:
    """
    >>> sum_calibration_values([
    ...     b'two1nine',
    ...     b'eightwothree',
    ...     b'abcone2threexyz',
    ...     b'xtwone3four',
    ...     b'4nineeightseven2',
    ...     b'zoneight234',
    ...     b'7pqrstsixteen',
    ... ])
    281
    """
    return sum(extract_calibration_values(lines))


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=argparse.FileType('rb'))
    args = parser.parse_args()
    lines = (line.rstrip(b'\n') for line in args.input)

    if args.part == 1:
        print(sum_naive_calibration_values(lines))
    elif args.part == 2:
        print(sum_calibration_values(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
