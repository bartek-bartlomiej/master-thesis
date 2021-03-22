from abc import ABC, abstractmethod
from itertools import chain
from typing import Dict, List, Tuple

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
