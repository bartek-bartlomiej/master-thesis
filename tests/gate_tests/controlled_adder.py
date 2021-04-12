from typing import Dict, Callable
from unittest import TestCase

from tests.gate_experiments.controlled_adder import Experiment
from tests.gate_tests.adder import AdderTest


class Test(AdderTest):

    def __init__(self, n: int, test_case: TestCase):
        super().__init__(Experiment, n, test_case)

    def _set_up(self, initial_values: Dict[str, int]) -> None:
        super()._set_up(initial_values)
        self._ctrl: int = initial_values['ctrl']

    @property
    def _computations(self) -> Dict[str, Callable[[int], int]]:
        computations = super()._computations
        return {
            'y': lambda y: computations['y'](y) if self._ctrl == 0b1 else y
        }
