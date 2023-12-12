#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
from itertools import chain, groupby
from math import factorial
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

REPORT_FORMAT_DELIMITER = ' '
DAMAGED_CONTIGUOUS_RUN_LENGTH_DELIMITER = ','


class ConditionRecord(Enum):
    OPERATIONAL = '.'
    DAMAGED = '#'
    UNKNOWN = '?'


class Spring(NamedTuple):
    condition_records: tuple[ConditionRecord, ...]
    damaged_contiguous_run_lengths: tuple[int, ...]

    @classmethod
    def from_line(cls, line: str) -> 'Spring':
        (raw_condition_records, raw_damaged_contiguous_run_lengths) = line.split(REPORT_FORMAT_DELIMITER)
        condition_records = tuple(ConditionRecord(char) for char in raw_condition_records)
        damaged_contiguous_run_lengths = tuple(int(number) for number in raw_damaged_contiguous_run_lengths.split(DAMAGED_CONTIGUOUS_RUN_LENGTH_DELIMITER))
        assert all(n > 0 for n in damaged_contiguous_run_lengths)
        assert sum(damaged_contiguous_run_lengths) <= len(condition_records)
        return Spring(condition_records, damaged_contiguous_run_lengths)

    def __str__(self) -> str:
        raw_condition_records = ''.join(condition_record.value for condition_record in self.condition_records)
        raw_damaged_contiguous_run_lengths = DAMAGED_CONTIGUOUS_RUN_LENGTH_DELIMITER.join(str(run_length) for run_length in self.damaged_contiguous_run_lengths)
        return f'{raw_condition_records}{REPORT_FORMAT_DELIMITER}{raw_damaged_contiguous_run_lengths}'

    def simplify(self) -> 'Spring':
        """
        >>> str(Spring.from_line('???.### 1,1,3').simplify())
        '??? 1,1'
        >>> str(Spring.from_line('.??..??...?##. 1,1,3').simplify())
        '??.?? 1,1'
        >>> str(Spring.from_line('?#?#?#?#?#?#?#? 1,3,1,6').simplify())
        '?#?#?#?#?#?#?#? 1,3,1,6'
        >>> str(Spring.from_line('????.#...#... 4,1,1').simplify())
        '???? 4'
        >>> str(Spring.from_line('????.######..#####. 1,6,5').simplify())
        '???? 1'
        >>> str(Spring.from_line('?###???????? 3,2,1').simplify())
        '?###???????? 3,2,1'

        With more analysis, the last example could be simplified further to '???????? 2,1'.

        >>> str(Spring.from_line('#..#?#?.?????#.# 1,1,2,5,1').simplify())
        '? -1'
        """
        # Collapse contiguous runs of operational condition reports; they're only useful as sentinels (to delimit
        # contiguous runs of damaged condition reports), so their run length is irrelevant.
        condition_records = list(chain.from_iterable(
            condition_records_run if condition_record != ConditionRecord.OPERATIONAL else [condition_record]
            for (condition_record, condition_records_run)
            in groupby(self.condition_records)
        ))
        damaged_contiguous_run_lengths = list(self.damaged_contiguous_run_lengths)

        while condition_records:
            in_run = bool(damaged_contiguous_run_lengths) and (damaged_contiguous_run_lengths[0] < 0)
            # Trim leading and trailing operational condition reports.
            if not in_run and condition_records[0] == ConditionRecord.OPERATIONAL:
                condition_records.pop(0)
                continue
            if condition_records[-1] == ConditionRecord.OPERATIONAL:
                condition_records.pop()
                continue
            # Trim leading and trailing damaged condition reports.
            if damaged_contiguous_run_lengths:
                if condition_records[0] == ConditionRecord.DAMAGED:
                    leading_damaged_contiguous_run_length = abs(damaged_contiguous_run_lengths[0])
                    if leading_damaged_contiguous_run_length > 1:
                        if not ((len(condition_records) >= leading_damaged_contiguous_run_length) and (condition_records[1] in {ConditionRecord.DAMAGED, ConditionRecord.UNKNOWN})):
                            break
                        condition_records.pop(0)
                        damaged_contiguous_run_lengths[0] = -(leading_damaged_contiguous_run_length - 1)
                        continue
                    elif leading_damaged_contiguous_run_length == 1:
                        if not (((len(condition_records) > 1) and (condition_records[1] in {ConditionRecord.OPERATIONAL, ConditionRecord.UNKNOWN})) or (len(condition_records) == 1)):
                            break
                        condition_records.pop(0)
                        condition_records.pop(0)
                        damaged_contiguous_run_lengths.pop(0)
                        continue
                if condition_records[-1] == ConditionRecord.DAMAGED:
                    trailing_damaged_contiguous_run_length = abs(damaged_contiguous_run_lengths[-1])
                    if len(condition_records) < trailing_damaged_contiguous_run_length:
                        break
                    if len(condition_records) > trailing_damaged_contiguous_run_length:
                        if condition_records[-(trailing_damaged_contiguous_run_length + 1)] not in {ConditionRecord.OPERATIONAL, ConditionRecord.UNKNOWN}:
                            break
                    if any(condition_records[i] not in {ConditionRecord.DAMAGED, ConditionRecord.UNKNOWN} for i in range(-2, -(trailing_damaged_contiguous_run_length + 1), -1)):
                        break
                    condition_records = condition_records[:-trailing_damaged_contiguous_run_length]
                    if condition_records:
                        condition_records.pop()
                    damaged_contiguous_run_lengths.pop()
                    continue
            # We've exhausted our simple optimisations! :)
            break

        return Spring(tuple(condition_records), tuple(damaged_contiguous_run_lengths))

    def count_arrangements(self) -> int:
        """
        >>> Spring.from_line('???.### 1,1,3').count_arrangements()
        1
        >>> Spring.from_line('.??..??...?##. 1,1,3').count_arrangements()
        4
        >>> Spring.from_line('?#?#?#?#?#?#?#? 1,3,1,6').count_arrangements()
        1
        >>> Spring.from_line('????.#...#... 4,1,1').count_arrangements()
        1
        >>> Spring.from_line('????.######..#####. 1,6,5').count_arrangements()
        4
        >>> Spring.from_line('?###???????? 3,2,1').count_arrangements()
        10

        >>> Spring.from_line('#????.#.#..?? 3,1,1,1').count_arrangements()
        3
        >>> Spring.from_line('?##?#.????#?#??#??? 3,1,2,2,5').count_arrangements()
        1
        >>> Spring.from_line('????????????????? 3,2,2,1,1').count_arrangements()
        126
        >>> Spring.from_line('..?????.?.?#?#?. 4,4').count_arrangements()
        4
        >>> Spring.from_line('???????????#??.????? 1,1,1,7,1,1').count_arrangements()
        30
        >>> Spring.from_line('.....??#??.?.???? 2,1').count_arrangements()
        11
        >>> Spring.from_line('????.????????????. 2,3,1,1,1').count_arrangements()
        106

        Thanks Doru. <3 <https://discord.com/channels/246075715714416641/1180276776858026086/1184203218268455012>

        >>> Spring.from_line('#..#?#?.?????#.# 1,1,2,5,1').count_arrangements()
        1

        >>> Spring.from_line('???.###????.###????.###????.###????.### 1,1,3,1,1,3,1,1,3,1,1,3,1,1,3').count_arrangements()
        1
        >>> Spring.from_line('.??..??...?##.?.??..??...?##.?.??..??...?##.?.??..??...?##.?.??..??...?##. 1,1,3,1,1,3,1,1,3,1,1,3,1,1,3').count_arrangements()
        16384
        >>> Spring.from_line('?#?#?#?#?#?#?#???#?#?#?#?#?#?#???#?#?#?#?#?#?#???#?#?#?#?#?#?#???#?#?#?#?#?#?#? 1,3,1,6,1,3,1,6,1,3,1,6,1,3,1,6,1,3,1,6').count_arrangements()
        1
        >>> Spring.from_line('????.#...#...?????.#...#...?????.#...#...?????.#...#...?????.#...#... 4,1,1,4,1,1,4,1,1,4,1,1,4,1,1').count_arrangements()
        16
        >>> Spring.from_line('????.######..#####.?????.######..#####.?????.######..#####.?????.######..#####.?????.######..#####. 1,6,5,1,6,5,1,6,5,1,6,5,1,6,5').count_arrangements()
        2500
        >>> Spring.from_line('?###??????????###??????????###??????????###??????????###???????? 3,2,1,3,2,1,3,2,1,3,2,1,3,2,1').count_arrangements()
        506250
        """
        simplified_spring = self.simplify()

        if not simplified_spring.condition_records:
            if simplified_spring.damaged_contiguous_run_lengths:
                # This arrangement is not possible, as we're not expecting any more contiguous runs of damaged condition
                # reports.
                return 0
            # There's one way to arrange… nothing.
            return 1

        if not simplified_spring.damaged_contiguous_run_lengths:
            if ConditionRecord.DAMAGED in simplified_spring.condition_records:
                # This arrangement is not possible, as we're not expecting any more damaged condition reports.
                return 0
            # There's exactly one possible arrangement: any unknown condition reports must be operational.
            return 1

        num_condition_records = len(simplified_spring.condition_records)
        if num_condition_records < sum(simplified_spring.damaged_contiguous_run_lengths) + (len(simplified_spring.damaged_contiguous_run_lengths) - 1):
            return 0

        if simplified_spring.condition_records[0] != ConditionRecord.UNKNOWN:
            # This only happens if the simplification process encountered an invalid arrangement
            return 0

        in_run = simplified_spring.damaged_contiguous_run_lengths[0] < 0

        if not in_run and all(condition_record == ConditionRecord.UNKNOWN for condition_record in simplified_spring.condition_records):
            if len(simplified_spring.damaged_contiguous_run_lengths) > 1:
                # Consider `????????????????? 3,2,2,1,1`. Minimally, we can represent the contiguous run lengths of
                # damaged condition reports as `###.##.##.#.#`. We have four unknown condition reports left over, which
                # we can distribute to any of the four operational condition reports or the ends.
                #
                # In other words, how can we pick six slots into groups of four, with replacement?
                n = len(simplified_spring.damaged_contiguous_run_lengths) + 1
                k = num_condition_records - sum(simplified_spring.damaged_contiguous_run_lengths) - (len(simplified_spring.damaged_contiguous_run_lengths) - 1)
                if n >= k >= 0:
                    return factorial(n + k - 1) // (factorial(k) * factorial(n - 1))

        if in_run:
            operational_arrangements = 0
        else:
            operational_arrangements = Spring(simplified_spring.condition_records[1:], simplified_spring.damaged_contiguous_run_lengths).count_arrangements()
        damaged_contiguous_run_length = abs(simplified_spring.damaged_contiguous_run_lengths[0])
        assert num_condition_records >= damaged_contiguous_run_length
        if num_condition_records > damaged_contiguous_run_length:
            if simplified_spring.condition_records[damaged_contiguous_run_length] not in {ConditionRecord.OPERATIONAL, ConditionRecord.UNKNOWN}:
                return operational_arrangements
        if any(simplified_spring.condition_records[i] not in {ConditionRecord.DAMAGED, ConditionRecord.UNKNOWN} for i in range(1, damaged_contiguous_run_length)):
            return operational_arrangements
        new_condition_records = simplified_spring.condition_records[damaged_contiguous_run_length:]
        if new_condition_records:
            new_condition_records = new_condition_records[1:]
        damaged_arrangements = Spring(new_condition_records, simplified_spring.damaged_contiguous_run_lengths[1:]).count_arrangements()
        return operational_arrangements + damaged_arrangements


