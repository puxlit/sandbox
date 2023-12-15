#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
import re
from typing import NamedTuple, Optional


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_hash(string: bytes) -> int:
    """
    >>> calculate_hash(b'HASH')
    52
    >>> calculate_hash(b'rn=1')
    30
    >>> calculate_hash(b'cm-')
    253
    >>> calculate_hash(b'qp=3')
    97
    >>> calculate_hash(b'cm=2')
    47
    >>> calculate_hash(b'qp-')
    14
    >>> calculate_hash(b'pc=4')
    180
    >>> calculate_hash(b'ot=9')
    9
    >>> calculate_hash(b'ab=5')
    197
    >>> calculate_hash(b'pc-')
    48
    >>> calculate_hash(b'pc=6')
    214
    >>> calculate_hash(b'ot=7')
    231
    """
    value = 0
    for byte in string:
        value = ((value + byte) * 17) % 256
    return value


def extract_steps(lines: Iterator[bytes]) -> Iterator[bytes]:
    initialization_sequence = next(lines)
    for step in initialization_sequence.split(b','):
        yield step


def calculate_verification_number(lines: Iterable[bytes]) -> int:
    """
    >>> calculate_verification_number([b'rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7'])
    1320
    """
    return sum(calculate_hash(step) for step in extract_steps(iter(lines)))


########################################################################################################################
# Part 2
########################################################################################################################

# What are you doing…
STEP_PATTERN = re.compile(br'^([a-z]+)([-=])([1-9])?$')


class Operation(Enum):
    REMOVE_LENS = b'-'
    ADD_OR_REPLACE_LENS = b'='


class Step(NamedTuple):
    label: bytes
    box_number: int
    operation: Operation
    focal_length: Optional[int]

    @classmethod
    def from_string(cls, string: bytes) -> 'Step':
        match = STEP_PATTERN.fullmatch(string)
        if not match:
            raise ValueError(f'Step {string!r} does not match expected pattern /{STEP_PATTERN.pattern.decode()}/')
        label = match.group(1)
        box_number = calculate_hash(label)
        assert 0 <= box_number <= 255
        operation = Operation(match.group(2))
        if operation == Operation.ADD_OR_REPLACE_LENS:
            focal_length = int(match.group(3))
            assert 1 <= focal_length <= 9
        else:
            focal_length = None
        return Step(label, box_number, operation, focal_length)


def run_manual_arrangement_procedure(steps: Iterable[Step]) -> tuple[dict[bytes, int], ...]:
    boxes: list[dict[bytes, int]] = [{} for _ in range(256)]
    for step in steps:
        box = boxes[step.box_number]
        if step.operation == Operation.REMOVE_LENS:
            if step.label in box:
                del box[step.label]
        elif step.operation == Operation.ADD_OR_REPLACE_LENS:
            assert step.focal_length is not None
            # Since Python 3.7, dictionaries are guaranteed to preserve insertion order.
            box[step.label] = step.focal_length
        else:
            raise ValueError(f'Unknown step operation: {step.operation}')
    return tuple(boxes)


def sum_focusing_power(lines: Iterable[bytes]) -> int:
    """
    >>> sum_focusing_power([b'rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7'])
    145
    """
    steps = (Step.from_string(string) for string in extract_steps(iter(lines)))
    boxes = run_manual_arrangement_procedure(steps)
    return sum(
        ((box_number + 1) * (slot_number + 1) * focal_length)
        for (box_number, lens_slots) in enumerate(boxes)
        for (slot_number, focal_length) in enumerate(lens_slots.values())
    )


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=argparse.FileType('rb'))
    args = parser.parse_args()
    lines = (line.rstrip(b'\n') for line in args.input)

    if args.part == 1:
        print(calculate_verification_number(lines))
    elif args.part == 2:
        print(sum_focusing_power(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
