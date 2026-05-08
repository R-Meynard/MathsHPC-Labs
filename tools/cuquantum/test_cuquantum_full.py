#!/usr/bin/env python3
"""
Test complet d'import et inspection pour cuQuantum installé dans le venv.

Usage:
  . .cuq-venv/bin/activate
  python3 test_cuquantum_full.py
"""
import sys
import importlib
import pkgutil
import pprint

print("Python:", sys.version)
print()

# top-level modules detected containing 'cuquantum'
mods = [m.name for m in pkgutil.iter_modules() if "cuquantum" in m.name.lower()]
print("pkgutil detected modules containing 'cuquantum':", mods)
print()

def try_import(name):
    try:
        m = importlib.import_module(name)
        ver = getattr(m, "__version__", getattr(m, "VERSION", "(no __version__)"))
        print(f"Imported {name!r}: module={m.__name__}  version={ver}")
        return m
    except Exception as e:
        print(f"Failed to import {name!r}: {type(e).__name__}: {e}")
        return None

# Try the common names
cu = try_import("cuquantum")
_try = try_import("cuquantum_python")  # expected to fail in your case

print()
# Inspect cuquantum top-level if present
if cu is not None:
    print("cuquantum top-level attributes (sample):")
    attrs = [a for a in dir(cu) if not a.startswith("_")]
    pprint.pprint(attrs[:60])
    print()

    # Try importing key subpackages/modules
    for sub in ("custatevec", "cutensornet", "einsum", "tensor"):
        full = f"cuquantum.{sub}"
        mod = try_import(full)
        if mod is not None:
            # print first attributes of the submodule
            names = [n for n in dir(mod) if not n.startswith("_")]
            print(f"  {full} attributes (sample): {names[:20]}")
            print()
else:
    print("cuquantum not imported; cannot inspect submodules.")
    sys.exit(1)

# Optional: quick "sanity" call for cutensornet API if available
print("Quick check: cutensornet API availability and simple attribute calls")
ct = try_import("cuquantum.cutensornet")
if ct is not None:
    # print a few constants / helpers if present
    for name in ("VERSION", "create", "contract", "create_network_descriptor"):
        if hasattr(ct, name):
            print(f"  cutensornet has attribute: {name} -> {type(getattr(ct, name))}")
    # try to call create (safe check, do not perform heavy GPU ops)
    try:
        if hasattr(ct, "create"):
            print("  cutensornet.create exists (not calling it to avoid heavy ops).")
    except Exception as e:
        print("  calling create raised:", type(e).__name__, e)
else:
    print("cutensornet not importable.")

print()
print("If you want example scripts using custatevec or cutensornet operations, tell me which API you prefer (custatevec / cutensornet) and I will provide a minimal runnable example.")