#!/usr/bin/env python3
"""
Adaptive Perceval smoke-test

This script attempts to build a tiny 2-mode circuit (a beam splitter),
create a simple input state, pick an available backend, instantiate a
simulator and run a small simulation. It is defensive: it inspects the
available API in the currently installed Perceval and tries several
likely call patterns until one works.

Run:
    python3 perceval_example_run.py

The script will print what it tried and either a result (counts / samples /
amplitudes) or a diagnostic explaining why it failed.
"""
import inspect
import traceback
import pprint

def safe_print(*a, **k):
    print(*a, **k, flush=True)

def try_call(obj, name, *args, **kwargs):
    fn = getattr(obj, name, None)
    if not callable(fn):
        return False, f"No callable {name}"
    try:
        res = fn(*args, **kwargs)
        return True, res
    except Exception as e:
        return False, e

def main():
    try:
        import perceval as pv
    except Exception as e:
        safe_print("perceval import FAILED:", e)
        traceback.print_exc()
        return 1

    safe_print("Perceval version:", getattr(pv, "__version__", getattr(pv, "version", "unknown")))
    safe_print("Top-level: some available names:", ", ".join(sorted([n for n in dir(pv) if not n.startswith("_")]))[:400])

    # Step 1 — build a small circuit (2 modes) and try to add a beam splitter
    circuit = None
    try:
        Circuit = getattr(pv, "Circuit", None)
        if Circuit is None:
            safe_print("No pv.Circuit found -> aborting circuit creation.")
        else:
            circuit = Circuit(2)  # 2-mode circuit
            safe_print("Created Circuit(2):", circuit)
    except Exception as e:
        safe_print("Error creating Circuit(2):", type(e).__name__, e)
        traceback.print_exc()

    # Try to create a BS component
    bs = None
    try:
        BS = getattr(pv, "BS", None)
        if BS is None:
            safe_print("No pv.BS found")
        else:
            bs = BS()  # default parameters
            safe_print("Created BS():", bs)
    except Exception as e:
        safe_print("Error creating BS():", type(e).__name__, e)
        traceback.print_exc()

    # Try to add BS to circuit — try several candidate method names
    if circuit is not None and bs is not None:
        add_candidates = ["add", "add_component", "add_element", "add_unitary", "append"]
        added = False
        for name in add_candidates:
            if hasattr(circuit, name) and callable(getattr(circuit, name)):
                try:
                    # Try several plausible signatures
                    for args in [(bs,), (bs, 0), (bs, 0, 1), (bs, (0,1)), (bs, [0,1])]:
                        try:
                            getattr(circuit, name)(*args)
                            safe_print(f"Added BS to circuit using circuit.{name}{args}")
                            added = True
                            break
                        except TypeError:
                            # signature mismatch: try next
                            continue
                        except Exception as e:
                            safe_print(f"Calling circuit.{name}{args} raised {type(e).__name__}: {e}")
                            break
                    if added:
                        break
                except Exception as e:
                    safe_print(f"Error when trying {name}:", e)
        if not added:
            safe_print("Could not add BS to circuit automatically. Circuit repr follows:")
            try:
                safe_print(repr(circuit))
            except Exception:
                pass

    # Step 2 — prepare a basic input state if BasicState exists
    basic_state = None
    try:
        BasicState = getattr(pv, "BasicState", None)
        if BasicState is not None:
            try:
                basic_state = BasicState([1, 0])  # one photon in mode 0
                safe_print("Created BasicState([1,0]):", basic_state)
            except Exception as e:
                safe_print("BasicState creation failed:", type(e).__name__, e)
        else:
            safe_print("No BasicState class available in perceval.")
    except Exception:
        traceback.print_exc()

    # Step 3 — obtain a backend instance dynamically
    backend_instance = None
    backend_name_used = None
    # Prefer BACKEND_LIST if provided
    backend_list = getattr(pv, "BACKEND_LIST", None)
    tried_names = []
    candidates = []
    if backend_list:
        try:
            # If BACKEND_LIST is a mapping or list, extract names
            if isinstance(backend_list, (list, tuple)):
                candidates = list(backend_list)
            elif isinstance(backend_list, dict):
                candidates = list(backend_list.keys())
        except Exception:
            pass

    # Generic candidate names if BACKEND_LIST absent or empty
    candidates += ["NaiveBackend", "NaiveApproxBackend", "MPSBackend", "SLAPBackend", "SLOSBackend", "IFFBackend", "Clifford2017Backend"]

    # Find BackendFactory
    BackendFactory = getattr(pv, "BackendFactory", None)
    if BackendFactory is None:
        BackendFactory = getattr(getattr(pv, "backends", None), "BackendFactory", None)

    if BackendFactory:
        try:
            bf = BackendFactory()
            safe_print("Instantiated BackendFactory:", bf)
            # try common factory method names
            factory_methods = [m for m in dir(bf) if callable(getattr(bf, m)) and not m.startswith("_")]
            safe_print("BackendFactory methods sample:", factory_methods[:30])
            # try to obtain a backend by trying candidate names and possible factory methods
            for name in candidates:
                if name in tried_names:
                    continue
                tried_names.append(name)
                obtained = False
                for mname in ("get", "get_backend", "create", "create_backend", "get_backend_by_name", "get_backend_from_name", "get_backend_class"):
                    if hasattr(bf, mname):
                        try:
                            fn = getattr(bf, mname)
                            # try calling with the name
                            try:
                                inst = fn(name)
                                if inst is not None:
                                    backend_instance = inst
                                    backend_name_used = name
                                    obtained = True
                                    safe_print(f"Obtained backend via BackendFactory.{mname}('{name}') -> {type(inst)}")
                                    break
                            except Exception as e:
                                # some factories may want different args; ignore
                                safe_print(f"BackendFactory.{mname}('{name}') raised {type(e).__name__}: {e}")
                        except Exception:
                            continue
                if obtained:
                    break
        except Exception as e:
            safe_print("BackendFactory instantiation or usage failed:", type(e).__name__, e)
            traceback.print_exc()
    else:
        safe_print("No BackendFactory available in perceval")

    # If we could not use a factory, try to instantiate backend classes directly if present at top-level
    if backend_instance is None:
        for name in candidates:
            cls = getattr(pv, name, None)
            if cls and inspect.isclass(cls):
                try:
                    inst = cls()  # try default ctor
                    backend_instance = inst
                    backend_name_used = name
                    safe_print(f"Instantiated backend class {name}() -> {type(inst)}")
                    break
                except Exception as e:
                    safe_print(f"Instantiating backend class {name}() failed:", type(e).__name__, e)

    if backend_instance is None:
        safe_print("No backend instance found. Candidates tried:", candidates)
    else:
        safe_print("Using backend instance of type:", type(backend_instance), "name guessed:", backend_name_used)

    # Step 4 — instantiate a Simulator (via Simulator or SimulatorFactory)
    simulator = None
    if backend_instance is not None:
        # try direct Simulator(backend)
        Simulator = getattr(pv, "Simulator", None)
        if Simulator:
            try:
                simulator = Simulator(backend_instance)
                safe_print("Instantiated Simulator(backend_instance):", simulator)
            except Exception as e:
                safe_print("Simulator(backend_instance) construction failed:", type(e).__name__, e)
                traceback.print_exc()

        # Try SimulatorFactory as fallback
        if simulator is None:
            SF = getattr(pv, "SimulatorFactory", None)
            if SF:
                try:
                    sf = SF()
                    safe_print("Created SimulatorFactory:", sf)
                    # try common method names to obtain a simulator
                    for mname in ("get", "get_simulator", "create", "create_simulator", "get_simulator_for"):
                        if hasattr(sf, mname):
                            try:
                                fn = getattr(sf, mname)
                                # try with backend instance or name
                                for arg in (backend_instance, backend_name_used, circuit, None):
                                    try:
                                        simcand = fn(arg) if arg is not None else fn()
                                        if simcand is not None:
                                            simulator = simcand
                                            safe_print(f"SimulatorFactory.{mname}({arg}) -> {type(simcand)}")
                                            break
                                    except Exception as e:
                                        safe_print(f"SimulatorFactory.{mname}({arg}) raised {type(e).__name__}: {e}")
                                if simulator:
                                    break
                            except Exception:
                                continue
                    if simulator is None:
                        safe_print("SimulatorFactory did not return a simulator with tried methods.")
                except Exception as e:
                    safe_print("SimulatorFactory instantiation failed:", e)
            else:
                safe_print("No SimulatorFactory available")

    # Step 5 — run a tiny simulation using likely method names
    if simulator is None:
        safe_print("No simulator available -> cannot run simulation.")
        return 2

    safe_print("Simulator type:", type(simulator))
    # Inspect available methods to find a run/simulate/sample method
    sim_methods = [m for m in dir(simulator) if callable(getattr(simulator, m)) and not m.startswith("_")]
    safe_print("Simulator candidate methods (sample):", sim_methods[:80])

    run_candidates = ["run", "simulate", "sample", "get_amplitudes", "compute", "apply", "sim", "simulate_circuit"]
    result = None
    for rc in run_candidates:
        if hasattr(simulator, rc):
            fn = getattr(simulator, rc)
            # Try different plausible signatures
            trials = []
            if circuit is not None and basic_state is not None:
                trials = [
                    (circuit, basic_state),
                    (basic_state, circuit),
                    (circuit,),
                    (basic_state,),
                ]
            elif circuit is not None:
                trials = [(circuit,),]
            elif basic_state is not None:
                trials = [(basic_state,),]
            else:
                trials = [(),]

            for args in trials:
                try:
                    safe_print(f"Trying simulator.{rc}{args} ...")
                    res = fn(*args)
                    safe_print(f"Call simulator.{rc}{args} succeeded. Result type: {type(res)}")
                    result = res
                    break
                except TypeError as te:
                    safe_print(f"simulator.{rc}{args} TypeError: {te}")
                except Exception as e:
                    safe_print(f"simulator.{rc}{args} Exception: {type(e).__name__}: {e}")
                    # don't stop: try next signature
            if result is not None:
                break

    # If still no result, try to find a 'get_samples' / 'sample' on simulator or a 'run' on backend
    if result is None:
        # try backend-level sampling
        for rc in ("sample", "run", "simulate", "get_samples"):
            if hasattr(backend_instance, rc):
                try:
                    safe_print(f"Trying backend_instance.{rc} ...")
                    fn = getattr(backend_instance, rc)
                    # Try calling on circuit/basic_state
                    try:
                        if circuit is not None and basic_state is not None:
                            result = fn(circuit, basic_state)
                        elif circuit is not None:
                            result = fn(circuit)
                        elif basic_state is not None:
                            result = fn(basic_state)
                        else:
                            result = fn()
                        safe_print(f"backend.{rc} succeeded, result type {type(result)}")
                        break
                    except Exception as e:
                        safe_print(f"backend_instance.{rc} failed: {type(e).__name__}: {e}")
                except Exception:
                    pass

    # Step 6 — pretty print result if any
    if result is None:
        safe_print("No simulation result obtained. Please inspect the above diagnostics.")
        return 3

    safe_print("Simulation result (type):", type(result))
    try:
        # Try to pretty-print common result types
        if hasattr(result, "get_counts"):
            try:
                counts = result.get_counts()
                safe_print("result.get_counts():")
                pprint.pprint(counts)
            except Exception:
                safe_print("result.get_counts() raised:")
                traceback.print_exc()
        elif isinstance(result, dict):
            safe_print("Result dict:")
            pprint.pprint(result)
        else:
            # try to convert to list
            try:
                lst = list(result)
                safe_print("Result iterable -> first 50 elements:")
                pprint.pprint(lst[:50])
            except Exception:
                safe_print("Result repr:")
                safe_print(repr(result)[:1000])
    except Exception:
        safe_print("Error while printing result:")
        traceback.print_exc()

    safe_print("Done.")
    return 0

if __name__ == "__main__":
    exit(main())