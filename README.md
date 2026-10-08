# Automation Research

An academic research project that will eventually become a research paper.

## Current phase: topic chosen (topic search complete, 2026-10-08)

The topic search is finished, and the problem brief was approved on 2026-10-08. The next phase is detailed experiment design and running the experiments, as a separate effort. We are not writing the paper yet.

Areas of interest:

- AI-powered automation
- AI agents
- Workflow automation
- Cybersecurity automation

## Research question

How robust are reported LLM alert-triage results once simple non-LLM baselines and potentially label-revealing alert metadata are controlled for? See [`docs/problem-brief.md`](docs/problem-brief.md).

## Repository layout

| Path | Purpose |
| --- | --- |
| `.scratch/topic-search/` | The exploration map (`map.md`) and one ticket per question under `issues/`. Records how the topic was narrowed down. |
| `notes/` | One Markdown file per topic or source investigated, with every claim cited. Tickets link to these. |
| `CONTEXT.md` | Glossary of terms as this project uses them. Created when the first term is settled. |
| `docs/problem-brief.md` | The approved problem brief: research question, gap evidence, approach and workload. |
| `pilot/` | Feasibility pilot scripts, pinned download scripts and results (datasets and tools are git-ignored). |
| `docs/adr/` | Lasting decisions about the research approach. Used once a topic is chosen. |
| `docs/agents/` | Configuration for the agent skills. |

## Conventions

- Prefer primary sources: peer-reviewed venues and arXiv. Blog posts and vendor reports are only signals of what's popular.
- Cite with a DOI, arXiv ID, or venue and year. Don't commit PDFs.
- A candidate gap must answer three things: what has already been done, what is clearly missing, and whether we can realistically answer it.
