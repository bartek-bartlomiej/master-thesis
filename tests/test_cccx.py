import unittest
from itertools import chain

from qiskit import Aer, QuantumCircuit

from gates.cccx import triple_controlled_not
from tests.wip import test_gate


class CCCXTestCase(unittest.TestCase):
    def test_triple_controlled_not(self):

        def append_gate(qc: QuantumCircuit):
            qc.append(
                triple_controlled_not(),
                list(chain.from_iterable(qc.qregs))
            )

        ctrl = 7

        def test_triple_controlled_negation(x: int, value: int) -> bool:
            expected_value = (x + 1) % 2 if ctrl == 7 else x
            print(expected_value, value, expected_value == value)
            return expected_value == value

        backend = Aer.get_backend('qasm_simulator')

        test_gate(
            backend,
            regs_data=[('ctrl', 3), ('x', 1), ('g', 1)],
            initial_values={'ctrl': ctrl, 'x': 1},
            append_gate=append_gate,
            asserts={'x': test_triple_controlled_negation}
        )

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
