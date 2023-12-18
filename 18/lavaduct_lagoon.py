#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
import re
from typing import Callable, NamedTuple


########################################################################################################################
# Dig plan
########################################################################################################################

def pairs(iterable: Iterable[int]) -> Iterator[tuple[int, int]]:
    iter_ = iter(iterable)
    while True:
        try:
            a = next(iter_)
        except StopIteration:
            return
        try:
            b = next(iter_)
        except StopIteration:
            raise ValueError(f'Cannot finish pairing off odd number of elements in iterable; {a!r} is alone')
        yield (a, b)


class Direction(Enum):
    UP = 'U'
    RIGHT = 'R'
    DOWN = 'D'
    LEFT = 'L'

    @property
    def reverse(self):
        return {
            Direction.UP: Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
        }[self]

    @property
    def clockwise_orthogonal(self):
        return {
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
        }[self]

    @property
    def anticlockwise_orthogonal(self):
        return {
            Direction.UP: Direction.LEFT,
            Direction.RIGHT: Direction.UP,
            Direction.DOWN: Direction.RIGHT,
            Direction.LEFT: Direction.DOWN,
        }[self]


class Coordinate(NamedTuple):
    x: int
    y: int

    def translate(self, direction: Direction, length: int) -> 'Coordinate':
        if direction == Direction.UP:
            return Coordinate(self.x, self.y - length)
        elif direction == Direction.RIGHT:
            return Coordinate(self.x + length, self.y)
        elif direction == Direction.DOWN:
            return Coordinate(self.x, self.y + length)
        elif direction == Direction.LEFT:
            return Coordinate(self.x - length, self.y)
        else:
            raise ValueError(f'Unexpected direction: {direction!r}')


RGB_HEXADECIMAL_COLOUR_CODE_PATTERN = re.compile(r'^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$')


class Colour(NamedTuple):
    red: int
    green: int
    blue: int

    @classmethod
    def from_rgb_hexadecimal_colour_code(cls, colour_code: str) -> 'Colour':
        match = RGB_HEXADECIMAL_COLOUR_CODE_PATTERN.fullmatch(colour_code)
        if not match:
            raise ValueError(f'Invalid RGB hexadecimal colour code: {colour_code!r}')
        return Colour(*(int(component, 16) for component in match.groups()))


DIG_INSTRUCTION_PATTERN = re.compile(r'^([DLRU]) ([1-9]\d*) \((#[0-9a-f]{6})\)$')
CORRECT_DIG_INSTRUCTION_PATTERN = re.compile(r'^[DLRU] [1-9]\d* \(#([0-9a-f]{5})([0-3])\)$')


class DigInstruction(NamedTuple):
    start_grid_coord: Coordinate
    end_grid_coord: Coordinate
    direction: Direction
    length: int
    colour: Colour

    @classmethod
    def from_line(cls, line: str, start_grid_coord: Coordinate, allowed_directions: set[Direction]) -> 'DigInstruction':
        match = DIG_INSTRUCTION_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Invalid dig instruction: {line!r}')
        (raw_direction, raw_length, raw_colour) = match.groups()
        direction = Direction(raw_direction)
        if direction not in allowed_directions:
            raise ValueError(f'Invalid dig instruction (direction not allowed): {line!r}')
        length = int(raw_length)
        end_grid_coord = start_grid_coord.translate(direction, length)
        colour = Colour.from_rgb_hexadecimal_colour_code(raw_colour)
        return DigInstruction(start_grid_coord, end_grid_coord, direction, length, colour)

    @classmethod
    def from_correct_line(cls, line: str, start_grid_coord: Coordinate, allowed_directions: set[Direction]) -> 'DigInstruction':
        match = CORRECT_DIG_INSTRUCTION_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Invalid dig instruction: {line!r}')
        (raw_length, raw_direction) = match.groups()
        length = int(raw_length, 16)
        direction = [
            Direction.RIGHT,
            Direction.DOWN,
            Direction.LEFT,
            Direction.UP,
        ][int(raw_direction)]
        if direction not in allowed_directions:
            raise ValueError(f'Invalid dig instruction (direction not allowed): {line!r}')
        end_grid_coord = start_grid_coord.translate(direction, length)
        return DigInstruction(start_grid_coord, end_grid_coord, direction, length, Colour(0, 0, 0))


