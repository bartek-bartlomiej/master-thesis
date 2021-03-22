from qiskit import QuantumRegister, AncillaRegister, QuantumCircuit


def triple_controlled_not():
    ctrl_qreg = QuantumRegister(3, 'ctrl')
    x_qreg = QuantumRegister(1, 'x')
    g_qreg = AncillaRegister(1, 'g')

    circuit = QuantumCircuit(ctrl_qreg, x_qreg, g_qreg, name='CCCX')
    for _ in range(2):
        circuit.ccx(ctrl_qreg[0], ctrl_qreg[1], g_qreg[0])
        circuit.ccx(ctrl_qreg[2], g_qreg[0], x_qreg[0])

    return circuit.to_gate()
