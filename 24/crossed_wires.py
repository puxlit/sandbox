#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
import re
from typing import NamedTuple

from typing_extensions import assert_never


########################################################################################################################
# Even more graphs
########################################################################################################################

INITIAL_WIRE_VALUE_CONFIG_PATTERN = re.compile(r'^(\w{3}): ([01])$')
GATE_CONNECTION_CONFIG_PATTERN = re.compile(r'^(\w{3}) (AND|OR|XOR) (\w{3}) -> (\w{3})$')


class Gate(Enum):
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'


class Device(NamedTuple):
    initial_wire_values: dict[str, bool]
    gate_connections: dict[str, tuple[str, str, Gate]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Device':
        lines_iter = iter(lines)

        initial_wire_values: dict[str, bool] = {}
        for line in lines_iter:
            if (match := INITIAL_WIRE_VALUE_CONFIG_PATTERN.fullmatch(line)) is None:
                break
            initial_wire_values[match.group(1)] = bool(int(match.group(2)))

        unordered_gate_connections: dict[str, tuple[str, str, Gate]] = {}
        for line in lines_iter:
            assert (match := GATE_CONNECTION_CONFIG_PATTERN.fullmatch(line)) is not None
            unordered_gate_connections[match.group(4)] = (match.group(1), match.group(3), Gate(match.group(2)))

        gate_connections: dict[str, tuple[str, str, Gate]] = {}
        met_wire_dependencies = set(initial_wire_values.keys())
        while unordered_gate_connections:
            new_met_wire_dependencies: set[str] = set()
            for (output_wire, (input_wire_a, input_wire_b, gate)) in unordered_gate_connections.items():
                if (input_wire_a in met_wire_dependencies) and (input_wire_b in met_wire_dependencies):
                    gate_connections[output_wire] = (input_wire_a, input_wire_b, gate)
                    met_wire_dependencies.add(output_wire)
                    new_met_wire_dependencies.add(output_wire)
            # Ensure we're making progress.
            assert new_met_wire_dependencies
            for new_met_wire_dependency in new_met_wire_dependencies:
                del unordered_gate_connections[new_met_wire_dependency]

        return Device(initial_wire_values, gate_connections)

    def simulate(self) -> dict[str, bool]:
        """
        >>> sorted(Device.from_lines([
        ...     'x00: 1',
        ...     'x01: 1',
        ...     'x02: 1',
        ...     'y00: 0',
        ...     'y01: 1',
        ...     'y02: 0',
        ...     '',
        ...     'x00 AND y00 -> z00',
        ...     'x01 XOR y01 -> z01',
        ...     'x02 OR y02 -> z02',
        ... ]).simulate().items())
        [('x00', True), ('x01', True), ('x02', True), ('y00', False), ('y01', True), ('y02', False), ('z00', False), ('z01', False), ('z02', True)]
        >>> sorted(Device.from_lines([
        ...     'x00: 1',
        ...     'x01: 0',
        ...     'x02: 1',
        ...     'x03: 1',
        ...     'x04: 0',
        ...     'y00: 1',
        ...     'y01: 1',
        ...     'y02: 1',
        ...     'y03: 1',
        ...     'y04: 1',
        ...     '',
        ...     'ntg XOR fgs -> mjb',
        ...     'y02 OR x01 -> tnw',
        ...     'kwq OR kpj -> z05',
        ...     'x00 OR x03 -> fst',
        ...     'tgd XOR rvg -> z01',
        ...     'vdt OR tnw -> bfw',
        ...     'bfw AND frj -> z10',
        ...     'ffh OR nrd -> bqk',
        ...     'y00 AND y03 -> djm',
        ...     'y03 OR y00 -> psh',
        ...     'bqk OR frj -> z08',
        ...     'tnw OR fst -> frj',
        ...     'gnj AND tgd -> z11',
        ...     'bfw XOR mjb -> z00',
        ...     'x03 OR x00 -> vdt',
        ...     'gnj AND wpb -> z02',
        ...     'x04 AND y00 -> kjc',
        ...     'djm OR pbm -> qhw',
        ...     'nrd AND vdt -> hwm',
        ...     'kjc AND fst -> rvg',
        ...     'y04 OR y02 -> fgs',
        ...     'y01 AND x02 -> pbm',
        ...     'ntg OR kjc -> kwq',
        ...     'psh XOR fgs -> tgd',
        ...     'qhw XOR tgd -> z09',
        ...     'pbm OR djm -> kpj',
        ...     'x03 XOR y03 -> ffh',
        ...     'x00 XOR y04 -> ntg',
        ...     'bfw OR bqk -> z06',
        ...     'nrd XOR fgs -> wpb',
        ...     'frj XOR qhw -> z04',
        ...     'bqk OR frj -> z07',
        ...     'y03 OR x01 -> nrd',
        ...     'hwm AND bqk -> z03',
        ...     'tgd XOR rvg -> z12',
        ...     'tnw OR pbm -> gnj',
        ... ]).simulate().items())
        [('bfw', True), ('bqk', True), ('djm', True), ('ffh', False), ('fgs', True), ('frj', True), ('fst', True), ('gnj', True), ('hwm', True), ('kjc', False), ('kpj', True), ('kwq', False), ('mjb', True), ('nrd', True), ('ntg', False), ('pbm', True), ('psh', True), ('qhw', True), ('rvg', False), ('tgd', False), ('tnw', True), ('vdt', True), ('wpb', False), ('x00', True), ('x01', False), ('x02', True), ('x03', True), ('x04', False), ('y00', True), ('y01', True), ('y02', True), ('y03', True), ('y04', True), ('z00', False), ('z01', False), ('z02', False), ('z03', True), ('z04', False), ('z05', True), ('z06', True), ('z07', True), ('z08', True), ('z09', True), ('z10', True), ('z11', False), ('z12', False)]
        """
        wire_values = self.initial_wire_values.copy()
        for (output_wire, (input_wire_a, input_wire_b, gate)) in self.gate_connections.items():
            input_wire_a_value = wire_values[input_wire_a]
            input_wire_b_value = wire_values[input_wire_b]
            if gate == Gate.AND:
                output_wire_value = input_wire_a_value and input_wire_b_value
            elif gate == Gate.OR:
                output_wire_value = input_wire_a_value or input_wire_b_value
            elif gate == Gate.XOR:
                output_wire_value = input_wire_a_value != input_wire_b_value
            else:
                assert_never(gate)
            wire_values[output_wire] = output_wire_value
        return wire_values


def read_z_wires_value(wire_values: dict[str, bool]) -> int:
    assert (num_z_wires := sum(wire.startswith('z') for wire in wire_values.keys())) > 0
    z_wires_value = int(wire_values[f'z{num_z_wires - 1:02}'])
    for i in range(num_z_wires - 2, -1, -1):
        z_wires_value <<= 1
        z_wires_value += int(wire_values[f'z{i:02}'])
    return z_wires_value


########################################################################################################################
# Part 1
########################################################################################################################

def simulate_and_read_z_wires_value(lines: Iterable[str]) -> int:
    """
    >>> simulate_and_read_z_wires_value([
    ...     'x00: 1',
    ...     'x01: 1',
    ...     'x02: 1',
    ...     'y00: 0',
    ...     'y01: 1',
    ...     'y02: 0',
    ...     '',
    ...     'x00 AND y00 -> z00',
    ...     'x01 XOR y01 -> z01',
    ...     'x02 OR y02 -> z02',
    ... ])
    4
    >>> simulate_and_read_z_wires_value([
    ...     'x00: 1',
    ...     'x01: 0',
    ...     'x02: 1',
    ...     'x03: 1',
    ...     'x04: 0',
    ...     'y00: 1',
    ...     'y01: 1',
    ...     'y02: 1',
    ...     'y03: 1',
    ...     'y04: 1',
    ...     '',
    ...     'ntg XOR fgs -> mjb',
    ...     'y02 OR x01 -> tnw',
    ...     'kwq OR kpj -> z05',
    ...     'x00 OR x03 -> fst',
    ...     'tgd XOR rvg -> z01',
    ...     'vdt OR tnw -> bfw',
    ...     'bfw AND frj -> z10',
    ...     'ffh OR nrd -> bqk',
    ...     'y00 AND y03 -> djm',
    ...     'y03 OR y00 -> psh',
    ...     'bqk OR frj -> z08',
    ...     'tnw OR fst -> frj',
    ...     'gnj AND tgd -> z11',
    ...     'bfw XOR mjb -> z00',
    ...     'x03 OR x00 -> vdt',
    ...     'gnj AND wpb -> z02',
    ...     'x04 AND y00 -> kjc',
    ...     'djm OR pbm -> qhw',
    ...     'nrd AND vdt -> hwm',
    ...     'kjc AND fst -> rvg',
    ...     'y04 OR y02 -> fgs',
    ...     'y01 AND x02 -> pbm',
    ...     'ntg OR kjc -> kwq',
    ...     'psh XOR fgs -> tgd',
    ...     'qhw XOR tgd -> z09',
    ...     'pbm OR djm -> kpj',
    ...     'x03 XOR y03 -> ffh',
    ...     'x00 XOR y04 -> ntg',
    ...     'bfw OR bqk -> z06',
    ...     'nrd XOR fgs -> wpb',
    ...     'frj XOR qhw -> z04',
    ...     'bqk OR frj -> z07',
    ...     'y03 OR x01 -> nrd',
    ...     'hwm AND bqk -> z03',
    ...     'tgd XOR rvg -> z12',
    ...     'tnw OR pbm -> gnj',
    ... ])
    2024
    """
    device = Device.from_lines(lines)
    final_wire_values = device.simulate()
    return read_z_wires_value(final_wire_values)


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
        print(simulate_and_read_z_wires_value(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
