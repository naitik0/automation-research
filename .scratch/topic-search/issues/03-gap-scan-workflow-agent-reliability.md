# Gap scan: Reliability of LLM agents in multi-step workflow automation

Type: research
Status: resolved
Blocked by: none
Map: [Topic search](../map.md)
Findings: [notes/workflow-agent-reliability-gap-scan.md](../../../notes/workflow-agent-reliability-gap-scan.md) (also on branch `research/workflow-agent-reliability`)

## Question

Where is the strongest research gap in measuring how reliably LLM agents execute multi-step workflow-automation tasks (consistency across runs, error handling, failure modes, cost), outside of coding and web browsing? Answer using the gap-scan rubric in the map's Notes. Identify the existing agent/workflow benchmarks and whether any known flaws in how they evaluate reliability have been documented.

## Answer

**Verdict: weak-to-moderate gap; the area is crowded.** 2025–2026 papers already cover pass^k consistency, fault injection, duplicate side effects on retry, user-simulator bias, τ-bench evaluation flaws, and small or quantized models.

Best remaining candidate problem: *When the LLM steps in public n8n workflow templates are run k≥5 times with small or cheap models, how often do they fail or silently pass corrupted output to later nodes, and do the templates' own safeguards (output parsers, retry-on-fail) catch it?* The only large n8n study (arXiv:2606.29116) is static, with no runtime evaluation.

Scores for that candidate: gap 3, novelty 2, feasibility 3, data 3, cost 4, speed 3.

Two weaker candidates (pass^k stability on τ²-bench across user simulators; carrying the ICML 2026 reliability metrics over to AppWorld) are mostly replication.

Overlaps with the low-code workflow security gap scan: both would reuse public n8n templates. Before relying on it, check the n8n template licence and recent arXiv preprints.
