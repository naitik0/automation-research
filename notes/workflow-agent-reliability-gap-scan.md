# Gap scan: Reliability of LLM agents in multi-step workflow automation

**Question:** Where is the strongest research gap in measuring how reliably LLM agents execute multi-step workflow-automation tasks (consistency across runs, error handling, failure modes, cost), outside coding and web browsing? Which agent/workflow benchmarks exist, and have flaws in how they evaluate reliability been documented?

**Written:** 2026-10-08. Ticket: `.scratch/topic-search/issues/03-gap-scan-workflow-agent-reliability.md`.

**Short answer:** The area is **heavily crowded**. Between January and October 2026, preprints and papers have covered repeated-run consistency, perturbation and fault robustness, duplicate side effects under retries, user-simulator bias, annotation errors in benchmarks, statistical noise in single runs, and small or quantized models. The one gap I could still find is narrow: **runtime** reliability of the LLM steps inside real low-code workflows (n8n). The only large n8n study is static and says it cannot see runtime behaviour. This gap is real but modest, and the harness work it needs is a real risk in the time we have.

All sources below were opened in this session. Sources marked "arXiv" are preprints unless a venue is given.

---

## 1. Landscape (2023–2026)

### Benchmarks for tool use and workflows

- **τ-bench** (Yao et al., arXiv:2406.12045, 2024). Tool-agent-user tasks in retail and airline customer service. It introduced **pass^k**, the chance that an agent succeeds on all k trials of the same task. GPT-4o solves under 50% of tasks, and its pass^8 in retail is under 25%.
- **τ²-bench** (Barres et al., arXiv:2506.07982, 2025). Adds a "dual-control" telecom domain where the simulated user also acts on a shared environment. Performance drops sharply compared with the no-user setting. The repository is MIT-licensed, runs models through LiteLLM, and v1.0.1 (July 2026) shipped "75+ fixes" to tasks, citing SABER ([GitHub](https://github.com/sierra-research/tau2-bench)).
- **WorkArena** (Drouin et al., arXiv:2403.07718, 2024). 33 knowledge-work tasks on ServiceNow, run through BrowserGym. This is web-based, so it falls partly outside our scope. The arXiv page I opened does not state a venue.
- **AppWorld** (Trivedi et al., arXiv:2407.18901, ACL 2024). 9 apps, 457 APIs and 750 tasks, graded by state-based unit tests that also check for "collateral damage". The code is Apache 2.0, but protected parts may only be redistributed in encrypted form, and it needs Python 3.11+ ([GitHub](https://github.com/StonyBrookNLP/appworld)).
- **TheAgentCompany** (Xu et al., arXiv:2412.14161, 2024–25). A simulated software company; the best agent completes 30% of tasks autonomously. It is MIT-licensed, has 175 tasks, and needs Docker plus 30+ GB of disk. The baselines ran on EC2 t3.2xlarge instances ([GitHub](https://github.com/TheAgentCompany/TheAgentCompany)).
- **StableToolBench** (Guo et al., arXiv:2403.07714, 2024). Documents that **ToolBench evaluation was unstable**, because real API status changed over time and the evaluator was random. It fixes this with a virtual API server and a more stable evaluator.
- **AutomationBench** (Shepard & Salimans, arXiv:2604.18934, Apr 2026; the authors are at Zapier). Cross-application business workflows over REST APIs, graded programmatically on end state only. The best frontier models score under 10%. The abstract does not mention repeated-run reliability.
- **Workflow-generation benchmarks** (these grade generated workflows, not runtime reliability): Chat2Workflow (arXiv:2604.19667, Dify/Coze, measures "stability" of generated workflows) and MCPGen (arXiv:2609.23925, 100 projects derived from n8n community templates; no model exceeds 57% end-to-end execution success).

### Work on reliability metrics and evaluation flaws

- **AI Agents That Matter** (Kapoor et al., arXiv:2407.01502, 2024). Agent benchmarks ignore cost, lack proper holdout sets and are not standardised.
- **HAL, the Holistic Agent Leaderboard** (Kapoor et al., arXiv:2510.11977, Oct 2025). 21,730 rollouts covering 9 models and 9 benchmarks, at a cost of about $40k. It found agents searching for benchmark answers and misusing credit cards in flight booking.
- **Towards a Science of AI Agent Reliability** (Rabanser, Kapoor et al., arXiv:2602.16666, **ICML 2026**). Defines 12 metrics in four groups: consistency, robustness (fault, environment, prompt), predictability (calibration, AUROC, Brier score) and safety. Tested on **τ-bench (26 verified tasks) and GAIA**, with 5 runs, injected tool faults and paraphrased prompts. Its finding: capability gains brought only small reliability gains. The authors' own limitations: two benchmarks are "a narrow slice", they used one scaffold, and temperature 0 may overestimate reliability.
- **ReliabilityBench** (Gupta, arXiv:2601.06112, Jan 2026). Combines pass^k, task perturbations and infrastructure faults (timeouts, rate limits, schema drift) across scheduling, travel, support and e-commerce. Tested only Gemini 2.0 Flash and GPT-4o.
- **Establishing Best Practices for Rigorous Agentic Benchmarks (ABC)** (Zhu et al., arXiv:2507.02825, 2025). Shows that **τ-bench counts empty responses as successful**, and that flaws like this can overestimate performance by up to 100% in relative terms.
- **SABER** (Cuadron et al., arXiv:2512.07850, Nov 2025). Finds annotation errors in τ-bench and releases τ-Bench Verified. Each extra deviation in a *mutating* (state-changing) action cuts the odds of success by up to 92% in airline and 96% in retail.

## 2. Gap evidence

### What is already covered (and why it rules out the obvious ideas)

- **Repeated-run consistency.** Covered by the reliability-science paper (arXiv:2602.16666), ReliabilityBench (arXiv:2601.06112), Consistency as a Testable Property (arXiv:2605.10516, U-statistics and kernel trajectory metrics), Behavioral Consistency (arXiv:2602.11619; single runs misrank models about 29.3% of the time) and Beyond pass@1 (arXiv:2603.29231; reliability decay over long horizons). Agents Are Systems, Not Models (arXiv:2610.01618) attributes about 54% of outcome variance to run-to-run variability, though for scientific coding-agent tasks. The Unreliable Progress Bar (arXiv:2609.08589) shows that agents' own progress reports on τ²-bench cannot be trusted to control the flow of a task.
- **Repeated execution of natural-language workflows.** Artic (arXiv:2608.21341, Aug 2026) compiles natural-language workflows into artifact-driven ones and reports +56 points in repeated-execution consistency across 488 instances of 11 real-world workflows. **This is the nearest neighbour to candidate 1 below.** It covers text-defined workflows run by an agent, not LLM nodes inside n8n graphs, and it proposes a fix rather than a measurement study.
- **Robustness to noise and faults.** Covered by AgentNoiseBench (arXiv:2602.11348; user noise and tool noise injected into existing benchmarks) and by the fault tests in arXiv:2602.16666 and arXiv:2601.06112.
- **Error handling and duplicate side effects.** Covered by:
  - LIMBO / "Where Does Exactly-Once Live?" (arXiv:2609.29095): 25,930 episodes; 56–74% duplicate writes when the outcome cannot be checked; agents claim success in 90% of episodes that contain a duplicate.
  - UndoBench (arXiv:2610.05622, 4 Oct 2026): task completion 83.5% but recovery success only 46.7%.
  - Verified Tool Calls (arXiv:2608.02645).
  - Agent–tool boundary anomalies (arXiv:2609.15397): 98,291 MCP tools analysed.
- **Flaws in the user simulator.** Covered by Lost in Simulation (arXiv:2601.17087; agent success varies by up to 9 points across user LLMs, with a demographic bias) and UserProxyBench (arXiv:2609.38043, NeurIPS 2026 workshop; changing only the user proxy shifts mean reward by 15.2 points).
- **Benchmark annotation and grading flaws.** Covered by ABC (arXiv:2507.02825), SABER/τ-Bench Verified (arXiv:2512.07850), Automated Benchmark Auditing (arXiv:2605.26079; over 25.7% of tasks across 168 benchmarks have critical issues) and Invocation-Level Reliability (arXiv:2608.26189; scoring against fixed gold trajectories is flawed once the agent diverges).
- **Run-to-run statistical noise.** Covered by On Randomness in Agentic Evals (arXiv:2602.07150; single-run pass@1 moves by 2.2–6.0 points on SWE-bench Verified) and Don't Pass@k (arXiv:2510.04265, ICLR 2026; Bayesian estimates, tested on maths benchmarks only).
- **Small or quantized models.** Covered by AgentFloor (arXiv:2605.00334; 16 open models from 0.27B to 32B, 16,542 runs) and Flat Score, Amplified Failures (arXiv:2607.27275; 4-bit quantization amplifies τ²-bench failures by up to 2.5×, which the benchmark's error budget hides).

### Strongest remaining gap (our interpretation)

Nobody has measured, **at runtime**, how reliably the LLM steps inside real, user-built low-code workflows behave. Key questions are whether their outputs break or silently corrupt the next nodes across repeated runs, and whether the workflow's own safeguards (output parsers, retry-on-fail) catch this.

- The only large study, Tang et al. (arXiv:2606.29116, Jun 2026; 6,003 n8n workflows), is **purely static**. It states that workflow JSON reveals "encoded workflow design rather than runtime behaviour". It counts the safeguards: about 20% of workflows pair a chat model with an output parser, retry-on-fail appears in 1,854 workflows, error-trigger workflows in only 100, and human approval gates in only 167.
- FlowFixer (arXiv:2607.02882) repairs *collected* failures from Dify, Coze and n8n. Its abstract does not mention repeated-run measurement.
- Chat2Workflow and MCPGen grade *generation* of workflows, not repeated *execution* of existing ones.
- JSONSchemaBench (arXiv:2501.10868) measures schema compliance of constrained-decoding frameworks on standalone schemas, not on workflow context or effects on downstream nodes.

### Searches that did not find this already covered

Run on 2026-10-08:

- "executing real n8n workflows LLM nodes repeated runs output variability structured output failures empirical study". This returned only blogs and community threads (signals only), such as an n8n community thread on [non-deterministic outputs](https://community.n8n.io/t/ai-model-producing-different-outputs-for-the-same-input-in-n8n-agentic-workflow/84542). No paper.
- "arXiv 2026 runtime reliability LLM-powered low-code workflows Dify n8n execution failures empirical study bugs". This returned the static n8n study, FlowFixer, Compiled AI (arXiv:2604.05150) and a small n8n efficiency case study (not opened). None of them measures repeated-run reliability of template LLM nodes.
- "benchmark LLM agents n8n Zapier workflow automation execution arXiv 2025 2026". This returned AutomationBench and the generation benchmarks only.

**Honest caveat.** This gap sits next to a crowded field. A reviewer may call it "JSON-format reliability, already known". Its novelty rests on using real workflow context and measuring effects on downstream nodes, not on format compliance alone.

## 3. Candidate problems

1. **(Strongest)** *When the LLM steps of public n8n workflow templates are run repeatedly (k ≥ 5) with small or cheap models, how often does their output break or silently corrupt downstream nodes, and how much of this do the templates' built-in safeguards (output parser, retry-on-fail) catch?*
2. **(Weaker; a measurement-flaw angle)** *For cheap models on τ²-bench, are pass^k reliability rankings stable when the user-simulator model is changed and when the original tasks are swapped for the corrected ones?* This would extend Lost in Simulation and UserProxyBench, which report mean reward rather than pass^k rankings, using the 75+ τ²-bench fixes. It is mostly replication plus one new cut.
3. **(Weakest)** *Does the 12-metric reliability profile from arXiv:2602.16666 transfer from τ-bench and GAIA to a state-graded app benchmark (AppWorld) for cheap models?* The authors invite this extension ("narrow slice"), but it is mainly replication, and AppWorld tasks are long and use many tokens.

## 4. Data and environments

| Resource | Licence | Size / notes |
|---|---|---|
| n8n (self-hosted) | Sustainable Use License: internal, non-commercial and personal use allowed; commercial redistribution not allowed ([LICENSE](https://github.com/n8n-io/n8n/blob/master/LICENSE.md)) | Runs in Docker; fits 8 GB RAM (our assumption, not tested) |
| n8n study artefacts (arXiv:2606.29116) | Release promised at sites.google.com/view/n8n-empirical-study (**not checked** whether it is live) | 6,003 workflow IDs plus metadata |
| n8n.io public templates | **Licence not verified** | Source of workflow JSON |
| τ²-bench | MIT | 5 domains; LiteLLM backend |
| AppWorld | Apache 2.0; encrypted redistribution of protected parts | 750 tasks; Python 3.11+ |
| TheAgentCompany | MIT | 175 tasks; 30+ GB disk and Docker, too heavy for our laptop |
| JSONSchemaBench | CC BY 4.0 | 10K schemas (could act as a comparison point for candidate 1) |

## 5. Smallest useful version (candidate 1, 7–10 days)

- **Days 1–2: build the dataset.**
  - Select 20–30 public n8n templates that contain an LLM node followed by an output parser, code node or IF node.
  - From each template's JSON, extract the prompt, the schema or parser, and the fields the next node expects.
- **Day 3: write a Python replay harness.** It does not run n8n itself. For each node it builds about 10 realistic inputs (synthetic, which is a threat to validity), calls the model k = 10 times, and records four things:
  - (a) parse failure
  - (b) schema violation
  - (c) silent corruption, meaning the output parses but a downstream field is missing or has the wrong type or value
  - (d) whether retry-on-fail, as configured in the template, would have recovered the run
- **Days 4–7: run the models.**
  - One local model of 4B or fewer parameters via Ollama on the GTX 1650.
  - One or two cheap API models.
  - Rough load: 25 nodes × 10 inputs × 10 runs × 3 models ≈ 7.5k short calls, which should be well under $30 for cheap API models (not priced yet).
- **Days 8–10: analyse.** Compute pass^k-style consistency for each node, break down failure types, and compare runs with and without the template's safeguards.
- **Optional check:** run 3–5 templates end to end inside dockerised n8n with mocked credentials, to confirm that the replay matches real runtime behaviour.

## 6. Risks

- **Crowding (high).** This whole area moves weekly; UndoBench appeared on 4 Oct 2026 and UserProxyBench on 29 Sep 2026. Artic (arXiv:2608.21341) already measures repeated-execution consistency of natural-language workflows, so a reviewer may treat candidate 1 as a variant of it. The authors of the n8n study (arXiv:2606.29116) are well placed to publish a runtime follow-up. AutomationBench's maintainers could add pass^k.
- **Validity.** Synthetic inputs and replaying outside n8n may not match real executions, and reviewers may say so.
- **Dependencies.** The n8n template licence has not been checked, and the n8n study's dataset site may not be live. n8n's own licence is not open source, though research use looks allowed under "non-commercial".
- **Effort.** The harness is simple Python, but parsing n8n JSON (node types, expressions) may take longer than planned.
- **Candidate 2:** low novelty, because UserProxyBench and Lost in Simulation are very close.
- **Candidate 3:** close to replication, and cost risk on AppWorld.

## 7. Scores (1–5), for candidate 1 unless noted

| Criterion | Score | Justification |
|---|---|---|
| Gap strength | 3 | One clearly static prior study that explicitly says it cannot see runtime behaviour, but the gap is narrow. |
| Novelty | 2 | Neighbouring work on consistency, faults and schema compliance is dense; novelty rests on the workflow-context framing. |
| Feasibility | 3 | No training needed and the hardware fits, but extracting n8n JSON and building inputs is real work for a basic-Python solo author. |
| Data availability | 3 | Thousands of public templates exist, but their licence and the study's artefact release are unverified. |
| Cost | 4 | About 7.5k short calls plus a local model, well within $30. |
| Speed to results | 3 | First numbers by day 5–6 if template parsing goes smoothly. |
| *Area overall (gap strength)* | 2 | Consistency, faults, simulator flaws, annotation errors and small models are all covered in 2025–2026 work. |

---

## Takeaways (our interpretation)

- The broad "reliability of workflow agents" area is **too crowded** for a one-month solo paper. Almost every obvious angle (pass^k, fault injection, duplicate effects, simulator bias, benchmark audits, small or quantized models) has a 2026 paper.
- The best remaining angle is **candidate 1: runtime reliability of LLM steps inside real n8n workflows**. It also links to ticket 02 (low-code workflow security), since both use the same n8n templates, so the parsing work could be shared.
- **Verdict:** a weak-to-moderate gap. Choose it only if the low-code security and SOC-triage gap scans turn out weaker. If chosen, verify the template licence and check arXiv again just before committing.

## Unverified leads

These were seen in search results or remembered, but **not opened** in this session. Do not cite them without checking.

- Atomix, transactional tool use (arXiv:2602.14849)
- Beyond Single-Use Tokens (arXiv:2608.01710)
- Callability Is Not Operability (arXiv:2608.23628)
- τ-Knowledge (arXiv:2603.04370)
- T1-Bench (arXiv:2606.11070)
- DuMateBench (arXiv:2608.26546)
- HAS-Bench (arXiv:2607.04329)
- DataGovBench (arXiv:2512.04416)
- OdysseyBench
- FlowBench (arXiv:2406.14884)
- WorfBench (arXiv:2410.07869)
- Evaluation and Benchmarking of LLM Agents survey (arXiv:2507.21504)
- RealUserSim (arXiv:2605.20204)
- CUEing User Simulators (arXiv:2610.02460)
- Simulated Customers Never Walk Away (arXiv:2606.20708)
- Trajectory-Adapted UQ (arXiv:2608.11552)
- BC-Bench (arXiv:2608.20851)
- Korean public-API tool calling (arXiv:2609.05395)
- Evaluating Workflow Automation Efficiency Using n8n (arXiv:2602.01311)
- From recall: WorkArena++ (arXiv:2407.05291), WorkBench (arXiv:2405.00823), ToolLLM/ToolBench (arXiv:2307.16789), ToolSandbox, CRMArena / CRMArena-Pro, MAST "Why do multi-agent LLM systems fail" (arXiv:2503.13657), Who&When failure attribution
- WorkArena's ICML 2024 venue (not stated on the arXiv page I opened)
- Whether the n8n study's artefact site is live

## Sources

- arXiv:2406.12045 — Yao et al., τ-bench (2024)
- arXiv:2506.07982 — Barres et al., τ²-bench (2025)
- https://github.com/sierra-research/tau2-bench — τ²-bench repo (licence, v1.0.1 fixes)
- arXiv:2403.07718 — Drouin et al., WorkArena (2024)
- arXiv:2407.18901 — Trivedi et al., AppWorld (ACL 2024)
- https://github.com/StonyBrookNLP/appworld — AppWorld repo
- arXiv:2412.14161 — Xu et al., TheAgentCompany
- https://github.com/TheAgentCompany/TheAgentCompany — TheAgentCompany repo
- arXiv:2403.07714 — Guo et al., StableToolBench
- arXiv:2604.18934 — Shepard & Salimans, AutomationBench (2026)
- arXiv:2604.19667 — Zhong et al., Chat2Workflow (2026)
- arXiv:2609.23925 — Yang et al., MCPGen (2026)
- arXiv:2407.01502 — Kapoor et al., AI Agents That Matter (2024)
- arXiv:2510.11977 — Kapoor et al., Holistic Agent Leaderboard (2025)
- arXiv:2602.16666 — Rabanser et al., Towards a Science of AI Agent Reliability (ICML 2026)
- arXiv:2601.06112 — Gupta, ReliabilityBench (2026)
- arXiv:2605.10516 — Raj et al., Consistency as a Testable Property (2026)
- arXiv:2602.11619 — Mehta, When Agents Disagree With Themselves (ICML 2026 workshop)
- arXiv:2603.29231 — Khanal et al., Beyond pass@1 (2026)
- arXiv:2610.01618 — Wiedmann et al., Agents Are Systems, Not Models (2026)
- arXiv:2602.11348 — Wang et al., AgentNoiseBench (2026)
- arXiv:2507.02825 — Zhu et al., Agentic Benchmark Checklist (2025)
- arXiv:2512.07850 — Cuadron et al., SABER / τ-Bench Verified (2025)
- arXiv:2605.26079 — Wang et al., Automated Benchmark Auditing (2026)
- arXiv:2608.26189 — Noorain et al., Invocation-Level Reliability of Tool-Using Agents (2026)
- arXiv:2601.17087 — Seshadri et al., Lost in Simulation (2026)
- arXiv:2609.38043 — Jain & Sandhu, UserProxyBench (NeurIPS 2026 AABA4ET workshop)
- arXiv:2602.07150 — Bjarnason et al., On Randomness in Agentic Evals (2026)
- arXiv:2510.04265 — Hariri et al., Don't Pass@k (ICLR 2026)
- arXiv:2605.00334 — Karmakar & Chatterjee, AgentFloor (2026)
- arXiv:2607.27275 — Jang et al., Flat Score, Amplified Failures (2026)
- arXiv:2609.29095 — Li, Where Does Exactly-Once Live? / LIMBO (2026)
- arXiv:2610.05622 — Sah et al., UndoBench (2026)
- arXiv:2608.02645 — Mansoor et al., Verified Tool Calls (2026)
- arXiv:2609.15397 — Trofimov & Novikov, When Tool Calls Succeed but Workflows Fail (2026)
- arXiv:2609.08589 — Wang et al., The Unreliable Progress Bar (2026)
- arXiv:2608.21341 — Xu et al., Natural-Language Workflows Are Not Software Yet (2026)
- arXiv:2606.29116 — Tang et al., Characterizing LLM Agentic Workflows: A Study on N8n Ecosystem (2026)
- arXiv:2607.02882 — Ma et al., FlowFixer (2026)
- arXiv:2604.05150 — Trooskens et al., Compiled AI (2026)
- arXiv:2501.10868 — Geng et al., JSONSchemaBench (2025)
- https://github.com/n8n-io/n8n/blob/master/LICENSE.md — n8n Sustainable Use License
- Signal only (community forum, not a primary source): https://community.n8n.io/t/ai-model-producing-different-outputs-for-the-same-input-in-n8n-agentic-workflow/84542
