from qiskit.circuit import Gate

from gates.modulo_exponentiation import controlled_U, controlled_U_regs
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
        return controlled_U(self._constant, self._N, self._n)

    @property
    def _qregs_spec(self) -> QRegsSpec:
        return controlled_U_regs(self._n)
