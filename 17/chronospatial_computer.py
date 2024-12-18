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

COMBO_OPERAND_REGISTER_A = 4
COMBO_OPERAND_REGISTER_B = 5
COMBO_OPERAND_REGISTER_C = 6


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

    @classmethod
    def from_lines(cls, lines: tuple[str, str, str]) -> 'State':
        (register_a_line, register_b_line, register_c_line) = lines
        assert register_a_line.startswith(REGISTER_A_HEADER)
        a = int(register_a_line[len(REGISTER_A_HEADER):])
        assert register_b_line.startswith(REGISTER_B_HEADER)
        b = int(register_b_line[len(REGISTER_B_HEADER):])
        assert register_c_line.startswith(REGISTER_C_HEADER)
        c = int(register_c_line[len(REGISTER_C_HEADER):])
        return State(a, b, c, 0, False)

    def execute(self, program: tuple[Instruction, ...]) -> tuple['State', Optional[int]]:
        """
        >>> State(a=0, b=0, c=9, ip=0, halted=False).execute(tuple(Instruction(opcode) for opcode in (2, 6)))
        (State(a=0, b=1, c=9, ip=2, halted=False), None)
        >>> State(a=0, b=29, c=0, ip=0, halted=False).execute(tuple(Instruction(opcode) for opcode in (1, 7)))
        (State(a=0, b=26, c=0, ip=2, halted=False), None)
        >>> State(a=0, b=2024, c=43690, ip=0, halted=False).execute(tuple(Instruction(opcode) for opcode in (4, 0)))
        (State(a=0, b=44354, c=43690, ip=2, halted=False), None)
        """
        # Halt if we try to read an OOB opcode.
        if not 0 <= self.ip < len(program):
            return (self._replace(halted=True), None)

        instruction = program[self.ip]
        next_ip = self.ip + 2
        if instruction == Instruction.ADV:
            result = self.a // (2 ** self.combo_operand(program))
            return (self._replace(a=result, ip=next_ip), None)
        elif instruction == Instruction.BXL:
            result = self.b ^ self.literal_operand(program)
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.BST:
            result = self.combo_operand(program) % 8
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.JNZ:
            result = next_ip if (self.a == 0) else self.literal_operand(program)
            return (self._replace(ip=result), None)
        elif instruction == Instruction.BXC:
            result = self.b ^ self.c
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.OUT:
            output = self.combo_operand(program) % 8
            return (self._replace(ip=next_ip), output)
        elif instruction == Instruction.BDV:
            result = self.a // (2 ** self.combo_operand(program))
            return (self._replace(b=result, ip=next_ip), None)
        elif instruction == Instruction.CDV:
            result = self.a // (2 ** self.combo_operand(program))
            return (self._replace(c=result, ip=next_ip), None)
        assert_never(instruction)

    def literal_operand(self, program: tuple[Instruction, ...]) -> int:
        return program[self.ip + 1].value

    def combo_operand(self, program: tuple[Instruction, ...]) -> int:
        literal_operand = self.literal_operand(program)
        assert 0 <= literal_operand < 7
        if literal_operand == COMBO_OPERAND_REGISTER_A:
            return self.a
        elif literal_operand == COMBO_OPERAND_REGISTER_B:
            return self.b
        elif literal_operand == COMBO_OPERAND_REGISTER_C:
            return self.c
        else:
            return literal_operand


def parse_state_and_program(lines: Iterable[str]) -> tuple[State, tuple[Instruction, ...]]:
    lines_iter = iter(lines)
    state = State.from_lines((next(lines_iter), next(lines_iter), next(lines_iter)))
    assert next(lines_iter) == ''
    assert (line := next(lines_iter)).startswith(PROGRAM_HEADER)
    program = tuple(Instruction(int(opcode)) for opcode in line[len(PROGRAM_HEADER):].split(PROGRAM_OPCODE_SEPARATOR))
    return (state, program)


def execute_until_halt_or_cycle(state: State, program: tuple[Instruction, ...]) -> Iterator[Optional[int]]:
    witnessed_states: set[State] = {state}
    while not state.halted:
        (state, output) = state.execute(program)
        if state in witnessed_states:
            yield None
        witnessed_states.add(state)
        if output is not None:
            yield output


