#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator, Sequence
from itertools import count
from typing import NamedTuple, Optional


########################################################################################################################
# Disk data structures
########################################################################################################################

class Run(NamedTuple):
    file_id: Optional[int]
    length: int

    def calculate_checksum(self, block_position: int) -> int:
        if self.file_id is None:
            return 0
        return sum(range(block_position, block_position + self.length)) * self.file_id


########################################################################################################################
# Part 1
########################################################################################################################

def parse_disk_map(disk_map: str) -> Iterator[Run]:
    """
    >>> tuple(parse_disk_map('12345'))
    (Run(file_id=0, length=1), Run(file_id=None, length=2), Run(file_id=1, length=3), Run(file_id=None, length=4), Run(file_id=2, length=5))
    >>> tuple(parse_disk_map('2333133121414131402'))
    (Run(file_id=0, length=2), Run(file_id=None, length=3), Run(file_id=1, length=3), Run(file_id=None, length=3), Run(file_id=2, length=1), Run(file_id=None, length=3), Run(file_id=3, length=3), Run(file_id=None, length=1), Run(file_id=4, length=2), Run(file_id=None, length=1), Run(file_id=5, length=4), Run(file_id=None, length=1), Run(file_id=6, length=4), Run(file_id=None, length=1), Run(file_id=7, length=3), Run(file_id=None, length=1), Run(file_id=8, length=4), Run(file_id=9, length=2))
    """
    file_ids = count()
    for (i, digit) in enumerate(disk_map):
        num_blocks = int(digit)
        if i % 2 == 0:
            assert num_blocks > 0
            yield Run(next(file_ids), num_blocks)
        else:
            if num_blocks > 0:
                yield Run(None, num_blocks)


