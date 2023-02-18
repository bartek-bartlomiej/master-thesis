# Abstract class providing project API and base logic of Shor algorithm. 
# Based on corresponding class from Qiskit project.
#
# (C) Copyright IBM 2019, 2020.
# (C) Copyright Bartłomiej Stępień 2021-2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Union, Tuple, Optional

import numpy as np
from abc import ABC, abstractmethod
from itertools import chain

from qiskit import QuantumRegister, AncillaRegister, QuantumCircuit, ClassicalRegister
from qiskit.algorithms import AlgorithmResult
from qiskit.circuit import Instruction
from qiskit.circuit.library import QFT

import logging
import math
from fractions import Fraction

from qiskit.providers import BaseBackend, Backend
from qiskit.utils import QuantumInstance
from qiskit.utils.validation import validate_min


logger = logging.getLogger(__name__)


class Shor(ABC):

    def __init__(self,
                 quantum_instance: Optional[
                     Union[QuantumInstance, BaseBackend, Backend]] = None) -> None:
        self._quantum_instance = None
        if quantum_instance:
            self.quantum_instance = quantum_instance

    @property
    def quantum_instance(self) -> Optional[QuantumInstance]:
        return self._quantum_instance

    @quantum_instance.setter
    def quantum_instance(self, quantum_instance: Union[QuantumInstance,
                                                       BaseBackend, Backend]) -> None:
        if isinstance(quantum_instance, (BaseBackend, Backend)):
            quantum_instance = QuantumInstance(quantum_instance)
        self._quantum_instance = quantum_instance

    def factor(self, a: int, N: int, semi_classical: bool) -> Optional[Tuple[int, int]]:
        shor_result = self.get_order(a, N, semi_classical)
        if shor_result.order:
            order = shor_result.order
            factors = self._get_factors(order, a, N)
            if factors:
                logger.info('Found factors %s from order %s.', factors, order)
                return factors

        return None

    def get_order(self, a: int, N: int, semi_classical=False) -> 'ShorResult':
        self._validate_input(a, N)

        result = ShorResult()

        circuit = self.construct_circuit(a, N, semi_classical, measurement=True)
        counts = self.quantum_instance.execute(circuit).get_counts(circuit)

        result.total_counts = len(counts)
        result.total_shots = self.quantum_instance.run_config.shots

        for measurement, shots in counts.items():
            measurement = self._parse_measurement(measurement, semi_classical)
            order = self._get_order(measurement, a, N)
            if order:
                if order == 1:
                    logger.info('Skip trivial order.')
                    continue

                if result.order and not result.order == order:
                    logger.error(f'Currently computed order {order} differs from already stored: {result.order}.')
                    continue

                result.order = order
                result.successful_counts += 1
                result.successful_shots += shots

        return result

    def construct_circuit(self, a: int, N: int, semi_classical: bool = False, measurement: bool = True):
        self._validate_input(a, N)

        n = N.bit_length()

        if semi_classical:
            if not measurement:
                raise ValueError('Semi-classical implementation have to contain measurement parts.')
            return self._construct_circuit_with_semiclassical_QFT(a, N, n)
        else:
            return self._construct_circuit(a, N, n, measurement)

    @staticmethod
    def _validate_input(a: int, N: int):
        validate_min('N', N, 3)
        validate_min('a', a, 2)

        if N < 1 or N % 2 == 0:
            raise ValueError(f'The input N needs to be an odd integer greater than 1. Provided N = {N}.')
        if a >= N or math.gcd(a, N) != 1:
            raise ValueError(f'The integer a needs to satisfy a < N and gcd(a, N) = 1. Provided a = {a}.')

    @staticmethod
    def _parse_measurement(measurement: str, semi_classical=False):
        if semi_classical:
            measurement = measurement.replace(' ', '')
        return int(measurement, base=2)

    @staticmethod
    def _get_order(measurement: int, a: int, N: int) -> Union[int, None]:
        if measurement == 0:
            logger.info('Measurement = 0, order is trivial: r = 1.')
            return 1

        logger.info(f'Measurement = {measurement}.')
        n = N.bit_length()
        phase = measurement / pow(2, 2 * n)
        logger.info(f'Measured phase = {phase}.')
        fraction = Fraction(phase).limit_denominator(N)
        logger.info(f'Fractional approximation: {fraction}.')

        r = fraction.denominator

        if pow(a, r, mod=N) == 1:
            logger.info(f'Success, order: r = {r} from measurement {measurement}.')
            return r
        else:
            logger.info(f'Denominator {r} is not the order. '
                        f'Trying multiplication for case when numerator and denominator had a common factor.')
            r0 = r
            for i in range(2, n):
                r = i * r0
                if pow(a, r, mod=N) == 1:
                    logger.info(f'Success, order: r = {i}*{r0} = {r}.')
                    return r

            logger.info(f'Multiplication failed, maximum test factor = {n} was too small.')
            return None

    @staticmethod
    def _get_factors(r: int, a: int, N: int) -> Optional[Tuple[int, int]]:
        if r % N == 1:
            logger.info('Odd order, cannot find factors.')
            return None

        guess = math.gcd(pow(a, r // 2) + 1, N)
        if guess in [1, N]:
            logger.info(f'Trivial factor found: {guess}.')
            return 1, N
        else:
            logger.info(f'Non-trivial factor found: {guess}.')
            return guess, N // guess

    def _construct_circuit(self, a: int, N: int, n: int, measurement: bool) -> QuantumCircuit:
        x_qreg = QuantumRegister(2 * n, 'x')
        y_qreg = QuantumRegister(n, 'y')
        aux_qreg = AncillaRegister(self._get_aux_register_size(n), 'aux')

        circuit = QuantumCircuit(x_qreg, y_qreg, aux_qreg, name=self._get_name(a, N))

        circuit.h(x_qreg)
        circuit.x(y_qreg[0])

        modular_exponentiation_gate = self._modular_exponentiation_gate(a, N, n)
        circuit.append(
            modular_exponentiation_gate,
            circuit.qubits
        )

        iqft = QFT(len(x_qreg)).inverse().to_gate()
        circuit.append(
            iqft,
            x_qreg
        )

        if measurement:
            x_creg = ClassicalRegister(2 * n, name='xValue')
            circuit.add_register(x_creg)
            circuit.measure(x_qreg, x_creg)

        return circuit

    def _construct_circuit_with_semiclassical_QFT(self, a: int, N: int, n: int) -> QuantumCircuit:
        x_qreg = QuantumRegister(1, 'x')
        y_qreg = QuantumRegister(n, 'y')
        aux_qreg = AncillaRegister(self._get_aux_register_size(n), 'aux')

        x_creg = [ClassicalRegister(1, f'xV{i}') for i in range(2 * n)]

        name = f'{self._get_name(a, N)} (semi-classical QFT)'
        circuit = QuantumCircuit(x_qreg, y_qreg, aux_qreg, *x_creg, name=name)

        circuit.x(y_qreg[0])

        max_i = 2 * n - 1
        for i in range(0, 2 * n):
            circuit.h(x_qreg)

            partial_constant = pow(a, pow(2, max_i - i), mod=N)
            modular_multiplication_gate = self._modular_multiplication_gate(partial_constant, N, n)
            circuit.append(
                modular_multiplication_gate,
                chain([x_qreg[0]], y_qreg, aux_qreg)
            )

            for j in range(i):
                angle = -np.pi / float(pow(2, i - j))
                circuit.p(angle, x_qreg[0]).c_if(x_creg[j], 1)

            circuit.h(x_qreg)
            circuit.measure(x_qreg[0], x_creg[i][0])
            circuit.x(x_qreg).c_if(x_creg[i], 1)

        return circuit

    @abstractmethod
    def _get_aux_register_size(self, n: int) -> int:
        raise NotImplemented

    def _get_name(self, a: int, N: int) -> str:
        return f'{self._prefix} Shor(a={a}, N={N})'

    @property
    @abstractmethod
    def _prefix(self) -> str:
        raise NotImplemented

    @abstractmethod
    def _modular_exponentiation_gate(self, constant: int, N: int, n: int) -> Instruction:
        raise NotImplemented

    @abstractmethod
    def _modular_multiplication_gate(self, constant: int, N: int, n: int) -> Instruction:
        raise NotImplemented


class ShorResult(AlgorithmResult):

    def __init__(self) -> None:
        super().__init__()
        self._order = None
        self._total_counts = 0
        self._successful_counts = 0
        self._total_shots = 0
        self._successful_shots = 0

    @property
    def order(self) -> Optional[int]:
        return self._order

    @order.setter
    def order(self, value: int) -> None:
        self._order = value

    @property
    def total_counts(self) -> int:
        return self._total_counts

    @total_counts.setter
    def total_counts(self, value: int) -> None:
        self._total_counts = value

    @property
    def successful_counts(self) -> int:
        return self._successful_counts

    @successful_counts.setter
    def successful_counts(self, value: int) -> None:
        self._successful_counts = value

    @property
    def total_shots(self) -> int:
        return self._total_shots

    @total_shots.setter
    def total_shots(self, value: int) -> None:
        self._total_shots = value

    @property
    def successful_shots(self) -> int:
        return self._successful_shots

    @successful_shots.setter
    def successful_shots(self, value: int) -> None:
        self._successful_shots = value
