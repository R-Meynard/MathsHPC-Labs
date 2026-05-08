#!/usr/bin/env python3
import sys

def try_import(name):
    try:
        m = __import__(name)
        ver = getattr(m, "__version__", getattr(m, "VERSION", "(no __version__)"))
        print(f"{name}: {ver}")
    except Exception as e:
        print(f"{name} import failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("Python:", sys.version)
    try_import("cuquantum")
    try_import("cuquantum_python")