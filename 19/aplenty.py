#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from math import prod
import operator
import re
from typing import Callable, NamedTuple, Optional, Union


########################################################################################################################
# Workflows and part ratings
########################################################################################################################

PART_RATINGS_PATTERN = re.compile(r'^{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}$')


class PartRatings(NamedTuple):
    x: int
    m: int
    a: int
    s: int

    @classmethod
    def from_line(cls, line: str) -> 'PartRatings':
        match = PART_RATINGS_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Invalid part ratings: {line!r}')
        return PartRatings(*(int(score) for score in match.groups()))


RULE_PATTERN = re.compile(r'(?:([amsx])([<>])(\d+):)?([AR]|[a-z]+)')
LT_OP = '<'
GT_OP = '>'
ACCEPT_ACTION = 'A'
REJECT_ACTION = 'R'


class Rule(NamedTuple):
    category_comparison_threshold: Optional[tuple[str, str, int]]
    condition: Callable[[PartRatings], bool]
    action: Union[bool, str]

    @classmethod
    def from_string(cls, string: str) -> 'Rule':
        match = RULE_PATTERN.fullmatch(string)
        if not match:
            raise ValueError(f'Invalid rule: {string!r}')
        (raw_a, raw_op, raw_b, raw_action) = match.groups()
        if raw_a is raw_op is raw_b is None:
            category_comparison_threshold = None

            def condition(part_ratings: PartRatings) -> bool:
                return True
        else:
            a_getter = operator.attrgetter(raw_a)
            if raw_op == LT_OP:
                op = operator.lt
            elif raw_op == GT_OP:
                op = operator.gt
            else:
                raise ValueError(f'Invalid rule (unexpected operator): {string!r}')
            b = int(raw_b)
            category_comparison_threshold = (raw_a, raw_op, b)

            def condition(part_ratings: PartRatings) -> bool:
                return op(a_getter(part_ratings), b)
        action: Union[bool, str] = (
            True if raw_action == ACCEPT_ACTION else
            False if raw_action == REJECT_ACTION else
            raw_action
        )
        return Rule(category_comparison_threshold, condition, action)


WORKFLOW_PATTERN = re.compile(r'^([a-z]+){([^}]+)}$')
RULE_DELIMITER = ','


class Workflow(NamedTuple):
    name: str
    rules: tuple[Rule, ...]

    @classmethod
    def from_line(cls, line: str) -> 'Workflow':
        match = WORKFLOW_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Invalid workflow: {line!r}')
        (name, raw_rules) = match.groups()
        rules = tuple(Rule.from_string(raw_rule) for raw_rule in raw_rules.split(RULE_DELIMITER))
        return Workflow(name, rules)


ENTRY_WORKFLOW_NAME = 'in'


def parse_workflows(lines: Iterator[str]) -> dict[str, Workflow]:
    workflows: dict[str, Workflow] = {}
    forward_declared_workflows: set[str] = set()
    for line in lines:
        if not line:
            break
        workflow = Workflow.from_line(line)
        if workflow.name in workflows:
            raise ValueError(f'Workflow {workflows[workflow.name]!r} redefined as {workflow!r}')
        if workflow.name in forward_declared_workflows:
            forward_declared_workflows.remove(workflow.name)
        for rule in workflow.rules:
            if isinstance(rule.action, str):
                if rule.action == workflow.name:
                    raise ValueError(f'Workflow {workflow!r} contains self-referential rule')
                if rule.action not in workflows:
                    forward_declared_workflows.add(rule.action)
        workflows[workflow.name] = workflow
    if ENTRY_WORKFLOW_NAME not in workflows:
        raise ValueError(f'Entry workflow {ENTRY_WORKFLOW_NAME!r} not defined')
    if forward_declared_workflows:
        raise ValueError(f'The following workflows were referenced in rules but never defined: {forward_declared_workflows!r}')
    return workflows


########################################################################################################################
# Part 1
########################################################################################################################

