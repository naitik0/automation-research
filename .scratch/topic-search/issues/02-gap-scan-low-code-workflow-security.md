# Gap scan: Security of low-code AI workflow automation

Type: research
Status: resolved
Blocked by: none
Map: [Topic search](../map.md)
Findings: [notes/low-code-workflow-security-gap-scan.md](../../../notes/low-code-workflow-security-gap-scan.md) (also on branch `research/low-code-workflow-security`)

## Question

Have the security risks of LLM/agent nodes in low-code workflow platforms (n8n, Zapier, Make, Dify, Flowise, Langflow and similar) been evaluated, especially prompt injection that flows through workflow inputs such as email, webhooks, forms or documents into tool-using actions? Answer using the gap-scan rubric in the map's Notes. Compare against existing agent prompt-injection benchmarks (e.g. AgentDojo, InjecAgent) to show what they do and don't cover, and check whether these platforms can be self-hosted for free in Docker for a sandboxed evaluation.

## Answer

**Verdict: feasible and cheap, but the main gap I expected isn't there.** The idea that nobody has tested prompt injection into tools through n8n triggers is wrong. JAW (arXiv:2605.11229, May 2026) does exactly that for n8n templates: it found 8 hijackable templates out of 9,154 and confirmed the attacks in an isolated instance. Two May–June 2026 preprints do the same for LLM agents in GitHub Actions (arXiv:2605.07135, arXiv:2606.09935).

What is still open (an untested setting, which is the weaker of the two accepted gap types):
- No paper measures attack *rates*, or the effect of n8n's own defences (the Guardrails node, human-approval steps, keeping untrusted input out of the system prompt, structured output), across models.
- Business-logic actions (send email, HTTP requests, CRM or spreadsheet writes) aren't reported for n8n. JAW's n8n findings are SQL and shell.
- No comparison with Dify, Flowise or Langflow.

Candidate problems:
1. How much do n8n's built-in defences reduce injection success, and what do they cost in task usefulness, across small local models and one cheap API model?
2. What share of public n8n AI templates send untrusted input through an LLM node to a sensitive action without a guard?
3. Do attack success rates from AgentDojo-style benchmarks predict what happens when the same tasks run inside an n8n workflow?

Scores: gap 2, novelty 2, feasibility 4, data 4, cost 5, speed 4. Problems 1 and 3 together make a modest paper for a regional venue, as long as it presents JAW as its direct predecessor.
