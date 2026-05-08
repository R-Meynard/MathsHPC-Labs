#!/usr/bin/env python3
import inspect, traceback, pprint
try:
    import perceval as pv
except Exception as e:
    print("Impossible d'importer perceval:", e)
    raise

def show(obj, name=None):
    if name is None:
        name = getattr(obj, "__name__", str(type(obj)))
    print("="*80)
    print("OBJECT:", name)
    print("TYPE:", type(obj))
    try:
        print("REPR:", repr(obj)[:400])
    except Exception:
        pass
    if inspect.ismodule(obj) or inspect.isclass(obj) or inspect.isfunction(obj) or hasattr(obj, "__call__"):
        try:
            sig = inspect.signature(obj)
            print("SIGNATURE:", sig)
        except Exception:
            pass
    try:
        doc = inspect.getdoc(obj)
        if doc:
            print("DOC:", doc.strip().splitlines()[0][:400])
    except Exception:
        pass
    print()

pv_names = sorted([n for n in dir(pv) if not n.startswith("_")])
print("Perceval top-level members (sample):", pv_names[:200])
print()

# Instantiate a 2-mode Circuit and a BS to inspect runtime attributes
Circuit = getattr(pv, "Circuit", None)
BS = getattr(pv, "BS", None)
Processor = getattr(pv, "Processor", None)
BackendFactory = getattr(pv, "BackendFactory", None)

if Circuit:
    try:
        c = Circuit(2)
        show(c, "Circuit(2) instance")
    except Exception as e:
        print("Création Circuit(2) a échoué:", e)
        traceback.print_exc()

if BS:
    try:
        bs = BS()
        show(bs, "BS() instance")
        # show some useful attributes if present
        for a in ("m","m_in","m_out","n","is_unitary"):
            if hasattr(bs, a):
                try:
                    print(f"bs.{a} ->", getattr(bs, a))
                except Exception as e:
                    print(f"bs.{a} -> exception reading attribute: {e}")
    except Exception as e:
        print("Création BS() a échoué:", e)
        traceback.print_exc()
print()

# Show candidate methods and signatures for Circuit and Processor classes (if available)
for cls_name in ("Circuit","ACircuit"):
    cls = getattr(pv, cls_name, None)
    if cls:
        show(cls, f"{cls_name} class")
        # list methods of class related to adding components
        methods = [m for m in dir(cls) if any(k in m for k in ("add","append","unitary","component","port","set"))]
        print(f"{cls_name} related methods sample:", methods[:80])
        print()

# Processor
if Processor:
    show(Processor, "Processor class")
    proc_methods = [m for m in dir(Processor) if any(k in m for k in ("add","set","run","sample","circuit","input","backend","port","source"))]
    print("Processor related methods sample:", proc_methods[:200])
    print()
    # try to instantiate Processor using BackendFactory if possible (like you did)
    try:
        bf = BackendFactory()
        print("BackendFactory list:", getattr(bf, "list", lambda : "no-list")())
    except Exception as e:
        print("BackendFactory instantiation/list failed:", e)

# Show signature/docs for a few candidate functions we tried previously
candidates = [
    ("Circuit.add", Circuit and getattr(Circuit, "add", None)),
    ("Circuit.append", Circuit and getattr(Circuit, "append", None)),
    ("Circuit.add_unitary", Circuit and getattr(Circuit, "add_unitary", None)),
    ("Processor.add", Processor and getattr(Processor, "add", None)),
    ("Processor.add_port", Processor and getattr(Processor, "add_port", None)),
    ("Processor.set_circuit", Processor and getattr(Processor, "set_circuit", None)),
    ("Processor.run", Processor and getattr(Processor, "run", None)),
    ("Simulator.set_circuit", getattr(pv, "Simulator", None) and getattr(pv.Simulator, "set_circuit", None)),
]
for name, obj in candidates:
    if obj:
        print("-"*40)
        print(name)
        try:
            print(" signature:", inspect.signature(obj))
        except Exception:
            pass
        try:
            doc = inspect.getdoc(obj)
            if doc:
                print(" doc (first line):", doc.strip().splitlines()[0][:400])
        except Exception:
            pass
    else:
        print("-"*40)
        print(name, "-> not found")
print("="*80)
print("Fin de l'inspection. Copiez-collez la sortie complète ici.")