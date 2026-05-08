#!/usr/bin/env python3
import traceback, pprint, inspect

def safe_print(*a, **k):
    print(*a, **k, flush=True)

def try_call(obj, name, *args, **kwargs):
    if not hasattr(obj, name):
        return False, f"no {name}"
    fn = getattr(obj, name)
    if not callable(fn):
        return False, f"{name} not callable"
    try:
        res = fn(*args, **kwargs)
        return True, res
    except Exception as e:
        return False, e

def main():
    try:
        import perceval as pv
    except Exception as e:
        safe_print("Impossible d'importer perceval:", e)
        traceback.print_exc()
        return 2

    safe_print("Perceval version:", getattr(pv, "__version__", "unknown"))

    # Build a simple circuit description (we'll prefer Processor to compose it)
    try:
        BasicState = getattr(pv, "BasicState")
        basic_state = BasicState([1, 0])
        safe_print("BasicState created:", basic_state)
    except Exception as e:
        safe_print("Impossible de créer BasicState:", e)
        basic_state = None

    # Prepare a Processor instance (try several ways)
    backend_instance = None
    Processor = getattr(pv, "Processor", None)
    BackendFactory = getattr(pv, "BackendFactory", None)

    # Try BackendFactory first to get a backend instance
    if BackendFactory:
        try:
            bf = BackendFactory()
            safe_print("BackendFactory created")
            # Prefer SLOS or Naive backends for small examples
            preferred = ["SLOS", "NaiveBackend", "NaiveApproxBackend", "SLOSBackend", "SLAPBackend", "MPSBackend", "Clifford2017Backend"]
            for name in preferred:
                try:
                    inst = bf.get_backend(name)
                    if inst is not None:
                        backend_instance = inst
                        safe_print(f"Got backend via factory: {name} -> {type(inst)}")
                        break
                except Exception:
                    continue
            # fallback: try list()
            if backend_instance is None:
                try:
                    lst = bf.list()
                    safe_print("BackendFactory.list():", lst)
                    if lst:
                        backend_instance = bf.get_backend(lst[0])
                        safe_print("Got backend via list:", type(backend_instance))
                except Exception:
                    pass
        except Exception as e:
            safe_print("BackendFactory usage failed:", e)

    # If no backend instance, try to instantiate by name via Processor string constructor later
    proc = None
    used_proc_creation = None
    if Processor:
        # Try Processor with backend instance (if available)
        if backend_instance is not None:
            ok, res = try_call(Processor, "__call__") if False else (False, None)
            try:
                # try Processor(backend_instance, m_circuit=2)
                try:
                    proc = Processor(backend_instance, 2)
                    used_proc_creation = "Processor(backend_instance, 2)"
                    safe_print("Created Processor with backend instance:", proc)
                except Exception as e:
                    safe_print("Processor(backend_instance,2) failed:", e)
                    proc = None
                # try alternative: Processor("SLOS", 2)
                if proc is None:
                    try:
                        proc = Processor("SLOS", 2)
                        used_proc_creation = 'Processor("SLOS", 2)'
                        safe_print('Created Processor("SLOS", 2):', proc)
                    except Exception as e:
                        safe_print('Processor("SLOS",2) failed:', e)
                        proc = None
            except Exception:
                pass
        else:
            # No backend instance: try to create Processor by string name
            try:
                proc = Processor("SLOS", 2)
                used_proc_creation = 'Processor("SLOS", 2)'
                safe_print('Created Processor("SLOS", 2):', proc)
            except Exception as e:
                safe_print('Processor("SLOS",2) failed:', e)
                proc = None

    if proc is None:
        safe_print("Impossible de créer un Processor automatiquement. Voici des infos utiles pour débogage:")
        safe_print("Processor object:", Processor)
        safe_print("BackendFactory:", BackendFactory)
        return 3

    # Try to add a BS component to the Processor (several signatures)
    BS = getattr(pv, "BS", None)
    if BS is None:
        safe_print("BS component non disponible dans perceval.")
    else:
        added = False
        add_attempts = [
            ("add", (BS(), 0, 1)),
            ("add", (BS(), (0, 1))),
            ("add_component", (BS(), 0, 1)),
            ("add_component", (BS(), (0,1))),
            ("append", (BS(), (0,1))),
            ("add_unitary", (BS(), (0,1))),
            ("add", (BS(),)),
        ]
        for name, args in add_attempts:
            if hasattr(proc, name):
                try:
                    getattr(proc, name)(*args)
                    safe_print(f"Added BS via proc.{name}{args}")
                    added = True
                    break
                except AssertionError as ae:
                    safe_print(f"proc.{name}{args} -> AssertionError: {ae}")
                except TypeError as te:
                    safe_print(f"proc.{name}{args} -> TypeError: {te}")
                except Exception as e:
                    safe_print(f"proc.{name}{args} -> Exception: {type(e).__name__}: {e}")
                    safe_print(traceback.format_exc())
        if not added:
            safe_print("Ajout automatique du BS au Processor a échoué. Le Processor peut toutefois accepter un circuit lors de l'instanciation.")

    # Try to run / simulate: Processor often has methods like run/sample/process/compute
    run_methods = ["run", "sample", "process", "compute", "execute", "simulate"]
    result = None
    for rm in run_methods:
        if hasattr(proc, rm):
            fn = getattr(proc, rm)
            # try plausible signatures
            tries = []
            if basic_state is not None:
                tries = [(basic_state,), ()]
            else:
                tries = [()]
            for args in tries:
                try:
                    safe_print(f"Trying proc.{rm}{args} ...")
                    r = fn(*args)
                    safe_print(f"proc.{rm}{args} -> success, type {type(r)}")
                    result = r
                    break
                except TypeError as te:
                    safe_print(f"proc.{rm}{args} -> TypeError: {te}")
                except Exception as e:
                    safe_print(f"proc.{rm}{args} -> Exception: {type(e).__name__}: {e}")
            if result is not None:
                break

    # If Processor did not produce result, try backend on processor (proc.backend or proc._backend)
    if result is None:
        backend_attrs = ["backend", "_backend", "get_backend"]
        backend_obj = None
        for a in backend_attrs:
            if hasattr(proc, a):
                backend_obj = getattr(proc, a)
                safe_print("Recovered backend object from Processor via attr", a, "->", backend_obj)
                break
        if backend_obj:
            for rm in ("sample", "run", "get_samples", "simulate", "probs", "probability"):
                if hasattr(backend_obj, rm):
                    fn = getattr(backend_obj, rm)
                    try:
                        safe_print(f"Trying backend_obj.{rm}(basic_state) ...")
                        r = fn(basic_state) if basic_state is not None else fn()
                        safe_print(f"backend_obj.{rm} succeeded -> {type(r)}")
                        result = r
                        break
                    except Exception as e:
                        safe_print(f"backend_obj.{rm} raised {type(e).__name__}: {e}")

    if result is None:
        safe_print("Aucun résultat obtenu via Processor / backend automatique. Affichage d'info pour debug :")
        try:
            safe_print("Processor methods sample:", [m for m in dir(proc) if not m.startswith("_")][:200])
        except Exception:
            pass
        return 4

    # Print/interpret result
    safe_print("=== Résultat brut obtenu ===")
    try:
        if hasattr(result, "get_counts"):
            safe_print("result.get_counts():")
            pprint.pprint(result.get_counts())
        elif isinstance(result, dict):
            pprint.pprint(result)
        else:
            try:
                it = list(result)
                safe_print("Result iterable sample:")
                pprint.pprint(it[:50])
            except Exception:
                safe_print("Result repr:", repr(result)[:1000])
    except Exception as e:
        safe_print("Erreur lors de l'affichage du résultat:", e)
        traceback.print_exc()

    safe_print("Terminé.")
    return 0

if __name__ == "__main__":
    exit(main())