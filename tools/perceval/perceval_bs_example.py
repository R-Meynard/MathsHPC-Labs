#!/usr/bin/env python3
"""
Exemple minimal Perceval : construire un circuit 2 modes avec un BS 50/50,
le charger dans le simulateur et calculer les probabilités pour l'état |1,0>.

Usage:
    python3 perceval_bs_example.py
"""
import traceback, pprint

def safe_print(*a, **k):
    print(*a, **k, flush=True)

def main():
    try:
        import perceval as pv
    except Exception as e:
        safe_print("Impossible d'importer perceval:", e)
        return 2

    safe_print("Perceval version:", getattr(pv, "__version__", "unknown"))

    try:
        # 1) Construire un circuit 2 modes et y ajouter un BS correctement
        Circuit = pv.Circuit
        BS = pv.BS
        circuit = Circuit(2)
        bs = BS()  # paramètres par défaut (50/50)
        # IMPORTANT : signature Circuit.add(port_range, component, ...)
        circuit.add((0, 1), bs)
        safe_print("Circuit after adding BS:", repr(circuit))
    except Exception as e:
        safe_print("Erreur lors de la création du circuit / ajout du BS:", type(e).__name__, e)
        traceback.print_exc()
        return 3

    try:
        # 2) état d'entrée : 1 photon en mode 0
        BasicState = pv.BasicState
        state = BasicState([1, 0])
        safe_print("Input BasicState:", state)
    except Exception as e:
        safe_print("Erreur création BasicState:", e)
        traceback.print_exc()
        return 4

    try:
        # 3) obtenir un backend et créer le simulateur
        bf = pv.BackendFactory()
        # choisir explicitement SLOS (fonctionne dans votre conteneur)
        backend = bf.get_backend("SLOS")
        safe_print("Backend chosen:", backend)
        Simulator = pv.Simulator
        sim = Simulator(backend)
        safe_print("Simulator instantiated:", type(sim))
    except Exception as e:
        safe_print("Erreur obtention backend / simulateur:", e)
        traceback.print_exc()
        return 5

    try:
        # 4) enregistrer le circuit dans le simulateur (signature : set_circuit(circuit, m=None))
        sim.set_circuit(circuit)
        safe_print("Circuit enregistré dans le simulateur.")
    except Exception as e:
        safe_print("Erreur sim.set_circuit:", type(e).__name__, e)
        traceback.print_exc()
        return 6

    try:
        # 5) calculer les probabilités / obtenir un échantillon
        # d'après vos tests précédents, sim.probs(state) fonctionne après set_circuit
        res = sim.probs(state)
        safe_print("Résultat brut (type):", type(res))
        # afficher le résultat de manière lisible
        try:
            # res est souvent une distribution ou un itérable d'états
            lst = list(res)
            safe_print("Samples / states (premiers éléments):")
            pprint.pprint(lst[:50])
        except Exception:
            safe_print("Résultat (repr):")
            safe_print(repr(res)[:1000])
    except Exception as e:
        safe_print("Erreur lors de sim.probs:", type(e).__name__, e)
        traceback.print_exc()
        return 7

    safe_print("Terminé avec succès.")
    return 0

if __name__ == "__main__":
    exit(main())