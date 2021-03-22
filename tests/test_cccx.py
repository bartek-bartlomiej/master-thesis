import unittest
from typing import List, Tuple, Dict, Callable

from qiskit.circuit import Gate

from gates.cccx import triple_controlled_not
from tests.wip import QuantumExperiment, GateTest


class CCCXTestCase(unittest.TestCase):
    def test_triple_controlled_not(self):
        test = CCCXTest(self)

        params = [{'ctrl': ctrl, 'x': x, 'g': g} for g in range(2) for x in range(2) for ctrl in reversed(range(8))]
        test.run_subtests(params)


class CCCXTest(GateTest):
    def __init__(self, test_case: unittest.TestCase):
        super().__init__(TripleControlledNotExperiment(), test_case)
        self._ctrl: int = 0

    def _update_params(self, initial_values: Dict[str, int]) -> None:
        self._ctrl = initial_values['ctrl']

    def _get_name(self, initial_values: Dict[str, int]) -> str:
        return f'CCCX({self._ctrl}, {initial_values["x"]})_4_qubits'

    @property
    def _custom_asserts(self) -> Dict[str, Tuple[Callable[[int], int], Callable[[int, int, int], str]]]:
        return {
            'x': (
                lambda x: (x + 1) % 2 if self._ctrl == 0b111 else x,
                lambda x, y, v: f'Wrong value after experiment (expected CCCX({self._ctrl}, {x}) = {y}, got {v})'
            )
        }


class TripleControlledNotExperiment(QuantumExperiment):
    @property
    def _qregs_spec(self) -> List[Tuple[str, int]]:
        return [
            ('ctrl', 3),
            ('x', 1),
            ('g', 1),
        ]

    @property
    def _gate(self) -> Gate:
        return triple_controlled_not()


if __name__ == '__main__':
    unittest.main()
