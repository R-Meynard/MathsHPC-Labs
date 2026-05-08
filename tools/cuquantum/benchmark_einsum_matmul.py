#!/usr/bin/env python3
"""
Benchmark helper: compare numpy.einsum, cupy.einsum and cupy.matmul (cuBLAS).
Run with venv activated that contains cupy.

Usage:
  . .cuq-venv/bin/activate
  python3 benchmark_einsum_matmul.py
"""
import time
import numpy as np

sizes = [256, 512, 1024, 1536, 2048]  # adjust / reduce if out of memory

def time_numpy(n, repeats=3):
    A = np.random.randn(n, n).astype(np.float32)
    B = np.random.randn(n, n).astype(np.float32)
    # warmup
    C = np.einsum("ij,jk->ik", A, B)
    t0 = time.perf_counter()
    for _ in range(repeats):
        C = np.einsum("ij,jk->ik", A, B)
    dt = (time.perf_counter() - t0) / repeats
    return dt

def time_cupy_einsum(n, repeats=3):
    try:
        import cupy as cp
    except Exception as e:
        return None, f"cupy import failed: {e}"
    A = cp.random.randn(n, n, dtype=cp.float32)
    B = cp.random.randn(n, n, dtype=cp.float32)
    # warmup
    _ = cp.einsum("ij,jk->ik", A, B)
    cp.cuda.Stream.null.synchronize()
    t0 = time.perf_counter()
    for _ in range(repeats):
        _ = cp.einsum("ij,jk->ik", A, B)
        cp.cuda.Stream.null.synchronize()
    dt = (time.perf_counter() - t0) / repeats
    return dt, None

def time_cupy_matmul(n, repeats=3):
    try:
        import cupy as cp
    except Exception as e:
        return None, f"cupy import failed: {e}"
    A = cp.random.randn(n, n, dtype=cp.float32)
    B = cp.random.randn(n, n, dtype=cp.float32)
    # warmup
    _ = A @ B
    cp.cuda.Stream.null.synchronize()
    t0 = time.perf_counter()
    for _ in range(repeats):
        _ = A @ B
        cp.cuda.Stream.null.synchronize()
    dt = (time.perf_counter() - t0) / repeats
    return dt, None

def main():
    print("Benchmark: numpy.einsum vs cupy.einsum vs cupy.matmul (cuBLAS)")
    print("Note: GPU times include synchronization; reduce sizes if OOM.")
    try:
        import cupy as _cp
        print("cupy available:", _cp.__version__)
    except Exception:
        print("cupy not available; install cupy-cuda12x in venv to run GPU tests.")
    print()
    for n in sizes:
        print(f"Size: {n}x{n}")
        try:
            t_numpy = time_numpy(n)
            print(f"  numpy.einsum     : {t_numpy:.6f} s")
        except Exception as e:
            print(f"  numpy.einsum     : failed: {e}")
        t_cu_einsum, err = time_cupy_einsum(n)
        if err:
            print(f"  cupy.einsum      : {err}")
        else:
            print(f"  cupy.einsum      : {t_cu_einsum:.6f} s")
        t_cu_matmul, err = time_cupy_matmul(n)
        if err:
            print(f"  cupy.matmul      : {err}")
        else:
            print(f"  cupy.matmul      : {t_cu_matmul:.6f} s")
        print("-" * 60)

if __name__ == "__main__":
    main()