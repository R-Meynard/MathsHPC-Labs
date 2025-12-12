#!/usr/bin/env python3
import sys, importlib, importlib.util, traceback, os

def main():
    print("python:", sys.executable)
    names = ('qiskit','qiskit.providers.aer','qiskit.providers.basicaer','qiskit_aer')
    for name in names:
        try:
            spec = importlib.util.find_spec(name)
            print(f"spec {name}: {spec}")
            if spec is not None:
                print("  origin:", getattr(spec, 'origin', None))
        except Exception as e:
            print(f"find_spec {name} error:", e)

    try:
        import qiskit
        print("qiskit import OK")
        print(" qiskit.__file__:", getattr(qiskit, '__file__', None))
        print(" qiskit.__path__:", getattr(qiskit, '__path__', None))
        print(" qiskit.__version__:", getattr(qiskit, '__version__', getattr(qiskit, 'version', None)))
    except Exception as e:
        print("qiskit import error:", e)

    # show candidate site-packages / dist-packages and any qiskit-related entries
    site_dirs = [p for p in sys.path if 'site-packages' in (p or '') or 'dist-packages' in (p or '')]
    print("site-packages candidates:", site_dirs)
    for d in site_dirs:
        try:
            if os.path.isdir(d):
                entries = os.listdir(d)
                q_entries = [e for e in entries if 'qiskit' in e.lower()]
                if q_entries:
                    print(f"In {d} found qiskit-related:", q_entries)
        except Exception as e:
            print("listing error for", d, ":", e)

    # Try several import patterns for Aer and related modules
    for stmt in [
        "from qiskit import Aer",
        "from qiskit.providers.aer import Aer",
        "import qiskit.providers.aer as qa",
        "import qiskit_aer as qaa"
    ]:
        try:
            exec(stmt, globals())
            print("Succeeded exec:", stmt)
        except Exception as e:
            print("Failed exec:", stmt, "->", type(e).__name__, e)

    # If Aer was imported, try a tiny circuit run
    if 'Aer' in globals():
        try:
            backend = Aer.get_backend('aer_simulator')
            print("Backend:", backend)
            from qiskit import QuantumCircuit, transpile
            qc = QuantumCircuit(1,1)
            qc.h(0); qc.measure(0,0)
            tq = transpile(qc, backend)
            job = backend.run(tq, shots=64)
            res = job.result()
            print("counts:", res.get_counts())
        except Exception:
            traceback.print_exc()
    else:
        print("Aer not imported; will not run circuit.")

if __name__ == "__main__":
    main()