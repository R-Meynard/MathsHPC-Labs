#!/usr/bin/env python3
import importlib
import subprocess
import sys
import os

def run(cmd):
    try:
        p = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return p.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR (rc {e.returncode}): {e.output}"

def show_pkg(pkg):
    try:
        m = importlib.import_module(pkg)
        v = getattr(m, "__version__", None) or getattr(m, "version", None) or "no __version__"
        return f"OK, version={v}"
    except Exception as e:
        return f"IMPORT FAIL: {type(e).__name__}: {e}"

print("== pip / setuptools / wheel ==")
print(run("pip3 --version"))
for p in ("pip","setuptools","wheel"):
    print(f"{p:12s}: {run(f'pip3 show {p} || true')}")

print("\n== torch / torchvision / torchaudio ==")
print("torch:", show_pkg("torch"))
print("torch.cuda available check (if torch import OK):")
try:
    import torch
    print("  torch.__version__:", torch.__version__)
    try:
        print("  cuda_available:", torch.cuda.is_available())
        print("  cuda_device_count:", torch.cuda.device_count())
        if torch.cuda.is_available():
            try:
                print("  device0 name:", torch.cuda.get_device_name(0))
            except Exception as e:
                print("  get_device_name error:", e)
    except Exception as e:
        print("  torch.cuda check error:", e)
except Exception as e:
    print("  torch import failed:", type(e).__name__, e)

print("torchvision:", show_pkg("torchvision"))
print("torchaudio:", show_pkg("torchaudio"))

print("\n== tensorflow ==")
print("tensorflow:", show_pkg("tensorflow"))
try:
    import tensorflow as tf
    try:
        gpus = tf.config.list_physical_devices('GPU')
        print("  TF physical GPUs:", gpus)
    except Exception as e:
        print("  TF GPU query error:", e)
except Exception as e:
    print("  tensorflow import failed:", type(e).__name__, e)

print("\n== jax / jaxlib ==")
print("jax:", show_pkg("jax"))
print("jaxlib:", show_pkg("jaxlib"))
try:
    import jax
    try:
        devices = jax.devices()
        print("  jax.devices():", devices)
    except Exception as e:
        print("  jax.devices() error:", e)
except Exception as e:
    print("  jax import failed:", type(e).__name__, e)

print("\n== pip packages info (pip show) ==")
for p in ("transformers","accelerate","optimum","datasets","tokenizers","safetensors","deepspeed","bitsandbytes","xformers"):
    print(p + " -> " + run(f"pip3 show {p} || true"))

print("\n== NVIDIA / system checks ==")
print("nvidia-smi:\n", run("nvidia-smi || true"))
print("uname -a:", run("uname -a"))

print("\n== deepspeed CLI ==")
print(run("deepspeed --version || true"))

print("\n== bitsandbytes quick import test ==")
print(run("python3 -c \"import bitsandbytes as bnb; print(getattr(bnb,'__version__','unknown')); print(getattr(bnb,'cuda_available', 'no attr'))\" || true"))

print("\n== xformers import test ==")
print(run("python3 -c \"import xformers; print(getattr(xformers,'__version__','unknown'))\" || true"))

print("\n== micromamba ==")
micromamba_path = "/opt/micromamba/bin/micromamba"
if os.path.exists(micromamba_path):
    print("micromamba exists:", run(f"{micromamba_path} --version || true"))
    # NOTE: the next line actually runs micromamba clean; safe but destructive of caches
    print("micromamba clean --all (dry-run not available, only showing command output):")
    print(run(f"{micromamba_path} clean --all -f -y || true"))
else:
    print(f"micromamba not found at {micromamba_path}, check PATH: {run('which micromamba || true')}")