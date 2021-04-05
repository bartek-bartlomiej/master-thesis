from qiskit import QuantumCircuit
from qiskit.circuit import Gate

from utils.bits import as_bits_reversed
from utils.circuit_creation import create_circuit
from utils.typing_ import QRegsSpec


def carry(constant, n) -> Gate:
    circuit = create_circuit(carry_regs(n), f'Carry_({constant})')

    if n == 1:
        x_qreg, c_qreg = circuit.qregs
        if constant == 1:
            circuit.cx(x_qreg[0], c_qreg[0])
    else:
        x_qreg, g_qreg, c_qreg = circuit.qregs

        body = _carry_body(constant, n, x_qreg, g_qreg)
        qubits = x_qreg[:] + g_qreg[:]

        circuit.cx(g_qreg[n-2], c_qreg)
        circuit.append(body, qubits)
        circuit.cx(g_qreg[n-2], c_qreg)
        circuit.append(body.inverse(), qubits)

    return circuit.to_gate()


def _carry_body(constant, n, x_qreg, g_qreg):
    circuit = QuantumCircuit(x_qreg, g_qreg, name=f'Carry_({constant})_body')
    constant_bits = as_bits_reversed(constant, n)

    for i in reversed(range(2, n)):
        if constant_bits[i] == '1':
            circuit.cx(x_qreg[i], g_qreg[i-1])
            circuit.x(x_qreg[i])
        circuit.ccx(g_qreg[i-2], x_qreg[i], g_qreg[i-1])

    if constant_bits[1] == '1':
        circuit.cx(x_qreg[1], g_qreg[0])
        circuit.x(x_qreg[1])

    if constant_bits[0] == '1':
        circuit.ccx(x_qreg[0], x_qreg[1], g_qreg[0])

    for i in range(2, n):
        circuit.ccx(g_qreg[i-2], x_qreg[i], g_qreg[i-1])

    return circuit.to_gate()


def carry_regs(n: int) -> QRegsSpec:
    """ return definition of carry gate registers
    |x> - input register
    |g> - dirty ancillary register; initial state must be restored
    |carry> - output register - information about carry
    """
    if n == 1:
        return [
            ('x', n),
            ('carry', 1)
        ]
    else:
        return [
            ('x', n),
            ('g', n-1),
            ('carry', 1)
        ]
