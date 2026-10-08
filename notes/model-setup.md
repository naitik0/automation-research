# Which LLMs can we actually run for experiments on our hardware and budget?

Written: 2026-10-08. All prices, free tiers and limits below were checked on the provider's official page on **2026-10-08**. They change often, so check again before running experiments.

Ticket: [05 – Feasible model setup](../.scratch/topic-search/issues/05-feasible-model-setup.md)

Constraints (from the map): 8 GB system RAM, NVIDIA GTX 1650 with 4 GB VRAM, free API tiers, and under $20–30 of paid API use in total. Agent experiments need tool (function) calling.

Citations are numbered as `[n]` and listed under `## Sources`. Our own arithmetic and judgement are labelled **(our estimate)** or kept under `## Takeaways`.

---

## 1. Local open-weight models (Ollama / llama.cpp)

### What the hardware supports

- Ollama supports NVIDIA GPUs with compute capability 5.0+ and driver 550+. Its compute capability 7.5 row lists Turing cards, including the "GTX 1650 Ti" [33]. NVIDIA lists the GTX 1650 (G5 and G6 variants) as Turing, with 896 CUDA cores, 4 GB of GDDR5 or GDDR6 on a 128-bit bus, and **no Tensor Cores** [38]. So expect compute capability 7.5. Confirm with `nvidia-smi` on the laptop.
- By default Ollama uses a **4,096-token context**. You can change it with `OLLAMA_CONTEXT_LENGTH` or `num_ctx`. `ollama ps` shows whether a model runs "100% GPU", "100% CPU" or split (for example "48%/52% CPU/GPU"). Models that don't fit in VRAM are **partially offloaded** to system RAM. Setting `OLLAMA_FLASH_ATTENTION=1` and `OLLAMA_KV_CACHE_TYPE=q8_0` halves the KV-cache memory (`q4_0` cuts it to a quarter) [32].
- **Memory budget (our estimate):** the KV cache grows with context. From the model configs [37]:
  - Qwen3-4B-Instruct-2507 has 36 layers, 8 KV heads and head_dim 128. That is about 144 KiB per token at f16, so about **0.56 GiB at 4k context** and about **1.1 GiB at 8k**, on top of 2.5 GB of Q4_K_M weights. It fits in 4 GB at 4k. At 8k it is tight, but q8_0 KV-cache quantization brings it back to about 0.56 GiB.
  - Qwen3.5-4B has only 8 full-attention layers out of 32, with 4 KV heads and head_dim 256. Its KV cache is about 32 KiB per token, but its Q4_K_M download is 3.3 GB (the tag lists image input too) [26]. That will be borderline or partly offloaded on 4 GB.
- **Speed (our estimate, not measured):** generating tokens on a GPU is limited mainly by memory bandwidth. Roughly, the upper bound is bandwidth ÷ bytes of weights read per token. NVIDIA's comparison table gives the bus width (128-bit) but not the bandwidth [38]. A search summary claimed 128 GB/s (G5) and 192 GB/s (G6) for the desktop card, but I could not confirm it on an NVIDIA page I opened, and laptop clocks vary. If those figures hold, a 2.5 GB Q4 model gets at most about 50–75 tokens/s. Real throughput will be lower, and it drops sharply once layers spill to the CPU (system RAM is much slower). **Measure it in the feasibility pilot** with `ollama run <model> --verbose` before planning the run count.
- **Planning arithmetic (our estimate):** at 20 tokens/s, a call with 500 output tokens takes about 25 s, so 1,000 calls take about 7 h of generation. "Thinking" models write far longer outputs and would be much slower.
- 8 GB of system RAM is shared with Windows. Run one model at a time, and avoid partial offload of models larger than about 3 GB.

### Candidate models (≤ ~4B, Q4_K_M sizes from the Ollama library)

