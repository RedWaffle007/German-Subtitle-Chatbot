# backend/model_loader.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "models/mistral_merged_fp16"

def load_model():
    print("Loading merged FP16 Mistral model (CPU+GPU offload)...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=False)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        device_map="auto"       # ✅ FIXED
    )

    print("Model ready (transformers backend).")
    return tokenizer, model
