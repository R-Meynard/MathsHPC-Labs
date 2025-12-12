#!/usr/bin/env python3
import sys

def try_import(name):
    try:
        m = __import__(name)
        print(f"Imported {name}: module={m.__name__}, version={getattr(m, '__version__', '(no __version__)')}")
        return True
    except Exception as e:
        print(f"Failed to import {name}: {type(e).__name__}: {e}")
        return False

print("Python:", sys.version)
print("--- Try cuquantum imports ---")
ok1 = try_import("cuquantum")
ok2 = try_import("cuquantum_python")
# optional module that often exists if cuQuantum Python bindings installed
ok3 = try_import("cuquantum.cutensornet") or try_import("cutensornet")

if not (ok1 or ok2):
    print("cuQuantum imports failed. Check that the installed wheel matches your Python/CUDA version.")
    sys.exit(1)

print("If imports succeeded, cuQuantum appears installed. You can run small examples from the cuQuantum docs.")
print("End of test.")