BFCL is the Berkeley Function Calling Leaderboard, V4, last updated 2026-04-12 [24]. "Overall" is overall accuracy. "MT" is multi-turn accuracy, the most agent-like category.

| Model (Ollama tag) | Q4 size | Tools tag on Ollama | BFCL V4 (independent) | Notes |
|---|---|---|---|---|
| Qwen3-4B-Instruct-2507 (`qwen3:4b-instruct-2507-q4_K_M`) | 2.5 GB, 256K ctx [25] | yes [25] | Overall 35.68%, MT 22.12% (FC mode) [24] | Best independently scored general ≤4B model that fits fully in VRAM. Apache 2.0 [25]. |
| Llama 3.2 3B (`llama3.2:3b`) | 2.0 GB, 128K ctx [27] | yes [27] | Overall 21.95%, MT 4.00% (FC) [24] | Different model family; a weak end of the range. |
| Qwen3.5-4B (`qwen3.5:4b-q4_K_M`) | 3.3 GB, 256K ctx [26] | yes [26] | Not on BFCL. Self-reported BFCL-V4 50.3, TAU2-Bench 79.9 [34] | Newest (Feb 2026, Apache 2.0). Thinking mode is on by default [34], so outputs are long and slow. Tight in 4 GB. |
| Qwen3.5-2B (`qwen3.5:2b-q4_K_M`) | 1.9 GB [26] | yes [26] | Not on BFCL. Self-reported BFCL-V4 43.6 (thinking) / 25.3 (non-thinking) [35] | Card warns it is "more prone to entering thinking loops" [35]. |
| xLAM-2-3b-fc-r (GGUF on Hugging Face, not in the Ollama library) | not checked | needs a custom import | Overall 41.22%, **MT 58.38%** (FC) [24] | Fine-tuned specifically for function calling. **CC-BY-NC-4.0, "for research purposes only"** [36]. That is acceptable for an academic paper. |
| Phi-4-mini 3.8B (`phi4-mini`) | 2.5 GB [28] | yes [28] | not listed | |
| Granite 4 3B (`granite4:3b`) | 2.1 GB [29] | yes [29] | only the 350M variant is listed (18.98%) [24] | |
| Ministral 3 3B (`ministral-3:3b`) | 3.0 GB [30] | described as "native function calling" [30] | not listed | Includes vision, so it is heavier. |
| Gemma 4 E2B/E4B | 4.6–9.5 GB [31] | native function-calling [31] | not listed | **Does not fit** in 4 GB VRAM. |
| Gemma 3 4B | – | – | Overall 19.62%, MT 0.38% (prompt mode) [24] | Weak at tool calling. |

**Is tool calling reliable at this size?** Not for multi-turn agent work. On BFCL V4 [24], the best ≤4B general models score about 20–36% overall and 4–22% on multi-turn. Frontier API models score 60–77% overall. Small models do fairly well on single-call tasks (non-live AST is 82–88% for Qwen3-4B-2507 and Llama-3.2-3B). They fail mainly on multi-step tasks. Two exceptions are worth noting. xLAM-2-3b-fc-r scores 58% on multi-turn, and Nanbeige4-3B-Thinking scores 51.40% overall, though it is a thinking model and its Ollama availability was not checked [24].

---

## 2. Free API tiers

To estimate calls per day we assume 2,500 tokens per call (2,000 in + 500 out).

