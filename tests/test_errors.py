from automata import *


def test_invalid_rule_number() -> None:

    def _test_invalid_rule_number(rule_number: int, base: int) -> None:
        try:
            Rule(rule_number, base=base)
        except CellularAutomataError:
            assert True
        else:
            assert False, "Expected a CellularAutomataError but didn't get one."

    _test_invalid_rule_number(512, base=2)
    _test_invalid_rule_number(-1, base=3)
    _test_invalid_rule_number(700, base=2)


def test_invalid_boundary_conditions() -> None:

    def _test_invalid_boundary_conditions(rule_number: int, boundary_condition) -> None:
        try:
            CellularAutomata(rule_number, '1', boundary_condition=boundary_condition)
        except CellularAutomataError:
            assert True
        else:
            assert False, (f"Expected a CellularAutomataError but didn't get one for"
                           f" boundary_condition={boundary_condition}.")

    _test_invalid_boundary_conditions(30, "invalid_boundary")
    _test_invalid_boundary_conditions(30, 5)
    _test_invalid_boundary_conditions(30, None)


def test_invalid_initial_conditions() -> None:
    try:
        CellularAutomata(30, '1002', base=2)  # '2' is invalid for base 2
    except CellularAutomataError:
        assert True
    else:
        assert False, "Expected a CellularAutomataError but didn't get one."


def test_invalid_base_in_encode() -> None:
    try:
        Rule._encode(30, base=40, length=8)
    except ValueError:
        assert True
    else:
        assert False, "Expected a ValueError but didn't get one."


def test_invalid_base_in_decode() -> None:
    try:
        Rule._decode('00011110', base=40)
    except ValueError:
        assert True
    else:
        assert False, "Expected a ValueError but didn't get one."
