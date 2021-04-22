from typing import Dict, Callable
from unittest import TestCase

from tests.gate_experiments.controlled_carry import Experiment
from tests.gate_tests.carry import CarryTest


class Test(CarryTest):

    def __init__(self, constant: int, n: int, test_case: TestCase):
        super().__init__(Experiment, constant, n, test_case)
        self._ctrl: int

    def _set_up(self, initial_values: Dict[str, int]) -> None:
        super()._set_up(initial_values)
        self._ctrl = initial_values['ctrl']

    @property
    def _computations(self) -> Dict[str, Callable[[int], int]]:
        computations = super()._computations
        return {
            'c': lambda _: computations['c'](_) if self._ctrl == 0b1 else 0
        }
