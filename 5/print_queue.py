#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from typing import NamedTuple


########################################################################################################################
# Print job
########################################################################################################################

class PrintJob(NamedTuple):
    ordering_rules: dict[int, set[int]]
    updates: tuple[tuple[int, ...], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'PrintJob':
        lines_iter = iter(lines)

        ordering_rules: dict[int, set[int]] = {}
        for line in lines_iter:
            # Handle blank line section delimiter.
            if not line:
                break
            (dependant_page, page) = map(int, line.split('|'))
            dependant_pages = ordering_rules.setdefault(page, set())
            assert dependant_page not in dependant_pages
            dependant_pages.add(dependant_page)

        updates: list[tuple[int, ...]] = []
        for line in lines_iter:
            updates.append(tuple(map(int, line.split(','))))

        return PrintJob(ordering_rules, tuple(updates))

    def correctly_ordered_updates(self) -> Iterator[tuple[int, ...]]:
        for update in self.updates:
            following_pages = set(update)
            # Expect no duplicate pages.
            assert len(following_pages) == len(update)
            is_correctly_ordered = True
            for page in update:
                following_pages.remove(page)
                if page not in self.ordering_rules:
                    continue
                missing_dependant_pages = self.ordering_rules[page] & following_pages
                if missing_dependant_pages:
                    is_correctly_ordered = False
                    break
            if is_correctly_ordered:
                yield update


########################################################################################################################
# Part 1
########################################################################################################################

def get_middle_page_number(update: tuple[int, ...]) -> int:
    """
    >>> get_middle_page_number((75, 47, 61, 53, 29))
    61
    >>> get_middle_page_number((97, 61, 53, 29, 13))
    53
    >>> get_middle_page_number((75, 29, 13))
    29
    """
    assert len(update) % 2 == 1
    return update[len(update) // 2]


def sum_middle_page_numbers_from_correctly_ordered_updates(lines: Iterable[str]) -> int:
    """
    >>> sum_middle_page_numbers_from_correctly_ordered_updates([
    ...     '47|53',
    ...     '97|13',
    ...     '97|61',
    ...     '97|47',
    ...     '75|29',
    ...     '61|13',
    ...     '75|53',
    ...     '29|13',
    ...     '97|29',
    ...     '53|29',
    ...     '61|53',
    ...     '97|53',
    ...     '61|29',
    ...     '47|13',
    ...     '75|47',
    ...     '97|75',
    ...     '47|61',
    ...     '75|61',
    ...     '47|29',
    ...     '75|13',
    ...     '53|13',
    ...     '',
    ...     '75,47,61,53,29',
    ...     '97,61,53,29,13',
    ...     '75,29,13',
    ...     '75,97,47,61,53',
    ...     '61,13,29',
    ...     '97,13,75,29,47',
    ... ])
    143
    """
    print_job = PrintJob.from_lines(lines)
    return sum(map(get_middle_page_number, print_job.correctly_ordered_updates()))


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
        print(sum_middle_page_numbers_from_correctly_ordered_updates(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
