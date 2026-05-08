#!/usr/bin/env python3
"""
Minimal einsum/contraction demo:
- Try cuquantum.einsum
- Fallback to cuquantum.cutensornet.einsum if present
- Final fallback: numpy.einsum

This is safe: the script first checks available symbols and prints which backend is used.
"""
import time
import numpy as np

def try_cuquantum_einsum(A, B):
    try:
        import cuquantum as cq
        # prefer top-level einsum if present
        if hasattr(cq, "einsum"):
            t0 = time.time()
            C = cq.einsum("ij,jk->ik", A, B)
            return ("cuquantum.einsum", C, time.time() - t0)
        # else try cutensornet.einsum if present
        if hasattr(cq, "cutensornet") and hasattr(cq.cutensornet, "einsum"):
            t0 = time.time()
            C = cq.cutensornet.einsum("ij,jk->ik", A, B)
            return ("cuquantum.cutensornet.einsum", C, time.time() - t0)
        return ("no-cq-einsum", None, None)
    except Exception as e:
        return ("cq-import-failed", e, None)

def main():
    np.random.seed(0)
    n = 256  # safe size for small GPU (reduce if memory issues)
    A = np.random.randn(n, n).astype(np.float32)
    B = np.random.randn(n, n).astype(np.float32)

    tag, result, dt = try_cuquantum_einsum(A, B)
    if tag == "cuquantum.einsum" or tag == "cuquantum.cutensornet.einsum":
        print(f"Used {tag}, time: {dt:.6f}s, result type: {type(result)}")
        # Try to convert to numpy if it's not already
        try:
            Cnp = np.array(result)
            print("Converted result to numpy array, shape:", Cnp.shape, "dtype:", Cnp.dtype)
        except Exception:
            print("Result is not directly convertible to numpy array (possibly GPU-backed).")
    elif tag == "no-cq-einsum":
        print("cuQuantum einsum not available, falling back to numpy.einsum")
        t0 = time.time()
        C = np.einsum("ij,jk->ik", A, B)
        print("Used numpy.einsum, time: {:.6f}s, shape: {}".format(time.time() - t0, C.shape))
    else:
        print("cuQuantum import/usage failed:", result)
        print("Falling back to numpy.einsum")
        t0 = time.time()
        C = np.einsum("ij,jk->ik", A, B)
        print("Used numpy.einsum, time: {:.6f}s, shape: {}".format(time.time() - t0, C.shape))

if __name__ == "__main__":
    main()