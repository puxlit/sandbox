#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import Counter
from collections.abc import Iterable
from itertools import chain, count
import re
from typing import Callable, Optional, Union


########################################################################################################################
# Part 1
########################################################################################################################

FlipFlopModuleState = bool
ConjunctionModuleState = tuple[tuple[str, Optional[bool]], ...]  # I can't be bothered whipping up a hashable frozen dict.
BroadcastModuleState = type(None)
ModuleState = Union[FlipFlopModuleState, ConjunctionModuleState, BroadcastModuleState]

ProcessPulseCallable = Callable[[ModuleState, bool, str], tuple[ModuleState, Optional[bool]]]
ModulesConfig = dict[str, tuple[ProcessPulseCallable, tuple[str, ...]]]
ModulesState = tuple[ModuleState, ...]

FLIP_FLOP_MODULE_NAME_PREFIX = '%'
CONJUNCTION_MODULE_NAME_PREFIX = '&'
BROADCAST_MODULE_NAME_PREFIX = None

BUTTON_MODULE_NAME = 'button'
BROADCASTER_MODULE_NAME = 'broadcaster'

MODULE_CONFIG_LINE_PATTERN = re.compile(r'^([%&])?([a-z]+) *-> *([ ,a-z]+)$')
DOWNSTREAM_MODULE_NAME_DELIMITER = ','


def process_pulse_to_flip_flop_module(state: ModuleState, pulse: bool, upstream_module_name: str) -> tuple[ModuleState, Optional[bool]]:
    assert isinstance(state, FlipFlopModuleState)
    if pulse:
        # Ignore high pulses.
        return (state, None)
    # For low pulses, flip the state. If the new state is on, send a high pulse. If the new state is off, send a low
    # pulse.
    state = not state
    return (state, state)


def process_pulse_to_conjunction_module(state: ModuleState, pulse: bool, upstream_module_name: str) -> tuple[ModuleState, Optional[bool]]:
    assert isinstance(state, tuple) and all((isinstance(a, str) and (isinstance(b, bool) or b is None)) for (a, b) in state)
    temp_state = dict(state)
    assert upstream_module_name in temp_state
    temp_state[upstream_module_name] = pulse
    new_state = tuple(sorted(temp_state.items()))
    if all(sub_state for (_, sub_state) in new_state):
        # Memory of most recent pulse from all upstream/input modules is high; send a low pulse.
        return (new_state, False)
    # Otherwise, send a high pulse.
    return (new_state, True)


def process_pulse_to_broadcast_module(state: ModuleState, pulse: bool, upstream_module_name: str) -> tuple[ModuleState, Optional[bool]]:
    assert state is None
    # Pass through the pulse as-is.
    return (None, pulse)


def parse_modules_config(lines: Iterable[str]) -> tuple[ModulesConfig, ModulesState]:
    config: ModulesConfig = {}
    initial_state: list[ModuleState] = []
    upstream_modules: dict[str, set[str]] = {}
    for (i, line) in enumerate(lines):
        match = MODULE_CONFIG_LINE_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Invalid module config on line {i + 1}: {line!r}')
        (prefix, module_name, raw_downstream_module_names) = match.groups()
        if prefix == FLIP_FLOP_MODULE_NAME_PREFIX:
            process_pulse = process_pulse_to_flip_flop_module
            initial_state.append(False)  # Flip-flop modules are initially off by default.
        elif prefix == CONJUNCTION_MODULE_NAME_PREFIX:
            process_pulse = process_pulse_to_conjunction_module
            initial_state.append(())  # We'll properly initialise these later.
        elif prefix == BROADCAST_MODULE_NAME_PREFIX:
            process_pulse = process_pulse_to_broadcast_module
            initial_state.append(None)  # Broadcast modules don't store state.
        else:
            raise ValueError(f'Invalid module config on line {i + 1} (unexpected prefix): {line!r}')
        if module_name in config:
            raise ValueError(f'Redefinition of module config {config[module_name]!r} on line {i + 1}: {line!r}')
        if module_name == BUTTON_MODULE_NAME:
            raise ValueError(f'Module config on line {i + 1} uses reserved name {BUTTON_MODULE_NAME!r}: {line!r}')
        downstream_module_names = tuple(
            raw_downstream_module_name.strip()
            for raw_downstream_module_name
            in raw_downstream_module_names.split(DOWNSTREAM_MODULE_NAME_DELIMITER)
        )
        duplicate_downstream_module_names = {
            downstream_module_name
            for (downstream_module_name, count)
            in Counter(downstream_module_names).items()
            if count > 1
        }
        if duplicate_downstream_module_names:
            raise ValueError(f'Downstream modules {duplicate_downstream_module_names!r} repeated on line {i + 1}: {line!r}')
        config[module_name] = (process_pulse, downstream_module_names)
        for downstream_module_name in downstream_module_names:
            if downstream_module_name not in upstream_modules:
                upstream_modules[downstream_module_name] = set()
            upstream_modules[downstream_module_name].add(module_name)

    if BROADCASTER_MODULE_NAME not in config:
        raise ValueError(f'Missing module config for name {BROADCASTER_MODULE_NAME!r}')

    for (i, (module_name, state)) in enumerate(zip(config.keys(), initial_state)):
        if state == ():
            # Conjunction modules initially remember the most recent pulse as low for all upstream/input modules.
            # However, we'll draw a distinction between the default most recent pulse and a real most recent pulse of
            # low.
            initial_state[i] = tuple((upstream_module_name, None) for upstream_module_name in sorted(upstream_modules[module_name]))

    return (config, tuple(initial_state))


