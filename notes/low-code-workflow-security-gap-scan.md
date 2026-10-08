# Gap scan: Security of low-code AI workflow automation

**Question:** Have the security risks of LLM/agent nodes in low-code workflow platforms (n8n, Zapier, Make, Dify, Flowise, Langflow and similar) been evaluated, especially prompt injection that flows through workflow inputs (email, webhooks, forms, documents) into tool-using actions? How does this compare with agent prompt-injection benchmarks (AgentDojo, InjecAgent), and can the platforms be self-hosted for free in Docker for a sandboxed evaluation?

**Written:** 2026-10-08. Ticket: [02-gap-scan-low-code-workflow-security](../.scratch/topic-search/issues/02-gap-scan-low-code-workflow-security.md).

**Short answer:** The hunch that this area is under-studied is **partly wrong**. A May 2026 preprint (JAW, arXiv:2605.11229) already does automated prompt-injection hijacking of n8n templates and validates the attacks in an isolated n8n instance. Two more 2026 preprints do the same for LLM agents in GitHub Actions (arXiv:2605.07135, arXiv:2606.09935). What is still open is narrower. No paper we found measures attack *rates* or the effect of *platform-native defenses* (such as the n8n Guardrails node or human-approval steps) across models, and none compares Dify, Flowise or Langflow with n8n.

Interpretation is marked **Interpretation:**. Everything else restates a cited source.

---

## 1. Landscape

Papers and benchmarks closest to the question, newest and most relevant first.

| # | Work | Venue / ID | What it does | Relevance |
|---|------|-----------|--------------|-----------|
| 1 | **Comment and Control: Hijacking Agentic Workflows via Context-Grounded Evolution** (JAW), Fendley, Liu, Guan, Zhong, Cao | arXiv:2605.11229 (May 2026, cs.CR) | JAW combines static path-feasibility analysis, dynamic prompt-provenance analysis and capability analysis to evolve hijacking inputs. It found 4,714 vulnerable GitHub Actions workflows and 8 hijackable n8n templates (out of 9,154 collected from the n8n gallery as of March 2026), spread across 2 official nodes: postgresTool (SQL injection via chat input) and executeCommand (shell RCE via a Telegram trigger). Attacks were validated in an "isolated n8n instance with mock credentials or local service endpoints". Artifacts are posted at an anonymous.4open.science link, with sensitive details withheld. | **Direct overlap.** It already covers prompt injection from n8n triggers into tools. |
| 2 | **Demystifying and Detecting Agentic Workflow Injection Vulnerabilities in GitHub Actions** (TaintAWI), Wang et al. | arXiv:2605.07135 (May 2026) | Taint analysis from untrusted event context to agent prompts and privileged sinks. It reports 519 potential vulnerabilities in 13,392 agentic workflows, 343 of them zero-days. | Same threat model, on CI/CD rather than low-code. Shows the "workflow injection" framing is now active. |
| 3 | **GitInject: Real-World Prompt Injection Attacks in AI-Powered CI/CD Pipelines**, Isbarov, Suleymanov, Shumailov, Kantarcioglu | arXiv:2606.09935 (Jun 2026) | Triggers real workflow runs on ephemeral repos and reports 11 attack classes across all tested providers. The framework is open source. | Same: CI/CD, not low-code. |
| 4 | **Characterizing LLM Agentic Workflows: A Study on n8n Ecosystem**, Tang, Zhou, Chen | arXiv:2606.29116 (Jun 2026) | Analyses 6,003 public n8n LLM workflows (task distribution, structure, reliability, autonomy). 41.80% are "logic-gated", 26.52% are "automated action", and only 2.78% (167) have human-mediated paths before external actions. The authors say they release their dataset, but we found no URL. The paper does **not** study security. | Gives a ready-made population and statistics. Its lack of security analysis leaves a gap. |
| 5 | **Demystifying the Lifecycle of Failures in Platform-Orchestrated Agentic Workflows** (AgentFail), Ma et al. | arXiv:2509.23735 (Sep 2025, rev. Feb 2026) | 307 real failure cases from Dify/Coze-style platforms. Covers reliability, not security. | Shows low-code agent platforms are being studied, but for reliability. |
| 6 | **Understanding and Mitigating Prompt Leaking Attacks in Real-World LLM-Based Applications**, Yang et al. | ACM CCS 2026; arXiv:2606.18673 | 1,200 apps on GPT Store, Poe, Coze, Tongyi, Baidu AgentBuilder and Tencent Yuanqi. Over 80% leak system prompts, and some leak third-party API keys. | Covers no-code *agent builders* for system-prompt leakage. Excludes n8n, Dify and Zapier. |
| 7 | **When AI Meets the Web: Prompt Injection Risks in Third-Party AI Chatbot Plugins**, Kaya et al. | IEEE S&P 2026; arXiv:2511.05797 | Chatbot plugins on more than 10,000 websites. Finds forged conversation histories and indirect injection via scraped content. | Measurement-study template for "deployed integrations". |
| 8 | **AgentDojo**, Debenedetti et al. | NeurIPS 2024 D&B; arXiv:2406.13352 | 97 tasks and 629 security test cases (email, banking, travel) in a Python environment. MIT licence, `pip install agentdojo`. | Main baseline. Agents run in a Python harness, not inside a workflow engine. |
| 9 | **InjecAgent**, Zhan, Liang, Ying, Kang | ACL Findings 2024; arXiv:2403.02691 | 1,054 cases, 17 user tools and 62 attacker tools. ReAct GPT-4 is vulnerable 24% of the time. | Baseline. Uses simulated tool responses. |
| 10 | **Agent Security Bench (ASB)**, Zhang et al. | ICLR 2025; arXiv:2410.02644 | 10 scenarios, more than 400 tools, 27 attack and defense methods. Highest average ASR is 84.30%. | Baseline. |
| 11 | **LivePI**, Zhao, Bhaskar, Dobriban | arXiv:2605.17986 (May 2026) | Indirect prompt injection against a real OpenClaw agent on a VM with live but test-controlled email, chat, web, file, repo and wallet interfaces. ASR ranges from 10.7% to 29.6%. | A "more realistic environment" benchmark, but an autonomous agent rather than a workflow platform. |
| 12 | **ChainFuzzer**, Wu, Yao, Nan, Zheng | arXiv:2603.12614 (Mar 2026) | Greybox fuzzing of multi-tool source-to-sink chains in 20 open-source agent apps. Finds 365 reproducible vulnerabilities. | Workflow-level tool chains, but in code-first agent apps. |
| 13 | **LLM-Enabled Open-Source Systems in the Wild: Vulnerabilities in GHSA**, Shifat et al. | LLMSC 2026 workshop; arXiv:2604.04288 | 295 GHSA advisories (Jan 2025 to Jan 2026). Mostly injection and deserialization CWEs, plus Excessive Agency and Prompt Injection patterns. | Platform-bug angle (projects not named in the abstract). |

