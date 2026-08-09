import json
import subprocess
from pathlib import Path

ROOT = Path(".")
INPUT = ROOT / "inputs/test.txt"
OUT = ROOT / "runs/s1"
OUT.mkdir(parents=True, exist_ok=True)

tests = {
    "cut": {
        "original": ROOT / "binaries/cut_O0",
        "variants": sorted((ROOT / "binaries_20").glob("cut_v*")),
        "args": ["-c", "1-4", str(INPUT)],
    },
    "head": {
        "original": ROOT / "binaries/head_O0",
        "variants": sorted((ROOT / "binaries_20").glob("head_v*")),
        "args": ["-n", "3", str(INPUT)],
    },
}

def run(binary, args):
    p = subprocess.run(
        [str(binary)] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )
    return {
        "returncode": p.returncode,
        "stdout": p.stdout.decode(errors="replace"),
        "stderr": p.stderr.decode(errors="replace"),
    }

results = []

for program, cfg in tests.items():

    print("=" * 70)
    print(program.upper())
    print("=" * 70)

    baseline = run(cfg["original"], cfg["args"])

    print("ORIGINAL")
    print("returncode:", baseline["returncode"])
    print("stdout:")
    print(repr(baseline["stdout"]))
    print("stderr:")
    print(repr(baseline["stderr"]))

    for binary in cfg["variants"]:

        result = run(binary, cfg["args"])

        stdout_same = result["stdout"] == baseline["stdout"]
        stderr_same = result["stderr"] == baseline["stderr"]
        returncode_same = result["returncode"] == baseline["returncode"]

        identical = (
            stdout_same
            and stderr_same
            and returncode_same
        )

        record = {
            "phase": "S1",
            "program": program,
            "binary": binary.name,
            "original": str(cfg["original"]),
            "input": str(INPUT),
            "args": cfg["args"],
            "original_returncode": baseline["returncode"],
            "variant_returncode": result["returncode"],
            "original_stdout": baseline["stdout"],
            "variant_stdout": result["stdout"],
            "original_stderr": baseline["stderr"],
            "variant_stderr": result["stderr"],
            "stdout_same": stdout_same,
            "stderr_same": stderr_same,
            "returncode_same": returncode_same,
            "identical": identical,
        }

        results.append(record)

        status = "PASS" if identical else "DIVERGENCE"

        print(
            f"{binary.name:12} "
            f"{status:11} "
            f"stdout={stdout_same} "
            f"stderr={stderr_same} "
            f"rc={returncode_same}"
        )

with (OUT / "s1_results.jsonl").open("w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")

print()
print("=" * 70)
print("S1 SUMMARY")
print("=" * 70)

print("Total variants:", len(results))
print(
    "Identical:",
    sum(r["identical"] for r in results)
)
print(
    "Divergences:",
    sum(not r["identical"] for r in results)
)

print()
print("Output:")
print(OUT / "s1_results.jsonl")
