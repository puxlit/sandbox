#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
import operator
import re
from typing import Callable, NamedTuple, Union


########################################################################################################################
# Part 1
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
    condition: Callable[[PartRatings], bool]
    action: Union[bool, str]

    @classmethod
    def from_string(cls, string: str) -> 'Rule':
        match = RULE_PATTERN.fullmatch(string)
        if not match:
            raise ValueError(f'Invalid rule: {string!r}')
        (raw_a, raw_op, raw_b, raw_action) = match.groups()
        if raw_a is raw_op is raw_b is None:
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

            def condition(part_ratings: PartRatings) -> bool:
                return op(a_getter(part_ratings), b)
        action: Union[bool, str] = (
            True if raw_action == ACCEPT_ACTION else
            False if raw_action == REJECT_ACTION else
            raw_action
        )
        return Rule(condition, action)


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
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