**Platform-level advisories** (classic bugs, not prompt injection; from official CVE records via the cveawg.mitre.org API):
- n8n: CVE-2025-68613, RCE via expression injection by authenticated users, CVSS 10.0. CVE-2026-21858, unauthenticated file access via form/webhook request handling, CVSS 10.0.
- Langflow: CVE-2025-3248, unauthenticated RCE via `/api/v1/validate/code`, CVSS 9.8.
- Flowise: CVE-2025-59528, RCE via the CustomMCP node config, CVSS 10.0.
- A GitHub Advisory Database search for "n8n" returned 277 advisories on 2026-10-08.

**Weakly related.** arXiv:2505.12490 (Louck, Stulman, Dvir; A2A protocol) contains one anecdotal n8n case study in which one agent coaxes a secret out of another. It is not a systematic evaluation.

## 2. Gap evidence

**The originally hypothesised gap ("nobody has tested prompt injection through n8n/low-code triggers into tools") is not real.** JAW (arXiv:2605.11229) does exactly this for n8n. It covers chat and Telegram triggers, with webhook, form and email fields in its threat model, and validates the attacks in an isolated instance. The adjacent CI/CD setting got two papers in May–June 2026 (arXiv:2605.07135, arXiv:2606.09935).

**What JAW and the others leave open** (from what we read in JAW's HTML; JAW's n8n section is short):
- **Rates and defenses.** JAW reports *existence* (8 hijackable templates, <0.1% of 9,154). It gives no stage-by-stage filtering numbers, does not say which target LLMs ran the n8n agents, and does not evaluate n8n's own defenses. n8n ships a **Guardrails node** with Jailbreak, PII, Secret Keys and Topical Alignment checks that can run before or after an LLM call (n8n docs). We found **no paper that evaluates it**.
- **Sinks.** JAW's n8n findings are code and DB sinks (SQL, shell). Business-logic sinks (send email, HTTP request, CRM or sheet writes) that n8n templates commonly wire to agents are not reported for n8n.
- **Other platforms.** We found no security evaluation of prompt injection through Dify, Flowise or Langflow workflows. The papers we found on these platforms cover reliability (AgentFail) or CVEs in platform code. Zapier and Make are closed SaaS and appear in no paper we found.
- **Transfer from benchmarks.** AgentDojo, InjecAgent and ASB run agents in Python harnesses. In n8n, untrusted trigger data is often interpolated via expressions into the *system prompt* or user message, tools are fixed nodes with stored credentials, and LLM output feeds deterministic downstream nodes. Whether benchmark ASRs predict behaviour in these node graphs is **untested** in what we found.
- **Population exposure.** The n8n characterization study (arXiv:2606.29116) gives the population (6,003 workflows, 2.78% with a human gate) but no security analysis. We found no census of untrusted-trigger to LLM to privileged-sink paths across that population.

