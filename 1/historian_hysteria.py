#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import Counter
from collections.abc import Iterable


########################################################################################################################
# Part 1
########################################################################################################################

def parse_lists(lines: Iterable[str]) -> tuple[list[int], list[int]]:
    """
    >>> parse_lists([
    ...     '3   4',
    ...     '4   3',
    ...     '2   5',
    ...     '1   3',
    ...     '3   9',
    ...     '3   3',
    ... ])
    ([3, 4, 2, 1, 3, 3], [4, 3, 5, 3, 9, 3])
    """
    left_list: list[int] = []
    right_list: list[int] = []
    for line in lines:
        (left_number, right_number) = line.split()
        left_list.append(int(left_number))
        right_list.append(int(right_number))
    return (left_list, right_list)


def sum_distances(lines: Iterable[str]) -> int:
    """
    >>> sum_distances([
    ...     '3   4',
    ...     '4   3',
    ...     '2   5',
    ...     '1   3',
    ...     '3   9',
    ...     '3   3',
    ... ])
    11
    """
    (left_list, right_list) = parse_lists(lines)
    distances = (abs(right_number - left_number) for (left_number, right_number) in zip(sorted(left_list), sorted(right_list)))
    return sum(distances)


########################################################################################################################
# Part 2
########################################################################################################################

def sum_similarity_scores(lines: Iterable[str]) -> int:
    """
    >>> sum_similarity_scores([
    ...     '3   4',
    ...     '4   3',
    ...     '2   5',
    ...     '1   3',
    ...     '3   9',
    ...     '3   3',
    ... ])
    31
    """
    (left_list, right_list) = parse_lists(lines)
    occurrences = Counter(right_list)
    similarity_scores = (left_number * occurrences.get(left_number, 0) for left_number in left_list)
    return sum(similarity_scores)


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
        print(sum_distances(lines))
    elif args.part == 2:
        print(sum_similarity_scores(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
