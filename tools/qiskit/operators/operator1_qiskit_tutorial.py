
#!/usr/bin/env python3
"""
Qiskit tutorial - minimal examples

Examples included:
1) Build a Bell state and inspect the Statevector (amplitudes).
2) Run the circuit on a simulator to get measurement counts (Aer).
3) Compute expectation value of Z⊗Z on the Bell state.

This script tries to import Aer from qiskit.providers.aer, and falls back
to qiskit_aer if necessary (useful when "from qiskit import Aer" fails).
"""
from math import sqrt
import numpy as np

# Qiskit imports (modern APIs)
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, Operator, SparsePauliOp

# Try Aer import with fallback to qiskit_aer if needed
try:
    # preferred when qiskit exposes Aer
    from qiskit.providers.aer import Aer
    aer_source = "qiskit.providers.aer"
except Exception:
    try:
        # fallback: qiskit_aer package (works if installed standalone)
        import qiskit_aer as _qaa  # noqa: F401
        from qiskit_aer import Aer
        aer_source = "qiskit_aer"
    except Exception:
        Aer = None
        aer_source = None

def example_bell_state():
    print("Example 1 — Bell state (|00> + |11>)/√2 (statevector)")
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    # get statevector from the circuit
    sv = Statevector.from_instruction(qc)
    print("Statevector amplitudes (index -> amplitude):")
    for i, amp in enumerate(sv.data):
        print(f"  |{i:02b}> -> {amp}")
    print()

def example_measure_counts(shots=1024):
    print("Example 2 — Measurement sampling (counts) with Aer simulator")
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    # add measurement
    qc.measure([0, 1], [0, 1])

    if Aer is None:
        print("  Aer is not available in this environment; cannot run sampling.")
        return

    backend = Aer.get_backend("aer_simulator")
    # transpile/assemble then run; Aer simulator expects circuits with measurements
    tqc = transpile(qc, backend)
    job = backend.run(tqc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    print(f"  Using Aer backend from: {aer_source}")
    print("  Measurement counts (sample):")
    for state, c in counts.items():
        print(f"    {state} -> {c}")
    print()

def example_expectation_z_z():
    print("Example 3 — Expectation value <Z⊗Z> on the Bell state")
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    sv = Statevector.from_instruction(qc)

    # Build Z⊗Z operator using SparsePauliOp
    op = SparsePauliOp.from_list([("ZZ", 1.0)])
    # Statevector.expectation_value accepts Operator or SparsePauliOp
    try:
        exp_val = sv.expectation_value(op)
    except Exception:
        # fallback: convert to dense Operator matrix then compute
        mat = Operator(op.to_matrix())
        exp_val = np.vdot(sv.data, mat.data @ sv.data)

    print("  Expectation <Z⊗Z> =", exp_val)
    print("  For the Bell state we expect +1 (perfect correlation).")
    print()

def example_visual_check_unitary():
    print("Example 4 — Circuit unitary matrix (2-mode BS-like example)")
    # simple 2-qubit circuit: H, CX -> its 4x4 unitary
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    # Try to get unitary via Statevector on basis vectors (cheap for small circuits)
    # Build matrix columns by evolving computational basis states
    dim = 2**2
    U = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        # prepare basis state |i>
        b = Statevector.from_label(f"{i:02b}")
        sv_out = b.evolve(QuantumCircuit(qc)) if False else Statevector.from_instruction(qc).data  # placeholder
    # Simpler: use Statevector.from_instruction on basis vectors composed with circuit
    # Proper approach: use Operator(qc) if qiskit version supports it
    try:
        from qiskit.quantum_info import Operator as QOperator
        U = QOperator(qc).data
        print("  Unitary matrix (4x4):")
        print(U)
    except Exception:
        print("  Could not extract unitary via Operator(qc) with current Qiskit.")
    print()

def main():
    print("Qiskit minimal tutorial")
    print("-----------------------")
    print("This environment Aer backend source:", aer_source)
    print()

    example_bell_state()
    example_measure_counts(shots=512)
    example_expectation_z_z()
    # unitary example might be backend/version-dependent
    example_visual_check_unitary()

    print("Tutorial finished. Next steps you may try:")
    print(" - Change the circuit (add phase gates, try 2-photon experiments).")
    print(" - Use different backends (qiskit-aer, AerSimulator) if available.")
    print(" - Explore qiskit.primitives (Sampler/Estimator) for modern execution APIs.")

if __name__ == "__main__":
    main()

