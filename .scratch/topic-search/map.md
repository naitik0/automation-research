# Map: Topic search

Label: wayfinder:map
Started: 2026-10-08
Deadline: 2026-10-13 (topic search closes; pick the strongest candidate problem and move to experiments)

## Destination

An approved **problem brief** (see `CONTEXT.md`) for one **chosen problem** in AI agents / AI-powered automation, whose smallest useful version yields meaningful experimental results within 7–10 days and supports a complete conference-style paper within one month (draft due ~2026-11-08).

## Notes

**Who and what:** Solo MCA student (BCA in cybersecurity, coursework level). Basic Python; has used Docker, n8n, LLM APIs. No advisor yet; a professor may review later. Target: complete conference-style paper (mid-tier/regional venue; arXiv fallback). Not a top-tier guarantee.

**Budget for the whole month:** ~70 hours total; topic search capped at ~12–15 hours. API/cloud spend under ~$20–30 total. Free/open-source tools and public datasets preferred.

**Hardware:** 8 GB RAM laptop, NVIDIA GTX 1650 (4 GB VRAM). Local models limited to roughly ≤4B parameters (quantized); larger models via free API tiers or cheap paid APIs.

**Contribution type:** Empirical evaluation or benchmark. A small evaluation harness is fine; no large system, no training or fine-tuning.

**What counts as a real gap:** (i) an untested setting, or (ii) a demonstrably flawed existing evaluation. Replication only as supporting evidence, unless it reveals an important new finding.

**Area weighting:** AI agents / AI-powered automation are the core. Cybersecurity is the preferred application, workflow automation also matters. Don't force cybersecurity if another area has a clearly stronger gap and better feasibility.

**Skills:** research tickets use `/research`; HITL tickets use `/grilling` + `/domain-modeling`. Use the terms in `CONTEXT.md`. Findings go in `notes/<slug>.md` per `notes/README.md`.

**Gap-scan rubric.** Every area gap-scan answers:

1. **Landscape:** the 5–10 most relevant papers/benchmarks (2023–2026), each with venue or arXiv ID.
2. **Gap evidence:** the strongest untested setting or flawed evaluation, and the searches that failed to find it already covered.
3. **Candidate problems:** 1–3, each phrased as a research question.
4. **Data and environments:** public datasets/tools, licence, size.
5. **Smallest useful version:** what produces results in 7–10 days on our hardware and budget.
6. **Risks:** crowding (especially preprints from the last 6 months), dependency or access risks.
7. **Scores (1–5):** gap strength, novelty, feasibility, data availability, cost, speed to results.

## Decisions so far

<!-- one line per closed ticket: [title](issues/NN-slug.md): gist -->

## Not yet specified

- **Feasibility pilot for the chosen problem:** a smoke test (dataset loads, a model runs the task, one metric computes) before the brief is approved. Its shape depends on which problem is chosen.
- **Venue shortlist:** which specific conferences fit the chosen problem, and their page limits and deadlines. May shape the brief's scope.

## Out of scope

- **LLM agents solving CTF challenges as the main topic:** established benchmarks already exist (e.g. Cybench, NYU CTF Bench); too crowded for a one-month solo paper.
- **Human-subject studies, live offensive testing outside sandboxes, proprietary data, model training/fine-tuning:** ruled out by constraints.
- **Detailed experiment design, running experiments, writing the paper:** these come after the destination, as a separate effort.
