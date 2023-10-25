from automata import *


# noinspection PyProtectedMember
def _test_automaton(rule_number: int, base: int, initial_conditions: str,
                    frame_width: int, frame_steps: int,
                    rule_string: str, lattice_dict: dict) -> None:

    test_ca = CellularAutomata(rule_number, initial_conditions, base,
                               frame_width, frame_steps)

    for step in lattice_dict:
        assert ''.join(test_ca._lattice[step]) == lattice_dict[step]

    assert test_ca.frame_steps == frame_steps
    assert test_ca.frame_width == frame_width

    test_rule = test_ca.rule

    assert max(max(row) for row in test_ca._lattice) <= Rule.ALPHABET[base - 1]
    assert max(min(row) for row in test_ca._lattice) >= '0'
    assert all(element in Rule.ALPHABET[:base] for element in test_ca._lattice.flatten())

    assert test_rule.rule_number == rule_number
    assert test_rule.base == base
    assert test_rule.n_input_patterns == test_rule.base ** test_rule.input_span
    assert Rule._encode(test_rule.rule_number, base=test_rule.base,
                        length=test_rule.n_input_patterns) == rule_string


def test_automaton() -> None:
    _test_automaton(30, 2, '1000000',
                    31, 80,
                    '00011110',
                    {
                        4: '0000000011001000100000000000000'})
    _test_automaton(30, 2, '1000000',
                    81, 30,
                    '00011110',
                    {
                        4: '000000000000000000000000000000000110010001000000000000000000000000000000000000000',
                        20: '000000000000000001100100011100111100000111101110110001000100000000000000000000000'})
