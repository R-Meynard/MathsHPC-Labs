#!/usr/bin/env python3
# Petit test : utiliser Aer depuis le package qiskit_aer installé directement
from qiskit import QuantumCircuit, transpile
import qiskit
print("qiskit version:", qiskit.__version__)

try:
    import qiskit_aer as qaa
    print("qiskit_aer module:", getattr(qaa, "__file__", "no __file__"))
    # Try to import Aer from qiskit_aer
    from qiskit_aer import Aer
    print("Got Aer from qiskit_aer:", Aer)
    backend = Aer.get_backend("aer_simulator")
    print("Backend:", backend)
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    tq = transpile(qc, backend)
    job = backend.run(tq, shots=256)
    res = job.result()
    print("counts:", res.get_counts())
except Exception as e:
    import traceback
    print("Error using qiskit_aer:", type(e).__name__, e)
    traceback.print_exc()