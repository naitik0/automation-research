# Which LLMs can we actually run for experiments on our hardware and budget?

Type: research
Status: open
Blocked by: none
Map: [Topic search](../map.md)
Findings: branch `research/model-setup`, file `notes/model-setup.md` (in progress)

## Question

As of October 2026, which LLMs can we use for evaluation experiments given an 8 GB RAM laptop with a GTX 1650 (4 GB VRAM), free API tiers, and under $20–30 of paid API use in total? List: (1) open-weight models runnable locally via Ollama or llama.cpp, with realistic speed and tool-calling support; (2) free API tiers (e.g. Gemini, Groq, OpenRouter free models, others), with their rate limits and terms on research use; (3) one or two cheap paid models suitable as a stronger reference, with per-token prices and an estimate of how many evaluation calls $20 buys. Note which options support tool/function calling, since agent experiments need it.
