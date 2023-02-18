from qiskit.circuit import Gate

from gates.haner.constant_modulo_adder import double_controlled_constant_modulo_adder, \
    double_controlled_constant_modulo_adder_regs
from tests.gate_experiment import GateExperiment
from utils.custom_typing import QRegsSpec


class Experiment(GateExperiment):
    def __init__(self, constant: int, N: int, n: int):
        super().__init__()
        self._constant = constant
        self._N = N
        self._n = n

    @property
    def _gate(self) -> Gate:
        return double_controlled_constant_modulo_adder(self._constant, self._N, self._n)

    @property
    def _qregs_spec(self) -> QRegsSpec:
        return double_controlled_constant_modulo_adder_regs(self._n)
