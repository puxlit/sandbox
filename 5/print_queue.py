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
            (prerequisite_page, dependant_page) = map(int, line.split('|'))
            prerequisite_pages = ordering_rules.setdefault(dependant_page, set())
            assert prerequisite_page not in prerequisite_pages
            prerequisite_pages.add(prerequisite_page)

        updates: list[tuple[int, ...]] = []
        for line in lines_iter:
            updates.append(tuple(map(int, line.split(','))))

        return PrintJob(ordering_rules, tuple(updates))

    def filter_updates(self, *, correctly_ordered: bool) -> Iterator[tuple[int, ...]]:
        for update in self.updates:
            following_pages = set(update)
            # Expect no duplicate pages.
            assert len(following_pages) == len(update)
            is_correctly_ordered = True
            for page in update:
                following_pages.remove(page)
                if page not in self.ordering_rules:
                    continue
                missing_prerequisite_pages = self.ordering_rules[page] & following_pages
                if missing_prerequisite_pages:
                    is_correctly_ordered = False
                    break
            if is_correctly_ordered == correctly_ordered:
                yield update

    def reorder_update(self, update: tuple[int, ...]) -> tuple[int, ...]:
        """
        >>> print_job = PrintJob.from_lines([
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
        ... ])
        >>> print_job.reorder_update((75, 97, 47, 61, 53))
        (97, 75, 47, 61, 53)
        >>> print_job.reorder_update((61, 13, 29))
        (61, 29, 13)
        >>> print_job.reorder_update((97, 13, 75, 29, 47))
        (97, 75, 47, 29, 13)
        """
        all_pages = set(update)
        # Expect no duplicate pages.
        assert len(all_pages) == len(update)

        page_to_prerequisite_pages: dict[int, set[int]] = {}
        page_to_dependant_pages: dict[int, set[int]] = {}
        for page in update:
            prerequisite_pages = self.ordering_rules.get(page, set()) & (all_pages - {page})
            assert page not in page_to_prerequisite_pages
            page_to_prerequisite_pages[page] = prerequisite_pages
            page_to_dependant_pages.setdefault(page, set())
            for prerequisite_page in prerequisite_pages:
                page_to_dependant_pages.setdefault(prerequisite_page, set()).add(page)
        assert len(page_to_prerequisite_pages) == len(page_to_dependant_pages) == len(update)

        reordered_update: list[int] = []
        while page_to_prerequisite_pages:
            processed_pages: list[int] = []
            for (page, prerequisite_pages) in page_to_prerequisite_pages.items():
                if prerequisite_pages:
                    continue
                reordered_update.append(page)
                processed_pages.append(page)
                for dependant_page in page_to_dependant_pages[page]:
                    assert page in page_to_prerequisite_pages[dependant_page]
                    page_to_prerequisite_pages[dependant_page].remove(page)
            assert len(processed_pages) > 0
            for processed_page in processed_pages:
                del page_to_prerequisite_pages[processed_page]
        return tuple(reordered_update)


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
    correctly_ordered_updates = print_job.filter_updates(correctly_ordered=True)
    middle_page_numbers = map(get_middle_page_number, correctly_ordered_updates)
    return sum(middle_page_numbers)


########################################################################################################################
# Part 2
########################################################################################################################

def sum_middle_page_numbers_from_fixed_incorrectly_ordered_updates(lines: Iterable[str]) -> int:
    """
    >>> sum_middle_page_numbers_from_fixed_incorrectly_ordered_updates([
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
    123
    """
    print_job = PrintJob.from_lines(lines)
    incorrectly_ordered_updates = print_job.filter_updates(correctly_ordered=False)
    fixed_incorrectly_ordered_updates = map(print_job.reorder_update, incorrectly_ordered_updates)
    middle_page_numbers = map(get_middle_page_number, fixed_incorrectly_ordered_updates)
    return sum(middle_page_numbers)


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
    elif args.part == 2:
        print(sum_middle_page_numbers_from_fixed_incorrectly_ordered_updates(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
