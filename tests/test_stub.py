# sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from automata import *


def test_automaton() -> None:
    test_ca = CellularAutomata(30, '1000000', frame_steps=10, frame_width=31)
    assert ''.join(test_ca._lattice[4]) == '0000000011001000100000000000000'
