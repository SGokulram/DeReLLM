# DeReLLM: Deterministic Reverse Engineering with Hybrid LLM Reasoning

## Abstract

DeReLLM is a hybrid reverse-engineering framework that integrates static analysis, execution signals, and large language model (LLM) reasoning. The system enforces determinism through controlled configurations and multi-seed evaluation, addressing the inconsistency and non-reproducibility of LLM-based approaches. Unlike purely LLM-driven systems, DeReLLM ensures reproducibility, interpretability, and stability across executions.

---

## Problem Statement

LLM-based program understanding systems suffer from:

- Non-deterministic outputs  
- Lack of reproducibility  
- Weak grounding in execution-level signals  

DeReLLM addresses these limitations using a hybrid pipeline combining static analysis, runtime signals, and structured LLM reasoning.

---

## Methodology

The system follows a multi-phase pipeline:

### 1. Static Analysis
- Binary analysis using reverse engineering tools  
- Pseudocode extraction and normalization  

### 2. Signal Collection
- Execution traces  
- Coverage data  
- Decision logs  

### 3. LLM Reasoning
- Multi-seed evaluation (3 seeds)  
- Temperature fixed at 0  
- Context window fixed (8192)  

### 4. Retrieval-Augmented Generation (RAG)
- Indexed retrieval system  
- Proposal generation  
- Judgment validation  

### 5. Hybrid Decision Engine
- Combines static + dynamic + LLM outputs  
- Produces final structured result  

---

## Evaluation

### Consistency
- Multiple seeds per input  
- Reduced variation across outputs  

### Determinism
- Fixed inference parameters  
- Controlled runtime environment  

### Reproducibility
All outputs are validated using an automated audit system.

---

## Baseline Comparison

| Method        | Determinism | Stability | Interpretability |
|--------------|------------|----------|------------------|
| Static Only  | High       | High     | Medium           |
| LLM Only     | Low        | Low      | Low              |
| DeReLLM      | High       | High     | High             |

---

## Reproducibility

Run the full validation:

\`\`\`bash
./final_audit.sh
\`\`\`

Expected output:

\`\`\`
🎯 ALL GREEN → PAPER DATA 100% COMPLETE
\`\`\`

---

## Repository Structure
derellm/
├── README.md
├── final_audit.sh
├── .gitignore

├── src/                        # ALL core logic
│   ├── static/                # ghidra / parsing
│   ├── llm/                   # phase 7
│   ├── rag/                   # phase 8
│   └── decision/              # hybrid engine

├── data/                       # ONLY lightweight + structured
│   ├── sample/                # small reproducible data (IMPORTANT)
│   │   ├── phase7_final.json
│   │   ├── decision_log.jsonl
│   │   └── pseudocode_dataset.json
│   │
│   └── README.md              # explain dataset (optional)

├── artifacts/                  # generated outputs (not required for repo)
│   ├── logs/
│   ├── coverage/
│   └── rag/

├── binaries/                  # compiled test binaries
│   ├── head
│   └── cut

├── paper/                     # PAPER SUPPORT
│   ├── figures/
│   ├── diagrams/
│   └── tables/

└── docs/                      # optional explanation

## Key Contributions

- Hybrid reverse engineering framework combining static analysis, execution signals, and LLM reasoning  
- Deterministic LLM evaluation using multi-seed and fixed parameters  
- Integration of RAG for contextual grounding  
- Fully reproducible pipeline validated through automated auditing  

---

## Notes

- External tools (e.g., Ghidra) are not included due to size constraints  
- These tools should be installed separately if required  

---

## Future Work

- Quantitative benchmarking with standard datasets  
- Integration of graph-based program representations  
- Fine-tuned domain-specific LLM models  

---

## Author

Gokulram S    

---

## Status

Research-ready system with reproducible results.
