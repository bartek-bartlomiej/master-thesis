from itertools import chain

from gates.constant_modulo_multiplier import controlled_constant_modulo_multiplier, \
    controlled_constant_modulo_multiplier_regs
from utils.circuit_creation import create_circuit
from utils.typing_ import QRegsSpec


def modulo_exponentiation(constant: int, N: int, n: int):
    circuit = create_circuit(modulo_exponentiation_regs(n), f'Exp({constant})_Mod_{N}')
    x_qreg, y_qreg, aux_qreg = circuit.qregs

    for i in range(2 * n):
        partial_constant = get_partial_constant(constant, i, N)
        circuit.append(
            controlled_U(partial_constant, N, n),
            list(chain([x_qreg[i]], y_qreg, aux_qreg))
        )

    return circuit.to_gate()


def modulo_exponentiation_regs(n: int) -> QRegsSpec:
    return {
        'x': 2 * n,
        'y': n,
        'aux': n + 1
    }


def get_partial_constant(constant: int, i: int, N: int) -> int:
    return pow(constant, pow(2, i), mod=N)


def controlled_U(constant, N, n):
    circuit = create_circuit(controlled_U_regs(n), f'C-U({constant})_Mod_{N}')
    ctrl_qreg, x_qreg, aux_qreg, flag_qreg = circuit.qregs

    circuit.append(
        controlled_constant_modulo_multiplier(constant, N, n),
        chain.from_iterable(circuit.qregs)
    )

    for i in range(n):
        circuit.cswap(ctrl_qreg[0], x_qreg[i], aux_qreg[i])

    constant_inv = pow(constant, -1, mod=N)
    circuit.append(
        controlled_constant_modulo_multiplier(constant_inv, N, n).inverse(),
        chain.from_iterable(circuit.qregs)
    )

    return circuit.to_gate()


def controlled_U_regs(n: int) -> QRegsSpec:
    spec = controlled_constant_modulo_multiplier_regs(n)
    return {(name if name != 'y' else 'aux'): size for (name, size) in spec.items()}
