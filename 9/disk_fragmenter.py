#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import bisect_left
from collections.abc import Iterable, Iterator, Sequence
from itertools import count
from typing import NamedTuple, Optional, Union


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


def compact_blocks(runs: Sequence[Run]) -> Iterator[Run]:
    """
    Compact disk by relocating file blocks (from the right) to free space blocks (from the left).

    The official inputs guarantee that: (i) runs alternate between files and free space; (ii) runs are merged (i.e. no
    adjacent runs are for the same file or free space); (iii) each file has exactly one run; (iv) file IDs monotonically
    increase.

    However, for my amusement, this function can tolerate degenerate inputs (such as unmerged runs).

    >>> tuple(compact_blocks([]))
    ()
    >>> tuple(compact_blocks([
    ...     Run(file_id=6, length=9),
    ... ]))
    (Run(file_id=6, length=9),)
    >>> tuple(compact_blocks([
    ...     Run(file_id=None, length=0),
    ...     Run(file_id=6, length=3),
    ...     Run(file_id=6, length=3),
    ...     Run(file_id=None, length=0),
    ...     Run(file_id=6, length=3),
    ... ]))
    (Run(file_id=6, length=9),)
    >>> tuple(compact_blocks([
    ...     Run(file_id=6, length=9),
    ...     Run(file_id=4, length=2),
    ... ]))
    (Run(file_id=6, length=9), Run(file_id=4, length=2))
    >>> tuple(compact_blocks([
    ...     Run(file_id=None, length=1),
    ...     Run(file_id=6, length=9),
    ...     Run(file_id=4, length=2),
    ... ]))
    (Run(file_id=4, length=1), Run(file_id=6, length=9), Run(file_id=4, length=1))
    >>> tuple(compact_blocks([
    ...     Run(file_id=None, length=69),
    ... ]))
    ()
    >>> tuple(compact_blocks([
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

    >>> tuple(compact_blocks([
    ...     Run(file_id=0, length=1),
    ...     Run(file_id=None, length=2),
    ...     Run(file_id=1, length=3),
    ...     Run(file_id=None, length=4),
    ...     Run(file_id=2, length=5),
    ... ]))
    (Run(file_id=0, length=1), Run(file_id=2, length=2), Run(file_id=1, length=3), Run(file_id=2, length=3))
    >>> tuple(compact_blocks([
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


def calculate_checksum_after_block_compaction(lines: Iterable[str]) -> int:
    """
    >>> calculate_checksum_after_block_compaction(['12345'])
    60
    >>> calculate_checksum_after_block_compaction(['2333133121414131402'])
    1928
    """
    runs = parse_disk_map(next(iter(lines)))
    compacted_runs = compact_blocks(tuple(runs))
    return calculate_checksum(compacted_runs)


########################################################################################################################
# Part 2
########################################################################################################################

class RelocationIndex(NamedTuple):
    free_space_block_position: int
    free_space_length: int
    relocation_pointer: int

    def dereference(self, relocations: list[Optional[tuple[list[Run], int, int]]]) -> Optional[tuple[list[Run], int, int]]:
        relocation = relocations[self.relocation_pointer]
        if relocation is not None:
            assert (relocation[1] == self.free_space_block_position) and (relocation[2] == self.free_space_length)
        return relocation


class FileIndex(NamedTuple):
    file_id: int
    file_block_position: int
    relocatable_run_pointer: int

    def dereference(self, relocatable_runs: list[Union[Run, int]]) -> Run:
        relocatable_run = relocatable_runs[self.relocatable_run_pointer]
        assert isinstance(relocatable_run, Run) and (relocatable_run.file_id == self.file_id)
        return relocatable_run


def compact_files(runs: Sequence[Run]) -> Iterator[Run]:
    """
    Compact disk by relocating whole files (from highest ID) to free space blocks (from the left).

    We expect each file to have exactly one run.

    >>> tuple(compact_files([]))
    ()
    >>> tuple(compact_files([
    ...     Run(file_id=6, length=9),
    ... ]))
    (Run(file_id=6, length=9),)
    >>> tuple(compact_files([
    ...     Run(file_id=None, length=0),
    ...     Run(file_id=6, length=3),
    ...     Run(file_id=None, length=3),
    ... ]))
    (Run(file_id=6, length=3),)
    >>> tuple(compact_files([
    ...     Run(file_id=None, length=3),
    ...     Run(file_id=None, length=3),
    ...     Run(file_id=2, length=3),
    ...     Run(file_id=3, length=4),
    ...     Run(file_id=1, length=5),
    ... ]))
    (Run(file_id=3, length=4), Run(file_id=None, length=2), Run(file_id=2, length=3), Run(file_id=None, length=4), Run(file_id=1, length=5))

    >>> tuple(compact_files([
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
    (Run(file_id=0, length=2), Run(file_id=9, length=2), Run(file_id=2, length=1), Run(file_id=1, length=3), Run(file_id=7, length=3), Run(file_id=None, length=1), Run(file_id=4, length=2), Run(file_id=None, length=1), Run(file_id=3, length=3), Run(file_id=None, length=4), Run(file_id=5, length=4), Run(file_id=None, length=1), Run(file_id=6, length=4), Run(file_id=None, length=5), Run(file_id=8, length=4))
    """
    ####################
    # Phase one: index.
    ####################
    # List elements are: (i) a file run; or (ii) an index into `relocations`. (Since other data structures index into
    # `relocatable_runs`, we don't want relocations to shift indices around. And linked lists are kinda clunky in
    # Python. Thus, we use tombstones.)
    relocatable_runs: list[Union[Run, int]] = []
    # Tuple comprises: (i) a list of relocated file runs; (ii) starting block position for the remaining free space run;
    # and (iii) length of remaining free space run (which could be zero).
    relocations: list[Optional[tuple[list[Run], int, int]]] = []
    # List is sorted by starting block position.
    relocation_indices: list[RelocationIndex] = []
    # List is sorted by file ID.
    file_indices: list[FileIndex] = []
    num_file_runs = 0
    block_position = 0
    last_run_was_free_space = False
    for run in runs:
        if run.file_id is not None:
            # Handle file run.
            relocatable_run_pointer = len(relocatable_runs)
            relocatable_runs.append(run)
            file_index = FileIndex(run.file_id, block_position, relocatable_run_pointer)
            # The official inputs guarantee the file IDs monotonically increase, so this is only here to handle the
            # degenerate case where file IDs are encountered out of order.
            i = bisect_left(file_indices, file_index)
            # Ensure we don't have two runs for the same file.
            if i < len(file_indices):
                assert file_indices[i].file_id != run.file_id
            file_indices.insert(i, file_index)
            num_file_runs += 1
            last_run_was_free_space = False
        elif not last_run_was_free_space:
            # Handle free space run.
            relocation_pointer = len(relocations)
            relocatable_runs.append(relocation_pointer)
            relocations.append(([], block_position, run.length))
            relocation_indices.append(RelocationIndex(block_position, run.length, relocation_pointer))
            last_run_was_free_space = True
        else:
            # Handle follow-on free space run.
            relocation_pointer = len(relocations) - 1
            relocatable_runs.append(relocation_pointer)
            relocation = relocations[relocation_pointer]
            assert relocation is not None
            (relocated_runs, free_space_block_position, old_free_space_length) = relocation
            new_free_space_length = old_free_space_length + run.length
            relocations[relocation_pointer] = (relocated_runs, free_space_block_position, new_free_space_length)
            relocation_indices[relocation_pointer] = RelocationIndex(free_space_block_position, new_free_space_length, relocation_pointer)
        block_position += run.length
    assert len(relocatable_runs) == len(runs)
    assert len(relocation_indices) == len(relocations)
    assert len(file_indices) == num_file_runs

    #######################
    # Phase two: relocate.
    #######################
    # One might think we could be clever and try packing free space runs from the left by files with the highest IDs
    # that'll fit. But that's not the case.
    while file_indices:
        file_index = file_indices.pop()
        (file_id, file_block_position, relocatable_run_pointer) = file_index
        file_run = file_index.dereference(relocatable_runs)
        for (i, relocation_index) in enumerate(relocation_indices):
            (free_space_block_position, free_space_length, relocation_pointer) = relocation_index
            if free_space_block_position >= file_index.file_block_position:
                # We've exhausted all free space runs to the left of us. This file run cannot be relocated.
                break
            if free_space_length < file_run.length:
                # This free space run is too small.
                continue
            # We've found a suitable free space run. Relocate the file run to its new destination.
            relocation = relocation_index.dereference(relocations)
            assert relocation is not None
            relocated_runs = relocation[0]
            relocated_runs.append(file_run)
            free_space_block_position += file_run.length
            free_space_length -= file_run.length
            relocations[relocation_pointer] = (relocated_runs, free_space_block_position, free_space_length)
            relocation_indices[i] = RelocationIndex(free_space_block_position, free_space_length, relocation_pointer)
            # Tombstone the old source. First, either extend the preceding free space run or create a new one.
            if (relocatable_run_pointer > 0) and isinstance(tombstone_relocation_pointer := relocatable_runs[relocatable_run_pointer - 1], int):
                relocatable_runs[relocatable_run_pointer] = tombstone_relocation_pointer
                tombstone_relocation = relocations[tombstone_relocation_pointer]
                assert tombstone_relocation is not None
                (tombstone_relocated_runs, tombstone_free_space_block_position, old_tombstone_free_space_length) = tombstone_relocation
                new_tombstone_free_space_length = old_tombstone_free_space_length + file_run.length
                relocations[tombstone_relocation_pointer] = (tombstone_relocated_runs, tombstone_free_space_block_position, new_tombstone_free_space_length)
                tombstone_relocation_index = RelocationIndex(tombstone_free_space_block_position, old_tombstone_free_space_length, tombstone_relocation_pointer)
                j = bisect_left(relocation_indices, tombstone_relocation_index)
                assert relocation_indices[j] == tombstone_relocation_index
                tombstone_relocation_index = RelocationIndex(tombstone_free_space_block_position, new_tombstone_free_space_length, tombstone_relocation_pointer)
                relocation_indices[j] = tombstone_relocation_index
            else:
                tombstone_relocation_pointer = len(relocations)
                relocatable_runs[relocatable_run_pointer] = tombstone_relocation_pointer
                relocations.append(([], file_block_position, file_run.length))
                tombstone_relocation_index = RelocationIndex(file_block_position, file_run.length, tombstone_relocation_pointer)
                j = bisect_left(relocation_indices, tombstone_relocation_index)
                if j < len(relocation_indices):
                    assert relocation_indices[j].free_space_block_position != file_block_position
                relocation_indices.insert(j, tombstone_relocation_index)
            # Next, merge with following free space run, if possible. (These two steps could be simplified by always
            # creating a free space run, then doing merges on either side.)
            if (relocatable_run_pointer < len(relocatable_runs) - 1) and isinstance(subsumable_relocation_pointer := relocatable_runs[relocatable_run_pointer + 1], int):
                subsumable_relocation = relocations[subsumable_relocation_pointer]
                assert subsumable_relocation is not None
                (subsumable_relocated_runs, subsumable_free_space_block_position, subsumable_free_space_length) = subsumable_relocation
                if len(subsumable_relocated_runs) == 0:
                    relocatable_runs[relocatable_run_pointer + 1] = tombstone_relocation_pointer
                    relocations[subsumable_relocation_pointer] = None
                    subsumable_relocation_index = RelocationIndex(subsumable_free_space_block_position, subsumable_free_space_length, subsumable_relocation_pointer)
                    k = bisect_left(relocation_indices, subsumable_relocation_index)
                    assert relocation_indices[k] == subsumable_relocation_index
                    del relocation_indices[k]
                    tombstone_relocation = relocations[tombstone_relocation_pointer]
                    assert tombstone_relocation is not None
                    (tombstone_relocated_runs, tombstone_free_space_block_position, old_tombstone_free_space_length) = tombstone_relocation
                    new_tombstone_free_space_length = old_tombstone_free_space_length + subsumable_free_space_length
                    relocations[tombstone_relocation_pointer] = (tombstone_relocated_runs, tombstone_free_space_block_position, new_tombstone_free_space_length)
                    tombstone_relocation_index = RelocationIndex(tombstone_free_space_block_position, new_tombstone_free_space_length, tombstone_relocation_pointer)
                    relocation_indices[j] = tombstone_relocation_index
            break

    #####################
    # Phase three: emit.
    #####################
    num_file_runs_remaining = num_file_runs
    for relocatable_run in relocatable_runs:
        if isinstance(relocatable_run, Run):
            assert relocatable_run.file_id is not None
            yield relocatable_run
            num_file_runs_remaining -= 1
            continue
        relocation = relocations[relocatable_run]
        if relocation is None:
            continue
        (relocated_runs, _, free_space_length) = relocation
        for relocated_run in relocated_runs:
            assert relocated_run.file_id is not None
            yield relocated_run
            num_file_runs_remaining -= 1
        if free_space_length > 0:
            # Don't emit trailing free space runs.
            if num_file_runs_remaining <= 0:
                break
            yield Run(None, free_space_length)
        relocations[relocatable_run] = None


def calculate_checksum_after_file_compaction(lines: Iterable[str]) -> int:
    """
    >>> calculate_checksum_after_file_compaction(['2333133121414131402'])
    2858
    """
    runs = parse_disk_map(next(iter(lines)))
    compacted_runs = compact_files(tuple(runs))
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
        print(calculate_checksum_after_block_compaction(lines))
    elif args.part == 2:
        print(calculate_checksum_after_file_compaction(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
