from typing import Dict, Callable
from unittest import TestCase

from tests.gate_experiments.comparator import ComparatorExperiment, Experiment
from tests.gate_test import GateTest


class ComparatorTest(GateTest):

    def __init__(self, experiment: Callable[[int, int], ComparatorExperiment], constant: int, n: int,
                 test_case: TestCase):
        super().__init__(experiment(constant, n), test_case)
        self._constant = constant
        self._n = n
        self._x: int

    def _set_up(self, initial_values: Dict[str, int]) -> None:
        self._x = initial_values['x']

    @property
    def _computations(self) -> Dict[str, Callable[[int], int]]:
        return {
            'c': lambda _: 1 if self._x < self._constant else 0,
        }


class Test(ComparatorTest):

    def __init__(self, constant: int, n: int, test_case: TestCase):
        super().__init__(Experiment, constant, n, test_case)