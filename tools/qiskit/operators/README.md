```markdown
# Tutoriel Qiskit minimal

Ce dépôt contient un script Python d'introduction à Qiskit montrant :
- création de circuits (Hadamard, CNOT, Bell state),
- simulation d'état (Statevector),
- simulation par échantillonnage (Aer / aer_simulator),
- calcul d'une valeur d'attente (Z ⊗ Z) pour un état Bell.

Prérequis
- Python 3.8+ et Qiskit installé.
- Si `from qiskit import Aer` échoue, le script essaiera `from qiskit_aer import Aer` automatiquement (utile si votre environnement n'expose pas Aer via qiskit.providers.aer).

Fichiers
- operator1_qiskit_tutorial.py : script tutoriel (exécutable).

Exécution
- Lancer :
  python3 operator1_qiskit_tutorial.py

- Le script imprimera les vecteurs d'état, probabilités de mesure et valeur d'attente.

Notes
- Le script utilise `qiskit.quantum_info.Statevector` et `qiskit.quantum_info.SparsePauliOp` (API modernes).
- Si vous préférez une version adaptée à un autre backend ou davantage d'exemples (VQE, estimation, circuits paramétrés, circuits sur hardware), dites‑le et je l'ajoute.