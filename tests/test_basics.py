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


def test_rule_encode_decode() -> None:
    """
    Tests the encoding and decoding functionality of the Rule class.
    """
    assert Rule._encode(30, base=2, length=8) == '00011110'
    assert Rule._encode(5, base=2, length=4) == '0101'
    assert Rule._decode('00011110', base=2) == 30
    assert Rule._decode('0101', base=2) == 5


def test_pattern_to_output() -> None:
    """
    Tests the pattern to output mapping for a given rule.
    """
    rule_30 = Rule(30, base=2)
    assert rule_30.pattern_to_output['111'] == '0'
    assert rule_30.pattern_to_output['110'] == '0'
    assert rule_30.pattern_to_output['101'] == '0'
    assert rule_30.pattern_to_output['011'] == '1'


def test_automaton_repr() -> None:
    """
    Tests the repr of the CellularAutomata.
    """
    ca = CellularAutomata(30, '1000000')
    assert repr(ca) == '\n'.join([''.join(row) for row in ca._lattice])


def test_automaton_dict_representation() -> None:
    """
    Tests the dictionary representation of the CellularAutomata.
    """
    ca = CellularAutomata(30, '1000000')
    ca_dict = ca.to_dict()
    assert 'args' in ca_dict
    assert ca_dict['args']['rule_number'] == 30
    assert ca_dict['args']['base'] == 2
    assert ca_dict['args']['frame_width'] == 101
    assert ca_dict['args']['frame_steps'] == 200
    assert ca_dict['args']['boundary_condition'] == 'zero'
    assert ca_dict['args']['initial_conditions'] == '1000000'
