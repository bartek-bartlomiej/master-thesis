import unittest
from abc import ABC, abstractmethod
from itertools import chain
from typing import Dict, List, Tuple, Callable

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister, execute, Aer
from qiskit.circuit import Gate
from qiskit.providers import Backend
from qiskit.result import Result

from utils import as_bits_reversed


class QuantumExperiment(ABC):
    def __init__(self, backend: Backend = Aer.get_backend('qasm_simulator')):
        self._backend = backend

    def run(self, initial_values: Dict[str, int], name: str) -> Result:
        circuit = self._construct_circuit(initial_values, name)
        job = execute(circuit, self._backend, shots=1)
        return job.result()

    def _construct_circuit(self, initial_values: Dict[str, int], name: str) -> QuantumCircuit:
        circuit = _create_circuit(self._qregs_spec, name)
        _initialize(circuit, initial_values)
        _append_gate(circuit, self._gate)
        _measure(circuit)

        return circuit

    @property
    @abstractmethod
    def _qregs_spec(self) -> List[Tuple[str, int]]:
        pass

    @property
    @abstractmethod
    def _gate(self) -> Gate:
        pass

    @property
    def qreg_names(self) -> List[str]:
        return [name for (name, _) in self._qregs_spec]


def _create_circuit(regs_data: List[Tuple[str, int]], name: str) -> QuantumCircuit:
    qregs = [QuantumRegister(size, name=name) for (name, size) in regs_data]
    return QuantumCircuit(*qregs, name=name)


def _initialize(circuit: QuantumCircuit, values: Dict[str, int]) -> None:
    for qreg in circuit.qregs:
        value = values.get(qreg.name, 0)
        value_str = as_bits_reversed(value, qreg.size)

        for qubit, bit in enumerate(value_str):
            if bit == '1':
                circuit.x(qreg[qubit])

    circuit.barrier(*circuit.qregs)


def _append_gate(circuit: QuantumCircuit, gate: Gate) -> None:
    qubits = list(chain.from_iterable(circuit.qregs))
    circuit.append(gate, qubits)


def _measure(circuit: QuantumCircuit) -> None:
    qregs = circuit.qregs
    cregs = [ClassicalRegister(qreg.size, name=f'{qreg.name}Value') for qreg in qregs]
    circuit.add_register(*cregs)

    circuit.barrier(*qregs)

    for qreg, creg in zip(qregs, cregs):
        circuit.measure(qreg[:], creg[:])


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
