#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from itertools import combinations


########################################################################################################################
# More graphs
########################################################################################################################

CONNECTION_DELIMITER = '-'
CHIEF_HISTORIAN_COMPUTER_NAME_PREFIX = 't'


def parse_network_map(lines: Iterable[str]) -> dict[str, set[str]]:
    adjacency_list: dict[str, set[str]] = {}
    for line in lines:
        (a, b) = line.split(CONNECTION_DELIMITER)
        assert len(a) == len(b) == 2
        adjacency_list.setdefault(a, set()).add(b)
        adjacency_list.setdefault(b, set()).add(a)
    return adjacency_list


def sets_of_three_interconnected_computers(adjacency_list: dict[str, set[str]]) -> Iterator[tuple[str, str, str]]:
    """
    >>> tuple(sets_of_three_interconnected_computers(parse_network_map([
    ...     'kh-tc',
    ...     'qp-kh',
    ...     'de-cg',
    ...     'ka-co',
    ...     'yn-aq',
    ...     'qp-ub',
    ...     'cg-tb',
    ...     'vc-aq',
    ...     'tb-ka',
    ...     'wh-tc',
    ...     'yn-cg',
    ...     'kh-ub',
    ...     'ta-co',
    ...     'de-co',
    ...     'tc-td',
    ...     'tb-wq',
    ...     'wh-td',
    ...     'ta-ka',
    ...     'td-qp',
    ...     'aq-cg',
    ...     'wq-ub',
    ...     'ub-vc',
    ...     'de-ta',
    ...     'wq-aq',
    ...     'wq-vc',
    ...     'wh-yn',
    ...     'ka-de',
    ...     'kh-ta',
    ...     'co-tc',
    ...     'wh-qp',
    ...     'tb-vc',
    ...     'td-yn',
    ... ])))
    (('aq', 'cg', 'yn'), ('aq', 'vc', 'wq'), ('co', 'de', 'ka'), ('co', 'de', 'ta'), ('co', 'ka', 'ta'), ('de', 'ka', 'ta'), ('kh', 'qp', 'ub'), ('qp', 'td', 'wh'), ('tb', 'vc', 'wq'), ('tc', 'td', 'wh'), ('td', 'wh', 'yn'), ('ub', 'vc', 'wq'))
    """
    processed_computer_names: set[str] = set()
    for a in sorted(adjacency_list.keys()):
        for (b, c) in combinations(sorted(adjacency_list[a]), 2):
            if (b not in processed_computer_names) and (c not in processed_computer_names) and (c in adjacency_list[b]):
                yield (a, b, c)
        processed_computer_names.add(a)


########################################################################################################################
# Part 1
########################################################################################################################

def count_sets_of_three_interconnected_computers_including_suspect_computer(lines: Iterable[str]) -> int:
    """
    >>> count_sets_of_three_interconnected_computers_including_suspect_computer([
    ...     'kh-tc',
    ...     'qp-kh',
    ...     'de-cg',
    ...     'ka-co',
    ...     'yn-aq',
    ...     'qp-ub',
    ...     'cg-tb',
    ...     'vc-aq',
    ...     'tb-ka',
    ...     'wh-tc',
    ...     'yn-cg',
    ...     'kh-ub',
    ...     'ta-co',
    ...     'de-co',
    ...     'tc-td',
    ...     'tb-wq',
    ...     'wh-td',
    ...     'ta-ka',
    ...     'td-qp',
    ...     'aq-cg',
    ...     'wq-ub',
    ...     'ub-vc',
    ...     'de-ta',
    ...     'wq-aq',
    ...     'wq-vc',
    ...     'wh-yn',
    ...     'ka-de',
    ...     'kh-ta',
    ...     'co-tc',
    ...     'wh-qp',
    ...     'tb-vc',
    ...     'td-yn',
    ... ])
    7
    """
    adjacency_list = parse_network_map(lines)
    return sum(
        any(computer_name.startswith(CHIEF_HISTORIAN_COMPUTER_NAME_PREFIX) for computer_name in computer_names)
        for computer_names in sets_of_three_interconnected_computers(adjacency_list)
    )


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
        print(count_sets_of_three_interconnected_computers_including_suspect_computer(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
