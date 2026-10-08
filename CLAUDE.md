## Project

Academic research project, currently exploring the research space to choose a topic. See `README.md` for the phase and layout.

- Research findings go in `notes/<topic-slug>.md`, following `notes/README.md`. Cite every claim; prefer peer-reviewed venues and arXiv.
- The topic search is tracked as a wayfinder map at `.scratch/topic-search/`.
- Don't write the paper or build a system unless asked.

## Agent skills

### Issue tracker

Issues and specs are tracked as local Markdown files under `.scratch/<feature>/` (no remote tracker). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.
