import unittest

from qiskit.circuit import Gate

from gates.cccx import triple_controlled_not, cccx_regs
from tests.experiment import QuantumExperiment
from tests.test_gate import GateTest
from utils.typing_ import QRegsSpec, ComputationsMap, ValuesMap


class CCCXTestCase(unittest.TestCase):
    def test_triple_controlled_not(self):
        test = Test(self)

        params = [{'ctrl': ctrl, 'x': x, 'g': g}
                  for g in range(2) for x in range(2) for ctrl in reversed(range(8))]
        test.run_subtests(params)


class Test(GateTest):

    def __init__(self, test_case: unittest.TestCase):
        super().__init__(Experiment(), test_case)
        self._ctrl: int = 0b00

    def _set_up(self, initial_values: ValuesMap) -> None:
        self._ctrl = initial_values['ctrl']

    @property
    def _computations(self) -> ComputationsMap:
        return {
            'x': lambda x: (x + 1) % 2 if self._ctrl == 0b111 else x
        }


class Experiment(QuantumExperiment):

    @property
    def _gate(self) -> Gate:
        return triple_controlled_not()

    @property
    def _qregs_spec(self) -> QRegsSpec:
        return cccx_regs


if __name__ == '__main__':
    unittest.main()
