#!/usr/bin/env python3
"""
cupy_einsum_demo.py

Comparer cupy.einsum (GPU) et numpy.einsum (CPU) sur une petite matrice.
Exécuter avec le venv (.cuq-venv) activé.
"""
import time
import numpy as np

try:
    import cupy as cp
except Exception as e:
    print("cupy import failed:", type(e).__name__, e)
    print("Install cupy-cuda12x in the venv if you want GPU acceleration.")
    cp = None

def run_numpy(n=256):
    A = np.random.randn(n, n).astype(np.float32)
    B = np.random.randn(n, n).astype(np.float32)
    t0 = time.time()
    C = np.einsum("ij,jk->ik", A, B)
    t1 = time.time()
    print(f"numpy.einsum time: {t1-t0:.6f}s, shape={C.shape}, dtype={C.dtype}")

def run_cupy(n=512):
    if cp is None:
        print("cupy not available -> skipping cupy test")
        return
    A = cp.random.randn(n, n, dtype=cp.float32)
    B = cp.random.randn(n, n, dtype=cp.float32)
    # warmup
    cp.cuda.Stream.null.synchronize()
    t0 = time.time()
    C = cp.einsum("ij,jk->ik", A, B)
    # ensure computation finished
    cp.cuda.Stream.null.synchronize()
    t1 = time.time()
    print(f"cupy.einsum time: {t1-t0:.6f}s, shape={C.shape}, dtype={C.dtype}")
    # optional: copy small slice back to host
    print("sample element C[0,0]:", float(C[0,0].get()))

def main():
    print("CPU test (numpy)")
    run_numpy(n=256)
    print()
    print("GPU test (cupy) - reduce n if out-of-memory")
    run_cupy(n=512)

if __name__ == "__main__":
    main()