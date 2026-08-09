#!/bin/bash

echo "================ 🔍 FINAL STRICT PAPER AUDIT ================="

pass=true

check() {
    if eval "$1" >/dev/null 2>&1; then
        echo "✔ $2"
    else
        echo "❌ $2"
        pass=false
    fi
}

echo "---- PHASE 0/1: SETUP ----"
check "git rev-parse --is-inside-work-tree" "Git repo initialized"
check "which gcc && which java && which strace && which gcovr" "Dependencies installed"
check "test -f BUILDFLAGS.txt" "Build flags logged"
check "ollama list | grep -q qwen" "LLM model present"
check "ollama list | grep -q nomic" "Embedding model present"

echo "---- ASLR ----"
check "setarch $(uname -m) -R bash -c 'cat /proc/sys/kernel/randomize_va_space' | grep -q 0" "ASLR disabled"

echo "---- BINARIES ----"
check "test -f sbase/head && test -f sbase/cut" "Binaries exist"

echo "---- PHASE 3: DETERMINISM ----"
check "test -f runs/phase3_determinism.json" "Determinism file exists"

echo "---- PHASE 5: STATIC + PSEUDOCODE ----"
check "test -d runs/ghidra_output" "Ghidra output exists"
check "[ \$(jq length runs/pseudocode_dataset.json) -gt 0 ]" "Pseudocode dataset > 0"
check "test -f runs/pseudocode_clean_log.json" "Pseudocode cleaning logged"

echo "---- PHASE 6: SIGNALS ----"
check "[ \$(wc -l < runs/decision_log.jsonl) -ge 20 ]" "Decision log sufficient (>=20)"
check "ls runs/*coverage* >/dev/null 2>&1" "Coverage exists"

echo "---- PHASE 7: LLM ----"
check "[ \$(wc -l < runs/phase7_inputs.jsonl) -eq 20 ]" "20 inputs"
check "[ \$(wc -l < runs/phase7.jsonl) -eq 60 ]" "60 outputs"
check "[ \$(jq length runs/phase7_final.json) -eq 20 ]" "20 final results"
check "grep -q '\"num_ctx\": 8192' runs/phase7.jsonl" "num_ctx correct"
check "grep -q '\"temperature\": 0' runs/phase7.jsonl" "temperature correct"
check "[ \$(grep -o '\"seed\": [0-9]*' runs/phase7.jsonl | sort -u | wc -l) -eq 3 ]" "3 seeds used"

echo "---- PHASE 8: RAG ----"
check "test -f runs/rag_index.json" "RAG index exists"
check "[ \$(wc -l < runs/phase8_rag_proposals.jsonl) -eq 18 ]" "18 proposals"
check "[ \$(wc -l < runs/phase8_judgement.jsonl) -eq 18 ]" "18 judgements"

echo "---- FINAL DECISION ----"
if [ "$pass" = true ]; then
    echo "🎯🎯🎯 ALL GREEN → PAPER DATA 100% COMPLETE 🎯🎯🎯"
else
    echo "⚠️ SOME CHECKS FAILED → FIX BEFORE SUBMISSION"
fi

