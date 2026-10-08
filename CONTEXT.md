# Automation Research

Glossary for an academic research project on AI agents and AI-powered automation, with cybersecurity as the preferred application area.

## Language

### Choosing a topic

**Candidate problem**:
A research problem still under consideration that has not yet been chosen or rejected.
_Avoid_: Idea, topic option

**Gap evidence**:
Cited proof that a candidate problem is not yet answered: what prior work has done and what it clearly leaves open.
_Avoid_: Novelty claim, gap (when used without citations)

**Chosen problem**:
The single candidate problem the project commits to, as stated in the problem brief.
_Avoid_: Final topic, selected idea

**Fallback problem**:
The one candidate problem named in advance to become the chosen problem if a kill criterion fires, without reopening the whole comparison.
_Avoid_: Backup topic, plan B

**Kill criterion**:
A condition, agreed before the feasibility pilot, which if met drops the chosen problem in favour of the fallback problem.
_Avoid_: Abort condition, red flag

**Label-revealing metadata**:
Alert fields that may reveal the triage label without any reasoning about the alert's content, such as the name of the rule that fired. It is a potential source of shortcut information until experiments establish how much it actually reveals.
_Avoid_: Leakage, label leak (before it has been measured)

**Information condition**:
One setting of which alert fields an LLM is shown when it triages an alert, for example the full benchmark prompt, or the prompt with label-revealing metadata removed.
_Avoid_: Ablation (when used without saying which fields), prompt variant

**Problem brief**:
A 1–2 page document stating the chosen problem: its research question, why it matters, gap evidence, a feasibility check, a rough approach, 1–2 rejected candidate problems with reasons, and the fallback problem with its kill criteria.
_Avoid_: Proposal, topic summary