def propagate(config: ModulesConfig, state: ModulesState) -> tuple[ModulesState, tuple[int, int]]:
    next_state: dict[str, ModuleState] = {module_name: module_state for (module_name, module_state) in zip(config.keys(), state)}
    num_low_pulses = 1  # The button module sends a low pulse to the broadcast module named "broadcaster".
    num_high_pulses = 0
    pulses_to_process = [('button', False, 'broadcaster')]

    while pulses_to_process:
        (upstream_module_name, received_pulse, module_name) = pulses_to_process.pop(0)
        (process_pulse, downstream_module_names) = config[module_name]
        module_state = next_state[module_name]
        (next_module_state, transmitted_pulse) = process_pulse(module_state, received_pulse, upstream_module_name)
        next_state[module_name] = next_module_state  # Updating existing keys won't affect preserved insertion order.
        if transmitted_pulse is None:
            continue
        if transmitted_pulse:
            num_high_pulses += len(downstream_module_names)
        else:
            num_low_pulses += len(downstream_module_names)
        for downstream_module_name in downstream_module_names:
            if downstream_module_name in config:
                pulses_to_process.append((module_name, transmitted_pulse, downstream_module_name))

    return (tuple(next_state.values()), (num_low_pulses, num_high_pulses))


def count_pulse_types(config: ModulesConfig, state: ModulesState, num_button_presses: int) -> tuple[int, int]:
    witnessed_states: dict[ModulesState, tuple[int, int, int]] = {}
    witnessed_state_sequence: list[ModulesState] = []
    total_low_pulses = 0
    total_high_pulses = 0
    for i in range(num_button_presses):
        if state in witnessed_states:
            break
        (next_state, (num_low_pulses, num_high_pulses)) = propagate(config, state)
        witnessed_states[state] = (i, num_low_pulses, num_high_pulses)
        witnessed_state_sequence.append(state)
        total_low_pulses += num_low_pulses
        total_high_pulses += num_high_pulses
        state = next_state
    if i < num_button_presses - 1:
        cycle_start_index = witnessed_states[state][0]
        cycle_length = i - cycle_start_index
        if cycle_length > 0:
            remaining_button_presses = num_button_presses - i
            (full_cycles, partial_cycle_pos) = divmod(remaining_button_presses, cycle_length)
            if full_cycles > 0:
                total_low_pulses += sum(witnessed_states[witnessed_state][1] for witnessed_state in witnessed_state_sequence[cycle_start_index:]) * full_cycles
                total_high_pulses += sum(witnessed_states[witnessed_state][2] for witnessed_state in witnessed_state_sequence[cycle_start_index:]) * full_cycles
            if partial_cycle_pos > 0:
                total_low_pulses += sum(witnessed_states[witnessed_state][1] for witnessed_state in witnessed_state_sequence[cycle_start_index:cycle_start_index + partial_cycle_pos])
                total_high_pulses += sum(witnessed_states[witnessed_state][2] for witnessed_state in witnessed_state_sequence[cycle_start_index:cycle_start_index + partial_cycle_pos])

    return (total_low_pulses, total_high_pulses)


def calculate_product_of_pulse_types_after_thousand_button_presses(lines: Iterable[str]) -> int:
    """
    >>> calculate_product_of_pulse_types_after_thousand_button_presses([
    ...     'broadcaster -> a, b, c',
    ...     '%a -> b',
    ...     '%b -> c',
    ...     '%c -> inv',
    ...     '&inv -> a',
    ... ])
    32000000
    >>> calculate_product_of_pulse_types_after_thousand_button_presses([
    ...     'broadcaster -> a',
    ...     '%a -> inv, con',
    ...     '&inv -> b',
    ...     '%b -> con',
    ...     '&con -> output',
    ... ])
    11687500
    """
    (config, initial_state) = parse_modules_config(lines)
    (num_low_pulses, num_high_pulses) = count_pulse_types(config, initial_state, 1000)
    return num_low_pulses * num_high_pulses


########################################################################################################################
# Part 2
########################################################################################################################

def count_button_presses_until_rx_is_triggered(lines: Iterable[str]) -> int:
    (config, initial_state) = parse_modules_config(chain.from_iterable((
        lines,
        ('&rx -> dummy',),
    )))
    state = initial_state
    for i in count(1):
        (state, _) = propagate(config, state)
        rx_state = state[-1]
        assert isinstance(rx_state, tuple) and all((isinstance(a, str) and (isinstance(b, bool) or b is None)) for (a, b) in rx_state)
        if any(s is False for (_, s) in rx_state):
            break
    return i


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
        print(calculate_product_of_pulse_types_after_thousand_button_presses(lines))
    elif args.part == 2:
        print(count_button_presses_until_rx_is_triggered(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
