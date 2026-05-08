#!/usr/bin/env python3
import inspect
import importlib
import traceback
import sys

def show(name, obj):
    print("="*80)
    print(name)
    print("- type:", type(obj))
    try:
        print("- repr:", repr(obj)[:300])
    except Exception:
        pass
    if inspect.isclass(obj) or inspect.isfunction(obj) or inspect.ismodule(obj):
        try:
            sig = inspect.signature(obj)
            print("- signature:", sig)
        except Exception:
            pass
        try:
            doc = inspect.getdoc(obj)
            if doc:
                print("- doc (first 400 chars):")
                print(doc[:400].strip().replace("\n", " "))
        except Exception:
            pass
    print()

def try_get(mod, name):
    try:
        obj = getattr(mod, name)
        show(f"{mod.__name__}.{name}", obj)
        return obj
    except Exception as e:
        print(f"Could not get {name} from {mod.__name__}: {e}")
        return None

def list_module(modname):
    try:
        mod = importlib.import_module(modname)
        print("\nMODULE:", modname, "->", getattr(mod, "__file__", None))
        members = sorted([m for m in dir(mod) if not m.startswith("_")])
        print("Top-level members (first 200):", members[:200])
        return mod
    except Exception as e:
        print(f"Failed to import module {modname}: {e}")
        traceback.print_exc()
        return None

def main():
    print("Python:", sys.executable)
    pv = list_module("perceval")
    if pv is None:
        return
    # inspect top-level useful names
    candidates = ["Circuit", "ACircuit", "BS", "Source", "AProcessor", "Processor", 
                  "Simulator", "SimulatorFactory", "AStrongSimulationBackend", "FFSimulator",
                  "ABackend", "ASamplingBackend"]
    for name in candidates:
        try_get(pv, name)

    # Inspect submodules likely to contain components / simulators
    comps = list_module("perceval.components")
    sims = list_module("perceval.simulators")
    backends = list_module("perceval.backends")

    # In components, show a few frequent classes if present
    if comps:
        for name in ["Circuit", "Source", "BS", "Detector", "Processor", "AComponent"]:
            try_get(comps, name)

    # In simulators, show a few names
    if sims:
        for name in ["Simulator", "SimulatorFactory", "FFSimulator", "NoisySamplingSimulator"]:
            try_get(sims, name)

    print("\nFinished inspection. Copy the full output and I will prepare a runnable Perceval example based on the available API.")
    
if __name__ == "__main__":
    main()