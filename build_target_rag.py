import json
import urllib.request
from pathlib import Path

INPUT = Path("runs/target_filtered.jsonl")
OUTPUT = Path("runs/rag_target/target_embeddings.jsonl")

MODEL = "nomic-embed-text"
URL = "http://localhost:11434/api/embed"

def embed(text):
    payload = json.dumps({
        "model": MODEL,
        "input": text
    }).encode()

    req = urllib.request.Request(
        URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req) as r:
        data = json.load(r)

    return data["embeddings"][0]

records = []

with INPUT.open() as f:
    for line in f:
        d = json.loads(line)

        for fn in d["functions"]:
            text = (
                f"Program: {d['program']}\n"
                f"Binary: {d['binary']}\n"
                f"Function: {fn['name']}\n"
                f"Entry: {fn['entry']}\n"
                f"Callers: {', '.join(fn['callers'])}\n"
                f"Pseudocode:\n{fn['pseudocode']}"
            )

            print(
                f"Embedding {d['binary']} :: "
                f"{fn['name']}"
            )

            vector = embed(text)

            if len(vector) != 768:
                raise RuntimeError(
                    f"Unexpected embedding dimension: {len(vector)}"
                )

            records.append({
                "binary": d["binary"],
                "program": d["program"],
                "function": fn["name"],
                "entry": fn["entry"],
                "callers": fn["callers"],
                "embedding_model": MODEL,
                "embedding_dimensions": len(vector),
                "text": text,
                "embedding": vector
            })

with OUTPUT.open("w") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")

print()
print("========================================")
print("TARGET RAG BUILD COMPLETE")
print("========================================")
print("Records:", len(records))
print("Expected:", 70)
print("Model:", MODEL)
print("Dimensions:", 768)
print("Output:", OUTPUT)

if len(records) != 70:
    raise RuntimeError(
        f"Expected 70 records, got {len(records)}"
    )