def compact(runs: Sequence[Run]) -> Iterator[Run]:
    """
    >>> tuple(compact([]))
    ()
    >>> tuple(compact([
    ...     Run(file_id=6, length=9),
    ... ]))
    (Run(file_id=6, length=9),)
    >>> tuple(compact([
    ...     Run(file_id=None, length=0),
    ...     Run(file_id=6, length=3),
    ...     Run(file_id=6, length=3),
    ...     Run(file_id=None, length=0),
    ...     Run(file_id=6, length=3),
    ... ]))
    (Run(file_id=6, length=9),)
    >>> tuple(compact([
    ...     Run(file_id=6, length=9),
    ...     Run(file_id=4, length=2),
    ... ]))
    (Run(file_id=6, length=9), Run(file_id=4, length=2))
    >>> tuple(compact([
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=6, length=9),
    ...     Run(file_id=4, length=2),
    ... ]))
    (Run(file_id=4, length=1), Run(file_id=6, length=9), Run(file_id=4, length=1))
    >>> tuple(compact([
    ...     Run(file_id=None, length=69),
    ... ]))
    ()
    >>> tuple(compact([
    ...     Run(file_id=None, length=10),
    ...     Run(file_id=None, length=10),
    ...     Run(file_id=3, length=1),
    ...     Run(file_id=None, length=20),
    ...     Run(file_id=4, length=5),
    ...     Run(file_id=4, length=5),
    ...     Run(file_id=None, length=30),
    ...     Run(file_id=5, length=5),
    ...     Run(file_id=None, length=40),
    ...     Run(file_id=None, length=50),
    ... ]))
    (Run(file_id=5, length=5), Run(file_id=4, length=10), Run(file_id=3, length=1))

    >>> tuple(compact([
    ...     Run(file_id=0, length=1),
    ...     Run(file_id=None, length=2),
    ...     Run(file_id=1, length=3),
    ...     Run(file_id=None, length=4),
    ...     Run(file_id=2, length=5),
    ... ]))
    (Run(file_id=0, length=1), Run(file_id=2, length=2), Run(file_id=1, length=3), Run(file_id=2, length=3))
    >>> tuple(compact([
    ...     Run(file_id=0, length=2),
    ...     Run(file_id=None, length=3),
    ...     Run(file_id=1, length=3),
    ...     Run(file_id=None, length=3),
    ...     Run(file_id=2, length=1),
    ...     Run(file_id=None, length=3),
    ...     Run(file_id=3, length=3),
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=4, length=2),
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=5, length=4),
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=6, length=4),
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=7, length=3),
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=8, length=4),
    ...     Run(file_id=9, length=2),
    ... ]))
    (Run(file_id=0, length=2), Run(file_id=9, length=2), Run(file_id=8, length=1), Run(file_id=1, length=3), Run(file_id=8, length=3), Run(file_id=2, length=1), Run(file_id=7, length=3), Run(file_id=3, length=3), Run(file_id=6, length=1), Run(file_id=4, length=2), Run(file_id=6, length=1), Run(file_id=5, length=4), Run(file_id=6, length=2))
    """
    next_i = 0
    next_j = len(runs) - 1

    def __gen_left_runs() -> Iterator[Run]:
        nonlocal next_i, next_j
        while next_i <= next_j:
            curr_i = next_i
            next_i += 1
            yield runs[curr_i]
    left_runs = __gen_left_runs()

    def __gen_right_runs() -> Iterator[Run]:
        nonlocal next_i, next_j
        while next_i <= next_j:
            curr_j = next_j
            next_j -= 1
            yield runs[curr_j]
    right_runs = __gen_right_runs()

    scavenged_right_file_run: Optional[Run] = None
    while True:
        # Yield compacted file runs from the left.
        found_free_space_run = False
        compacted_left_file_run: Optional[Run] = None
        for left_run in left_runs:
            if left_run.file_id is None:
                if left_run.length == 0:
                    continue
                found_free_space_run = True
                break
            if compacted_left_file_run is None:
                compacted_left_file_run = left_run
                continue
            if left_run.file_id == compacted_left_file_run.file_id:
                compacted_left_file_run = Run(left_run.file_id, compacted_left_file_run.length + left_run.length)
                continue
            yield compacted_left_file_run
            compacted_left_file_run = left_run
        if compacted_left_file_run is not None:
            yield compacted_left_file_run
        if not found_free_space_run:
            assert next_i > next_j
            if scavenged_right_file_run is not None:
                yield scavenged_right_file_run
            break

        # Determine length of compacted free space runs from the left.
        assert left_run.file_id is None
        num_free_space_blocks = left_run.length
        while (next_i <= next_j) and (runs[next_i].file_id is None):
            num_free_space_blocks += next(left_runs).length

        # Fill free space.
        while num_free_space_blocks > 0:
            # Yield scavenged file run.
            if scavenged_right_file_run is not None:
                if scavenged_right_file_run.length <= num_free_space_blocks:
                    yield scavenged_right_file_run
                    num_free_space_blocks -= scavenged_right_file_run.length
                    scavenged_right_file_run = None
                elif next_i <= next_j:
                    yield Run(scavenged_right_file_run.file_id, num_free_space_blocks)
                    scavenged_right_file_run = Run(scavenged_right_file_run.file_id, scavenged_right_file_run.length - num_free_space_blocks)
                    break
                else:
                    # Don't fragment the remaining file run.
                    yield scavenged_right_file_run
                    scavenged_right_file_run = None
                    break

            # Skip free space runs from the right.
            while (next_i <= next_j) and (runs[next_j].file_id is None):
                next(right_runs)
            if next_i > next_j:
                break

            # Compact scavenged file run from the right.
            assert scavenged_right_file_run is None
            scavenged_right_file_run = next(right_runs)
            while (next_i <= next_j) and (runs[next_j].file_id == scavenged_right_file_run.file_id):
                scavenged_right_file_run = Run(scavenged_right_file_run.file_id, scavenged_right_file_run.length + next(right_runs).length)


def calculate_checksum(runs: Iterable[Run]) -> int:
    """
    >>> calculate_checksum([
    ...     Run(file_id=0, length=2),
    ...     Run(file_id=9, length=2),
    ...     Run(file_id=8, length=1),
    ...     Run(file_id=1, length=3),
    ...     Run(file_id=8, length=3),
    ...     Run(file_id=2, length=1),
    ...     Run(file_id=7, length=3),
    ...     Run(file_id=3, length=3),
    ...     Run(file_id=6, length=1),
    ...     Run(file_id=4, length=2),
    ...     Run(file_id=6, length=1),
    ...     Run(file_id=5, length=4),
    ...     Run(file_id=6, length=2),
    ... ])
    1928
    """
    checksum = 0
    block_position = 0
    for run in runs:
        checksum += run.calculate_checksum(block_position)
        block_position += run.length
    return checksum


def calculate_checksum_after_compaction(lines: Iterable[str]) -> int:
    """
    >>> calculate_checksum_after_compaction(['12345'])
    60
    >>> calculate_checksum_after_compaction(['2333133121414131402'])
    1928
    """
    runs = parse_disk_map(next(iter(lines)))
    compacted_runs = compact(tuple(runs))
    return calculate_checksum(compacted_runs)


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
        print(calculate_checksum_after_compaction(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
