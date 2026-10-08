# Which LLMs can we actually run for experiments on our hardware and budget?

Type: research
Status: resolved
Blocked by: none
Map: [Topic search](../map.md)
Findings: [notes/model-setup.md](../../../notes/model-setup.md) (also on branch `research/model-setup`)

## Question

As of October 2026, which LLMs can we use for evaluation experiments given an 8 GB RAM laptop with a GTX 1650 (4 GB VRAM), free API tiers, and under $20–30 of paid API use in total? List: (1) open-weight models runnable locally via Ollama or llama.cpp, with realistic speed and tool-calling support; (2) free API tiers (e.g. Gemini, Groq, OpenRouter free models, others), with their rate limits and terms on research use; (3) one or two cheap paid models suitable as a stronger reference, with per-token prices and an estimate of how many evaluation calls $20 buys. Note which options support tool/function calling, since agent experiments need it.

## Answer

Recommended setup (prices and limits checked on official pages, 2026-10-08):

1. **Qwen3-4B-Instruct-2507, local** (Q4_K_M, about 2.5 GB). Fits in 4 GB of VRAM; best tool calling among models of 4B parameters or fewer (BFCL v4 overall 35.7%). Free.
2. **Llama 3.2 3B, local** (about 2.0 GB). A second model family, at the weak end (22.0%). Free. Alternative: xLAM-2-3b-fc-r, a function-calling specialist, but its licence allows research use only.
3. **gpt-oss-120b on Groq's free tier.** About 80 calls a day per model (200K tokens a day); paid overflow is about $0.0006 a call.
4. **Reference model: Claude Haiku 4.5** (BFCL 68.7%, multi-turn 53.6%). About $0.0045 a call at 2,000 input and 500 output tokens, so about 4,400 calls for $20.

Estimated spend: $10–15 of the $20–30 cap.

Caveats that affect choosing a problem:
- Small models are weak at multi-turn tool calling (4–22% on BFCL multi-turn). Problems that need long agent loops on local models are risky; single-step or short-chain tasks suit them better.
- Laptop speeds are estimates. Measure them in the feasibility pilot.
- Gemini free-tier limits couldn't be verified.
- **OpenRouter requires written approval for prompt-injection or jailbreak experiments.** Other providers' policies on adversarial testing weren't checked. Check them before any security-attack experiment.
