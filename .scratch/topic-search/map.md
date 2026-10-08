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

- [Gap scan: LLM agents for SOC alert triage and log analysis](issues/01-gap-scan-soc-alert-triage.md): crowded, but strongest gap so far (a flawed evaluation): LLM triage benchmarks lack cheap baselines; a rule-majority lookup beat the reported LLM average on SecAlertBench in a pilot; nobody has compared LLMs with risk-based alerting.
- [Gap scan: Reliability of LLM agents in multi-step workflow automation](issues/03-gap-scan-workflow-agent-reliability.md): crowded area, weak-to-moderate gap; best angle is runtime reliability of LLM steps in public n8n templates (overlaps with low-code security).
- [Gap scan: Security of low-code AI workflow automation](issues/02-gap-scan-low-code-workflow-security.md): main hunch wrong, since JAW (arXiv:2605.11229) already hijacks n8n templates; a narrower gap remains in measuring n8n's built-in defences and attack rates across models.
- [Which LLMs can we actually run for experiments on our hardware and budget?](issues/05-feasible-model-setup.md): Qwen3-4B and Llama 3.2 3B local, gpt-oss-120b on Groq free tier, Claude Haiku 4.5 as reference; about $10–15. Small models are weak at multi-turn tool calling.
- [Gap scan: LLM detection of Docker and infrastructure-as-code misconfigurations](issues/04-gap-scan-docker-iac-misconfiguration.md): crowded, narrow gap; best angle is LLMs vs KICS on hand-labelled docker-compose files, plus showing that tool-derived ground truth distorts results. Cheap, but needs 10–15 hours of hand labelling.
- [Choose the problem](issues/06-choose-the-problem.md): the chosen problem is SOC alert triage, "Are LLM alert triagers better than cheap baselines?" The core experiment is a rule-shortcut audit on SecAlertBench (reusing its published per-alert predictions); the second compares LLMs with risk-based alerting on CATS. Docker Compose vs KICS is the fallback, behind 4 kill criteria; the two n8n candidates are rejected.
- [Feasibility pilot for SOC alert triage](issues/08-feasibility-pilot-soc-alert-triage.md): kill criteria 1, 2 and 4 did not fire. Scored like the benchmark (per-model balanced samples), a rule-majority lookup gets F1 0.898 / FPR 0.036 against the LLM average of 0.709 / 0.441; data usable (Gemini file removed by Defender); local Qwen3-4B takes 9 s/alert (about 24–27 h of planned runs), but answered "Attack" every time.
- [Prior-work check for SOC alert triage](issues/09-prior-work-check-soc-alert-triage.md): kill criterion 3 did not fire; neither a baseline on SecAlertBench nor LLM-vs-RBA found. The SecAlertBench paper itself was not found (main residual risk); Uetz et al. is submitted to USENIX Security '27, not accepted.
- [Venue shortlist for the SOC alert triage paper](issues/10-venue-shortlist.md): CODASPY 2027 (23 Nov), AsiaCCS 2027 (11 Dec), AI-SEC 2027 (10 Dec), then WOSOC and DIMVA with estimated dates; plan an 8–10 page paper with A1 as the core.
- [Write and approve the problem brief](issues/07-write-the-problem-brief.md): approved 2026-10-08 ([docs/problem-brief.md](../../docs/problem-brief.md)). The question is how robust LLM alert-triage evaluation is once simple baselines and label-revealing metadata are controlled for. A1 is the core: out-of-sample references against 15 models' published predictions, three information conditions × 4 models × 1,000 alerts, and grouped-by-rule unseen-rule splits. A2 (LLMs vs RBA) is optional. **Destination reached; the topic search is complete.**

## Not yet specified

_(nothing: no kill criterion fired, so the fallback problem needs no pilot of its own.)_

## Out of scope

- **LLM agents solving CTF challenges as the main topic:** established benchmarks already exist (e.g. Cybench, NYU CTF Bench); too crowded for a one-month solo paper.
- **Human-subject studies, live offensive testing outside sandboxes, proprietary data, model training/fine-tuning:** ruled out by constraints.
- **Detailed experiment design, running experiments, writing the paper:** these come after the destination, as a separate effort.