def is_part_accepted(part_ratings: PartRatings, workflows: dict[str, Workflow]):
    applied_workflows: set[str] = set()
    workflow = workflows[ENTRY_WORKFLOW_NAME]
    while True:
        if workflow.name in applied_workflows:
            raise ValueError(f'Cycle detected when processing {part_ratings!r}; '
                             f'revisiting workflow {workflow.name!r} '
                             f'after already visiting workflows {applied_workflows!r}')
        applied_workflows.add(workflow.name)
        has_matched_rule = False
        for rule in workflow.rules:
            if rule.condition(part_ratings):
                if isinstance(rule.action, bool):
                    return rule.action
                workflow = workflows[rule.action]
                has_matched_rule = True
                break
        if not has_matched_rule:
            raise ValueError(f'Matched no rules when processing {part_ratings!r} '
                             f'with workflow {workflow!r}; already visited workflows {applied_workflows!r}')


def sum_accepted_parts_ratings(lines: Iterable[str]) -> int:
    """
    >>> sum_accepted_parts_ratings([
    ...     'px{a<2006:qkq,m>2090:A,rfg}',
    ...     'pv{a>1716:R,A}',
    ...     'lnx{m>1548:A,A}',
    ...     'rfg{s<537:gd,x>2440:R,A}',
    ...     'qs{s>3448:A,lnx}',
    ...     'qkq{x<1416:A,crn}',
    ...     'crn{x>2662:A,R}',
    ...     'in{s<1351:px,qqz}',
    ...     'qqz{s>2770:qs,m<1801:hdj,R}',
    ...     'gd{a>3333:R,R}',
    ...     'hdj{m>838:A,pv}',
    ...     '',
    ...     '{x=787,m=2655,a=1222,s=2876}',
    ...     '{x=1679,m=44,a=2067,s=496}',
    ...     '{x=2036,m=264,a=79,s=2244}',
    ...     '{x=2461,m=1339,a=466,s=291}',
    ...     '{x=2127,m=1623,a=2188,s=1013}',
    ... ])
    19114
    """
    lines_iter = iter(lines)
    workflows = parse_workflows(lines_iter)
    parts_ratings = (PartRatings.from_line(line) for line in lines_iter)
    return sum(sum(part_ratings) for part_ratings in parts_ratings if is_part_accepted(part_ratings, workflows))


########################################################################################################################
# Part 2
########################################################################################################################

class Range(NamedTuple):
    min_inclusive: int
    max_inclusive: int


class PartRatingsRanges(NamedTuple):
    x: tuple[Range, ...]
    m: tuple[Range, ...]
    a: tuple[Range, ...]
    s: tuple[Range, ...]

    def split(self, category: str, comparison: str, threshold: int) -> tuple[Optional['PartRatingsRanges'], Optional['PartRatingsRanges']]:
        ranges = operator.attrgetter(category)(self)
        assert comparison in {LT_OP, GT_OP}
        if comparison == LT_OP:
            # We'll split the affected ranges into what's less than or equal to some threshold, and what's greater than
            # that threshold. If the comparison is less than, then after adjusting the threshold, the matching half is
            # the smaller ranges. If the comparison is greater than, then the matching half is the larger ranges.
            threshold -= 1
        smaller_ranges: list[Range] = []
        larger_ranges: list[Range] = []
        for range_ in ranges:
            (min_inclusive, max_inclusive) = range_
            if max_inclusive <= threshold:
                smaller_ranges.append(range_)
            elif min_inclusive <= threshold < max_inclusive:
                smaller_ranges.append(Range(min_inclusive, threshold))
                larger_ranges.append(Range(threshold + 1, max_inclusive))
            else:
                assert threshold < min_inclusive
                larger_ranges.append(range_)
        smaller_part_ratings_ranges = None if not smaller_ranges else self._replace(**{category: tuple(smaller_ranges)})
        larger_part_ratings_ranges = None if not larger_ranges else self._replace(**{category: tuple(larger_ranges)})
        if comparison == LT_OP:
            return (smaller_part_ratings_ranges, larger_part_ratings_ranges)
        elif comparison == GT_OP:
            return (larger_part_ratings_ranges, smaller_part_ratings_ranges)
        else:
            raise ValueError(f'Unexpected comparison: {comparison!r}')

    def count_distinct_combinations(self) -> int:
        return prod(sum((max_inclusive - min_inclusive + 1) for (min_inclusive, max_inclusive) in ranges) for ranges in self)


