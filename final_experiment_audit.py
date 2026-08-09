import json
import glob
import numpy as np
from pathlib import Path
from collections import Counter

ROOT = Path("runs/rag_target")

TARGET = Path("runs/target_filtered.jsonl")
EMBED = ROOT / "target_embeddings.jsonl"
RETRIEVAL = ROOT / "retrieval_results.json"
ABLATION = ROOT / "retrieval_pseudocode_only.json"
PAIRWISE = ROOT / "full_pairwise_audit.json"

errors = []
warnings = []

print("=" * 75)
print("DeReLLM — FINAL EXPERIMENT CONSISTENCY AUDIT")
print("=" * 75)

# ------------------------------------------------------------
# 1. TARGET DATASET
# ------------------------------------------------------------

with TARGET.open() as f:
    target = [json.loads(line) for line in f]

print("\n[1] TARGET DATASET")
print("Records:", len(target))

if len(target) != 20:
    errors.append(f"Target dataset has {len(target)} records; expected 20")

binaries = [r["binary"] for r in target]

print("Unique binaries:", len(set(binaries)))

if len(set(binaries)) != 20:
    errors.append("Binary coverage is not exactly 20 unique binaries")

programs = Counter(r["program"] for r in target)

print("Programs:", dict(programs))

if programs != {"cut": 10, "head": 10}:
    errors.append(f"Unexpected program distribution: {programs}")

target_count = sum(len(r["functions"]) for r in target)

print("Target function records:", target_count)

if target_count != 70:
    errors.append(f"Expected 70 target functions; got {target_count}")

# ------------------------------------------------------------
# 2. TARGET FUNCTION IDENTITY
# ------------------------------------------------------------

print("\n[2] TARGET FUNCTION IDENTITY")

expected = {
    "cut": {"main", "cut_fields", "cut_bytes", "cut_file"},
    "head": {"main", "head_bytes", "head_lines"}
}

identity_errors = []

for r in target:
    names = {fn["name"] for fn in r["functions"]}

    if names != expected[r["program"]]:
        identity_errors.append(
            f"{r['binary']}: {sorted(names)}"
        )

print("Expected semantic identity: (program, function)")

if identity_errors:
    errors.extend(identity_errors)
    print("FAIL")
    for e in identity_errors:
        print(" ", e)
else:
    print("PASS — all 20 binaries have correct target functions")

# ------------------------------------------------------------
# 3. PSEUDOCODE COMPLETENESS
# ------------------------------------------------------------

print("\n[3] PSEUDOCODE COMPLETENESS")

empty_pseudo = []

for r in target:
    for fn in r["functions"]:
        if not fn.get("pseudocode", "").strip():
            empty_pseudo.append(
                f"{r['binary']}::{fn['name']}"
            )

print("Empty pseudocode:", len(empty_pseudo))

if empty_pseudo:
    errors.extend(
        f"Empty pseudocode: {x}"
        for x in empty_pseudo
    )
else:
    print("PASS — 70/70 functions contain pseudocode")

# ------------------------------------------------------------
# 4. EMBEDDINGS
# ------------------------------------------------------------

print("\n[4] EMBEDDING DATASET")

with EMBED.open() as f:
    embeddings = [json.loads(line) for line in f]

print("Embedding records:", len(embeddings))

if len(embeddings) != 70:
    errors.append(
        f"Expected 70 embeddings; got {len(embeddings)}"
    )

dims = Counter(
    len(r.get("embedding", []))
    for r in embeddings
)

print("Dimensions:", dict(dims))

if dims != {768: 70}:
    errors.append(
        f"Unexpected embedding dimensions: {dims}"
    )

models = Counter(
    r.get("embedding_model")
    for r in embeddings
)

print("Models:", dict(models))

if models != {"nomic-embed-text": 70}:
    errors.append(
        f"Unexpected embedding models: {models}"
    )

# Verify identity correspondence
target_ids = {
    (r["binary"], r["program"], fn["name"])
    for r in target
    for fn in r["functions"]
}

embedding_ids = {
    (r["binary"], r["program"], r["function"])
    for r in embeddings
}

if target_ids != embedding_ids:
    errors.append(
        "Target dataset and embedding identity sets do not match"
    )
else:
    print("PASS — target/embedding identities match exactly")

# ------------------------------------------------------------
# 5. RETRIEVAL RESULTS
# ------------------------------------------------------------

print("\n[5] RETRIEVAL RESULTS")

with RETRIEVAL.open() as f:
    retrieval = json.load(f)

metrics = retrieval["metrics"]

print("Queries:", retrieval["queries"])
print("Candidates:", retrieval["candidates"])
print("Top-1:", metrics["top1_accuracy"])
print("Top-3:", metrics["top3_accuracy"])
print("Top-5:", metrics["top5_accuracy"])
print("MRR:", metrics["mrr"])

if retrieval["queries"] != 70:
    errors.append("Retrieval query count is not 70")

if retrieval["candidates"] != 70:
    errors.append("Retrieval candidate count is not 70")

if len(retrieval["results"]) != 70:
    errors.append("Retrieval result entries are not 70")

for metric in [
    "top1_accuracy",
    "top3_accuracy",
    "top5_accuracy"
]:
    if not np.isclose(metrics[metric], 1.0):
        warnings.append(
            f"Retrieval {metric} is {metrics[metric]}"
        )

