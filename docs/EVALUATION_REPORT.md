# RAG Evaluation Report — reproducible measurement plan

**Status at packaging:** No embedding model corpus was downloaded or indexed in this build environment; therefore live retrieval scores and LLM answer quality measurements are intentionally not fabricated. Run in the deployed application and append actual outputs.

## Dataset and metrics

- 18 synthetic documents and 30 labeled questions, with expected document references in `data/evaluation/test_questions.json`.
- `/api/evaluation/run`: measures per-question Precision@5, Recall@5 and wall-clock latency for hybrid retrieval.
- `python -m app.embedding_benchmark`: two embedding models (`all-MiniLM-L6-v2`, `intfloat/e5-small-v2`) using the same corpus and questions; writes JSON and CSV.
- Response accuracy: manual label per answer against ground truth; divide accurate answers by rated answers.
- Hallucination rate: human verification of unsupported factual statements; divide hallucinating answers by rated answers.
- LLM-specific result must be separated from extractive (no API key) mode.

## Acceptance gates

1. At least 30 measured questions with recorded precision/recall.
2. Quote tested model names, runtime hardware, top_k, chunk_size and overlap.
3. Validate source page numbers on sampled PDFs.
4. Run tests, inspect failures, report measurement not available where the environment prevents execution.
5. Business-impact reduction requires baseline staff document-search times and measured copilot times; the PDF's aspirational 80–90% is **not a measured result**.
