import json
import numpy as np
from pathlib import Path

INPUT = Path("runs/rag_target/retrieval_pseudocode_only.json")

with INPUT.open() as f:
    d = json.load(f)

results = d["results"]

same = []
different = []

for r in results:
    query_function = r["query_function"]

    for candidate in r["top_candidates"]:
        if candidate["function"] == query_function:
            same.append(candidate["similarity"])
        else:
            different.append(candidate["similarity"])

print("=" * 70)
print("RETRIEVAL SEPARATION AUDIT")
print("=" * 70)

print("Same-function observations:", len(same))
print("Different-function observations:", len(different))

print()
print("SAME FUNCTION")
print("Mean:", np.mean(same))
print("Min :", np.min(same))
print("Max :", np.max(same))
print("Std :", np.std(same))

print()
print("DIFFERENT FUNCTION")
print("Mean:", np.mean(different))
print("Min :", np.min(different))
print("Max :", np.max(different))
print("Std :", np.std(different))

print()
print("SEPARATION")

margin = np.mean(same) - np.mean(different)

print("Mean separation:", margin)

print()
print("FINAL")
print("Audit completed.")