def sum_arrangements(lines: Iterable[str]) -> int:
    """
    >>> sum_arrangements([
    ...     '???.### 1,1,3',
    ...     '.??..??...?##. 1,1,3',
    ...     '?#?#?#?#?#?#?#? 1,3,1,6',
    ...     '????.#...#... 4,1,1',
    ...     '????.######..#####. 1,6,5',
    ...     '?###???????? 3,2,1',
    ... ])
    21
    """
    springs = (Spring.from_line(line) for line in lines)
    return sum(map(lambda spring: spring.count_arrangements(), springs))


########################################################################################################################
# Part 2
########################################################################################################################

UNFOLD_FACTOR = 5


def unfold_lines(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        (raw_condition_records, raw_damaged_contiguous_run_lengths) = line.split(REPORT_FORMAT_DELIMITER)
        unfolded_condition_records = ConditionRecord.UNKNOWN.value.join([raw_condition_records] * UNFOLD_FACTOR)
        unfolded_damaged_contiguous_run_lengths = DAMAGED_CONTIGUOUS_RUN_LENGTH_DELIMITER.join([raw_damaged_contiguous_run_lengths] * UNFOLD_FACTOR)
        yield f'{unfolded_condition_records}{REPORT_FORMAT_DELIMITER}{unfolded_damaged_contiguous_run_lengths}'


def sum_unfolded_arrangements(lines: Iterable[str]) -> int:
    """
    >>> sum_unfolded_arrangements([
    ...     '???.### 1,1,3',
    ...     '.??..??...?##. 1,1,3',
    ...     '?#?#?#?#?#?#?#? 1,3,1,6',
    ...     '????.#...#... 4,1,1',
    ...     '????.######..#####. 1,6,5',
    ...     '?###???????? 3,2,1',
    ... ])
    525152
    """
    springs = (Spring.from_line(unfolded_line) for unfolded_line in unfold_lines(lines))
    return sum(map(lambda spring: spring.count_arrangements(), springs))


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
        print(sum_arrangements(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
