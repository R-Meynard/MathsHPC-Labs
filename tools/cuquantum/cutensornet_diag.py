#!/usr/bin/env python3
"""
Diagnostic for cuQuantum / cutensornet NOT_SUPPORTED error.

Run with the cuquantum venv activated:
  . .cuq-venv/bin/activate
  python3 cutensornet_diag.py
"""
import subprocess, sys, traceback

print("Python:", sys.version)
print("\n--- nvidia-smi output ---")
try:
    out = subprocess.check_output(["nvidia-smi"], text=True)
    print(out)
except Exception as e:
    print("Could not run nvidia-smi:", type(e).__name__, e)

print("\n--- cupy device properties (if cupy available) ---")
try:
    import cupy as cp
    dev = cp.cuda.runtime.getDevice()
    props = cp.cuda.runtime.getDeviceProperties(dev)
    # print some useful properties
    for k in ("name", "major", "minor", "totalGlobalMem", "multiProcessorCount"):
        print(f"{k}: {props.get(k, props.get(k.encode(), 'n/a'))}")
    print("cupy runtime summary:", props)
except Exception as e:
    print("cupy not available or failed to query device:", type(e).__name__, e)

print("\n--- cuquantum / cutensornet info ---")
try:
    import cuquantum
    print("cuquantum __version__:", getattr(cuquantum, "__version__", "(no __version__)"))
    try:
        import cuquantum.cutensornet as ct
        print("cutensornet VERSION:", getattr(ct, "VERSION", "(no VERSION)"))
        for attr in ("MAJOR_VER", "MINOR_VER", "PATCH_VER"):
            if hasattr(ct, attr):
                print(f"{attr} = {getattr(ct, attr)}")
        # list some key callables
        keys = ["create", "create_network_descriptor", "contract", "contract_path", "check_status"]
        for k in keys:
            print(f"cutensornet has {k}: {hasattr(ct, k)}")
    except Exception as e:
        print("Failed to import cuquantum.cutensornet:", type(e).__name__, e)
except Exception as e:
    print("Failed to import cuquantum:", type(e).__name__, e)

print("\n--- Try a small conditional call to provoke a detailed error (safe) ---")
try:
    import cuquantum
    # try to call a small symbol if present to get detailed error (we do not perform heavy ops)
    if hasattr(cuquantum, "cutensornet") and hasattr(cuquantum.cutensornet, "contract"):
        try:
            # call contract with impossible args on purpose to inspect error handling
            cuquantum.cutensornet.contract(None)
        except Exception as e:
            print("cutensornet.contract raised (expected):", type(e).__name__)
            traceback.print_exc()
    else:
        print("cutensornet.contract not present; skipping invocation.")
except Exception as e:
    print("Error while attempting diagnostic invocation:", type(e).__name__, e)
    traceback.print_exc()

print("\n--- End of diagnostic ---")
print("Next suggestions:")
print("  * If compute capability < 7.0 (Pascal/6.x), cutensornet optimizations may be unsupported on this GPU.")
print("  * You can continue using numpy fallback or use custatevec APIs if they suit your needs.")
print("  * For GPU acceleration, consider a more recent NVIDIA GPU (Turing/Ampere) or run on a machine/container with a supported architecture.")