**Searches that did not find the residual gap already covered** (WebSearch, 2026-10-08):
- "arXiv security low-code LLM workflow platforms Dify Flowise Langflow prompt injection"
- "n8n AI agent workflow prompt injection security study arXiv 2025"
- "agentic workflow platforms vulnerabilities empirical study Dify Coze n8n arXiv" (this one found JAW, AgentFail and the n8n characterization)
- "site:arxiv.org n8n prompt injection", "site:arxiv.org Dify prompt injection workflow", "site:arxiv.org Langflow OR Flowise security agent"
- "taint analysis static analysis low-code LLM workflow JSON n8n Dify DSL prompt injection detection paper" (found TaintAWI, TaintP2X, AgentFuzz; all code-level or GitHub Actions)
- "benchmark prompt injection workflow automation n8n OR Zapier OR Make.com LLM node email webhook arXiv" (blogs only)
- "arXiv 2026 low-code agentic workflow prompt injection measurement templates Make Zapier n8n" (no match)
- "Microsoft Copilot Studio OR Zapier agents prompt injection research paper" (vendor blogs only)
- "n8n Guardrails node ... jailbreak prompt injection detection" (docs and blogs only, no evaluation papers)

**Interpretation:** The residual gap is mainly an *untested setting*. Platform-native defenses and benchmark-to-platform transfer have not been measured. Of the two gap types the map's Notes accept, this is the weaker one. It is a sound empirical contribution, but a reviewer who knows JAW will read it as "a follow-up measurement".

## 3. Candidate problems

1. **RQ1 (defense efficacy).** In common n8n AI-agent workflow patterns fed by untrusted triggers (email, form, webhook, document), how much do platform-native mitigations reduce indirect-prompt-injection success and task utility across small local models and one cheap API model? Mitigations: the Guardrails node's jailbreak check, a human-approval gate, putting untrusted data in the user message rather than the system prompt, and a structured-output parser.
2. **RQ2 (exposure census).** What fraction of public n8n AI workflow templates have an untrusted-trigger to LLM-node to privileged-sink path with no guard or human gate? How often is untrusted data interpolated into the system prompt? This would be a static analysis of template JSON, scoped beyond JAW's 8 confirmed code/DB exploits to business-logic sinks.
3. **RQ3 (benchmark transfer).** Do attack success rates measured in AgentDojo-style Python harnesses predict ASR when the *same* tasks and injections run inside an n8n workflow graph? This would make RQ1 a "flawed or unrepresentative evaluation" contribution if the numbers diverge.

**Interpretation:** RQ1 combined with RQ3 is the strongest single paper. RQ2 is a cheap add-on section that motivates which patterns to test.

## 4. Data and environments

