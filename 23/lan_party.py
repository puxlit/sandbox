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


def parse_network_map(lines: Iterable[str]) -> dict[str, set[str]]:
    adjacency_list: dict[str, set[str]] = {}
    for line in lines:
        (a, b) = line.split(CONNECTION_DELIMITER)
        assert len(a) == len(b) == 2
        adjacency_list.setdefault(a, set()).add(b)
        adjacency_list.setdefault(b, set()).add(a)
    return adjacency_list


def three_computer_cliques(adjacency_list: dict[str, set[str]]) -> Iterator[tuple[str, str, str]]:
    """
    >>> tuple(three_computer_cliques(parse_network_map([
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


def maximum_clique(adjacency_list: dict[str, set[str]]) -> tuple[str, ...]:
    """
    >>> maximum_clique(parse_network_map([
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
    ... ]))
    ('co', 'de', 'ka', 'ta')
    """
    maximum_clique: set[str] = set()
    for a in adjacency_list.keys():
        clique = {a, *adjacency_list[a]}
        for b in adjacency_list[a]:
            if b in clique:
                clique &= {b, *adjacency_list[b]}
        if len(clique) > len(maximum_clique):
            maximum_clique = clique
    return tuple(sorted(maximum_clique))


########################################################################################################################
# Part 1
########################################################################################################################

CHIEF_HISTORIAN_COMPUTER_NAME_PREFIX = 't'


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
        for computer_names in three_computer_cliques(adjacency_list)
    )


########################################################################################################################
# Part 2
########################################################################################################################

LAN_PARTY_PASSWORD_COMPUTER_NAME_DELIMITER = ','


def get_lan_party_password(lines: Iterable[str]) -> str:
    """
    >>> get_lan_party_password([
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
    'co,de,ka,ta'
    """
    adjacency_list = parse_network_map(lines)
    return LAN_PARTY_PASSWORD_COMPUTER_NAME_DELIMITER.join(maximum_clique(adjacency_list))


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
    elif args.part == 2:
        print(get_lan_party_password(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
