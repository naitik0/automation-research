# Gap scan: LLM detection of Docker and infrastructure-as-code misconfigurations

Type: research
Status: resolved
Blocked by: none
Map: [Topic search](../map.md)
Findings: [notes/iac-misconfiguration-gap-scan.md](../../../notes/iac-misconfiguration-gap-scan.md) (also on branch `research/iac-misconfiguration`)

## Question

Where is the strongest research gap in using LLMs to detect (or fix) security misconfigurations in Dockerfiles, docker-compose, Kubernetes manifests or Terraform, compared with static analysers such as Hadolint, Checkov, Trivy or KICS? Answer using the gap-scan rubric in the map's Notes. Identify labelled public datasets of misconfigured files and whether existing studies use a sound ground truth.

## Answer

**Verdict: wins on cost and feasibility, but the gap is narrow and could be taken by someone else soon.** Kubernetes detection and repair, Terraform repair, and Ansible/Puppet smell detection have about 10 papers from 2024–2026, several from the last month. A fine-tuned Dockerfile detector trained on 4,000 hand-labelled files was published in September 2026 (DOI 10.1007/s10515-026-00684-z).

Candidate problems (scores: gap / novelty / feasibility / data / cost / speed):
1. **Docker Compose detection plus a ground-truth check (best):** How well do off-the-shelf LLMs and KICS detect security misconfigurations in docker-compose files, scored against hand labels? And how much do the results change if KICS output is used as ground truth instead? No LLM study of Compose files was found, and KICS is the only one of the four analysers that documents Compose support. **3/3/4/2/5/3.**
2. **Ground-truth check alone:** How much do labels taken from analyser output distort LLM-versus-tool comparisons? Two Kubernetes studies (arXiv:2405.19954, arXiv:2609.20834) score LLMs against labels made from tool output, which is circular. This is a flawed-evaluation gap. **3/2/4/4/5/4.**
3. Prompted general-purpose LLMs on the September 2026 Dockerfile paper's hand-labelled data. **2/2/3/2/5/4**, or speed 2 if the data turns out to be unusable.

Main costs and risks:
- No labelled Compose dataset exists, so we'd label one ourselves: about 300 files × 8 risk types, roughly 10–15 hours of the 70-hour budget. With a single annotator, labelling is the main threat to validity.
- KICS is the only baseline for Compose.
- Two active Kubernetes research groups could move to Compose within weeks.
