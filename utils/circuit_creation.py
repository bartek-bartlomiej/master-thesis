from qiskit import QuantumRegister, QuantumCircuit

from utils.custom_typing import Name, QRegsSpec


def create_circuit(regs: QRegsSpec, name: Name) -> QuantumCircuit:
    qregs = [QuantumRegister(size, name=name) for name, size in regs.items()]
    return QuantumCircuit(*qregs, name=name)
