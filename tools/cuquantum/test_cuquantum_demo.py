#!/usr/bin/env python3
"""
Inspection / test minimal pour cuQuantum installé dans le venv.

Usage:
  . .cuq-venv/bin/activate
  python3 test_cuquantum_demo.py
"""
import sys, importlib, pprint, ctypes, os

def try_import(name):
    try:
        m = importlib.import_module(name)
        print(f"Imported {name}: module={m.__name__}, version={getattr(m, '__version__', '(no __version__)')}")
        return m
    except Exception as e:
        print(f"Failed to import {name}: {type(e).__name__}: {e}")
        return None

def show_attrs(mod, n=50):
    if mod is None:
        return
    names = [x for x in dir(mod) if not x.startswith('_')]
    print(f"  Attributes (first {n}):")
    pprint.pprint(names[:n])

def check_libcudart():
    # heuristic check for libcudart presence in runtime loader
    try:
        # try to find libcudart via ctypes (Linux typical name)
        ctypes.CDLL("libcudart.so")
        print("libcudart.so found via ctypes.CDLL('libcudart.so')")
    except OSError:
        # try common CUDA lib locations
        found = False
        for p in ("/usr/local/cuda/lib64/libcudart.so", "/usr/local/cuda-12.4/lib64/libcudart.so"):
            if os.path.exists(p):
                print(f"Found libcudart at: {p}")
                found = True
        if not found:
            print("libcudart not found via ctypes or common paths. If imports fail with missing libcudart, check LD_LIBRARY_PATH and installed CUDA runtime.")

def main():
    print("Python:", sys.version)
    print("--- cuquantum modules ---")
    cu = try_import("cuquantum")
    show_attrs(cu, 80)

    print("\n--- cuquantum_python (optional bindings) ---")
    cu_py = try_import("cuquantum_python")

    print("\n--- cutensornet / bindings ---")
    # try multiple possible import names
    ctn = None
    for name in ("cuquantum.cutensornet", "cutensornet", "cuquantum.cutensornet.cutensornet"):
        if ctn is None:
            ctn = try_import(name)
    show_attrs(ctn, 120)

    print("\n--- Quick runtime checks ---")
    check_libcudart()
    try:
        import subprocess
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,cuda_version", "--format=csv,noheader"], text=True)
        print("nvidia-smi summary:", out.strip())
    except Exception:
        print("Could not run nvidia-smi from Python (you may run it manually).")

    print("\nIf you need the cuquantum_python bindings, install the versioned wheel matching your CUDA:")
    print("  python3 -m pip install --no-cache-dir cuquantum-python-cu12")
    print("Or, if you prefer the meta-package (less recommended):")
    print("  python3 -m pip install --no-cache-dir cuquantum-python")
    print("End of test.")

if __name__ == '__main__':
    main()