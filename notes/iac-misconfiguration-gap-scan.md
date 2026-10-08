# Gap scan: LLM detection of Docker and IaC security misconfigurations

**Question.** Where is the strongest research gap in using LLMs to detect (or fix) security misconfigurations in Dockerfiles, docker-compose, Kubernetes manifests or Terraform, compared with static analysers (Hadolint, Checkov, Trivy, KICS)? Which labelled public datasets exist, and do existing studies use a sound ground truth?

**Written:** 2026-10-08. Ticket: `.scratch/topic-search/issues/04-gap-scan-docker-iac-misconfiguration.md`.

**Short answer.** The area is crowded. Kubernetes detection, Kubernetes and Terraform *repair*, and Ansible/Puppet/Chef smell detection all have several 2024–2026 papers, many from the last six months. Two narrow openings remain. (a) **Docker Compose** has no LLM security-detection study that we could find, and only one of the four named analysers documents Compose support. (b) **Ground truth**: most Kubernetes detection studies label their data with the output of the same rule-based tools they compare against, which is circular. A small study that measures how much this distorts the reported results is feasible. Neither opening is wide.

---

## 1. Landscape

What each source says. Our assessment is in the Takeaways section below.

| # | Work | Venue / ID | Artefact | Task | Ground truth |
|---|------|-----------|----------|------|--------------|
| 1 | GenKubeSec (Malul et al.) | arXiv:2405.19954 (conference paper, Dec 2024) | Kubernetes | Detect, localise, explain, repair | Labels taken from the union of **Checkov, KubeLinter and Terrascan** output, mapped to a 169-item index. Experts re-checked the model's "false positives" and judged 408/489 (83.4%) to be correct. 30 repair outputs were checked by one expert. Dataset and code are public. Detector is a fine-tuned CodeT5p-770M; repairer is Mistral-7B used with prompting. |
| 2 | Ghorab & Saied, "Towards Secure Cloud-Native Computing…" | IEEE CLOUD 2025; arXiv:2609.20834 | Kubernetes | Detect | Labels: "any issue flagged by at least one tool" among **Snyk, Kube Score and Datree**. Dataset 4 adds synthetic mutations validated by the same tools. Fine-tuned BERT, CodeBERT, RoBERTa and LLaMA3 are compared with 6 tools. The replication package is on anonymous.4open.science. |
| 3 | Ghorab, Abdel Latif & Saied, "Kubernetes Misconfigurations in the Wild" | AIware 2026; arXiv:2609.27030; DOI 10.1145/3805760.3814908 | Kubernetes | Taxonomy and repair | Built from 2,662 Stack Overflow issues. The Kubecurity schema-guided repair reaches 98.5% correction accuracy; the best plain LLM reaches 89.06%. |
| 4 | LLMSecConfig (Ye, Le & Babar) | MSR 2025; arXiv:2502.02009 | Kubernetes (from Helm/ArtifactHub) | Repair | Success means the YAML parses **and Checkov re-scans clean**. No kubectl dry-run or semantic check. Reports a 94% success rate on 1,000 configurations with Mistral Large 2 and GPT-4o-mini. States that "there is an absence of public datasets specifically designed for container misconfiguration remediation." |
| 5 | Minna, Massacci & Tuma, Helm charts | MSR 2024 Registered Report; arXiv:2403.09537 | Helm/Kubernetes | Detect with tools, repair with LLM | Misconfigurations come from Checkov and KICS. LLM fixes are re-checked by the same tools, plus a manual check of a subset. |
| 6 | Zhang & Omoronyia, "Security smell detection in Dockerfiles" | Automated Software Engineering 33:135 (Sep 2026); DOI 10.1007/s10515-026-00684-z | Dockerfile | Detect and explain | **4,000 Dockerfiles annotated by hand by domain experts** (from the Henkel and Lin corpora), covering 10 of 29 taxonomy categories. No inter-annotator agreement is reported. A QLoRA fine-tuned Qwen3-8B reaches macro P 0.97 / R 0.94. Tool recall: Hadolint 0.65, KICS 0.70, Trivy 0.66. **No general-purpose LLM (GPT/Claude/Llama) baseline**; the only prompted baseline is few-shot Qwen3-8B. **Dockerfiles only; no Compose.** The authors list as a limitation "the absence of an external, independently annotated benchmark for Dockerfile security smells". The artefact is a supplementary ZIP. |
| 7 | IntelliSA (Mei & Fu) | MSR 2026; arXiv:2601.14595 | Ansible, Puppet, Chef | Detect | A human-labelled set of 241 scripts (11,814 LOC). Compared with SLIC, SLAC, GLITCH and three LLMs (Claude-4, Grok-4, GPT-5). |
| 8 | War et al., semantics-aware IaC smell detection | arXiv:2509.18790 (Sep 2025) | Ansible, Puppet | Detect | Uses existing misconfiguration datasets. Combines CodeBERT and LongFormer and compares against 4 LLMs. |
| 9 | TerraProbe (Alsaid et al.) | arXiv:2606.26590 (journal-first, Empirical Software Engineering) | Terraform | Repair evaluation | Layered oracle plus human adjudication (κ = 0.78). The targeted Checkov finding is removed in **83.3%** of repairs, but the full scanner comes back clean in only **10.4%**. 71.4% of the plan-compared repairs were "deceptive". Uses TerraDS. |
| 10 | IaC-Guard-V (Chauhan) | QRS 2026; arXiv:2609.28488 | Terraform, Kubernetes | Repair verification | 70 samples. Only 32–50% of single-shot repairs pass a 4-dimension verification; iterative repair reaches 68–92%. |

