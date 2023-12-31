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
        with pytest.raises(CellularAutomataError, match=str(boundary_condition)):
            CellularAutomata(rule_number, '1', boundary_condition=boundary_condition)

    _test_invalid_boundary_conditions(30, "invalid_boundary")
    _test_invalid_boundary_conditions(30, 5)
    _test_invalid_boundary_conditions(30, None)


def test_invalid_initial_conditions() -> None:

    def _test_invalid_initial_conditions(rule_number: int, initial_conditions: str, base: int) -> None:
        with pytest.raises(CellularAutomataError):
            CellularAutomata(rule_number, initial_conditions, base)

    _test_invalid_initial_conditions(30, '1002', 2)
    _test_invalid_initial_conditions(50, 'A002', 4)
    _test_invalid_initial_conditions(20, '0 1 0', 2)
    _test_invalid_initial_conditions(50, ' ', 2)


def test_invalid_base_in_encode() -> None:

    def _test_invalid_base_in_encode(value: int, base: int, length: int) -> None:
        with pytest.raises(ValueError, match="Can't handle base"):
            Rule._encode(value, base, length)

    _test_invalid_base_in_encode(30, 40, 8)
    _test_invalid_base_in_encode(30, 50, 8)
    _test_invalid_base_in_encode(30, 1, 8)
    _test_invalid_base_in_encode(30, 0, 8)


def test_invalid_base_in_decode() -> None:

    def _test_invalid_base_in_decode(encoding: str, base: int) -> None:
        with pytest.raises(ValueError):
            Rule._decode(encoding, base)

    _test_invalid_base_in_decode('00011110', 40)
    _test_invalid_base_in_decode('00011110', 0)
    _test_invalid_base_in_decode('00011210', 2)
    _test_invalid_base_in_decode('4', 2)