def count_distinct_accepted_combinations(lines: Iterable[str]) -> int:
    """
    >>> count_distinct_accepted_combinations([
    ...     'px{a<2006:qkq,m>2090:A,rfg}',
    ...     'pv{a>1716:R,A}',
    ...     'lnx{m>1548:A,A}',
    ...     'rfg{s<537:gd,x>2440:R,A}',
    ...     'qs{s>3448:A,lnx}',
    ...     'qkq{x<1416:A,crn}',
    ...     'crn{x>2662:A,R}',
    ...     'in{s<1351:px,qqz}',
    ...     'qqz{s>2770:qs,m<1801:hdj,R}',
    ...     'gd{a>3333:R,R}',
    ...     'hdj{m>838:A,pv}',
    ...     '',
    ...     '{x=787,m=2655,a=1222,s=2876}',
    ...     '{x=1679,m=44,a=2067,s=496}',
    ...     '{x=2036,m=264,a=79,s=2244}',
    ...     '{x=2461,m=1339,a=466,s=291}',
    ...     '{x=2127,m=1623,a=2188,s=1013}',
    ... ])
    167409079868000
    """
    workflows = parse_workflows(iter(lines))
    permissible_part_ratings_ranges = PartRatingsRanges((Range(1, 4000),), (Range(1, 4000),), (Range(1, 4000),), (Range(1, 4000),))
    unresolved_combinations: list[tuple[PartRatingsRanges, Workflow]] = [
        (permissible_part_ratings_ranges, workflows[ENTRY_WORKFLOW_NAME]),
    ]
    total_distinct_combinations = permissible_part_ratings_ranges.count_distinct_combinations()
    distinct_accepted_combinations = 0
    distinct_rejected_combinations = 0
    while unresolved_combinations:
        (part_ratings_ranges, workflow) = unresolved_combinations.pop(0)
        unmatched_part_ratings_ranges: Optional[PartRatingsRanges] = part_ratings_ranges
        for rule in workflow.rules:
            if unmatched_part_ratings_ranges is None:
                break
            matched_part_ratings_ranges: Optional[PartRatingsRanges] = None
            if rule.category_comparison_threshold is None:
                # Unconditional match.
                matched_part_ratings_ranges = unmatched_part_ratings_ranges
                unmatched_part_ratings_ranges = None
            else:
                (matched_part_ratings_ranges, unmatched_part_ratings_ranges) = unmatched_part_ratings_ranges.split(*rule.category_comparison_threshold)
            if matched_part_ratings_ranges is not None:
                if isinstance(rule.action, bool):
                    if rule.action:
                        distinct_accepted_combinations += matched_part_ratings_ranges.count_distinct_combinations()
                    else:
                        distinct_rejected_combinations += matched_part_ratings_ranges.count_distinct_combinations()
                else:
                    unresolved_combinations.append((matched_part_ratings_ranges, workflows[rule.action]))
        if unmatched_part_ratings_ranges is not None:
            raise ValueError(f'{unmatched_part_ratings_ranges!r} matched no rules '
                             f'when processing {part_ratings_ranges!r} with workflow {workflow!r}')
    assert distinct_accepted_combinations + distinct_rejected_combinations == total_distinct_combinations
    return distinct_accepted_combinations


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
        print(sum_accepted_parts_ratings(lines))
    elif args.part == 2:
        print(count_distinct_accepted_combinations(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
