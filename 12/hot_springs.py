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
# Condition records
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

        >>> Spring.from_line('????#??.?????????? 2,4,2,1').count_arrangements()
        36
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

        if not in_run:
            leading_unknown_run_length = 0
            for (i, condition_record) in enumerate(simplified_spring.condition_records):
                if condition_record == ConditionRecord.UNKNOWN:
                    leading_unknown_run_length += 1
                    continue
                break
            should_continue = True
            requires_annoying_bounds_checks = False
            if leading_unknown_run_length < 2:
                should_continue = False
            if should_continue and (leading_unknown_run_length < num_condition_records):
                if simplified_spring.condition_records[leading_unknown_run_length] != ConditionRecord.OPERATIONAL:
                    assert simplified_spring.condition_records[leading_unknown_run_length] == ConditionRecord.DAMAGED
                    requires_annoying_bounds_checks = True
            if should_continue:
                remaining_condition_records = simplified_spring.condition_records[leading_unknown_run_length + (1 if not requires_annoying_bounds_checks else 0):]
                # This is the maximum sequence of contiguous run lengths of damaged condition reports that we can fit
                # within the leading contiguous run of unknown condition reports.
                #
                # Well, almost. If our leading contiguous run is terminated by a _damaged_ condition report, then this
                # is slightly _more_ than what we can fit.
                max_leading_damaged_contiguous_run_lengths: tuple[int, ...] = ()
                k = leading_unknown_run_length
                for (i, damaged_contiguous_run_length) in enumerate(simplified_spring.damaged_contiguous_run_lengths):
                    new_k = k - damaged_contiguous_run_length - (0 if i == 0 else 1)
                    if new_k < 0 and not requires_annoying_bounds_checks:
                        break
                    max_leading_damaged_contiguous_run_lengths += (damaged_contiguous_run_length,)
                    if new_k < 0:
                        break
                    k = new_k
                num_arrangements = 0
                for i in range(len(max_leading_damaged_contiguous_run_lengths) + 1):
                    leading_damaged_contiguous_run_lengths = max_leading_damaged_contiguous_run_lengths[:i]
                    trailing_damaged_contiguous_run_lengths = simplified_spring.damaged_contiguous_run_lengths[i:]
                    if not leading_damaged_contiguous_run_lengths:
                        factor = 1
                        num_new_arrangements = factor * Spring(remaining_condition_records, trailing_damaged_contiguous_run_lengths).count_arrangements()
                    elif len(leading_damaged_contiguous_run_lengths) == 1:
                        n = leading_unknown_run_length - leading_damaged_contiguous_run_lengths[0] + 1
                        if requires_annoying_bounds_checks:
                            # For a leading contiguous run of unknown condition reports terminated by a damaged
                            # condition report, we treat the last unknown condition report as an operational condition
                            # report that separates the leading contiguous run from the terminating damaged condition
                            # report.
                            n -= 1
                        if n >= 1:
                            factor = n
                            num_new_arrangements = factor * Spring(remaining_condition_records, trailing_damaged_contiguous_run_lengths).count_arrangements()
                        else:
                            # Example case: `?????#……… 9`.
                            assert requires_annoying_bounds_checks
                            num_new_arrangements = 0
                        if requires_annoying_bounds_checks:
                            run_remaining = -1 if n >= 1 else -max(1, leading_damaged_contiguous_run_lengths[0] - leading_unknown_run_length)
                            # We now try runs that're adjacent to the terminating damaged condition report.
                            for j in range(run_remaining, -leading_damaged_contiguous_run_lengths[0], -1):
                                adjusted_trailing_damaged_contiguous_run_lengths = (j,) + trailing_damaged_contiguous_run_lengths
                                num_new_arrangements += Spring(remaining_condition_records, adjusted_trailing_damaged_contiguous_run_lengths).count_arrangements()
                    else:
                        # Consider `????????????????? 3,2,2,1,1`. Minimally, we can represent the contiguous run lengths
                        # of damaged condition reports as `###.##.##.#.#`. We have four unknown condition reports left
                        # over, which we can distribute to any of the four operational condition reports or the ends.
                        #
                        # In other words, how can we pick six slots into groups of four, with replacement?
                        n = len(leading_damaged_contiguous_run_lengths) + 1
                        k = leading_unknown_run_length - sum(leading_damaged_contiguous_run_lengths) - (len(leading_damaged_contiguous_run_lengths) - 1)
                        if requires_annoying_bounds_checks:
                            k -= 1
                        if n > 0 and k >= 0:
                            factor = factorial(n + k - 1) // (factorial(k) * factorial(n - 1))
                            num_new_arrangements = factor * Spring(remaining_condition_records, trailing_damaged_contiguous_run_lengths).count_arrangements()
                        else:
                            # Example case: `?????#……… 3,2`.
                            assert requires_annoying_bounds_checks
                            num_new_arrangements = 0
                        if requires_annoying_bounds_checks:
                            available_run_length = leading_unknown_run_length - 1 - sum(leading_damaged_contiguous_run_lengths[:-1]) - (len(leading_damaged_contiguous_run_lengths[:-1]) - 1)
                            run_remaining = -1 if available_run_length >= leading_damaged_contiguous_run_lengths[-1] else -max(1, leading_damaged_contiguous_run_lengths[-1] - available_run_length)
                            # We now count scenarios where the last run is adjacent to the terminating damaged condition
                            # report.
                            for j in range(run_remaining, -leading_damaged_contiguous_run_lengths[-1], -1):
                                factor = Spring((ConditionRecord.UNKNOWN,) * (leading_unknown_run_length - leading_damaged_contiguous_run_lengths[-1] - 1 - j), leading_damaged_contiguous_run_lengths[:-1]).count_arrangements()
                                adjusted_trailing_damaged_contiguous_run_lengths = (j,) + trailing_damaged_contiguous_run_lengths
                                num_new_arrangements += factor * Spring(remaining_condition_records, adjusted_trailing_damaged_contiguous_run_lengths).count_arrangements()
                    num_arrangements += num_new_arrangements
                return num_arrangements

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


########################################################################################################################
# Part 1
########################################################################################################################

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
    elif args.part == 2:
        print(sum_unfolded_arrangements(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