def explain(program: tuple[Instruction, ...]) -> Iterator[str]:
    """
    >>> for line in explain(tuple(Instruction(opcode) for opcode in (0, 3, 5, 4, 3, 0))):
    ...     print(line)
    1. a >>= 3
    2. print(a & 0b111)
    3. if a ≠ 0, jump to #1
    """
    assert len(program) % 2 == 0
    counter_width = len(str(len(program) // 2))
    combo_operands = [0, 1, 2, 3, 'a', 'b', 'c']
    for (i, ip) in enumerate(range(0, len(program), 2)):
        counter = f'{(i + 1):{counter_width}}'
        instruction = program[ip]
        literal_operand = program[ip + 1].value
        if instruction == Instruction.ADV:
            yield f'{counter}. a >>= {combo_operands[literal_operand]}'
        elif instruction == Instruction.BXL:
            yield f'{counter}. b ^= {literal_operand}'
        elif instruction == Instruction.BST:
            yield f'{counter}. b = {combo_operands[literal_operand]} & 0b111'
        elif instruction == Instruction.JNZ:
            assert literal_operand % 2 == 0
            yield f'{counter}. if a ≠ 0, jump to #{(literal_operand // 2) + 1}'
        elif instruction == Instruction.BXC:
            yield f'{counter}. b ^= c'
        elif instruction == Instruction.OUT:
            yield f'{counter}. print({combo_operands[literal_operand]} & 0b111)'
        elif instruction == Instruction.BDV:
            yield f'{counter}. b = a >> {combo_operands[literal_operand]}'
        elif instruction == Instruction.CDV:
            yield f'{counter}. c = a >> {combo_operands[literal_operand]}'
        else:
            assert_never(instruction)


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
    (initial_state, program) = parse_state_and_program(lines)
    outputs: list[int] = []
    for output in execute_until_halt_or_cycle(initial_state, program):
        assert output is not None
        outputs.append(output)
    return OUTPUT_SEPARATOR.join(str(output) for output in outputs)


########################################################################################################################
# Part 2
########################################################################################################################

def assert_registers_b_and_c_are_scratch(program: tuple[Instruction, ...]) -> None:
    b_initialised = False
    c_initialised = False
    for ip in range(0, len(program), 2):
        instruction = program[ip]
        operand = program[ip + 1].value
        # We can only analyse sequential instructions.
        assert instruction != Instruction.JNZ
        if (instruction == Instruction.ADV) or (instruction == Instruction.OUT):
            if operand == COMBO_OPERAND_REGISTER_B:
                assert b_initialised
            elif operand == COMBO_OPERAND_REGISTER_C:
                assert c_initialised
        elif instruction == Instruction.BXL:
            assert b_initialised
        elif (instruction == Instruction.BST) or (instruction == Instruction.BDV):
            if operand == COMBO_OPERAND_REGISTER_B:
                assert b_initialised
            elif operand == COMBO_OPERAND_REGISTER_C:
                assert c_initialised
            b_initialised = True
        elif instruction == Instruction.BXC:
            assert b_initialised and c_initialised
        elif instruction == Instruction.CDV:
            if operand == COMBO_OPERAND_REGISTER_B:
                assert b_initialised
            elif operand == COMBO_OPERAND_REGISTER_C:
                assert c_initialised
            c_initialised = True
        else:
            assert_never(instruction)


def find_lowest_quine_inducing_register_a_value(lines: Iterable[str]) -> int:
    """
    >>> find_lowest_quine_inducing_register_a_value([
    ...     'Register A: 2024',
    ...     'Register B: 0',
    ...     'Register C: 0',
    ...     '',
    ...     'Program: 0,3,5,4,3,0',
    ... ])
    117440
    """
    (corrupted_initial_state, program) = parse_state_and_program(lines)
    expected_outputs = tuple(instruction.value for instruction in program)

    # Validate program.
    #
    #   - Expect the program to end with `jnz $0x0`. Expect no other `jnz` instructions.
    #   - Expect registers B and C to be initialised before they're used.
    #   - Expect the program to contain an `out %a`, `out %b`, or `out %c` instruction. Expect no other `out`
    #     instructions.
    assert len(program) % 2 == 0
    assert program[-2:] == (Instruction.JNZ, Instruction(0))
    assert_registers_b_and_c_are_scratch(program[:-2])
    out_instruction_found = False
    for ip in range(0, len(program), 2):
        if program[ip] == Instruction.OUT:
            assert not out_instruction_found
            out_instruction_found = True
            operand = program[ip + 1].value
            assert operand in (COMBO_OPERAND_REGISTER_A, COMBO_OPERAND_REGISTER_B, COMBO_OPERAND_REGISTER_C)
    assert out_instruction_found

    # Because we know the final instruction before halting is `jnz $0x0`, we know register A ends up as zero. We don't
    # know what registers B and C end up as.
    #
    # For trivial programs, we can work backwards. Consider the example program below.
    #
    #   1. a >>= 3               # Step (ii) : shift those three bits onto register A. If this is the last iteration
    #                                          (when executing forwards) and the final expected output is zero, then the
    #                                          next lowest value for register A would be 0b1000.
    #   2. print(a & 0b111)      # Step (i)  : learn the last three bits of register A from the next expected output.
    #   3. if a ≠ 0, jump to #1
    #
    # However, for our actual input, dependencies on higher bits complicate matters.
    #
    #   1. b = a & 0b111
    #   2. b ^= 3
    #   3. c = a >> b
    #   4. b ^= c                # Step (iii): uh-oh, we need to XOR by some unknown value. Looking further up, we see
    #                                          this unknown value is derived from the last three bits of register A and
    #                                          some other bits that might be further high up.
    #   5. b ^= 3                # Step (ii) : XOR by known value; this is a reversable operation.
    #   6. a >>= 3
    #   7. print(b & 0b111)      # Step (i)  : learn the last three bits of register B from the next expected output.
    #   8. if a ≠ 0, jump to #1
    #
    # Consequently, a constrained brute force search is the easiest way to solve this.
    def next_lowest_register_a_value(program: tuple[Instruction, ...], expected_outputs: tuple[int, ...]) -> Iterator[int]:
        assert len(expected_outputs) > 0
        if len(expected_outputs) == 1:
            for i in range(8):
                if tuple(execute_until_halt_or_cycle(corrupted_initial_state._replace(a=i), program)) == expected_outputs:
                    yield i
            return
        for a in next_lowest_register_a_value(program, expected_outputs[1:]):
            a <<= 3
            for i in range(8):
                if tuple(execute_until_halt_or_cycle(corrupted_initial_state._replace(a=(a + i)), program)) == expected_outputs:
                    yield a + i
    a = next(next_lowest_register_a_value(program, expected_outputs))

    # Finally, let's verify our answer.
    uncorrupted_initial_state = corrupted_initial_state._replace(a=a)
    assert tuple(execute_until_halt_or_cycle(uncorrupted_initial_state, program)) == expected_outputs

    return a


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
    elif args.part == 2:
        print(find_lowest_quine_inducing_register_a_value(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
