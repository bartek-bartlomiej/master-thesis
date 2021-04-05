import unittest
from typing import Dict, Callable

from tests.gate_experiments.carry import Experiment
from tests.gate_test import GateTest


class Test(GateTest):

    def __init__(self, constant: int, n: int, test_case: unittest.TestCase):
        super().__init__(Experiment(constant, n), test_case)
        self._constant = constant
        self._n = n
        self._x: int

    def _set_up(self, initial_values: Dict[str, int]) -> None:
        self._x: int = initial_values['x']

    @property
    def _computations(self) -> Dict[str, Callable[[int], int]]:
        return {
            'carry': lambda _: (self._x + self._constant) >> self._n
        }
