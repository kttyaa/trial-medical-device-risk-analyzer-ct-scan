import pandas as pd
import numpy as np
import torch
import faiss

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM


# ===========================
# LOAD DATASET FMEA CSV
# ===========================
df = pd.read_csv("fmea_example.csv")

# Filter kolom yang kamu tentukan
cols = ["Item/Function", "Failure Mode", "Effects of Failure", "Potential Cause(s)", "Recommended Actions"]
df = df[cols]


# ===========================
# EMBEDDING MODEL (retriever)
# ===========================
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Gabungkan row menjadi knowledge text
documents = []
for _, row in df.iterrows():
    text = (
        f"Item/Function: {row['Item/Function']}\n"
        f"Failure Mode: {row['Failure Mode']}\n"
        f"Effects: {row['Effects of Failure']}\n"
        f"Causes: {row['Potential Cause(s)']}\n"
        f"Controls: {row['Recommended Actions']}\n"
    )
    documents.append(text)

# Encode & build FAISS index
emb = embedder.encode(documents)
dimension = emb.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(emb))


# ===========================
# LOAD QWEN FOR GENERATION
# ===========================
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
).to("cpu").eval()


# ===========================
# RETRIEVAL FUNCTION
# ===========================
def retrieve_docs(query, k=5):
    q_emb = embedder.encode([query])
    distances, idx = index.search(np.array(q_emb), k)
    return [documents[i] for i in idx[0]]


# ===========================
# MAIN RAG FMEA FUNCTION
# ===========================
def ask_fmea(component: str) -> str:
    retrieved = "\n---\n".join(retrieve_docs(component, k=3))  # top-3 snippet paling relevan

    prompt = f"""
You are an FMEA expert. Use ONLY the knowledge below to generate structured FMEA suggestions.

Knowledge Base:
{retrieved}

Component: {component}

Respond using ONLY this format:

Failure Modes:
-

Effects of Failure:
-

Potential Causes:
-

Current Controls:
-
"""

    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=350,
            temperature=0.3
        )

    return tokenizer.decode(output[0], skip_special_tokens=True)


# ===========================
# TEST
# ===========================
if __name__ == "__main__":
    print(ask_fmea("Gantry motor"))
