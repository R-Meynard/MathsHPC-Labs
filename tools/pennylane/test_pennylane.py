#!/usr/bin/env python3
import pennylane as qml
import numpy as np

print("PennyLane version:", qml.__version__)

dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    return qml.expval(qml.PauliZ(0))

print("Circuit result (expect ~0):", float(circuit()))