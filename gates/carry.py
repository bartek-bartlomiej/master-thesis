from qiskit import QuantumCircuit
from qiskit.circuit import Gate

from utils.bits import as_bits_reversed
from utils.circuit_creation import create_circuit
from utils.typing_ import QRegsSpec


def carry(constant, n) -> Gate:
    circuit = create_circuit(carry_regs(n), f'Carry_({constant})')
    x_qreg, g_qreg, c_qreg = circuit.qregs

    body = _carry_body(constant, n, x_qreg, g_qreg)
    qubits = x_qreg[:] + g_qreg[:]

    circuit.cx(g_qreg[n - 1], c_qreg)
    circuit.append(body, qubits)
    circuit.cx(g_qreg[n - 1], c_qreg)
    circuit.append(body.inverse(), qubits)

    return circuit.to_gate()


def _carry_body(constant, n, x_qreg, g_qreg):
    circuit = QuantumCircuit(x_qreg, g_qreg, name=f'Carry_({constant})_body')
    constant_bits = as_bits_reversed(constant, n)

    for i in reversed(range(1, n)):
        if constant_bits[i] == '1':
            circuit.cx(x_qreg[i], g_qreg[i])
            circuit.x(x_qreg[i])
        circuit.ccx(g_qreg[i - 1], x_qreg[i], g_qreg[i])

    if constant_bits[0] == '1':
        circuit.cx(x_qreg[0], g_qreg[0])

    for i in range(1, n):
        circuit.ccx(g_qreg[i - 1], x_qreg[i], g_qreg[i])

    return circuit.to_gate()


def carry_regs(n: int) -> QRegsSpec:
    """ return definition of carry gate registers
    |x> - input register
    |g> - dirty ancillary register; initial state must be restored
    |carry> - output register - information about carry
    """
    return [
        ('x', n),
        ('g', n),
        ('carry', 1)
    ]
