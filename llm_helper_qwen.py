import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import pandas as pd

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

# ================= LOAD MODEL LLM =================
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
).to("cpu").eval()

# ================= LOAD EMBEDDING =================
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ================= LOAD CSV ======================
df = pd.read_csv("fmea_example.csv")

# gabungkan text tiap row
raw_docs = [
    f"Item: {row['Item/Function']}. Failure Mode: {row['Failure Mode']}. "
    f"Effects: {row['Effects of Failure']}. Causes: {row['Potential Cause(s)']}. "
    f"Controls: {row['Recommended Actions']}."
    for _, row in df.iterrows()
]

# ================= CHUNKING ======================
def chunk_text(text, chunk_size=70, overlap=15):
    words = text.split()
    chunks=[]
    for i in range(0, len(words), chunk_size-overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if len(chunk.split()) > 15:
            chunks.append(chunk)
    return chunks

chunks=[]
for d in raw_docs:
    chunks.extend(chunk_text(d))

print(f"📌 Loaded {len(raw_docs)} rows → {len(chunks)} chunks")

# ================= FAISS INDEX ==================
def build_faiss_index(chunks):
    embeddings = embed_model.encode(chunks, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, embeddings

index, embeddings = build_faiss_index(chunks)


# ================= RETRIEVAL =====================
def retrieve_relevant_docs(query, k=4, threshold=0.25):
    query_emb = embed_model.encode([query])
    distances, ids = index.search(query_emb, k)

    results=[]
    for dist, idx in zip(distances[0], ids[0]):
        sim = 1/(1+dist)                # biar nilai makin mirip makin tinggi
        if sim >= threshold:
            results.append(chunks[idx]) # ← bukan documents lagi

    return results if results else ["NOT ENOUGH DATA"]


# ================= FULL RAG ASK ==================
def ask_component_RAG(component:str):
    retrieved = retrieve_relevant_docs(component)

    context = "\n\n".join(retrieved)

    prompt = f"""
You must answer ONLY using context below.
If missing information -> say "Not available based on database".

Context:
{context}

Generate strict FMEA:

Failure Modes:
- 

Effects of Failure:
- 

Potential Causes:
- 

Current Controls:
- 
"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=250,
            temperature=0.0, 
            top_p=0.1,
            do_sample=False
        )

    return tokenizer.decode(output[0], skip_special_tokens=True)

# ====== TEST RUN ======
if __name__ == "__main__":
    print(ask_component_RAG("Gantry Motor"))