| Resource | Licence / terms | Size / requirements | Source |
|----------|-----------------|---------------------|--------|
| n8n (self-host, Docker) | Sustainable Use License v1.0: "use or modify the software only for your own internal business purposes or for non-commercial or personal use". Academic research fits. | `docker run ... n8nio/n8n` on port 5678; docs now recommend Docker Compose. No hardware minimum stated. | n8n docs; n8n `LICENSE.md` |
| n8n Self-hosted AI Starter Kit | Apache-2.0 | Compose bundle with n8n, Ollama, Qdrant and Postgres; has CPU and NVIDIA GPU profiles; meant for proof-of-concept use | GitHub n8n-io/self-hosted-ai-starter-kit |
| n8n Ollama Chat Model node and Guardrails node | Part of n8n | Ollama node plugs local models into agents. Guardrails LLM checks need a connected chat model. | n8n docs |
| n8n templates | Public gallery and API; endpoints listed in docs (`/templates/workflows/<id>`, `/templates/search`, ...). **Terms of use for bulk download not checked.** | About 9,154 templates (JAW, Mar 2026); 6,003 LLM workflows (arXiv:2606.29116) | n8n docs; arXiv:2605.11229; arXiv:2606.29116 |
| JAW artifact | Anonymous repository; vulnerable-workflow dataset partly withheld | Unknown | arXiv:2605.11229 Open Science appendix |
| n8n characterization dataset | Release promised; no URL found | 6,003 JSON workflows | arXiv:2606.29116 |
| Dify (self-host) | Modified Apache-2.0 (multi-tenant and logo conditions) | Minimum 2 CPU and 4 GiB RAM; **16 containers** (API, worker, Weaviate, Postgres, Redis, sandbox, SSRF proxy, ...) | Dify docs; Dify `LICENSE` |
| Flowise | Apache-2.0 | `docker compose up -d`, port 3000 | GitHub FlowiseAI/Flowise |
| Langflow | MIT | `docker run -p 7860:7860 langflowai/langflow:latest` | GitHub langflow-ai/langflow |
| AgentDojo | MIT; `pip install agentdojo` | 97 tasks, 629 injection cases | arXiv:2406.13352; GitHub ethz-spylab/agentdojo |
| InjecAgent | Public on GitHub (licence not checked) | 1,054 cases | arXiv:2403.02691 |
| Zapier, Make | Closed SaaS, no self-host | n/a. Testing would mean running experiments on a vendor's live service, which the map's constraints rule out. | (no source opened; inference from the platforms being SaaS-only) |

**Interpretation:** n8n, Flowise and Langflow are free to self-host in Docker on the target laptop. Dify's 16-container stack plus Ollama is likely too heavy for 8 GB RAM, so treat it as optional.

## 5. Smallest useful version (7–10 days, our hardware and budget)

- **Environment:** n8n (version pinned, bound to localhost only, never internet-facing given the CVE history), Ollama, and mock sinks (a local webhook catcher and a local SMTP catcher). All credentials are mock credentials. This mirrors JAW's isolated-instance validation.
- **Workflows:** 4–5 hand-built patterns modelled on common templates:
  - email triage agent with a send-email tool
  - form to LLM summary to HTTP post
  - webhook support bot with a DB-query tool
  - document Q&A with a file tool
