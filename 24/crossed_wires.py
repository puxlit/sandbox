#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import ChainMap, deque
from collections.abc import Iterable, Iterator, Sized
from enum import Enum
from itertools import chain
import logging
import re
from typing import NamedTuple, Optional

from typing_extensions import assert_never


########################################################################################################################
# Logger
########################################################################################################################

logger = logging.getLogger(__name__)


def pluralise(collection: Sized, singular_form: str) -> str:
    affix = 's' if len(collection) != 1 else ''
    return f'{len(collection)} {singular_form}{affix}'


########################################################################################################################
# Even more graphs
########################################################################################################################

INITIAL_WIRE_VALUE_CONFIG_PATTERN = re.compile(r'^(\w{3}): ([01])$')
GATE_CONNECTION_CONFIG_PATTERN = re.compile(r'^(\w{3}) (AND|OR|XOR) (\w{3}) -> (\w{3})$')

INPUT_WORD_ONE_WIRE_PREFIX = 'x'
INPUT_WORD_TWO_WIRE_PREFIX = 'y'
OUTPUT_WORD_WIRE_PREFIX = 'z'


class Gate(Enum):
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'


class Device(NamedTuple):
    initial_wire_values: dict[str, bool]
    gate_connections: dict[str, tuple[str, str, Gate]]
    input_words_length: int
    output_word_length: int

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Device':
        lines_iter = iter(lines)

        initial_wire_values: dict[str, bool] = {}
        for line in lines_iter:
            if (match := INITIAL_WIRE_VALUE_CONFIG_PATTERN.fullmatch(line)) is None:
                break
            initial_wire_values[match.group(1)] = bool(int(match.group(2)))

        assert (input_words_length := len(initial_wire_values) // 2) > 0
        assert all(((
            input_word_one_wire(i) in initial_wire_values
        ) and (
            input_word_two_wire(i) in initial_wire_values
        )) for i in range(input_words_length))

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

        assert (output_word_length := sum(is_output_word_wire(wire) for wire in gate_connections.keys())) > 0
        assert all((
            output_word_wire(i) in gate_connections
        ) for i in range(output_word_length))

        return Device(initial_wire_values, gate_connections, input_words_length, output_word_length)

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


def word_wire(prefix: str, bit_index: int) -> str:
    assert len(prefix) == 1
    assert 0 <= bit_index < 100
    return f'{prefix}{bit_index:02}'


def is_input_word_wire(wire: str) -> bool:
    return wire.startswith(INPUT_WORD_ONE_WIRE_PREFIX) or wire.startswith(INPUT_WORD_TWO_WIRE_PREFIX)


def input_word_one_wire(bit_index: int) -> str:
    return word_wire(INPUT_WORD_ONE_WIRE_PREFIX, bit_index)


def input_word_two_wire(bit_index: int) -> str:
    return word_wire(INPUT_WORD_TWO_WIRE_PREFIX, bit_index)


def is_output_word_wire(wire: str) -> bool:
    return wire.startswith(OUTPUT_WORD_WIRE_PREFIX)


def output_word_wire(bit_index: int) -> str:
    return word_wire(OUTPUT_WORD_WIRE_PREFIX, bit_index)


def scratch_wires() -> Iterator[str]:
    for i in range(256):
        yield f'_{i:02x}'


########################################################################################################################
# Part 1
########################################################################################################################

def read_output_word(wire_values: dict[str, bool], output_word_length: int) -> int:
    output_word = int(wire_values[output_word_wire(output_word_length - 1)])
    for i in range(output_word_length - 2, -1, -1):
        output_word <<= 1
        output_word += int(wire_values[output_word_wire(i)])
    return output_word


def simulate_and_read_output_word(lines: Iterable[str]) -> int:
    """
    >>> simulate_and_read_output_word([
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
    >>> simulate_and_read_output_word([
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
    return read_output_word(final_wire_values, device.output_word_length)


########################################################################################################################
# Part 2
########################################################################################################################

SWAPPED_OUTPUT_WIRE_DELIMITER = ','


def generate_and_gate_connections(input_words_length: int) -> dict[str, tuple[str, str, Gate]]:
    assert input_words_length > 0
    gate_connections: dict[str, tuple[str, str, Gate]] = {}
    for i in range(input_words_length):
        gate_connections[output_word_wire(i)] = (input_word_one_wire(i), input_word_two_wire(i), Gate.AND)
    return gate_connections


def generate_ripple_carry_adder_gate_connections(input_words_length: int) -> dict[str, tuple[str, str, Gate]]:
    assert input_words_length > 0
    gate_connections: dict[str, tuple[str, str, Gate]] = {}
    scratch_wires_iter = iter(scratch_wires())
    # Generate half adder.
    sum_wire = output_word_wire(0)
    gate_connections[sum_wire] = (input_word_one_wire(0), input_word_two_wire(0), Gate.XOR)
    carry_wire = output_word_wire(1) if (input_words_length == 1) else next(scratch_wires_iter)
    gate_connections[carry_wire] = (input_word_one_wire(0), input_word_two_wire(0), Gate.AND)
    # Generate full adders.
    for i in range(1, input_words_length):
        u_wire = next(scratch_wires_iter)
        gate_connections[u_wire] = (input_word_one_wire(i), input_word_two_wire(i), Gate.XOR)
        sum_wire = output_word_wire(i)
        gate_connections[sum_wire] = (u_wire, carry_wire, Gate.XOR)
        v_wire = next(scratch_wires_iter)
        gate_connections[v_wire] = (input_word_one_wire(i), input_word_two_wire(i), Gate.AND)
        w_wire = next(scratch_wires_iter)
        gate_connections[w_wire] = (u_wire, carry_wire, Gate.AND)
        carry_wire = output_word_wire(i + 1) if (i + 1 == input_words_length) else next(scratch_wires_iter)
        gate_connections[carry_wire] = (v_wire, w_wire, Gate.OR)
    return gate_connections


def describe_gate_connection(input_wires: frozenset[str], gate: Gate, output_wire: Optional[str] = None) -> str:
    (input_wire_a, input_wire_b) = input_wires
    if input_wire_a > input_wire_b:
        (input_wire_a, input_wire_b) = (input_wire_b, input_wire_a)
    if output_wire is None:
        output_wire = '???'
    return f'[{input_wire_a} {gate.value} {input_wire_b} → {output_wire}]'


def postfix_traversal_inverse_gate_connections(gate_connections: dict[str, tuple[str, str, Gate]], output_word_wires: set[str], met_wire_dependencies: set[str]) -> dict[tuple[frozenset[str], Gate], str]:
    inverse_gate_connections: dict[tuple[frozenset[str], Gate], str] = {}
    # We're going to mutate this map.
    gate_connections = gate_connections.copy()
    stack: deque[tuple[frozenset[str], Gate, str]] = deque()
    for output_wire in sorted(output_word_wires):
        (input_wire_a, input_wire_b, gate) = gate_connections[output_wire]
        stack.append((frozenset((input_wire_a, input_wire_b)), gate, output_wire))
    while stack:
        (input_wires, gate, output_wire) = stack[0]
        unknown_input_wires = input_wires - met_wire_dependencies
        if unknown_input_wires:
            for output_wire in sorted(unknown_input_wires, reverse=True):
                (input_wire_a, input_wire_b, gate) = gate_connections[output_wire]
                stack.appendleft((frozenset((input_wire_a, input_wire_b)), gate, output_wire))
        else:
            inverse_gate_connections[(input_wires, gate)] = output_wire
            del gate_connections[output_wire]
            met_wire_dependencies.add(output_wire)
            stack.popleft()
    assert len(gate_connections) == 0
    return inverse_gate_connections


def identify_swapped_pairs_of_output_wires(gate_connections: dict[str, tuple[str, str, Gate]], reference_gate_connections: dict[str, tuple[str, str, Gate]], input_words_length: int, output_word_length: int) -> tuple[tuple[str, str], ...]:
    """
    >>> device = Device.from_lines([
    ...     'x00: 0',
    ...     'x01: 1',
    ...     'x02: 0',
    ...     'x03: 1',
    ...     'x04: 0',
    ...     'x05: 1',
    ...     'y00: 0',
    ...     'y01: 0',
    ...     'y02: 1',
    ...     'y03: 1',
    ...     'y04: 0',
    ...     'y05: 1',
    ...     '',
    ...     'x00 AND y00 -> z05',
    ...     'x01 AND y01 -> z02',
    ...     'x02 AND y02 -> z01',
    ...     'x03 AND y03 -> z03',
    ...     'x04 AND y04 -> z04',
    ...     'x05 AND y05 -> z00',
    ... ])
    >>> reference_and_gate_connections = generate_and_gate_connections(device.input_words_length)
    >>> identify_swapped_pairs_of_output_wires(device.gate_connections, reference_and_gate_connections, device.input_words_length, device.output_word_length)
    (('z00', 'z05'), ('z01', 'z02'))
    """
    assert len(gate_connections) == len(reference_gate_connections)
    #####################
    # Graph isomorphisms
    #####################
    # We're going to compare `gate_connections` against `reference_gate_connections` (which we assume accurately
    # reflects the expected structure of `gate_connections`) to identify swapped pairs of output wires. To verify that
    # the graphs can become isomorphic, we're going to build a mapping of wire labels from `gate_connections` to
    # `reference_gate_connections`. To start, we expect wires with the prefixes `x`, `y`, and `z` to be common.
    #
    # `committed_isomorphism` is a map from `gate_connections` wires to `reference_gate_connections` wires.
    committed_isomorphism: dict[str, str] = {wire: wire for wire in chain.from_iterable((
        (input_word_one_wire(i) for i in range(input_words_length)),
        (input_word_two_wire(i) for i in range(input_words_length)),
        (output_word_wire(i) for i in range(output_word_length))
    ))}
    inverse_committed_isomorphism = committed_isomorphism.copy()
    # `tentative_isomorphism` is a speculative map from `gate_connections` wires to `reference_gate_connections` wires.
    tentative_isomorphism: dict[str, str] = {}
    inverse_tentative_isomorphism: dict[str, str] = {}
    # `isomorphism` let's us check both the speculative and certain map from `gate_connections` wires to
    # `reference_gate_connections` wires.
    isomorphism = ChainMap(tentative_isomorphism, committed_isomorphism)
    inverse_isomorphism = ChainMap(inverse_tentative_isomorphism, inverse_committed_isomorphism)
    ###################
    # Gate connections
    ###################
    # For simplicity, we're going to assume that no two gates of the same type share the same input wires.
    #
    # `inverse_gate_connections` maps input wires (+ gate) to output wires. Its initial ordering follows post-order
    # traversal (where output word wires are roots and input word wires are leaves), so we can make a lot of progress
    # per iteration.
    inverse_gate_connections: dict[tuple[frozenset[str], Gate], str] = postfix_traversal_inverse_gate_connections(gate_connections, set(output_word_wire(i) for i in range(output_word_length)), set(committed_isomorphism.keys()))
    assert len(inverse_gate_connections) == len(gate_connections)
    inverse_reference_gate_connections: dict[tuple[frozenset[str], Gate], str] = {
        (frozenset((input_wire_a, input_wire_b)), gate): output_wire
        for (output_wire, (input_wire_a, input_wire_b, gate)) in reference_gate_connections.items()
    }
    assert len(inverse_reference_gate_connections) == len(reference_gate_connections)
    ########################
    # Deduce valid mappings
    ########################
    # Keep track of the last gate on which we choked, to ensure we're making progress. (This is very rudimentary, and
    # will fail to detect us getting stuck on a cycle of gates.)
    last_problematic_gate: Optional[tuple[frozenset[str], Gate]] = None
    # If we haven't made progress after two loops, we're probably stuck.
    grace_loops = 2
    swapped_output_wires: set[str] = set()
    swapped_pairs_of_output_wires: list[tuple[str, str]] = []
    pass_counter = 0
    while inverse_gate_connections:
        assert grace_loops > 0
        grace_loops -= 1
        pass_counter += 1
        resolved_inverse_gate_connections: set[tuple[frozenset[str], Gate]] = set()
        logger.info(f'  - beginning pass #{pass_counter} (with {pluralise(inverse_gate_connections, "gate connection")} and {pluralise(committed_isomorphism, "committed mapping")})')
        for ((input_wires, gate), output_wire) in inverse_gate_connections.items():
            if not input_wires.issubset(isomorphism.keys()):
                # We don't know enough mappings to process this gate yet.
                unknown_input_wires = input_wires - isomorphism.keys()
                logger.info(f"      - {describe_gate_connection(input_wires, gate, output_wire)}: skipping because we don't know about the {pluralise(unknown_input_wires, 'input wire')} {' and '.join(sorted(unknown_input_wires))}")
                continue
            if ((input_wires, gate) == last_problematic_gate) and (grace_loops == 1):
                # We flagged this gate as problematic last iteration, so we must be near the end of this iteration.
                # Restart early so we can do a second pass and hopefully convert some tentative mappings into committed
                # mappings.
                logger.info(f'      - {describe_gate_connection(input_wires, gate, output_wire)}: encountered problematic gate connection from last pass; restarting early')
                break
            reference_input_wires = frozenset(isomorphism[wire] for wire in input_wires)
            if (reference_input_wires, gate) not in inverse_reference_gate_connections:
                # We've found an inconsistency: based on the mappings we know, we can't find the equivalent reference
                # gate. We must've learned a bad mapping. Move the problematic gate connection to the end of the queue,
                # flush everything we're unsure about, and start again.
                logger.info(f'      - {describe_gate_connection(input_wires, gate, output_wire)}: 🚨 no equivalent reference {describe_gate_connection(reference_input_wires, gate)}; discarding {pluralise(tentative_isomorphism, "tentative mapping")} and restarting')
                if output_wire in committed_isomorphism:
                    (reference_input_wire_a, reference_input_wire_b, reference_gate) = reference_gate_connections[committed_isomorphism[output_wire]]
                    if (reference_gate == gate) and (reference_input_wire_a in inverse_isomorphism) and (reference_input_wire_b in inverse_isomorphism):
                        problematic_wires = input_wires ^ {inverse_isomorphism[reference_input_wire_a], inverse_isomorphism[reference_input_wire_b]}
                        if len(problematic_wires) == 2:
                            output_wire = (set(problematic_wires) & input_wires).pop()
                            correct_output_wire = (set(problematic_wires) - {output_wire}).pop()
                            logger.info(f'          - will try swapping output wires {output_wire} and {correct_output_wire}')
                            assert (output_wire not in swapped_output_wires) and (correct_output_wire not in swapped_output_wires)
                            swapped_output_wires.update((output_wire, correct_output_wire))
                            swapped_pairs_of_output_wires.append((output_wire, correct_output_wire) if (output_wire < correct_output_wire) else (correct_output_wire, output_wire))
                            (input_wire_a, input_wire_b, gate) = gate_connections[output_wire]
                            input_wires = frozenset((input_wire_a, input_wire_b))
                            (other_input_wire_a, other_input_wire_b, other_gate) = gate_connections[correct_output_wire]
                            other_input_wires = frozenset((other_input_wire_a, other_input_wire_b))
                            gate_connections[correct_output_wire] = (input_wire_a, input_wire_b, gate)
                            inverse_gate_connections[(input_wires, gate)] = correct_output_wire
                            gate_connections[output_wire] = (other_input_wire_a, other_input_wire_b, other_gate)
                            inverse_gate_connections[(other_input_wires, other_gate)] = output_wire
                            last_problematic_gate = None
                            grace_loops = 2
                            tentative_isomorphism.clear()
                            inverse_tentative_isomorphism.clear()
                            break
                del inverse_gate_connections[(input_wires, gate)]
                inverse_gate_connections[(input_wires, gate)] = output_wire
                if (input_wires, gate) != last_problematic_gate:
                    last_problematic_gate = (input_wires, gate)
                    grace_loops = 2
                tentative_isomorphism.clear()
                inverse_tentative_isomorphism.clear()
                break
            reference_output_wire = inverse_reference_gate_connections[(reference_input_wires, gate)]
            if output_wire not in isomorphism:
                if reference_output_wire in inverse_isomorphism:
                    # We've found an inconsistency: we're about to have two wires map to the same reference wire. We
                    # must've learned a bad mapping. Move the problematic gate connection to the end of the queue, flush
                    # everything we're unsure about, and start again.
                    logger.info(f'      - {describe_gate_connection(input_wires, gate, output_wire)}: 🚨 was about to tentatively learn mapping {output_wire} ↔ {reference_output_wire}, but already learned {inverse_isomorphism[reference_output_wire]} ↔ {reference_output_wire}; discarding {pluralise(tentative_isomorphism, "tentative mapping")} and restarting')
                    if reference_output_wire in inverse_committed_isomorphism:
                        correct_output_wire = inverse_committed_isomorphism[reference_output_wire]
                        logger.info(f'          - will try swapping output wires {output_wire} and {correct_output_wire}')
                        assert (output_wire not in swapped_output_wires) and (correct_output_wire not in swapped_output_wires)
                        swapped_output_wires.update((output_wire, correct_output_wire))
                        swapped_pairs_of_output_wires.append((output_wire, correct_output_wire) if (output_wire < correct_output_wire) else (correct_output_wire, output_wire))
                        (input_wire_a, input_wire_b) = input_wires
                        (other_input_wire_a, other_input_wire_b, other_gate) = gate_connections[correct_output_wire]
                        other_input_wires = frozenset((other_input_wire_a, other_input_wire_b))
                        gate_connections[correct_output_wire] = (input_wire_a, input_wire_b, gate)
                        inverse_gate_connections[(input_wires, gate)] = correct_output_wire
                        gate_connections[output_wire] = (other_input_wire_a, other_input_wire_b, other_gate)
                        inverse_gate_connections[(other_input_wires, other_gate)] = output_wire
                        last_problematic_gate = None
                        grace_loops = 2
                    else:
                        del inverse_gate_connections[(input_wires, gate)]
                        inverse_gate_connections[(input_wires, gate)] = output_wire
                        if (input_wires, gate) != last_problematic_gate:
                            last_problematic_gate = (input_wires, gate)
                            grace_loops = 2
                    tentative_isomorphism.clear()
                    inverse_tentative_isomorphism.clear()
                    break
                else:
                    # Tentatively learn this mapping.
                    logger.info(f'      - {describe_gate_connection(input_wires, gate, output_wire)}: tentatively learning mapping {output_wire} ↔ {reference_output_wire}')
                    tentative_isomorphism[output_wire] = reference_output_wire
                    inverse_tentative_isomorphism[reference_output_wire] = output_wire
            elif reference_output_wire != isomorphism[output_wire]:
                # We've found an inconsistency: we didn't get the reference output wire we expected. If we're confident,
                # we can attempt a swap. Otherwise, we'll move the problematic gate connection to the end of the queue.
                # In any case, we'll need to flush everything we're unsure about and start again.
                logger.info(f'      - {describe_gate_connection(input_wires, gate, output_wire)}: 🚨 mismatch with equivalent reference {describe_gate_connection(reference_input_wires, gate, reference_output_wire)}; discarding {pluralise(tentative_isomorphism, "tentative mapping")} and restarting')
                if reference_output_wire in inverse_committed_isomorphism:
                    correct_output_wire = inverse_committed_isomorphism[reference_output_wire]
                    logger.info(f'          - will try swapping output wires {output_wire} and {correct_output_wire}')
                    assert (output_wire not in swapped_output_wires) and (correct_output_wire not in swapped_output_wires)
                    swapped_output_wires.update((output_wire, correct_output_wire))
                    swapped_pairs_of_output_wires.append((output_wire, correct_output_wire) if (output_wire < correct_output_wire) else (correct_output_wire, output_wire))
                    (input_wire_a, input_wire_b) = input_wires
                    (other_input_wire_a, other_input_wire_b, other_gate) = gate_connections[correct_output_wire]
                    other_input_wires = frozenset((other_input_wire_a, other_input_wire_b))
                    gate_connections[correct_output_wire] = (input_wire_a, input_wire_b, gate)
                    inverse_gate_connections[(input_wires, gate)] = correct_output_wire
                    gate_connections[output_wire] = (other_input_wire_a, other_input_wire_b, other_gate)
                    inverse_gate_connections[(other_input_wires, other_gate)] = output_wire
                    last_problematic_gate = None
                    grace_loops = 2
                else:
                    del inverse_gate_connections[(input_wires, gate)]
                    inverse_gate_connections[(input_wires, gate)] = output_wire
                    if (input_wires, gate) != last_problematic_gate:
                        last_problematic_gate = (input_wires, gate)
                        grace_loops = 2
                tentative_isomorphism.clear()
                inverse_tentative_isomorphism.clear()
                break
            else:
                logger.info(f'      - {describe_gate_connection(input_wires, gate, output_wire)}: matched equivalent reference {describe_gate_connection(reference_input_wires, gate, reference_output_wire)}')
            # If our output wire is a committed mapping, we can walk backwards and commit those mappings.
            if output_wire in committed_isomorphism:
                output_wires = deque([output_wire])
                while output_wires:
                    output_wire = output_wires.popleft()
                    if output_wire in tentative_isomorphism:
                        logger.info(f'          - committing mapping {output_wire} ↔ {reference_output_wire}')
                        reference_output_wire = tentative_isomorphism[output_wire]
                        committed_isomorphism[output_wire] = reference_output_wire
                        inverse_committed_isomorphism[reference_output_wire] = output_wire
                        del tentative_isomorphism[output_wire]
                        del inverse_tentative_isomorphism[reference_output_wire]
                    (input_wire_a, input_wire_b, gate) = gate_connections[output_wire]
                    input_wires = frozenset((input_wire_a, input_wire_b))
                    if (input_wires, gate) in inverse_gate_connections:
                        resolved_inverse_gate_connections.add((input_wires, gate))
                    for input_wire in input_wires:
                        if not is_input_word_wire(input_wire):
                            output_wires.append(input_wire)
        for resolved_inverse_gate_connection in resolved_inverse_gate_connections:
            del inverse_gate_connections[resolved_inverse_gate_connection]
            (input_wires, gate) = resolved_inverse_gate_connection
            reference_input_wires = frozenset(isomorphism[wire] for wire in input_wires)
            del inverse_reference_gate_connections[(reference_input_wires, gate)]
            grace_loops = 2
    return tuple(sorted(swapped_pairs_of_output_wires))


def combine_swapped_pairs_of_output_wires(lines: Iterable[str]) -> str:
    device = Device.from_lines(lines)
    reference_rca_gate_connections = generate_ripple_carry_adder_gate_connections(device.input_words_length)
    swapped_pairs_of_output_wires = identify_swapped_pairs_of_output_wires(device.gate_connections, reference_rca_gate_connections, device.input_words_length, device.output_word_length)
    assert len(swapped_pairs_of_output_wires) == 4
    return SWAPPED_OUTPUT_WIRE_DELIMITER.join(sorted(wire for pair in swapped_pairs_of_output_wires for wire in pair))


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=argparse.FileType('rt'))
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    lines = (line.rstrip('\n') for line in args.input)

    if args.part == 1:
        print(simulate_and_read_output_word(lines))
    elif args.part == 2:
        print(combine_swapped_pairs_of_output_wires(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
