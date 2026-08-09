import json
import numpy as np
from pathlib import Path
from collections import defaultdict

INPUT = Path("runs/rag_target/target_embeddings.jsonl")
OUTPUT = Path("runs/rag_target/full_pairwise_audit.json")

with INPUT.open() as f:
    records = [json.loads(line) for line in f]

print("=" * 70)
print("FULL PAIRWISE PSEUDOCODE SIMILARITY AUDIT")
print("=" * 70)

print("Records:", len(records))

# ------------------------------------------------------------
# Build normalized embedding matrix
# ------------------------------------------------------------

vectors = np.array(
    [r["embedding"] for r in records],
    dtype=np.float32
)

norms = np.linalg.norm(vectors, axis=1, keepdims=True)

if np.any(norms == 0):
    raise RuntimeError("Zero-length embedding detected")

vectors = vectors / norms

# Full 70 x 70 cosine matrix
similarity = vectors @ vectors.T

# ------------------------------------------------------------
# Pairwise categories
# ------------------------------------------------------------

same_function = []
different_function = []

same_program = []
cross_program = []

same_variant = []
different_variant = []

pairs = []

for i in range(len(records)):
    for j in range(i + 1, len(records)):

        a = records[i]
        b = records[j]

        score = float(similarity[i, j])

        same_fn = a["function"] == b["function"]
        same_prog = a["program"] == b["program"]
        same_bin = a["binary"] == b["binary"]

        # Same function family
        if same_fn:
            same_function.append(score)
        else:
            different_function.append(score)

        # Same program family
        if same_prog:
            same_program.append(score)
        else:
            cross_program.append(score)

        # Same binary should never happen because each binary
        # contains only one record for each target function.
        if same_bin:
            same_variant.append(score)
        else:
            different_variant.append(score)

        pairs.append({
            "binary_a": a["binary"],
            "function_a": a["function"],
            "binary_b": b["binary"],
            "function_b": b["function"],
            "program_a": a["program"],
            "program_b": b["program"],
            "similarity": score,
            "same_function": same_fn,
            "same_program": same_prog,
            "same_binary": same_bin
        })

# ------------------------------------------------------------
# Statistics helper
# ------------------------------------------------------------

def stats(values):
    arr = np.array(values, dtype=np.float64)

    return {
        "count": int(len(arr)),
        "mean": float(arr.mean()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "std": float(arr.std()),
        "median": float(np.median(arr)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75))
    }

# ------------------------------------------------------------
# Main statistics
# ------------------------------------------------------------

same_fn_stats = stats(same_function)
different_fn_stats = stats(different_function)

same_program_stats = stats(same_program)
cross_program_stats = stats(cross_program)

same_variant_stats = stats(same_variant)
different_variant_stats = stats(different_variant)

# ------------------------------------------------------------
# Separation
# ------------------------------------------------------------

mean_function_margin = (
    same_fn_stats["mean"] -
    different_fn_stats["mean"]
)

# Conservative threshold based on maximum negative example.
threshold = different_fn_stats["max"]

same_fn_above_threshold = sum(
    x > threshold for x in same_function
)

same_fn_recall_at_threshold = (
    same_fn_above_threshold / len(same_function)
)

different_fn_below_threshold = sum(
    x <= threshold for x in different_function
)

different_fn_rejection = (
    different_fn_below_threshold / len(different_function)
)

# ------------------------------------------------------------
# Counts
# ------------------------------------------------------------

total_pairs = len(pairs)

expected_pairs = len(records) * (len(records) - 1) // 2

if total_pairs != expected_pairs:
    raise RuntimeError(
        f"Pair count mismatch: {total_pairs} != {expected_pairs}"
    )

# ------------------------------------------------------------
# Cross-program breakdown
# ------------------------------------------------------------

cross_program_same_function = [
    p["similarity"]
    for p in pairs
    if p["same_function"] and not p["same_program"]
]

cross_program_different_function = [
    p["similarity"]
    for p in pairs
    if not p["same_function"] and not p["same_program"]
]

within_program_same_function = [
    p["similarity"]
    for p in pairs
    if p["same_function"] and p["same_program"]
]

within_program_different_function = [
    p["similarity"]
    for p in pairs
    if not p["same_function"] and p["same_program"]
]

breakdown = {
    "cross_program_same_function":
        stats(cross_program_same_function),

    "cross_program_different_function":
        stats(cross_program_different_function),

    "within_program_same_function":
        stats(within_program_same_function),

    "within_program_different_function":
        stats(within_program_different_function)
}

# ------------------------------------------------------------
# Per-function statistics
# ------------------------------------------------------------

per_function = defaultdict(list)

for p in pairs:
    if p["same_function"]:
        per_function[p["function_a"]].append(p["similarity"])

per_function_stats = {
    name: stats(values)
    for name, values in sorted(per_function.items())
}

# ------------------------------------------------------------
# Final output
# ------------------------------------------------------------

output = {
    "experiment":
        "full_pairwise_pseudocode_similarity",

    "embedding_model":
        records[0]["embedding_model"],

    "embedding_dimensions":
        records[0]["embedding_dimensions"],

    "records":
        len(records),

    "total_unique_pairs":
        total_pairs,

    "statistics": {
        "same_function":
            same_fn_stats,

        "different_function":
            different_fn_stats,

        "same_program":
            same_program_stats,

        "cross_program":
            cross_program_stats,

        "same_binary":
            same_variant_stats,

        "different_binary":
            different_variant_stats
    },

    "function_separation": {
        "mean_margin":
            float(mean_function_margin),

        "negative_max_threshold":
            float(threshold),

        "same_function_above_threshold":
            int(same_fn_above_threshold),

        "same_function_recall_at_threshold":
            float(same_fn_recall_at_threshold),

        "different_function_below_threshold":
            int(different_fn_below_threshold),

        "different_function_rejection":
            float(different_fn_rejection)
    },

    "program_breakdown":
        breakdown,

    "per_function":
        per_function_stats,

    "pairs":
        pairs
}

with OUTPUT.open("w") as f:
    json.dump(output, f, indent=2)

# ------------------------------------------------------------
# Console report
# ------------------------------------------------------------

print()
print("=" * 70)
print("PAIR COUNTS")
print("=" * 70)

print("Total records:", len(records))
print("Expected pairs:", expected_pairs)
print("Actual pairs:", total_pairs)

print()
print("=" * 70)
print("SAME FUNCTION")
print("=" * 70)

for k, v in same_fn_stats.items():
    print(f"{k:8}: {v}")

print()
print("=" * 70)
print("DIFFERENT FUNCTION")
print("=" * 70)

for k, v in different_fn_stats.items():
    print(f"{k:8}: {v}")

print()
print("=" * 70)
print("FUNCTION SEPARATION")
print("=" * 70)

print("Mean margin:",
      mean_function_margin)

print("Maximum different-function similarity:",
      different_fn_stats["max"])

print("Same-function recall at that threshold:",
      same_fn_recall_at_threshold)

print("Different-function rejection:",
      different_fn_rejection)

print()
print("=" * 70)
print("CROSS-PROGRAM SAME FUNCTION")
print("=" * 70)

for k, v in breakdown["cross_program_same_function"].items():
    print(f"{k:8}: {v}")

print()
print("=" * 70)
print("CROSS-PROGRAM DIFFERENT FUNCTION")
print("=" * 70)

for k, v in breakdown["cross_program_different_function"].items():
    print(f"{k:8}: {v}")

print()
print("=" * 70)
print("FINAL")
print("=" * 70)

print("PASS — full pairwise audit completed")
print("Output:", OUTPUT)
