#!/usr/bin/env python3
import traceback, pprint

def safe_print(*a, **kw):
    print(*a, **kw, flush=True)

def main():
    try:
        import perceval as pv
    except Exception as e:
        safe_print("Impossible d'importer perceval:", e)
        traceback.print_exc()
        return 2

    safe_print("Perceval version:", getattr(pv, "__version__", "unknown"))

    # 1) Construire circuit et état simple
    try:
        Circuit = getattr(pv, "Circuit")
        circuit = Circuit(2)
        safe_print("Circuit(2) créé")
    except Exception as e:
        safe_print("Erreur création Circuit:", e)
        circuit = None

    try:
        BasicState = getattr(pv, "BasicState")
        basic_state = BasicState([1, 0])
        safe_print("BasicState [1,0] créé")
    except Exception as e:
        safe_print("BasicState non disponible ou erreur:", e)
        basic_state = None

    # 2) Obtenir un backend via BackendFactory si possible
    backend_instance = None
    BackendFactory = getattr(pv, "BackendFactory", None)
    if BackendFactory:
        try:
            bf = BackendFactory()
            safe_print("BackendFactory instanciée")
            # Essayer quelques backends connus (NaiveBackend, SLOS, etc.)
            for name in ("NaiveBackend", "NaiveApproxBackend", "SLOSBackend", "SLAPBackend", "Clifford2017Backend", "SLOS"):
                try:
                    inst = bf.get_backend(name)
                    if inst is not None:
                        backend_instance = inst
                        safe_print(f"Backend obtenu via Factory: {name} -> {type(inst)}")
                        break
                except Exception as ee:
                    # ignore
                    pass
            # fallback: bf.list() then get first
            if backend_instance is None:
                try:
                    lst = bf.list()
                    safe_print("BackendFactory.list():", lst)
                    if lst:
                        backend_instance = bf.get_backend(lst[0])
                        safe_print("Backend obtenu via liste:", type(backend_instance))
                except Exception:
                    pass
        except Exception as e:
            safe_print("Erreur BackendFactory:", e)

    # 3) Si pas de factory, tenter d'instancier des classes top-level
    if backend_instance is None:
        for cand in ("NaiveBackend", "NaiveApproxBackend", "MPSBackend", "Clifford2017Backend", "SLOSBackend", "SLOS"):
            cls = getattr(pv, cand, None)
            if cls and callable(cls):
                try:
                    backend_instance = cls()
                    safe_print(f"Backend instancié directement: {cand} -> {type(backend_instance)}")
                    break
                except Exception as e:
                    safe_print(f"Instanciation {cand}() échouée:", e)

    if backend_instance is None:
        safe_print("Aucun backend trouvé — arrêt.")
        return 3

    # 4) Créer le Simulator (ou obtenir via factory)
    Simulator = getattr(pv, "Simulator", None)
    simulator = None
    if Simulator:
        try:
            simulator = Simulator(backend_instance)
            safe_print("Simulator instancié:", type(simulator))
        except Exception as e:
            safe_print("Instantiation Simulator échouée:", e)

    # 5) Essayer plusieurs schémas d'appel : set_circuit + probs(basic_state), ou set_circuit + probs(), ou sim.probs(circuit, basic_state) etc.
    tried = []
    result = None
    # helper pour tenter une action en imprimant exceptions
    def try_action(desc, fn, *args, **kwargs):
        nonlocal result
        safe_print("-> Try:", desc)
        try:
            r = fn(*args, **kwargs)
            safe_print("   SUCCESS:", desc, "->", type(r))
            result = r
            return True
        except Exception as e:
            safe_print("   FAIL:", desc, "->", type(e).__name__, e)
            return False

    # If simulator exists, try to set circuit/state then call probs/sample/etc
    sim_methods = ["probs", "probability", "prob_amplitude", "probs_svd", "probability_svd", "sample", "run"]
    set_methods = ["set_circuit", "set_circuit_and_config", "set_initial_state", "set_state", "set_basic_state", "set_input", "set_initial", "set_circuit_and_state"]

    if simulator:
        # try set_circuit on simulator
        for sm in set_methods:
            if hasattr(simulator, sm) and circuit is not None:
                try_action(f"simulator.{sm}(circuit)", getattr(simulator, sm), circuit)
                if result is not None:
                    break
        # try set_state on simulator
        for sm in set_methods:
            if hasattr(simulator, sm) and basic_state is not None:
                try_action(f"simulator.{sm}(basic_state)", getattr(simulator, sm), basic_state)
                if result is not None:
                    break
        # Now try calling run/probs methods with only basic_state or nothing
        for m in sim_methods:
            if result is not None:
                break
            if hasattr(simulator, m):
                fn = getattr(simulator, m)
                # try various plausible signatures
                if basic_state is not None and circuit is not None:
                    try_action(f"simulator.{m}(basic_state)", fn, basic_state)
                    if result is not None:
                        break
                    try_action(f"simulator.{m}(circuit)", fn, circuit)
                    if result is not None:
                        break
                try_action(f"simulator.{m}()", fn)
                if result is not None:
                    break

    # If still none, try backend_instance similarly
    if result is None and backend_instance:
        for sm in set_methods:
            if hasattr(backend_instance, sm) and circuit is not None:
                try_action(f"backend.{sm}(circuit)", getattr(backend_instance, sm), circuit)
                if result is not None:
                    break
        for sm in set_methods:
            if hasattr(backend_instance, sm) and basic_state is not None:
                try_action(f"backend.{sm}(basic_state)", getattr(backend_instance, sm), basic_state)
                if result is not None:
                    break
        for m in sim_methods + ["sample", "run"]:
            if result is not None:
                break
            if hasattr(backend_instance, m):
                fn = getattr(backend_instance, m)
                # try several call patterns
                try_action(f"backend.{m}(circuit, basic_state)", fn, circuit, basic_state)
                if result is not None:
                    break
                try_action(f"backend.{m}(basic_state)", fn, basic_state)
                if result is not None:
                    break
                try_action(f"backend.{m}()", fn)
                if result is not None:
                    break

    # Afficher résultat ou diagnostic final
    if result is None:
        safe_print("Aucun résultat obtenu après essais. Voir logs ci-dessus.")
        return 4

    safe_print("=== Résultat brut ===")
    try:
        if hasattr(result, "get_counts"):
            safe_print("result.get_counts():")
            pprint.pprint(result.get_counts())
        elif isinstance(result, dict):
            pprint.pprint(result)
        else:
            try:
                it = list(result)
                safe_print("result iterable -> sample:")
                pprint.pprint(it[:50])
            except Exception:
                safe_print("result repr:", repr(result)[:1000])
    except Exception as e:
        safe_print("Erreur affichage résultat:", e)
        traceback.print_exc()

    safe_print("Terminé.")
    return 0

if __name__ == "__main__":
    exit(main())