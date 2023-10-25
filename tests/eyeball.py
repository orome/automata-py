#!/usr/bin/env python
# encoding: utf8

import termcolor
from automata import *


HEADER_LENGTH = 100
DEFAULT_FRAME_STEPS = 30
DEFAULT_FRAME_WIDTH = 81


def print_header(level, label='', mark=None) -> None:
    if mark is None:
        mark = {0: '▲▼', 1: '==', 2: '--', 3: '- ', 4: ' . '}[level]
    rule = (mark * (HEADER_LENGTH//2))[:((HEADER_LENGTH+1-(len(label)+2))//2)]

    # Must be outside f-strings to run on Python < 3.12
    header_text = termcolor.colored(f"{rule} {label} {rule[::-1]}"[:HEADER_LENGTH],
                                    color='green' if level <= 0 else 'dark_grey',
                                    on_color=None if level <= 0 else 'on_black',
                                    attrs=['bold', 'dark'] if level <= 0 else ['bold'])
    header_blanks = '\n' if level != 1 else '\n\n'

    print(f"{header_blanks}{header_text}")


def eyeball_basic_ca(rule_number: int, initial_conditions: str, base: int,
                     frame_steps: int = DEFAULT_FRAME_STEPS, frame_width: int = DEFAULT_FRAME_WIDTH) -> None:
    test_ca = CellularAutomata(rule_number, initial_conditions, base,
                               frame_steps=frame_steps, frame_width=frame_width)

    print_header(3, f"{rule_number}+{base} @ {initial_conditions}")
    print(f"rule_number: {rule_number}\n"
          f"base: {base}\n"
          f"initial_conditions: {initial_conditions}\n"
          f"frame_steps: {frame_steps}\n"
          f"frame_width: {frame_width}\n")
    print(test_ca.to_dict()['args'])
    print(test_ca)


print_header(0, ' Automata Eyeball Checks ')

print_header(1, 'Basics')

print_header(2, 'Basic Lattice')
print(f"frame_steps: {DEFAULT_FRAME_STEPS}\n"
      f"frame_width: {DEFAULT_FRAME_WIDTH}\n")

eyeball_basic_ca(30, '1000000', 2)
eyeball_basic_ca(90, '1', 2,)
eyeball_basic_ca(130, '1', 2)
eyeball_basic_ca(130, '101010101', 3)
eyeball_basic_ca(130, '202121212201', 3)
eyeball_basic_ca(1, '202121212201', 3)
eyeball_basic_ca(2398373402626, '1', 3)

print_header(0, ' (End) Automata Eyeball Checks (End) ')
print("\n")
