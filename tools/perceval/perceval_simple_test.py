#!/usr/bin/env python3
"""
Petit test Perceval : on construit un circuit 2 modes, on tente d'ajouter un BS
(s'il accepte l'appel), on crée un état d'entrée simple et on simule avec le
simulateur disponible en appelant la méthode 'probs' / 'probability' / 'prob_amplitude'
suivant ce qui est supporté.

Exécution :
    python3 perceval_simple_test.py
"""
import traceback
import pprint

def safe_print(*a, **k):
    print(*a, **k, flush=True)

def try_add_bs(circuit, BS):
    bs = None
    try:
        bs = BS()
    except Exception as e:
        safe_print("Création BS() échouée:", e)
        return False
    safe_print("BS instance:", bs)
    # Essayer plusieurs signatures plausibles pour ajouter le BS au circuit
    attempts = [
        ("add", (bs, 0, 1)),
        ("add", (bs, (0, 1))),
        ("add", (bs, [0, 1])),
        ("append", (bs, (0, 1))),
        ("add_component", (bs, 0, 1)),
        ("add_unitary", (bs, (0, 1))),
        ("add", (bs, 0)),  # parfois l'API utilise (component, port)
    ]
    for name, args in attempts:
        fn = getattr(circuit, name, None)
        if not callable(fn):
            continue
        try:
            fn(*args)
            safe_print(f"Succès: circuit.{name}{args}")
            return True
        except AssertionError as ae:
            safe_print(f"Assertion lors de circuit.{name}{args}: {ae}")
        except TypeError as te:
            safe_print(f"TypeError lors de circuit.{name}{args}: {te}")
        except Exception as e:
            safe_print(f"Erreur lors de circuit.{name}{args}: {type(e).__name__}: {e}")
            safe_print(traceback.format_exc())
    return False