| Provider | Models with tool calling | Free limits (official) | Calls/day at 2.5K tokens (our estimate) | Data use / terms |
|---|---|---|---|---|
| **Groq** (free plan) | `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b` (preview). "All models hosted on Groq support tool use" [7][8] | gpt-oss-120b / gpt-oss-20b / qwen3.8-27b: **30 RPM, 1K RPD, 8K TPM, 200K TPD** each. Limits apply per organization [5] | ~80 per model (TPD-bound); ~3 per minute (TPM-bound) | No retention by default except up to 30 days for abuse monitoring. Zero Data Retention can be enabled. The docs do not mention training on inputs [9]. The website terms I read had no benchmark clause; the Services Agreement was not read [10]. |
| **OpenRouter** `:free` models | Free models with `tools` support on 2026-10-08 include `google/gemma-4-31b-it:free`, `google/gemma-4-26b-a4b-it:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `liquid/lfm-2.5-2.6b:free`, and the `openrouter/free` router [15] | **20 RPM**. **50 RPD** if less than 10 credits have ever been bought; **1,000 RPD** after buying at least 10 credits [11][12] | 50 or 1,000 (request-bound) | If you opt out of training, OpenRouter will not route to providers that train or log [12][13]. Terms (effective 2026-08-31): some models "may store or train on your Inputs" [14]. **Red Teaming (defined as "prompt injection, jailbreaking, or … adversarial action") requires prior written approval** [14]. This matters for security experiments. The free model list changes often. |
| **Google Gemini API** (free tier) | Function calling, including parallel and compositional calls, shown for Gemini 3.8 Flash [4]. A free tier is listed for Gemini 3.8/3.7/3.6/3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 2.5 Pro, 2.5 Flash and 2.5 Flash-Lite [2] | **Not published on the docs page.** The numbers are shown per project in AI Studio [1]. I could not verify them; third-party sites quote different figures. | unknown; check AI Studio | Free tier: "Content used to improve our products": **Yes** [2]. "Human reviewers may read, annotate, and process your API input and output". "Do not submit sensitive, confidential, or personal information" [3]. Must be 18+. No developing "models that compete with the Services". No explicit benchmarking ban found [3]. |
| **Cerebras** (free trial) | gpt-oss-120b, qwen-3.8-27b | 5 RPM, 30K TPM uncached, **1M TPD**. Only **$5 of credits that expire 30 days after grant** [16] | ~400 while credits last | Terms not reviewed. |
| **Mistral** (Free mode) | – | Limits are shown in the admin panel and not on the docs page [17] | unknown | Free mode: Mistral "may use your data (input and output) to train" its models. You can opt out [18]. |

---

## 3. Cheap paid models as a stronger reference

The cost per call assumes 2,000 input + 500 output tokens (standard tier, no caching) **(our arithmetic)**.

| Model | Price per 1M tokens (in / out) | $ per call | Calls per $20 | Independent tool-calling evidence |
|---|---|---|---|---|
| Claude Haiku 4.5 | $1 / $5; batch $0.50 / $2.50 [22] | $0.0045 | **~4,400** (batch ~8,900) | **BFCL V4 overall 68.70% (#6), MT 53.62%** [24]. Highest-scoring cheap model on the leaderboard. Now listed as a legacy model [23]. |
| Gemini 2.5 Flash | $0.30 / $2.50 [2] | $0.00185 | ~10,800 | BFCL V4 56.24%, MT 36.25% [24]. Also has a free tier [2]. |
| GPT-5-nano | $0.05 / $0.40 [20] | $0.0003 | ~66,700 | BFCL V4 51.45%, MT 34.50% [24] |
| Groq gpt-oss-120b (paid) | $0.15 / $0.60 [6] | $0.0006 | ~33,300 | not on BFCL |
| DeepSeek-Flash | $0.30 / $1.20 peak; $0.15 / $0.60 off-peak (cache miss) [19] | $0.0012 (off-peak $0.0006) | ~16,700 (~33,300) | Tool calls supported [19]; not on BFCL |
| DeepSeek-V4-Pro | $1.32 / $3.96 peak; $0.66 / $1.98 off-peak [19] | $0.0046 | ~4,300 (~8,700) | Tool calls supported [19]; not on BFCL |
| Claude Haiku 5.5 | $0.10 / $0.50 (prompts ≤100K); batch $0.05 / $0.25 [22] | $0.00045 | ~44,400 (batch ~88,900) | Not on BFCL V4. Supports tool use [23]. Uses the newer tokenizer (~30% more tokens for the same text) [22], so the real cost is about $0.0006 per call. |
| OpenAI gpt-6-luna | $0.10 / $0.50; batch/flex 50% off [20][21] | $0.00045 | ~44,400 | Not on BFCL V4. Function calling through the Responses API. In Chat Completions it is only available when `reasoning_effort` is `none` [21]. |
| Claude Sonnet 5.5 | $2 / $10; batch $1 / $5 [22] | $0.009 | ~2,200 (batch ~4,400) | not on BFCL V4 |

Caveats:

1. **Reasoning tokens are billed as output.** gpt-6-luna defaults to medium reasoning effort [21], and Claude 5.x models use adaptive thinking [23]. Real output per call can be several times 500 tokens, so turn reasoning down or off, or budget for it.
2. **One agent episode is many calls.** A 10-step episode is about 10 calls with growing context, so "calls per $20" is not "tasks per $20".
3. Prompt caching cuts the cost of repeated system prompts and tool schemas to 10% of the input price on Claude and gpt-6-luna [20][22]. That helps agent loops a lot.

---

## Takeaways (our interpretation)

**Recommended setup**

1. **Qwen3-4B-Instruct-2507, local** (`qwen3:4b-instruct-2507-q4_K_M`, 2.5 GB). It fits entirely in 4 GB VRAM at 4k–8k context. It has the best independently measured tool-calling score among general ≤4B models (BFCL V4 35.7%) and is Apache 2.0. Cost: $0.
2. **Llama 3.2 3B, local** (`llama3.2:3b`, 2.0 GB). It is a second model family, so results aren't specific to Qwen. Its BFCL score (22.0%, 4% multi-turn) marks the low end. Cost: $0. *Optional swap:* use **xLAM-2-3b-fc-r** if the paper wants a "general vs tool-specialized small model" contrast. It scores 58% on multi-turn and is licensed for research only.
3. **gpt-oss-120b on Groq's free tier.** This is a larger open-weight model with tool calling, run remotely. The free tier gives about 80 calls a day (200K tokens/day). If you need more volume, paid use costs about $0.0006 per call. Cost: $0 to about $3.
4. **Reference: Claude Haiku 4.5** (paid). It is the cheapest model with strong *independent* multi-turn tool-calling evidence (BFCL V4 68.7% overall, 53.6% multi-turn), which gives reviewers a known anchor. $20 buys about 4,400 calls (about 8,900 with the Batch API). Budget about $10 for about 2,000 reference calls. *Cheaper alternative:* Gemini 2.5 Flash (BFCL 56.2%) is free for low volume, but free-tier data is used for training and may be human-reviewed, and paid use costs about $0.0019 per call.

**Estimated total spend:** about **$10–15**: Haiku 4.5 reference ~$10, an optional Groq paid overflow ~$3, and optionally $10 of OpenRouter credits, which also lifts free models to 1,000 requests a day. That stays inside the $20–30 cap.

**Risks and open items**

- If the chosen problem involves prompt injection or jailbreaks (likely in cybersecurity agent work), OpenRouter requires prior written approval for "Red Teaming" [14]. Check the usage policies of Groq, Anthropic and Google for the same issue before choosing providers. I did not review them in this session.
- Measure tokens/s and VRAM fit (`ollama ps`, `--verbose`) in the feasibility pilot. The speed figures above are bandwidth bounds, not measurements.
- Gemini and Mistral free-tier numeric limits could not be verified from public docs.
- Free model lists (OpenRouter, Groq preview models) change often. Pin model IDs and record the date of each run.

## Sources

All accessed 2026-10-08.

1. Google, "Rate limits", Gemini API docs (last updated 2026-09-02). https://ai.google.dev/gemini-api/docs/rate-limits
2. Google, "Gemini Developer API pricing" (last updated 2026-10-07). https://ai.google.dev/gemini-api/docs/pricing
3. Google, "Gemini API Additional Terms of Service" (last updated 2026-04-28). https://ai.google.dev/gemini-api/terms
4. Google, "Function calling with the Gemini API". https://ai.google.dev/gemini-api/docs/function-calling
5. Groq, "Rate Limits". https://console.groq.com/docs/rate-limits
6. Groq, "Supported Models". https://console.groq.com/docs/models
7. Groq, "Tool Use". https://console.groq.com/docs/tool-use
8. Groq, "Qwen 3.8 27B" model page. https://console.groq.com/docs/model/qwen/qwen3.8-27b
9. Groq, "Your Data in GroqCloud". https://console.groq.com/docs/your-data
10. Groq, "Terms of Use" (effective 2025-10-15). https://groq.com/terms-of-use
11. OpenRouter, "API Rate Limits". https://openrouter.ai/docs/api-reference/limits
12. OpenRouter, "FAQ". https://openrouter.ai/docs/faq
13. OpenRouter, "Provider Logging". https://openrouter.ai/docs/guides/privacy/provider-logging
14. OpenRouter, "Terms of Service" (effective 2026-08-31), §6–8. https://openrouter.ai/terms
15. OpenRouter, Models API (live model list with pricing and `supported_parameters`). https://openrouter.ai/api/v1/models
16. Cerebras, "Rate Limits". https://inference-docs.cerebras.ai/support/rate-limits
17. Mistral AI, "Usage and limits". https://docs.mistral.ai/admin/billing-usage/usage-limits
18. Mistral AI Help Center, "Do you use my user data to train your Artificial Intelligence models?". https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models
19. DeepSeek, "Models & Pricing". https://api-docs.deepseek.com/quick_start/pricing
20. OpenAI, "Pricing". https://developers.openai.com/api/docs/pricing
21. OpenAI, "GPT-6 Luna" model page. https://developers.openai.com/api/docs/models/gpt-6-luna
22. Anthropic, "Pricing". https://platform.claude.com/docs/en/about-claude/pricing
23. Anthropic, "Models overview". https://platform.claude.com/docs/en/about-claude/models/overview
24. Berkeley Function Calling Leaderboard V4 (last updated 2026-04-12): https://gorilla.cs.berkeley.edu/leaderboard.html, with data from https://gorilla.cs.berkeley.edu/data_overall.csv
25. Ollama library, qwen3 (and tags). https://ollama.com/library/qwen3, https://ollama.com/library/qwen3/tags, https://ollama.com/library/qwen3:4b
26. Ollama library, qwen3.5 (and tags). https://ollama.com/library/qwen3.5, https://ollama.com/library/qwen3.5/tags
27. Ollama library, llama3.2. https://ollama.com/library/llama3.2
28. Ollama library, phi4-mini. https://ollama.com/library/phi4-mini
29. Ollama library, granite4. https://ollama.com/library/granite4
30. Ollama library, ministral-3. https://ollama.com/library/ministral-3
31. Ollama library, gemma4. https://ollama.com/library/gemma4
32. Ollama, "FAQ". https://docs.ollama.com/faq
33. Ollama, "Hardware support: GPU". https://docs.ollama.com/gpu
34. Qwen, "Qwen3.5-4B" model card, Hugging Face. https://huggingface.co/Qwen/Qwen3.5-4B
35. Qwen, "Qwen3.5-2B" model card, Hugging Face. https://huggingface.co/Qwen/Qwen3.5-2B
36. Salesforce, "xLAM-2-3b-fc-r" model card, Hugging Face. https://huggingface.co/Salesforce/xLAM-2-3b-fc-r
37. Model configs, Hugging Face: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/resolve/main/config.json, https://huggingface.co/Qwen/Qwen3.5-4B/resolve/main/config.json
38. NVIDIA, "Compare GeForce Graphics Cards" (GTX 16 Series table). https://www.nvidia.com/en-us/geforce/graphics-cards/compare/