class DigPlan(NamedTuple):
    max_grid_coord: Coordinate
    instructions: tuple[DigInstruction, ...]
    span_grid_coords_by_row: dict[int, tuple[tuple[int, int], ...]]

    @classmethod
    def from_lines(cls, lines: Iterable[str], instruction_parser: Callable[[str, Coordinate, set[Direction]], DigInstruction]) -> 'DigPlan':
        instructions: list[DigInstruction] = []
        origin_grid_coord = Coordinate(0, 0)
        min_grid_coord = origin_grid_coord
        max_grid_coord = origin_grid_coord
        start_grid_coord = origin_grid_coord
        allowed_directions = {Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT}
        for line in lines:
            instruction = instruction_parser(line, start_grid_coord, allowed_directions)

            if instruction.end_grid_coord.x < min_grid_coord.x:
                min_grid_coord = Coordinate(instruction.end_grid_coord.x, min_grid_coord.y)
            if instruction.end_grid_coord.y < min_grid_coord.y:
                min_grid_coord = Coordinate(min_grid_coord.x, instruction.end_grid_coord.y)
            if instruction.end_grid_coord.x > max_grid_coord.x:
                max_grid_coord = Coordinate(instruction.end_grid_coord.x, max_grid_coord.y)
            if instruction.end_grid_coord.y > max_grid_coord.y:
                max_grid_coord = Coordinate(max_grid_coord.x, instruction.end_grid_coord.y)

            instructions.append(instruction)
            start_grid_coord = instruction.end_grid_coord
            allowed_directions = {instruction.direction.clockwise_orthogonal, instruction.direction.anticlockwise_orthogonal}
        if instruction.end_grid_coord != origin_grid_coord:
            raise ValueError(f'Sequence of instructions do not return to the origin: {instructions!r}')
        if instructions[0].direction not in allowed_directions:
            # This guarantees that all instruction start/end coordinates are vertices on the formed polygon (and _don't_
            # lie on a straight line)/
            raise ValueError(f'Sequence of instructions do not return to the origin in a permissible manner: {instructions!r}')

        translated_instructions = tuple(DigInstruction(
            Coordinate(instruction.start_grid_coord.x - min_grid_coord.x, instruction.start_grid_coord.y - min_grid_coord.y),
            Coordinate(instruction.end_grid_coord.x - min_grid_coord.x, instruction.end_grid_coord.y - min_grid_coord.y),
            instruction.direction,
            instruction.length,
            instruction.colour,
        ) for instruction in instructions)
        translated_max_grid_coord = Coordinate(max_grid_coord.x - min_grid_coord.x, max_grid_coord.y - min_grid_coord.y)

        corner_grid_coords_by_row: dict[int, set[int]] = {}
        for translated_instruction in translated_instructions:
            row_corner_grid_coords = corner_grid_coords_by_row.setdefault(translated_instruction.end_grid_coord.y, set())
            row_corner_grid_coords.add(translated_instruction.end_grid_coord.x)
        span_grid_coords_by_row = {y: tuple(span for span in pairs(sorted(row_corner_grid_coords))) for (y, row_corner_grid_coords) in corner_grid_coords_by_row.items()}

        return DigPlan(translated_max_grid_coord, translated_instructions, span_grid_coords_by_row)

    def calculate_volume(self) -> int:
        volume = 0
        mask_spans: list[tuple[int, int]] = []
        prev_y = -1
        for y in sorted(self.span_grid_coords_by_row.keys()):
            row_spans = self.span_grid_coords_by_row[y]
            should_skip_mask_update = False
            if not mask_spans:
                mask_spans = list(row_spans)
                should_skip_mask_update = True
            height = y - prev_y
            for (mask_span_start, mask_span_end) in mask_spans:
                volume += height * (mask_span_end - mask_span_start + 1)
            prev_y = y
            if should_skip_mask_update:
                continue
            for row_span in row_spans:
                (row_span_start, row_span_end) = row_span
                for (i, mask_span) in enumerate(mask_spans):
                    (mask_span_start, mask_span_end) = mask_span
                    if row_span_end < mask_span_start:
                        # Row span is disjoint, strictly to the left of the mask span. Add to mask spans.
                        mask_spans.insert(i, row_span)
                        volume += row_span_end - row_span_start + 1
                        break
                    elif row_span_end == mask_span_start:
                        # Row span's right side touches mask span's left side. Extend mask span.
                        mask_spans[i] = (row_span_start, mask_span_end)
                        volume += row_span_end - row_span_start
                        break
                    elif row_span == mask_span:
                        # Row span and mask span are identical. Delete mask span.
                        mask_spans.pop(i)
                        break
                    elif mask_span_start <= row_span_start and row_span_end <= mask_span_end:
                        # Row span is covered by mask span. Subtract mask span.
                        mask_spans.pop(i)
                        if row_span_end != mask_span_end:
                            mask_spans.insert(i, (row_span_end, mask_span_end))
                        if mask_span_start != row_span_start:
                            mask_spans.insert(i, (mask_span_start, row_span_start))
                        break
                    elif mask_span_end == row_span_start:
                        # Row span's left side touches mask span's right side. Extend mask span.
                        mask_spans[i] = (mask_span_start, row_span_end)
                        volume += row_span_end - row_span_start
                        break
                    elif i == len(mask_spans) - 1:
                        # We've exhausted all mask spans. Row span must be disjoint, strictly to the right of the mask
                        # span. Add to mask spans.
                        mask_spans.append(row_span)
                        volume += row_span_end - row_span_start + 1
                        break
                # Compaction pass.
                i = 0
                while i < (len(mask_spans) - 1):
                    (mask_span_start, mask_span_end) = mask_spans[i]
                    (next_mask_span_start, next_mask_span_end) = mask_spans[i + 1]
                    if next_mask_span_start == mask_span_end:
                        mask_spans.pop(i)
                        mask_spans.pop(i)
                        mask_spans.insert(i, (mask_span_start, next_mask_span_end))
                        volume -= 1
                    i += 1
        # We should wind up with an empty mask at the very end.
        assert not mask_spans
        return volume


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_volume(lines: Iterable[str]) -> int:
    """
    ```
    △▶▶▶▶▶▶
    ▲#####▼
    ◀◀▲###▼
    ..▲###▼
    ..▲###▼
    ▲▶▶#◀◀▼
    ▲###▼..
    ◀▲##▼▶▶
    .▲####▼
    .◀◀◀◀◀▼
    ```

    >>> calculate_volume([
    ...     'R 6 (#70c710)',
    ...     'D 5 (#0dc571)',
    ...     'L 2 (#5713f0)',
    ...     'D 2 (#d2c081)',
    ...     'R 2 (#59c680)',
    ...     'D 2 (#411b91)',
    ...     'L 5 (#8ceee2)',
    ...     'U 2 (#caa173)',
    ...     'L 1 (#1b58a2)',
    ...     'U 2 (#caa171)',
    ...     'R 2 (#7807d2)',
    ...     'U 3 (#a77fa3)',
    ...     'L 2 (#015232)',
    ...     'U 2 (#7a21e3)',
    ... ])
    62

    ```
    ....◀▲.◀▲....
    ....▼▲.▼▲....
    ....▼◀◀▼▲....
    ....▼###▲....
    ◀◀◀◀▼###◁◀◀◀▲
    ▼▶▶▶▶▶▶▶▶▶##▲
    .........▼##▲
    ◀◀◀◀◀◀◀◀◀▼##▲
    ▼▶▶▶▶###▲▶▶▶▶
    ....▼###▲....
    ....▼###▲....
    ....▼###▲....
    ....▼▶▶▶▶....
    ```

    >>> calculate_volume([
    ...     'U 4 (#ffffff)',
    ...     'L 1 (#ffffff)',
    ...     'D 2 (#ffffff)',
    ...     'L 2 (#ffffff)',
    ...     'U 2 (#ffffff)',
    ...     'L 1 (#ffffff)',
    ...     'D 4 (#ffffff)',
    ...     'L 4 (#ffffff)',
    ...     'D 1 (#ffffff)',
    ...     'R 9 (#ffffff)',
    ...     'D 2 (#ffffff)',
    ...     'L 9 (#ffffff)',
    ...     'D 1 (#ffffff)',
    ...     'R 4 (#ffffff)',
    ...     'D 4 (#ffffff)',
    ...     'R 4 (#ffffff)',
    ...     'U 4 (#ffffff)',
    ...     'R 4 (#ffffff)',
    ...     'U 4 (#ffffff)',
    ...     'L 4 (#ffffff)',
    ... ])
    94
    """
    dig_plan = DigPlan.from_lines(lines, DigInstruction.from_line)
    return dig_plan.calculate_volume()


########################################################################################################################
# Part 2
########################################################################################################################

def calculate_correct_volume(lines: Iterable[str]) -> int:
    """
    >>> calculate_correct_volume([
    ...     'R 6 (#70c710)',
    ...     'D 5 (#0dc571)',
    ...     'L 2 (#5713f0)',
    ...     'D 2 (#d2c081)',
    ...     'R 2 (#59c680)',
    ...     'D 2 (#411b91)',
    ...     'L 5 (#8ceee2)',
    ...     'U 2 (#caa173)',
    ...     'L 1 (#1b58a2)',
    ...     'U 2 (#caa171)',
    ...     'R 2 (#7807d2)',
    ...     'U 3 (#a77fa3)',
    ...     'L 2 (#015232)',
    ...     'U 2 (#7a21e3)',
    ... ])
    952408144115
    """
    dig_plan = DigPlan.from_lines(lines, DigInstruction.from_correct_line)
    return dig_plan.calculate_volume()


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
        print(calculate_volume(lines))
    elif args.part == 2:
        print(calculate_correct_volume(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
