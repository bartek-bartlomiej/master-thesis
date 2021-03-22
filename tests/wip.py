from typing import Callable, Dict, List, Tuple

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister, execute
from qiskit.providers import Backend
from qiskit.result import Result

from utils import as_bits_reversed


def test_gate(backend: Backend,
              regs_data: List[Tuple[str, int]],
              initial_values: Dict[str, int],
              asserts: Dict[str, Callable[[int, int], bool]],
              append_gate: Callable[[QuantumCircuit], None]):

    circuit = _create_circuit(regs_data)
    _initialize(circuit, initial_values)
    append_gate(circuit)
    _measure(circuit)

    job = execute(circuit, backend, shots=1)
    result = job.result()

    values = _parse_result(result, circuit)
    _assert(circuit, values, initial_values, asserts)


def _create_circuit(regs_data: List[Tuple[str, int]]) -> QuantumCircuit:
    qregs = [QuantumRegister(size, name=name) for (name, size) in regs_data]
    return QuantumCircuit(*qregs)


def _initialize(circuit: QuantumCircuit, values: Dict[str, int]) -> None:
    for qreg in circuit.qregs:
        value = values.get(qreg.name, 0)
        value_str = as_bits_reversed(value, qreg.size)

        for qubit, bit in enumerate(value_str):
            if bit == '1':
                circuit.x(qreg[qubit])

    circuit.barrier(*circuit.qregs)


def _measure(circuit: QuantumCircuit) -> None:
    qregs = circuit.qregs
    cregs = [ClassicalRegister(qreg.size, name=f'{qreg.name}Value') for qreg in qregs]
    circuit.add_register(*cregs)

    circuit.barrier(*qregs)

    for qreg, creg in zip(qregs, cregs):
        circuit.measure(qreg[:], creg[:])


def _parse_result(result: Result, circuit: QuantumCircuit) -> List[int]:
    keys = list(result.get_counts(circuit).keys())
    assert len(keys) == 1

    values_as_str = keys[0].split(' ')
    values = [int(value, 2) for value in values_as_str]
    return values[::-1]


def _assert(circuit: QuantumCircuit,
            values: List[int],
            initial_values: Dict[str, int],
            asserts: Dict[str, Callable[[int, int], bool]]) -> None:

    for qreg, value in zip(circuit.qregs, values):
        assert_ = asserts.get(qreg.name, _default_assert)
        initial_value = initial_values.get(qreg.name, 0)

        print(initial_value, value, assert_(initial_value, value))


def _default_assert(initial_value: int, final_value: int) -> bool:
    return initial_value == final_value
