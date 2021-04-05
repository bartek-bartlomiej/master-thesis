import unittest

from tests.gate_tests.carry import Test


class CarryTestCase(unittest.TestCase):
    def test_too_much(self):
        for i in range(2, 5):
            self._test_for_n_qubits(i)

    def test_for_1_qubit(self):
        n = 1
        N = 2 ** n
        G = 2 ** n
        for constant in range(N):
            with self.subTest(constant=constant):
                self._test(constant, n, N, G)

    def _test_for_n_qubits(self, n: int):
        N = 2 ** n
        G = 2 ** (n - 1)
        for constant in range(N):
            with self.subTest(constant=constant):
                self._test(constant, n, N, G)

    def _test(self, constant, n, N, G):
        test = Test(constant, n, self)
        params = [{'x': x, 'g': g}
                  for g in range(G) for x in range(N)]
        test.run_subtests(params)


if __name__ == '__main__':
    unittest.main()
