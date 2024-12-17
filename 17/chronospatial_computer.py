#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import IntEnum
from typing import NamedTuple, Optional

from typing_extensions import assert_never


########################################################################################################################
# Computer
########################################################################################################################

REGISTER_A_HEADER = 'Register A: '
REGISTER_B_HEADER = 'Register B: '
REGISTER_C_HEADER = 'Register C: '
PROGRAM_HEADER = 'Program: '
PROGRAM_OPCODE_SEPARATOR = ','

OUTPUT_SEPARATOR = ','


class Instruction(IntEnum):
    ADV = 0
    BXL = 1
    BST = 2
    JNZ = 3
    BXC = 4
    OUT = 5
    BDV = 6
    CDV = 7


class State(NamedTuple):
    a: int
    b: int
    c: int
    ip: int
    halted: bool
    program: tuple[Instruction, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'State':
        lines_iter = iter(lines)
        assert (line := next(lines_iter)).startswith(REGISTER_A_HEADER)
        a = int(line[len(REGISTER_A_HEADER):])
        assert (line := next(lines_iter)).startswith(REGISTER_B_HEADER)
        b = int(line[len(REGISTER_B_HEADER):])
        assert (line := next(lines_iter)).startswith(REGISTER_C_HEADER)
        c = int(line[len(REGISTER_C_HEADER):])
        assert next(lines_iter) == ''
        assert (line := next(lines_iter)).startswith(PROGRAM_HEADER)
        program = tuple(Instruction(int(opcode)) for opcode in line[len(PROGRAM_HEADER):].split(PROGRAM_OPCODE_SEPARATOR))
        return State(a, b, c, 0, False, program)

    def execute(self) -> tuple['State', Optional[int]]:
        # Halt if we try to read an OOB opcode.
        if not 0 <= self.ip < len(self.program):
            return (self._replace(halted=True), None)

        instruction = self.program[self.ip]
        next_ip = self.ip + 2
        if instruction == Instruction.ADV:
            result = self.a // (2 ** self.combo_operand)
            return (self._replace(a=result, ip=next_ip), None)
        elif instruction == Instruction.BXL:
            result = self.b ^ self.literal_operand
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.BST:
            result = self.combo_operand % 8
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.JNZ:
            result = next_ip if (self.a == 0) else self.literal_operand
            return (self._replace(ip=result), None)
        elif instruction == Instruction.BXC:
            result = self.b ^ self.c
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.OUT:
            output = self.combo_operand % 8
            return (self._replace(ip=next_ip), output)
        elif instruction == Instruction.BDV:
            result = self.a // (2 ** self.combo_operand)
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.CDV:
            result = self.a // (2 ** self.combo_operand)
            return (self._replace(c=result, ip=next_ip), None)
        assert_never(instruction)

    @property
    def literal_operand(self) -> int:
        return self.program[self.ip + 1].value

    @property
    def combo_operand(self) -> int:
        literal_operand = self.literal_operand
        assert 0 <= literal_operand < 7
        if literal_operand == 4:
            return self.a
        elif literal_operand == 5:
            return self.b
        elif literal_operand == 6:
            return self.c
        else:
            return literal_operand


def execute_until_halt(state: State) -> Iterator[int]:
    while not state.halted:
        (state, output) = state.execute()
        if output is not None:
            yield output


########################################################################################################################
# Part 1
########################################################################################################################

def run_program(lines: Iterable[str]) -> str:
    """
    >>> print(run_program([
    ...     'Register A: 729',
    ...     'Register B: 0',
    ...     'Register C: 0',
    ...     '',
    ...     'Program: 0,1,5,4,3,0',
    ... ]))
    4,6,3,5,6,3,5,2,1,0
    """
    initial_state = State.from_lines(lines)
    return OUTPUT_SEPARATOR.join(str(output) for output in execute_until_halt(initial_state))


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
        print(run_program(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
