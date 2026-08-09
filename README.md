# DeReLLM

DeReLLM is a hybrid reverse-engineering and LLM-based reasoning system that combines static analysis, semantic reasoning, and retrieval-augmented generation.

## Features

- Deterministic pipeline  
- Multi-seed evaluation  
- Hybrid decision engine  
- Reproducible audit system  

## Run

\`\`\`bash
bash final_audit.sh
\`\`\`

## Sample Output

\`\`\`
🎯🎯🎯 ALL GREEN → PAPER DATA 100% COMPLETE 🎯🎯🎯
\`\`\`

## Structure

- src/ → core implementation  
- runs_sample/ → sample outputs  
- paper_assets/ → audit + paper support files  

## Reproducibility

This project includes a strict audit script (final_audit.sh) that validates:

- Deterministic execution  
- Data completeness  
- LLM configuration consistency  
- RAG pipeline integrity  

