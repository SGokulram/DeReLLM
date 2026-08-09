import json
import numpy as np
from pathlib import Path

INPUT = Path("runs/rag_target/target_embeddings.jsonl")
OUTPUT = Path("runs/rag_target/retrieval_results.json")

records = []

with INPUT.open() as f:
    for line in f:
        records.append(json.loads(line))

print("=" * 70)
print("TARGET FUNCTION RETRIEVAL EVALUATION")
print("=" * 70)

vectors = np.array([r["embedding"] for r in records], dtype=np.float32)

# Normalize for cosine similarity
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors = vectors / norms

# Function identity is the retrieval target.
# Same function name across different binary variants = correct family.
def function_family(r):
    return r["function"]

results = []

top1 = 0
top3 = 0
top5 = 0
rr_sum = 0.0

for i, query in enumerate(records):

    scores = vectors @ vectors[i]

    # Exclude the query itself
    scores[i] = -np.inf

    ranking = np.argsort(-scores)

    ranked_records = [records[j] for j in ranking]

    correct_positions = []

    for rank, candidate in enumerate(ranked_records, start=1):
        if function_family(candidate) == function_family(query):
            correct_positions.append(rank)

    if not correct_positions:
        continue

    first_rank = correct_positions[0]

    hit1 = first_rank <= 1
    hit3 = first_rank <= 3
    hit5 = first_rank <= 5

    if hit1:
        top1 += 1

    if hit3:
        top3 += 1

    if hit5:
        top5 += 1

    rr_sum += 1.0 / first_rank

    top_candidates = []

    for rank, candidate in enumerate(ranked_records[:5], start=1):
        top_candidates.append({
            "rank": rank,
            "binary": candidate["binary"],
            "program": candidate["program"],
            "function": candidate["function"],
            "similarity": float(scores[ranking[rank - 1]])
        })

    results.append({
        "query_binary": query["binary"],
        "query_program": query["program"],
        "query_function": query["function"],
        "correct_family": function_family(query),
        "first_correct_rank": first_rank,
        "top1": hit1,
        "top3": hit3,
        "top5": hit5,
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
    "embedding_model": records[0]["embedding_model"],
    "embedding_dimensions": records[0]["embedding_dimensions"],
    "queries": n,
    "candidates": len(records),
    "metrics": metrics,
    "results": results
}

with OUTPUT.open("w") as f:
    json.dump(output, f, indent=2)

print()
print("Queries:", n)
print("Candidates:", len(records))
print()
print("Top-1:", metrics["top1_accuracy"])
print("Top-3:", metrics["top3_accuracy"])
print("Top-5:", metrics["top5_accuracy"])
print("MRR   :", metrics["mrr"])
print()
print("Output:", OUTPUT)

print()
print("=" * 70)
print("RETRIEVAL EVALUATION COMPLETE")
print("=" * 70)
