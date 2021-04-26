from qiskit.circuit import Gate

from gates.modulo_exponentiation import modulo_exponentiation, modulo_exponentiation_regs
from tests.gate_experiment import GateExperiment
from utils.typing_ import QRegsSpec


class Experiment(GateExperiment):
    def __init__(self, constant: int, N: int, n: int):
        super().__init__()
        self._constant = constant
        self._N = N
        self._n = n

    @property
    def _gate(self) -> Gate:
        return modulo_exponentiation(self._constant, self._N, self._n)

    @property
    def _qregs_spec(self) -> QRegsSpec:
        return modulo_exponentiation_regs(self._n)