Related work, mostly not LLM detection:
- KubeGuard, LLM-assisted Kubernetes hardening using manifests plus runtime logs (arXiv:2509.04191).
- KuTIE, topology-aware Kubernetes patching, LLMSec@ESORICS 2026 (arXiv:2607.25995).
- Security of LLM-*generated* Terraform, SBSeg 2026 (arXiv:2608.02672).
- LLM-based Dockerfile refactoring for size and build time, MSR 2025 (arXiv:2501.14131).
- Industrial clustering of Dockerfile reference standards, ASE 2026 Industry (arXiv:2608.25793).
- Docker Hub image scanning at scale (arXiv:2608.02669).
- Pre-LLM baselines: GLITCH (arXiv:2205.14371); Rahman et al., Kubernetes manifests with SLI-KUBE, 2,039 manifests (ACM 2023, hdl.handle.net/10919/113801); Parfum (arXiv:2302.01707); Rosa et al., Dockerfile smell fixing, ICSME 2022 RR (arXiv:2208.09097).

## 2. Gap evidence

**Gap A, an untested setting: Docker Compose.**
- None of the searches found an LLM study that detects security misconfigurations in docker-compose files. Searches tried: "docker-compose security misconfiguration dataset LLM"; "Docker Compose security smells misconfiguration study LLM detection 2025 2026 arXiv" (extended); "Docker Compose security misconfigurations empirical study GitHub arXiv". Every hit was about Kubernetes or Dockerfiles, or was a non-academic tool.
- Zhang & Omoronyia explicitly exclude anything other than Dockerfiles (row 6).
- The closest empirical work is not about security detection. Ibrahim, Sayagh & Hassan (EMSE 2021, DOI 10.1007/s10664-021-10025-1) studied 4,103 GitHub projects and found only **4.3%** of multi-component apps use any security-related Compose option. Eng et al. (arXiv:2305.11293) catalogue composition patterns.
- Analyser coverage is thin. KICS documents Docker Compose support ([KICS platforms](https://docs.kics.io/latest/platforms/)). Hadolint is Dockerfile-only. Checkov's framework list includes Dockerfile but not Compose. Trivy's misconfiguration docs list Dockerfile, Kubernetes, Terraform, CloudFormation, ARM and Helm, but not Compose.
- So for Compose the LLM-versus-analyser comparison has essentially one rule-based baseline. That is both the opportunity and a weakness.

**Gap B, a flawed evaluation: tool-derived ground truth in LLM detection studies.**
- In two Kubernetes detection studies (rows 1 and 2), the "ground truth" is the output of rule-based tools, and the LLM is then scored against tools. With union-of-tools labels, the tool ensemble scores perfectly by construction: GenKubeSec reports RB-Ensemble P = R = F1 = 1.0.
- GenKubeSec's own manual check found that 83% of the model's "false positives" were real misconfigurations. That is direct evidence that the tool labels are incomplete, so they understate LLM precision.
- On the repair side the same flaw is shown and is now crowded: LLMSecConfig and the Helm study validate with the same scanners, and TerraProbe and IaC-Guard-V show that a scanner passing is a weak oracle.
- On the **detection** side, the only Docker/IaC study we found with expert labels that compares against Hadolint, KICS and Trivy is Zhang & Omoronyia, for Dockerfiles. It reports no inter-annotator agreement and no general-purpose LLM baseline.
- Searches tried: "evaluating LLMs detecting security misconfigurations Kubernetes manifests zero-shot ground truth manual annotation 2025 2026" (extended); "LLM Terraform misconfiguration detection vs Checkov tfsec … manually labelled" (extended). Neither found a study that quantifies how tool-derived labels distort LLM-versus-analyser detection results.

**What is not a gap (crowded):**
- Kubernetes detection (rows 1–3, plus KubeGuard).
- Kubernetes and Terraform repair (rows 3, 4, 9, 10, KuTIE). Five papers since Feb 2025, three since June 2026.
- Ansible/Puppet/Chef smell detection with LLM baselines (rows 7 and 8).
- Dockerfile detection with a fine-tuned LLM and expert labels (row 6, published Sep 2026).

## 3. Candidate problems

1. **CP1, Compose detection.** How accurately do off-the-shelf LLMs (small local models and cheap API models) detect security misconfigurations in real docker-compose files, compared with KICS, when both are scored against hand-labelled ground truth? Which misconfiguration types (privileged, host network or PID, docker.sock mounts, hard-coded secrets, missing `user`/`cap_drop`/`read_only`, exposed ports) does each one miss?
2. **CP2, ground-truth distortion.** When LLM misconfiguration detectors are scored against static-analyser output instead of manually adjudicated labels, how much do their reported precision, recall and ranking change? Does that change the conclusion "LLM vs analyser"? Setting: Kubernetes manifests and/or Dockerfiles, with labels adjudicated only on the disagreement set.
3. **CP3, a narrow follow-up.** Do general-purpose prompted LLMs, with no fine-tuning, match the fine-tuned Dockerfile detector and Hadolint/KICS/Trivy on an independently labelled Dockerfile set? This depends on reusing or extending Zhang & Omoronyia's labels. It is the weakest of the three and partly overlaps CP2.

Merging CP1 and CP2 is natural: a Compose benchmark labelled by hand, where the paper also reports how results would differ if KICS output were treated as the truth.

## 4. Data and environments

| Resource | Content / size | Licence | Labels? |
|----------|----------------|---------|---------|
| Binnacle (Henkel et al., ICSE 2020), [GitHub](https://github.com/jjhenkel/binnacle-icse2020) | A gold set of Dockerfiles plus a GitHub set about 450 times larger, as `jsonl.xz` | MIT | No security labels |
| Rosa et al. Dockerfile corpus (arXiv:2208.09097) | About 9.4M Dockerfiles with commit history, from World of Code | not checked | Hadolint-detected smells only (tool labels) |
| Zhang & Omoronyia artefact (DOI 10.1007/s10515-026-00684-z) | 4,000 expert-annotated Dockerfiles, 10 categories | not checked (supplementary ZIP) | **Manual** |
| GenKubeSec dataset (arXiv:2405.19954) | About 276k Kubernetes config files plus a unified misconfiguration index | stated public; licence not checked | Tool-derived (Checkov ∪ KubeLinter ∪ Terrascan) |
| LLMSecConfig dataset (arXiv:2502.02009) | 1,000 Kubernetes configs from ArtifactHub, on figshare | not checked | Checkov-derived |
| Ghorab & Saied package (arXiv:2609.20834) | 13.7k–276k Kubernetes entries; 2,097 Helm files | not checked | Tool-derived (Snyk ∪ Kube Score ∪ Datree) |
| TerraDS ([Zenodo 14217386](https://zenodo.org/records/14217386)) | 62,406 repos, 279,344 modules, about 785 MB | CC-BY-4.0 | None |
| IntelliSA set (arXiv:2601.14595) | 241 Ansible/Puppet/Chef scripts | not checked | Manual |
| Docker Compose | **No labelled public corpus found.** The Ibrahim et al. (4,103 projects) and Eng et al. corpora are candidate sources; availability was not checked. | — | — |

Tools:
- Hadolint: GPL-3.0, Dockerfile only, 67 DL rules plus ShellCheck. Relevant rules include DL3002 (last user root), DL3004 (sudo), DL3007 (latest), DL3020 (ADD vs COPY) and DL3064 (secrets in ARG/ENV).
- Checkov: Apache-2.0, 38 Dockerfile checks, Kubernetes, Terraform, Helm. Compose is not listed.
- Trivy: Apache-2.0. Compose is not listed in its misconfiguration docs.
- KICS: Apache-2.0, 20+ platforms including Docker Compose.
- All four run on a laptop with no GPU.

## 5. Smallest useful version (7–10 days)

For CP1 combined with CP2:
1. **Days 1–2.** Collect about 200–300 docker-compose files from public GitHub repositories with permissive licences, using a GitHub code search or sampling from the cited corpora. Deduplicate. Run KICS on all of them.
2. **Days 2–5.** Write a labelling guide for about 8 Compose risk types, grounded in KICS query descriptions and Docker documentation, then label by hand. One annotator is a threat to validity. Mitigate it by re-labelling a 20% subset after a week to get intra-rater κ. A peer second rater would count as collaboration, not a human-subjects study, but confirm that.
3. **Days 4–7.** Run 2–3 LLMs zero-shot and few-shot with a JSON output schema: one local model of 4B parameters or fewer via Ollama on the GTX 1650, and 1–2 cheap API models. 300 files × 3 models × about 3k tokens is roughly 3M tokens. This is expected to be well under $30 with low-cost models, but check prices in ticket 05.
4. **Days 7–9.** Compute per-type precision, recall and F1 against manual labels. Rescore everything against "KICS as ground truth" and report how the ranking changes; this is the CP2 result. Do a small error analysis.

Within the constraints: no training, no human subjects, laptop-scale compute.

## 6. Risks

- **Crowding.** The area moves very fast. 2609.* preprints (Ghorab ×2, IaC-Guard-V) and a Sep 2026 journal paper (row 6) appeared within the last month. The Ghorab/Saied group and the Malul/Shabtai group each have active Kubernetes lines and could plausibly move to Compose. **A Compose paper could be pre-empted within weeks.** Re-search arXiv just before committing.
- **Weak baseline.** Compose has one documented open-source analyser (KICS). Reviewers may call the comparison thin. Possible mitigation: add a hand-written rule set as a second baseline, at extra cost.
- **Ground-truth effort and validity.** Solo labelling is the bottleneck and the main threat to validity. 300 files × 8 types is about 2,400 judgements, roughly 10–15 hours, which is a large share of the 70-hour budget.
- **Contribution size.** "LLMs vs one linter on 300 Compose files" is a modest, workshop-level contribution. CP2's framing (that ground truth matters) carries more weight but is partly anticipated by TerraProbe for repair and by GenKubeSec's own false-positive audit.
- **Dependencies.** CP3 depends on whether Zhang & Omoronyia's ZIP really contains the labelled data, which was not verified. API pricing and model availability could change.

## 7. Scores (1–5)

| | Gap strength | Novelty | Feasibility | Data availability | Cost | Speed to results |
|---|---|---|---|---|---|---|
| **CP1 + CP2 (Compose, manual labels, ground-truth distortion)** | 3: Compose is clearly untested, but the gap is narrow and has one baseline | 3: a new setting with an established method | 4: small files, cheap inference, tools run locally | 2: no labelled Compose corpus, so labels must be built by hand | 5: a few dollars of API spend plus free tools | 3: labelling takes 4–5 days of the 7–10 |
| **CP2 alone (Kubernetes/Dockerfile)** | 3: the circular labels are documented in rows 1–2 | 2: GenKubeSec's FP audit and TerraProbe already point at it | 4: public tool-labelled datasets exist; only disagreements need labelling | 4: GenKubeSec and Ghorab packages are public | 5 | 4 |
| **CP3 (general-purpose LLMs on Dockerfile labels)** | 2: row 6 covers most of it | 2 | 3: depends on the artefact | 2: unverified | 5 | 4 if the artefact works, 2 if not |

## Takeaways (our interpretation)

- This area is **crowded**. Kubernetes and Terraform detection or repair should not be the chosen problem.
- The most defensible angle combines a genuinely untested artefact type (docker-compose) with a methodological point the field keeps getting wrong: scoring against static-analyser output. The ground-truth point is the more publishable half. The Compose setting is what keeps it from being a replication.
- The gap is **moderate at best**. Compared with other gap scans, this candidate wins on cost and feasibility, not on gap strength. If another area offers a clearer flawed-evaluation gap, prefer it.

## Unverified leads

- "Repairing Docker Smells with Large Language Models: An Empirical Study", proposing a Detect–Guide–Repair framework, MDPI *Applied Sciences* 16(13):6805 (2026?). Seen only in search snippets; the page returned 403.
- "A Comparative Study of Rule-Based and LLM-Based IaC Security Misconfiguration Detection in DevOps", University of Turku repository (utupub.fi). Probably a master's thesis on Terraform; a snippet claims Claude Sonnet 4.6 had 82 true positives against tfsec's 79. The page returned 403. **Signal only**, not peer-reviewed.
- TerraDS repository count: the MSR 2025 programme page (via search snippet) says 67,360 repositories; the Zenodo record says 62,406. Use the Zenodo figure.
- The abs page for arXiv:2609.20834 showed a July 2026 submission date, which does not match the 2609 ID. Re-check the date before citing.
- Rahman et al.'s Kubernetes paper is said in snippets to be a TOSEM paper with an oracle dataset. Neither the venue details nor the oracle's availability were confirmed.
- Lin et al.'s Dockerfile corpus (380k files, used in row 6) was not opened.

## Sources

- arXiv:2405.19954 GenKubeSec. https://arxiv.org/abs/2405.19954
- arXiv:2609.20834 Ghorab & Saied, IEEE CLOUD 2025. https://arxiv.org/abs/2609.20834
- arXiv:2609.27030 Ghorab, Abdel Latif & Saied, AIware 2026. https://arxiv.org/abs/2609.27030
- arXiv:2502.02009 LLMSecConfig, MSR 2025. https://arxiv.org/abs/2502.02009
- arXiv:2403.09537 Minna, Massacci & Tuma, MSR 2024 RR. https://arxiv.org/abs/2403.09537
- DOI 10.1007/s10515-026-00684-z Zhang & Omoronyia, Automated Software Engineering 2026. https://link.springer.com/article/10.1007/s10515-026-00684-z
- arXiv:2601.14595 IntelliSA, MSR 2026. https://arxiv.org/abs/2601.14595
- arXiv:2509.18790 War et al. https://arxiv.org/abs/2509.18790
- arXiv:2606.26590 TerraProbe. https://arxiv.org/abs/2606.26590
- arXiv:2609.28488 IaC-Guard-V, QRS 2026. https://arxiv.org/abs/2609.28488
- arXiv:2509.04191 KubeGuard. https://arxiv.org/abs/2509.04191
- arXiv:2607.25995 KuTIE, LLMSec@ESORICS 2026. https://arxiv.org/abs/2607.25995
- arXiv:2608.02672 Text-to-Terraform security, SBSeg 2026. https://arxiv.org/abs/2608.02672
- arXiv:2501.14131 Dockerfile refactoring, MSR 2025. https://arxiv.org/abs/2501.14131
- arXiv:2608.25793 Secure Dockerfile reference standards, ASE 2026 Industry. https://arxiv.org/abs/2608.25793
- arXiv:2608.02669 Docker Hub high-exposure images. https://arxiv.org/abs/2608.02669
- arXiv:2607.12723 Bulkhead (opened; judged out of scope as it targets container-escape code, not configs). https://arxiv.org/abs/2607.12723
- arXiv:2205.14371 GLITCH, ASE 2022. https://arxiv.org/abs/2205.14371
- arXiv:2302.01707 Parfum. https://arxiv.org/abs/2302.01707
- arXiv:2208.09097 Rosa et al., ICSME 2022 RR. https://arxiv.org/abs/2208.09097
- arXiv:2305.11293 Eng et al., Docker Compose patterns. https://arxiv.org/abs/2305.11293
- DOI 10.1007/s10664-021-10025-1 Ibrahim, Sayagh & Hassan, EMSE 2021. https://www.springerprofessional.de/en/a-study-of-how-docker-compose-is-used-to-compose-multi-component/19693126
- Rahman et al., Security Misconfigurations in Open Source Kubernetes Manifests, ACM 2023. http://hdl.handle.net/10919/113801 (via https://vtechworks.lib.vt.edu/items/6c35b89e-ab00-4053-b847-17fe67f95208)
- Binnacle ICSE 2020 artefact. https://github.com/jjhenkel/binnacle-icse2020
- TerraDS, Zenodo 14217386. https://zenodo.org/records/14217386
- Hadolint. https://github.com/hadolint/hadolint
- Checkov Dockerfile policy index. https://www.checkov.io/5.Policy%20Index/dockerfile.html ; repo https://github.com/bridgecrewio/checkov
- Trivy misconfiguration docs. https://trivy.dev/latest/docs/scanner/misconfiguration/ ; repo https://github.com/aquasecurity/trivy
- KICS platforms. https://docs.kics.io/latest/platforms/ ; repo https://github.com/Checkmarx/kics