if not np.isclose(metrics["mrr"], 1.0):
    warnings.append(
        f"Retrieval MRR is {metrics['mrr']}"
    )

# ------------------------------------------------------------
# 6. ABLATION
# ------------------------------------------------------------

print("\n[6] PSEUDOCODE-ONLY ABLATION")

with ABLATION.open() as f:
    ablation = json.load(f)

am = ablation["metrics"]

print("Queries:", ablation["queries"])
print("Candidates:", ablation["candidates"])
print("Top-1:", am["top1_accuracy"])
print("Top-3:", am["top3_accuracy"])
print("Top-5:", am["top5_accuracy"])
print("MRR:", am["mrr"])

if ablation["queries"] != 70:
    errors.append("Ablation query count is not 70")

if len(ablation["results"]) != 70:
    errors.append("Ablation result entries are not 70")

# ------------------------------------------------------------
# 7. PAIRWISE AUDIT
# ------------------------------------------------------------

print("\n[7] FULL PAIRWISE AUDIT")

with PAIRWISE.open() as f:
    pairwise = json.load(f)

print("Records:", pairwise["records"])
print("Unique pairs:", pairwise["total_unique_pairs"])

same = pairwise["statistics"]["same_function"]
different = pairwise["statistics"]["different_function"]

print("\nSame semantic function:")
print(" Count :", same["count"])
print(" Mean  :", same["mean"])
print(" Median:", same["median"])
print(" Min   :", same["min"])
print(" Max   :", same["max"])

print("\nDifferent semantic function:")
print(" Count :", different["count"])
print(" Mean  :", different["mean"])
print(" Median:", different["median"])
print(" Min   :", different["min"])
print(" Max   :", different["max"])

print("\nMean separation:",
      pairwise["function_separation"]["mean_margin"])

if pairwise["records"] != 70:
    errors.append("Pairwise records != 70")

if pairwise["total_unique_pairs"] != 2415:
    errors.append("Pairwise count != 2415")

if same["count"] != 315:
    errors.append(
        f"Same-function pair count != 315: {same['count']}"
    )

if different["count"] != 2100:
    errors.append(
        f"Different-function pair count != 2100: {different['count']}"
    )

# ------------------------------------------------------------
# 8. PAIRWISE RECOMPUTATION
# ------------------------------------------------------------

print("\n[8] PAIRWISE NUMERICAL RECOMPUTATION")

vectors = np.array(
    [r["embedding"] for r in embeddings],
    dtype=np.float64
)

vectors /= np.linalg.norm(
    vectors,
    axis=1,
    keepdims=True
)

sim = vectors @ vectors.T

same_values = []
different_values = []

for i in range(len(embeddings)):
    for j in range(i + 1, len(embeddings)):

        a = embeddings[i]
        b = embeddings[j]

        same_semantic = (
            a["program"],
            a["function"]
        ) == (
            b["program"],
            b["function"]
        )

        if same_semantic:
            same_values.append(sim[i, j])
        else:
            different_values.append(sim[i, j])

same_values = np.array(same_values)
different_values = np.array(different_values)

print("Recomputed same mean:",
      same_values.mean())

print("Stored same mean:",
      same["mean"])

print("Recomputed different mean:",
      different_values.mean())

print("Stored different mean:",
      different["mean"])

print("Recomputed margin:",
      same_values.mean() - different_values.mean())

print("Stored margin:",
      pairwise["function_separation"]["mean_margin"])

if not np.isclose(
    same_values.mean(),
    same["mean"],
    atol=1e-6
):
    errors.append("Same-function mean mismatch")

if not np.isclose(
    different_values.mean(),
    different["mean"],
    atol=1e-6
):
    errors.append("Different-function mean mismatch")

stored_margin = pairwise[
    "function_separation"
]["mean_margin"]

if not np.isclose(
    same_values.mean() - different_values.mean(),
    stored_margin,
    atol=1e-6
):
    errors.append("Pairwise margin mismatch")

# ------------------------------------------------------------
# 9. SEARCH FOR STALE METRICS
# ------------------------------------------------------------

print("\n[9] STALE-METRIC CHECK")

search_roots = [
    Path("runs"),
]

stale_patterns = [
    "0.6318",
    "0.8136483352828896",
    "0.9572216083363789",
    "0.724841600114649",
    "0.23238000822172988"
]

found_stale = []

for root in search_roots:
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue

        for pattern in stale_patterns:
            if pattern in text:
                found_stale.append(
                    (str(path), pattern)
                )

if found_stale:
    print("WARNING — old metric values found:")
    for path, pattern in found_stale:
        print(" ", path, "->", pattern)

    warnings.append(
        "Old experimental metric values still exist in runs/"
    )
else:
    print("PASS — no known stale metric values found")

# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print()
print("=" * 75)
print("FINAL EXPERIMENT GATE")
print("=" * 75)

print("Errors:", len(errors))
print("Warnings:", len(warnings))

if errors:
    print("\nFAIL — DO NOT UPDATE PAPER")
    for e in errors:
        print("ERROR:", e)
else:
    print("\nPASS — DATA PIPELINE IS INTERNALLY CONSISTENT")

if warnings:
    print("\nWarnings:")
    for w in warnings:
        print("WARNING:", w)

print()
print("Paper update status:")

if errors:
    print("BLOCKED")
else:
    print("READY FOR FINAL PAPER-NUMBER CONSOLIDATION")
