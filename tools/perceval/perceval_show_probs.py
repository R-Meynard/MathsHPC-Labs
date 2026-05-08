#!/usr/bin/env python3
"""
Inspecte un résultat de sim.probs() et tente d'en extraire des probabilités
ou des amplitudes de façon robuste, en testant plusieurs attributs/méthodes.
"""
import pprint, traceback

def safe_print(*a, **kw):
    print(*a, **kw, flush=True)

def extract_from_result(res):
    # 1) si c'est un mapping .items()
    try:
        if hasattr(res, "items"):
            try:
                d = dict(res.items())
                return "items", d
            except Exception:
                pass
    except Exception:
        pass

    # 2) méthodes usuelles possibles
    candidates = [
        "as_dict", "to_dict", "get_probs", "get_probabilities", "probabilities",
        "probs", "weights", "get_weights", "items", "distribution"
    ]
    for name in candidates:
        try:
            attr = getattr(res, name, None)
            if callable(attr):
                try:
                    out = attr()
                    if isinstance(out, dict):
                        return name + "()", out
                    # if out is iterable of pairs
                    try:
                        d = dict(out)
                        return name + "()", d
                    except Exception:
                        # continue
                        pass
                except Exception:
                    pass
            elif attr is not None:
                # attribute present
                if isinstance(attr, dict):
                    return name, attr
                # list/iterable of pairs?
                try:
                    d = dict(attr)
                    return name, d
                except Exception:
                    # maybe it's an array of weights aligning with states yielded by iterating res
                    pass
        except Exception:
            pass

    # 3) try to see if object has a .__iter__ and we can inspect elements + check for attached weights
    try:
        if hasattr(res, "__iter__"):
            lst = list(res)
            # try to find weights/attributes on the result object itself
            for maybe_w in ("weights", "probs", "probabilities"):
                if hasattr(res, maybe_w):
                    w = getattr(res, maybe_w)
                    try:
                        # assume parallel lists
                        d = {}
                        for s, p in zip(lst, list(w)):
                            d[str(s)] = float(p)
                        return "iter_plus_" + maybe_w, d
                    except Exception:
                        pass
            # fallback: return the list of states (no probs)
            return "iter_states", {str(s): None for s in lst}
    except Exception:
        pass

    # 4) give up: return repr and dir for manual inspection
    info = {"repr": repr(res)[:1000], "dir": [n for n in dir(res) if not n.startswith("_")]}
    return "unknown", info

def main():
    try:
        import perceval as pv
    except Exception as e:
        safe_print("Impossible d'importer perceval:", e)
        return 2

    try:
        # rebuild the same example: 2-mode circuit, BS, state, sim.probs
        Circuit = pv.Circuit
        BS = pv.BS
        circuit = Circuit(2)
        circuit.add((0,1), BS())
        BasicState = pv.BasicState
        state = BasicState([1,0])
        bf = pv.BackendFactory()
        backend = bf.get_backend("SLOS")
        sim = pv.Simulator(backend)
        sim.set_circuit(circuit)
        res = sim.probs(state)
    except Exception as e:
        safe_print("Erreur lors de la reproduction de la simulation:", e)
        traceback.print_exc()
        return 3

    safe_print("Type du résultat:", type(res))
    safe_print("repr(result) (troncature):", repr(res)[:400])
    safe_print("dir(result) sample (first 200):", [n for n in dir(res) if not n.startswith("_")][:200])

    kind, info = extract_from_result(res)
    safe_print("\nExtraction method:", kind)
    safe_print("Extracted info:")
    pprint.pprint(info)

    # If we got probabilities (numerical), print them in sorted order
    if isinstance(info, dict):
        if all(v is None for v in info.values()):
            safe_print("\nOnly states listed, no numeric probabilities available.")
        else:
            # convert keys to string and sort by prob desc (None treated as 0)
            items = [(k, (v if v is not None else 0.0)) for k, v in info.items()]
            items.sort(key=lambda x: -x[1])
            safe_print("\nState -> probability (sorted):")
            for s, p in items:
                safe_print(f"{s} -> {p:.6f}")
    else:
        safe_print("\nCould not extract numeric probabilities. Dumping info for manual inspection:")
        pprint.pprint(info)

    safe_print("\nSi vous voulez, je peux adapter l'extraction à la structure exacte affichée ci-dessus.")
    return 0

if __name__ == "__main__":
    exit(main())