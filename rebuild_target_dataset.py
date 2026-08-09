import json
import glob
import os

TARGETS = {
    "head": {
        "00400720": "main",
        "00401af0": "head_bytes",
        "00401bb0": "head_lines",
    },
    "cut": {
        "00400760": "main",
        "00400c20": "cut_fields",
        "00401260": "cut_bytes",
        "00401410": "cut_file",
    },
}

out = "runs/target_filtered.jsonl"

records = []
errors = []

for path in sorted(glob.glob("runs/ghidra_20/*.json")):

    filename = os.path.basename(path)

    with open(path) as f:
        d = json.load(f)

    binary = d["binary"]
    program = d["binary"].split("_")[0]

    if program not in TARGETS:
        errors.append(f"{filename}: unknown program {program}")
        continue

    by_entry = {
        fn["entry"]: fn
        for fn in d["functions"]
    }

    selected = []

    for entry, semantic_name in TARGETS[program].items():

        if entry not in by_entry:
            errors.append(
                f"{filename}: missing {semantic_name} at {entry}"
            )
            continue

        fn = by_entry[entry]

        if not fn.get("pseudocode", "").strip():
            errors.append(
                f"{filename}: {semantic_name} has empty pseudocode"
            )
            continue

        selected.append({
            "name": semantic_name,
            "ghidra_name": fn["name"],
            "entry": fn["entry"],
            "callers": fn["callers"],
            "pseudocode": fn["pseudocode"],
        })

    if len(selected) != len(TARGETS[program]):
        errors.append(
            f"{filename}: expected "
            f"{len(TARGETS[program])} targets, got {len(selected)}"
        )
        continue

    records.append({
        "binary": binary,
        "program": program,
        "functions": selected,
    })


with open(out, "w") as f:
    for record in records:
        f.write(json.dumps(record) + "\n")

print("=" * 70)
print("TARGET DATASET REBUILT")
print("=" * 70)
print("Output:", out)
print("Binary records:", len(records))
print("Expected:", 20)
print("Target functions:", sum(len(r["functions"]) for r in records))
print("Expected target functions:", 70)

print()
print("ERRORS:", len(errors))

for e in errors:
    print("FAIL:", e)

if not errors and len(records) == 20:
    print()
    print("PASS: 20/20 binaries included")
    print("PASS: 70/70 target-function instances included")