def main():
    try:
        import perceval as pv
    except Exception as e:
        safe_print("Impossible d'importer perceval:", e)
        return 2

    safe_print("Perceval version:", getattr(pv, "__version__", "unknown"))

    # 1) Construire un circuit 2 modes
    try:
        Circuit = getattr(pv, "Circuit")
        circuit = Circuit(2)
        safe_print("Circuit(2) créé OK:", circuit)
    except Exception as e:
        safe_print("Erreur création Circuit:", e)
        return 3

    # 2) Essayer d'ajouter un BS si BS présent
    BS = getattr(pv, "BS", None)
    if BS is None:
        safe_print("BS non disponible dans perceval; on continue sans BS.")
    else:
        ok = try_add_bs(circuit, BS)
        if not ok:
            safe_print("Ajout automatique du BS échoué — le circuit restera vide (identité).")

    # 3) Créer un état d'entrée simple (BasicState)
    BasicState = getattr(pv, "BasicState", None)
    basic_state = None
    if BasicState is not None:
        try:
            basic_state = BasicState([1, 0])  # 1 photon en mode 0
            safe_print("BasicState créé:", basic_state)
        except Exception as e:
            safe_print("Erreur création BasicState:", e)
    else:
        safe_print("BasicState non disponible dans perceval; on continuera sans état explicite.")

    # 4) Obtenir un backend via BackendFactory si possible
    backend_instance = None
    try:
        BackendFactory = getattr(pv, "BackendFactory", None)
        if BackendFactory is not None:
            bf = BackendFactory()
            safe_print("BackendFactory instanciée:", bf)
            # prefer built-in naive backends if present
            preferred = ["NaiveBackend", "NaiveApproxBackend", "MPSBackend", "SLAPBackend", "SLOSBackend", "IFFBackend", "Clifford2017Backend"]
            for name in preferred:
                try:
                    inst = bf.get_backend(name)
                    if inst is not None:
                        backend_instance = inst
                        safe_print(f"Backend obtenu: {name} ->", type(inst))
                        break
                except Exception as e:
                    # ignore and try next
                    pass
            # fallback: try factory.list or BACKEND_LIST
            if backend_instance is None:
                try:
                    lst = bf.list()
                    safe_print("BackendFactory.list() ->", lst)
                    if lst:
                        try:
                            backend_instance = bf.get_backend(lst[0])
                            safe_print("Backend obtenu via liste:", type(backend_instance))
                        except Exception:
                            backend_instance = None
                except Exception:
                    pass
    except Exception as e:
        safe_print("Erreur en manipulant BackendFactory:", e)

    # If still none, try to instantiate a backend class by name if exported at top-level
    if backend_instance is None:
        for cand in ("NaiveBackend", "NaiveApproxBackend", "MPSBackend", "Clifford2017Backend"):
            cls = getattr(pv, cand, None)
            if cls and callable(cls):
                try:
                    backend_instance = cls()
                    safe_print(f"Instancié backend direct {cand} ->", type(backend_instance))
                    break
                except Exception as e:
                    safe_print(f"Instanciation {cand}() failed:", e)

    if backend_instance is None:
        safe_print("Aucun backend disponible — arrêt.")
        return 4

    # 5) Construire un Simulator et appeler une méthode de probabilité
    Simulator = getattr(pv, "Simulator", None)
    if Simulator is None:
        safe_print("Simulator non disponible dans perceval -> arrêt.")
        return 5

    try:
        sim = Simulator(backend_instance)
        safe_print("Simulator instancié:", sim)
    except Exception as e:
        safe_print("Erreur instanciation Simulator:", e)
        return 6

    # Essayer des méthodes de simulation / probabilité connues
    sim_method_candidates = ["probs", "probability", "prob_amplitude", "probability_amplitude", "probs_svd", "probability_svd"]
    result = None
    for m in sim_method_candidates:
        if hasattr(sim, m):
            fn = getattr(sim, m)
            try:
                safe_print(f"Appel de sim.{m} avec (circuit, basic_state) ...")
                if basic_state is not None:
                    result = fn(circuit, basic_state)
                else:
                    result = fn(circuit)
                safe_print(f"sim.{m} a réussi ; type résultat: {type(result)}")
                break
            except Exception as e:
                safe_print(f"sim.{m} a levé {type(e).__name__}: {e}")

    # Si pas de résultat, essayer méthodes alternatives sur le backend
    if result is None:
        for m in ("sample", "run", "simulate", "get_samples"):
            if hasattr(backend_instance, m):
                try:
                    fn = getattr(backend_instance, m)
                    safe_print(f"Appel de backend.{m} ...")
                    if basic_state is not None:
                        result = fn(circuit, basic_state)
                    else:
                        result = fn(circuit)
                    safe_print(f"backend.{m} a réussi ; type résultat: {type(result)}")
                    break
                except TypeError as te:
                    safe_print(f"backend.{m} TypeError: {te}")
                except Exception as e:
                    safe_print(f"backend.{m} Exception: {type(e).__name__}: {e}")

    if result is None:
        safe_print("Aucun résultat de simulation obtenu. Voir diagnostics ci-dessus.")
        return 7

    safe_print("=== Résultat de simulation (tentative d'interprétation) ===")
    # Afficher quelques formats usuels
    try:
        if hasattr(result, "get_counts"):
            safe_print("result.get_counts():")
            pprint.pprint(result.get_counts())
        elif isinstance(result, dict):
            safe_print("Result dict:")
            pprint.pprint(result)
        else:
            # essayer de convertir en liste
            try:
                lst = list(result)
                safe_print("Result iterable -> premier éléments:")
                pprint.pprint(lst[:50])
            except Exception:
                safe_print("Result repr:")
                safe_print(repr(result)[:1000])
    except Exception as e:
        safe_print("Erreur lors de l'affichage du résultat:", e)
        safe_print(traceback.format_exc())

    safe_print("Fin du test.")
    return 0

if __name__ == "__main__":
    exit(main())