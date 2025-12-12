#!/usr/bin/env python3
import sys
import traceback

def safe_print(msg):
    print(msg, flush=True)

def try_import():
    try:
        import perceval as pv
        safe_print("import perceval -> OK")
        return pv
    except Exception as e:
        safe_print("import perceval -> FAIL: %s" % e)
        traceback.print_exc()
        return None

def show_overview(pv):
    try:
        ver = getattr(pv, "__version__", getattr(pv, "version", "unknown"))
    except Exception:
        ver = "unknown (error reading attribute)"
    safe_print(f"perceval version: {ver}")
    try:
        attrs = sorted([a for a in dir(pv) if not a.startswith("_")])
        safe_print("Top-level attributes (first 200 chars):")
        safe_print(", ".join(attrs)[:200] + ("..." if len(attrs) > 0 else ""))
    except Exception as e:
        safe_print("Error listing attributes: %s" % e)

def try_construct(pv, name, *args, **kwargs):
    obj = getattr(pv, name, None)
    if obj is None:
        safe_print(f"{name}: not found")
        return False
    if not callable(obj):
        safe_print(f"{name}: found but not callable (type={type(obj)})")
        return False
    safe_print(f"Trying to construct/call {name}...")
    try:
        inst = obj(*args, **kwargs)
        safe_print(f"{name} instantiation OK -> {type(inst)}")
        try:
            safe_print(f"repr: {repr(inst)[:500]}")
        except Exception:
            pass
        return True
    except Exception as e:
        safe_print(f"{name} instantiation FAILED: {e}")
        traceback.print_exc()
        return False

def main():
    pv = try_import()
    if pv is None:
        safe_print("perceval import failed; install perceval-quandela and retry.")
        sys.exit(1)

    show_overview(pv)

    # Try common constructors / entrypoints if present
    # These attempts are conservative and wrapped in try/except.
    candidates = ["Circuit", "Processor", "Machine", "State", "Source", "Mode", "Simulator"]
    for c in candidates:
        try_construct(pv, c, 1)

    # Try provider-specific import if present
    try:
        # Many installations expose subpackages; list a few and try importing them
        subs = ["components", "toolboxes", "backends", "processors", "circuits"]
        for s in subs:
            try:
                modname = "perceval." + s
                __import__(modname)
                safe_print(f"Imported submodule {modname}")
            except Exception as e:
                safe_print(f"Could not import submodule perceval.{s}: {e}")
    except Exception:
        pass

    # If there is a simulator class exposed, try a tiny run (very conservative).
    # We look for something named "Simulator" or "SimulatorEngine" in top-level attrs.
    simnames = [n for n in dir(pv) if "sim" in n.lower()]
    if simnames:
        safe_print(f"Simulator-like names found: {simnames[:10]}")
    else:
        safe_print("No obvious simulator class name found at top-level.")

    safe_print("Finished perceval quick-check. If you want me to run a specific example, paste the top-level attributes above and I will prepare a concrete example using the available API.")

if __name__ == "__main__":
    main()