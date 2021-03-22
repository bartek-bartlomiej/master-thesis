import unittest
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Callable

from qiskit.result import Result

from tests.experiment import QuantumExperiment


class GateTest(ABC):
    def __init__(self, experiment: QuantumExperiment, test_case: unittest.TestCase):
        self._experiment = experiment
        self.test_case = test_case

    def run_subtests(self, params: List[Dict[str, int]]):
        for initial_values in params:
            with self.test_case.subTest(initial_values):
                self.run(initial_values)

    def run(self, initial_values: Dict[str, int]):
        self._update_params(initial_values)

        name = self._get_name(initial_values)
        result = self._experiment.run(initial_values, name)

        asserts = self._custom_asserts
        for name, value in zip(self._experiment.qreg_names, self._parse_result(result, name)):
            initial_value = initial_values.get(name, 0)

            if name in asserts:
                (compute, msg) = asserts[name]
                expected_value = compute(initial_value)
                self.test_case.assertEqual(value, expected_value,
                                           msg(initial_value, expected_value, value))
            else:
                self.test_case.assertEqual(value, initial_value,
                                           f'Wrong value in register "{name}" (expected {initial_value}, got {value})')

    def _parse_result(self, result: Result, name: str) -> List[int]:
        output = list(result.get_counts(name).keys())
        self.test_case.assertEqual(len(output), 1)

        values_as_str = output[0].split(' ')
        values = [int(value, 2) for value in values_as_str]
        return values[::-1]

    @abstractmethod
    def _update_params(self, initial_values: Dict[str, int]) -> None:
        pass

    @abstractmethod
    def _get_name(self, initial_values: Dict[str, int]) -> str:
        pass

    @property
    @abstractmethod
    def _custom_asserts(self) -> Dict[str, Tuple[Callable[[int], int], Callable[[int, int, int], str]]]:
        pass