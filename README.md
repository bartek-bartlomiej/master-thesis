# Shor's Algorithm for IBM Qiskit

TODO description, references

## Requirements

* Python version >= 3.8
* IBMQ account with saved credentials (for better performance of simulation)  
* Basic knowledge about Shor's algorithm ;)

## Installation

1. Clone repository and enter project directory.
```bash
git clone https://github.com/bartek-bartlomiej/master-thesis.git

cd master-thesis
```

2. Create and activate virtual environment.

```bash
python3.8 -m venv venv

source venv/bin/activate
```

4. Install requirements.

```bash
pip install -r requirements.txt
```

5. For running tests, install development requirements.

```bash
pip install -r requirements-dev.txt
```

## Usage

### For students of quantum course at AGH

Run Jupyter

```bash
jupyter notebook
```

and open `laboratories_notebook.ipynb`.

### For general use

Import class from one of package in `implementations` and create instance:

```python
from implementations.mix import MixShor as Shor

from qiskit import Aer
from qiskit.utils import QuantumInstance

shor = Shor(quantum_instance=QuantumInstance(backend=Aer.get_backend('qasm_simulator')))
```

For constructing quantum part of the algorithm:
```python
circuit = shor.construct_circuit(a=4, N=15, semi_classical=False, measurement=True)
circuit.draw(output='mpl')
```

For acquiring the order `r` of an element `a` in the multiplicative group `(mod N)`:
```python
result = shor.get_order(a=4, N=15, semi_classical=True)
print(result.order)
```

For perform factorization of `N`:
```python
factors = shor.factor(a=4, N=15, semi_classical=True)
print(factors)
```

## Running tests

Run:
```bash
python -m unittest tests/test_implementations.py
```

## License
TODO