- **Attacks:** about 20 injection payloads adapted from AgentDojo and InjecAgent, injected through the trigger payload. Workflows are driven from a Python script via webhook URLs.
- **Conditions:** no defense; Guardrails jailbreak check; untrusted data in the user message rather than the system prompt; structured output. Optionally a human-approval gate, simulated as an auto-reject so the sink is never reached.
- **Models:** 1–2 local models of about 3–4B parameters via Ollama, plus one cheap API model. 5 patterns × 20 payloads × 4 conditions × 3 models × 3 repeats is about 3,600 runs. The API share at mini-model prices should be a few dollars (not costed precisely).
- **RQ3 slice:** run the same 20 payloads on the matching AgentDojo suite (email/workspace) with the same models and compare ASR.
- **RQ2 slice (2–3 days):** a Python script over template JSON that flags trigger to LLM to sink paths and system-prompt interpolation. Report counts only; do no live exploitation.
- **Metrics:** ASR (sink reached with the attacker's argument), utility under no attack, and the Guardrails false-positive rate on benign inputs.

## 6. Risks

- **Crowding (high).** JAW (May 2026) occupies the core n8n hijacking claim. Its authors, or the TaintAWI and GitInject groups, could plausibly extend to more low-code platforms or defenses within months. Three closely related preprints appeared in May–June 2026 alone. Reviewers will expect JAW as the direct predecessor and a clear delta.
- **"Benchmark in a new wrapper" critique.** Without RQ3's transfer comparison or a surprising defense result, RQ1 can read as AgentDojo rerun inside n8n.
- **Small-model validity.** AgentDojo reports that even state-of-the-art LLMs "fail at many tasks (even in the absence of attacks)". 3–4B local models may have very low utility, which makes ASR hard to interpret. Tool-calling quality of specific 3–4B models inside n8n's agent node was **not verified**.
- **Platform churn.** n8n is moving through major versions (2.x) with many security advisories (277 GHSA hits). Pin a version and report it. Guardrails node behaviour may change.
- **Data access.** Bulk template download terms are unchecked. The n8n characterization dataset URL was not found. The JAW dataset is partly withheld.
- **Ethics and constraints.** Keep to a local sandbox with mock credentials only. Do not probe public n8n instances or vendor SaaS (Zapier, Make, Copilot Studio). If the census finds a template that is dangerous as published, report it to n8n rather than publishing a payload.
- **Hardware.** Dify plus Ollama on 8 GB RAM is likely infeasible. Restrict cross-platform claims to n8n, plus Flowise and Langflow only if time allows.

## 7. Scores (1–5)

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Gap strength | **2** | The core "untested setting" is already covered for n8n by JAW (arXiv:2605.11229). What remains is a narrower defense-and-rates gap. |
| Novelty | **2** | Incremental over JAW plus AgentDojo. Novelty depends on RQ3 showing a benchmark-to-platform divergence or Guardrails failing. |
| Feasibility | **4** | n8n in Docker with Ollama and Python webhook driving fits the student's existing n8n and Docker skills. Small-model utility is the main doubt. |
| Data availability | **4** | Templates via a public API, AgentDojo (MIT) and InjecAgent payloads, all platforms free to self-host. Template bulk-use terms are unchecked. |
| Cost | **5** | Self-hosted software and local models, with only a few dollars of API spend. |
| Speed to results | **4** | First ASR numbers are realistic within a week. Building 4–5 workflows and the harness takes about 3–4 days. |

## Takeaways

- The planner's hunch should be revised. Low-code workflow prompt-injection security **is being studied as of 2026**, and n8n specifically was covered by JAW in May 2026. This is not a wide-open gap.
- A defensible, modest paper remains: **measure platform-native defenses and benchmark-to-platform transfer inside n8n** (RQ1 combined with RQ3), with a static exposure census (RQ2) as motivation. It is feasible and cheap, but crowding risk is high and novelty is moderate at best. It suits a regional venue or arXiv, not a top-tier one.
- Compare it against the other gap scans before choosing. If another area has a gap that is truly untested rather than "follow-up measurement", that area should probably win.

## Unverified leads

Seen only in search-result snippets or secondary write-ups; not opened, so not used as evidence above.
- "An Empirical Study on the Security Vulnerabilities of GPTs", arXiv:2512.00136.
- "Unsafe by Design? A First Look at Security and Privacy Risks in OpenAI's Custom GPT Ecosystem", DOI 10.1145/3733802.3764054.
- "From Prompt Injections to Protocol Exploits: Threats in LLM-Powered AI Agents Workflows", arXiv:2506.23260 (survey).
- "TaintP2X: Detecting Taint-Style Prompt-to-Anything Injection Vulnerabilities in LLM-Integrated Applications", ICSE 2026, DOI 10.1145/3744916.3773199.
- "Make Agent Defeat Agent" (AgentFuzz), USENIX Security 2025, as listed by the search engine.
- "How Your Credentials Are Leaked by LLM Agent Skills", arXiv:2604.03070.
- "Review of Tools for Zero-Code LLM Based Application Development", arXiv:2510.19747.
- **Signals only (vendor and press, not primary):**
  - Tenable blog on Copilot Studio prompt injection, plus a reported CVE-2026-21520 for Copilot Studio indirect prompt injection (not checked in the CVE API).
  - Coze Studio README security warnings, as reported by a third-party blog.
  - Imperva blog on Dify account-takeover and tenant-isolation bugs.
  - CSA research notes on n8n and Flowise exploitation.
  - GitGuardian finding of 321 n8n instances accepting leaked tokens, via The Hacker News.
  - Langflow CVE-2026-33017 and CVE-2026-9198 (not checked in the CVE API).

## Sources

Papers (all opened on 2026-10-08 via arxiv.org abstract or HTML pages):
- Fendley, Liu, Guan, Zhong, Cao. *Comment and Control: Hijacking Agentic Workflows via Context-Grounded Evolution.* arXiv:2605.11229 (2026). https://arxiv.org/abs/2605.11229
- Wang et al. *Demystifying and Detecting Agentic Workflow Injection Vulnerabilities in GitHub Actions.* arXiv:2605.07135 (2026). https://arxiv.org/abs/2605.07135
- Isbarov, Suleymanov, Shumailov, Kantarcioglu. *GitInject: Real-World Prompt Injection Attacks in AI-Powered CI/CD Pipelines.* arXiv:2606.09935 (2026). https://arxiv.org/abs/2606.09935
- Tang, Zhou, Chen. *Characterizing Large Language Model Agentic Workflows: A Study on N8n Ecosystem.* arXiv:2606.29116 (2026). https://arxiv.org/abs/2606.29116
- Ma et al. *Demystifying the Lifecycle of Failures in Platform-Orchestrated Agentic Workflows.* arXiv:2509.23735 (2025/2026). https://arxiv.org/abs/2509.23735
- Yang et al. *Understanding and Mitigating Prompt Leaking Attacks in Real-World LLM-Based Applications.* ACM CCS 2026; arXiv:2606.18673. https://arxiv.org/abs/2606.18673
- Kaya et al. *When AI Meets the Web: Prompt Injection Risks in Third-Party AI Chatbot Plugins.* IEEE S&P 2026; arXiv:2511.05797. https://arxiv.org/abs/2511.05797
- Debenedetti et al. *AgentDojo.* NeurIPS 2024 Datasets & Benchmarks; arXiv:2406.13352. https://arxiv.org/abs/2406.13352. Code: https://github.com/ethz-spylab/agentdojo
- Zhan, Liang, Ying, Kang. *InjecAgent.* Findings of ACL 2024; arXiv:2403.02691. https://arxiv.org/abs/2403.02691
- Zhang et al. *Agent Security Bench (ASB).* ICLR 2025; arXiv:2410.02644. https://arxiv.org/abs/2410.02644
- Zhao, Bhaskar, Dobriban. *LivePI.* arXiv:2605.17986 (2026). https://arxiv.org/abs/2605.17986
- Wu, Yao, Nan, Zheng. *ChainFuzzer.* arXiv:2603.12614 (2026). https://arxiv.org/abs/2603.12614
- Shifat et al. *LLM-Enabled Open-Source Systems in the Wild: An Empirical Study of Vulnerabilities in GitHub Security Advisories.* LLMSC 2026; arXiv:2604.04288. https://arxiv.org/abs/2604.04288
- Louck, Stulman, Dvir. *Improving Google A2A Protocol.* arXiv:2505.12490 (2025). https://arxiv.org/abs/2505.12490
- Shivakumar, Priya, Gao. *AgentFlow: A Flow-Centric Policy Language and Framework for Securing LLM Agent Systems.* arXiv:2608.22868 (2026). Opened to confirm it evaluates only on AgentDojo, ASB, InjecAgent etc., not low-code platforms. https://arxiv.org/abs/2608.22868
- Rajagopalan, Rao. *Authenticated Workflows.* arXiv:2602.10465 (2026). Opened; integrates code-first frameworks, not low-code platforms. https://arxiv.org/abs/2602.10465

Official docs, licences and advisories (opened 2026-10-08):
- n8n Docker install: https://docs.n8n.io/hosting/installation/docker/
- n8n licence (Sustainable Use License): https://github.com/n8n-io/n8n/blob/master/LICENSE.md
- n8n Guardrails node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.guardrails/
- n8n Ollama Chat Model node: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatollama/
- n8n workflow templates and API endpoints: https://docs.n8n.io/workflows/templates/
- n8n Self-hosted AI Starter Kit: https://github.com/n8n-io/self-hosted-ai-starter-kit
- Dify Docker Compose deployment: https://docs.dify.ai/en/getting-started/install-self-hosted/docker-compose
- Dify licence: https://github.com/langgenius/dify/blob/main/LICENSE
- Flowise repository: https://github.com/FlowiseAI/Flowise
- Langflow repository: https://github.com/langflow-ai/langflow
- GitHub Advisory Database, query "n8n": https://github.com/advisories?query=n8n
- CVE records via https://cveawg.mitre.org/api/cve/: CVE-2025-68613 (n8n), CVE-2026-21858 (n8n), CVE-2025-3248 (Langflow), CVE-2025-59528 (Flowise)
