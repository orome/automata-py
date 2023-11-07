import pytest
from automata import *


def test_invalid_rule_number() -> None:

    def _test_invalid_rule_number(rule_number: int, base: int) -> None:
        with pytest.raises(CellularAutomataError):
            Rule(rule_number, base=base)

    _test_invalid_rule_number(512, base=2)
    _test_invalid_rule_number(-1, base=3)
    _test_invalid_rule_number(700, base=2)


def test_invalid_boundary_conditions() -> None:

    def _test_invalid_boundary_conditions(rule_number: int, boundary_condition) -> None:
        with pytest.raises(CellularAutomataError):
            CellularAutomata(rule_number, '1', boundary_condition=boundary_condition)

    _test_invalid_boundary_conditions(30, "invalid_boundary")
    _test_invalid_boundary_conditions(30, 5)
    _test_invalid_boundary_conditions(30, None)


def test_invalid_initial_conditions() -> None:
    with pytest.raises(CellularAutomataError):
        CellularAutomata(30, '1002', base=2)  # '2' is invalid for base 2


def test_invalid_base_in_encode() -> None:
    with pytest.raises(ValueError, match="Can't handle base"):
        Rule._encode(30, base=40, length=8)


def test_invalid_base_in_decode() -> None:
    with pytest.raises(ValueError):
        Rule._decode('00011110', base=40)
