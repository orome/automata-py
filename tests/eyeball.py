#!/usr/bin/env python
# encoding: utf8

import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from automata import *

def eyeball_basic_ca(rule_number: int, initial_conditions: str, frame_steps: int, frame_width: int) -> None:
    test_ca = CellularAutomata(rule_number, initial_conditions, frame_steps=frame_steps, frame_width=frame_width)

    print(f"====================\nrule_number: {rule_number}\ninitial_conditions: {initial_conditions}\nframe_steps: {frame_steps}\nframe_width: {frame_width}\n====================")
    print(test_ca.to_dict()['args'])
    print(test_ca)

eyeball_basic_ca(30, '1000000', frame_steps=10, frame_width=31)
eyeball_basic_ca(90, '1', frame_steps=30, frame_width=51)
eyeball_basic_ca(130, '1', frame_steps=5, frame_width=21)
