import json
import numpy as np
from pathlib import Path

INPUT = Path("runs/rag_target/target_embeddings.jsonl")
OUTPUT = Path("runs/rag_target/retrieval_pseudocode_only.json")

records = []

with INPUT.open() as f:
    for line in f:
        records.append(json.loads(line))

print("=" * 70)
print("PSEUDOCODE-ONLY RETRIEVAL ABLATION")
print("=" * 70)

# Build embeddings from pseudocode ONLY.
# Deliberately exclude:
#   - binary name
#   - program name
#   - function name
#   - entry address
#   - caller names

def embed(text):
    import urllib.request

    payload = json.dumps({
        "model": "nomic-embed-text",
        "input": text
    }).encode()

    req = urllib.request.Request(
        "http://localhost:11434/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req) as r:
        data = json.load(r)

    return data["embeddings"][0]


print("Generating pseudocode-only embeddings...")

vectors = []

for i, r in enumerate(records, start=1):
    pseudo = r["text"].split("Pseudocode:\n", 1)[-1].strip()

    if not pseudo:
        raise RuntimeError(
            f"Empty pseudocode: {r['binary']}:{r['function']}"
        )

    vector = embed(pseudo)

    if len(vector) != 768:
        raise RuntimeError(
            f"Unexpected dimension for "
            f"{r['binary']}:{r['function']}"
        )

    vectors.append(vector)

    print(
        f"[{i:02d}/70] "
        f"{r['binary']}::{r['function']}"
    )

vectors = np.array(vectors, dtype=np.float32)

# Normalize
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors = vectors / norms

results = []

top1 = 0
top3 = 0
top5 = 0
rr_sum = 0.0

for i, query in enumerate(records):

    scores = vectors @ vectors[i]

    # Remove query itself
    scores[i] = -np.inf

    ranking = np.argsort(-scores)

    first_correct_rank = None

    for rank, idx in enumerate(ranking, start=1):
        candidate = records[idx]

        # Same semantic function across variants
        if (candidate["program"], candidate["function"]) == (query["program"], query["function"]):
            first_correct_rank = rank
            break

    if first_correct_rank is None:
        raise RuntimeError(
            f"No correct retrieval found for "
            f"{query['binary']}:{query['function']}"
        )

    if first_correct_rank <= 1:
        top1 += 1

    if first_correct_rank <= 3:
        top3 += 1

    if first_correct_rank <= 5:
        top5 += 1

    rr_sum += 1.0 / first_correct_rank

    top_candidates = []

    for rank, idx in enumerate(ranking[:5], start=1):
        candidate = records[idx]

        top_candidates.append({
            "rank": rank,
            "binary": candidate["binary"],
            "program": candidate["program"],
            "function": candidate["function"],
            "similarity": float(scores[idx])
        })

    results.append({
        "query_binary": query["binary"],
        "query_program": query["program"],
        "query_function": query["function"],
        "first_correct_rank": first_correct_rank,
        "top1": first_correct_rank <= 1,
        "top3": first_correct_rank <= 3,
        "top5": first_correct_rank <= 5,
        "top_candidates": top_candidates
    })

n = len(results)

metrics = {
    "queries": n,
    "candidates_per_query": len(records) - 1,
    "top1_accuracy": top1 / n,
    "top3_accuracy": top3 / n,
    "top5_accuracy": top5 / n,
    "mrr": rr_sum / n
}

output = {
    "experiment": "pseudocode_only_retrieval_ablation",
    "embedding_model": "nomic-embed-text",
    "embedding_dimensions": 768,
    "representation": "pseudocode_only",
    "excluded_metadata": [
        "binary",
        "program",
        "function",
        "entry",
        "callers"
    ],
    "queries": n,
    "candidates": len(records),
    "metrics": metrics,
    "results": results
}

with OUTPUT.open("w") as f:
    json.dump(output, f, indent=2)

print()
print("=" * 70)
print("PSEUDOCODE-ONLY RESULTS")
print("=" * 70)
print("Queries:", n)
print("Candidates:", len(records))
print()
print("Top-1:", metrics["top1_accuracy"])
print("Top-3:", metrics["top3_accuracy"])
print("Top-5:", metrics["top5_accuracy"])
print("MRR   :", metrics["mrr"])
print()
print("Output:", OUTPUT)
print("=" * 70)
