import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

INPUT = Path("runs/rag_target/target_embeddings.jsonl")
OUTPUT = Path("runs/rag_target/similarity_results.json")

records = []

with INPUT.open() as f:
    for line in f:
        records.append(json.loads(line))

# Group embeddings by binary
by_binary = {}

for r in records:
    by_binary.setdefault(r["binary"], []).append(r)

# Build one representation per binary:
# mean of its target-function embeddings
binary_vectors = {}

for binary, items in by_binary.items():
    vectors = np.array([x["embedding"] for x in items])
    binary_vectors[binary] = vectors.mean(axis=0)

# Separate head and cut binaries
head = sorted(
    b for b in binary_vectors
    if b.startswith("head_")
)

cut = sorted(
    b for b in binary_vectors
    if b.startswith("cut_")
)

# 10 x 10 cross-binary similarities
matrix = []

for h in head:
    row = []

    for c in cut:
        score = cosine_similarity(
            binary_vectors[h].reshape(1, -1),
            binary_vectors[c].reshape(1, -1)
        )[0][0]

        row.append(float(score))

    matrix.append(row)

matrix = np.array(matrix)

result = {
    "method": "mean target-function embedding per binary",
    "embedding_model": "nomic-embed-text",
    "embedding_dimensions": 768,
    "head_binaries": head,
    "cut_binaries": cut,
    "similarity_matrix": matrix.tolist(),
    "mean_cross_similarity": float(matrix.mean()),
    "min_cross_similarity": float(matrix.min()),
    "max_cross_similarity": float(matrix.max()),
    "std_cross_similarity": float(matrix.std())
}

with open(OUTPUT, "w") as f:
    json.dump(result, f, indent=2)

print("=" * 70)
print("TARGET SIMILARITY EXPERIMENT")
print("=" * 70)

print("Head binaries:", len(head))
print("Cut binaries:", len(cut))
print("Comparisons:", matrix.size)

print()
print("Mean:", result["mean_cross_similarity"])
print("Min :", result["min_cross_similarity"])
print("Max :", result["max_cross_similarity"])
print("Std :", result["std_cross_similarity"])

print()
print("Output:", OUTPUT)
