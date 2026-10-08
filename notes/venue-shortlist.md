# Which conferences or workshops fit a solo SOC alert-triage evaluation paper?

Written: 2026-10-08. Every date, limit and rule below was read on the venue's own page on **2026-10-08** unless it is marked **(estimate)** or **(not verified)**. Numbers in square brackets point to `## Sources`. Our own judgement is kept under `## Takeaways` and labelled **(our interpretation)**.

Ticket: [Venue shortlist](../.scratch/topic-search/issues/10-venue-shortlist.md)

The paper being placed (from [28]): an empirical evaluation of LLM security-alert triage against cheap baselines (rule-majority, ML) on public data. A1 is the rule-shortcut audit on SecAlertBench and must be able to stand alone. A2 compares zero-shot LLMs with risk-based alerting (RBA) on the CATS datasets. Authors: one student, no advisor. Window: submission deadline from about 2026-11-08 to early 2027.

Three things to know before the table:

- **Only AsiaCCS 2027, CODASPY 2027 and AI-SEC 2027 have a 2027 call for papers (CFP) that I could open with a deadline in the window.** WOSOC at NDSS 2027, DIMVA 2027 and ESORICS 2027 have no CFP yet, so their dates below are estimates from the previous edition.
- AI-SEC 2027 is a workshop of **AINA-2027** (a Springer conference in Tirana), not of AAAI. An earlier hand-off said AAAI; the official page says otherwise [15].
- No source I opened says a workshop paper is archival or not except where stated per venue below. Archival status matters because most of these venues forbid submitting the same work elsewhere at the same time.

---

## 1. Shortlist at a glance

| # | Venue | Deadline | Pages / format | Review | Archival? | Registration / fees |
|---|---|---|---|---|---|---|
| 1 | **WOSOC 2027** (NDSS workshop on SOC operations) | **No 2027 CFP yet.** Estimate: late Dec 2026 (2026 edition: 29 Dec 2025 after an extension) [7] | Short paper, 4 to 8 pages excluding references, NDSS template [7] | Not stated [7][8] | Yes: published in proceedings [7] | Not stated [7] |
| 2 | **ACM CODASPY 2027** (Fort Collins, 14-17 Jun 2027) | **Abstract 16 Nov, paper 23 Nov 2026**; notification 25 Jan 2027 [4][5] | Research paper: 12 pages ACM sigconf plus up to 2 appendix pages. Dataset/Tool paper: 6 pages plus 2 [4] | Anonymized (double-blind) [4] | Yes: ACM proceedings, open access [4] | No registration rule in the CFP. ACM open-access fee applies to some authors [4] |
| 3 | **ACM AsiaCCS 2027** (Macau, 12-16 Jul 2027), cycle 2 | **11 Dec 2026** (AoE); early rejection 5 Feb 2027; notification 31 Mar 2027 [1] | 12 pages of content in ACM sigconf, plus up to 10 for references and appendices [1] | Double-blind [1] | Yes: ACM proceedings, open access [1] | At least one author must register at the full conference rate [1]. ACM fee for some authors [1] |
| 4 | **AI-SEC 2027** (workshop at AINA-2027, Tirana, 24-26 Mar 2027) | **10 Dec 2026**; notification 10 Jan 2027; final version 25 Jan 2027 [14][15] | Max 10 pages including references, Springer Lecture Notes style [14] | Peer reviewed; blind or not is not stated [15] | Yes: Springer series, indexed in Scopus [14] | At least one author must register and present [14]. Amount for 2027 not found; AINA-2024 charged EUR 400 per paper [16] |
| 5 | **DIMVA 2027** (cycle 2 as the fallback) | **No 2027 CFP yet.** Estimate: cycle 1 around 10 Dec 2026, cycle 2 mid Feb 2027 (2026: 10 Dec 2025 and 18 Feb 2026) [17][18] | 25 pages in Springer LNCS: 18 content, 5 references, 2 appendix [17] | Double-blind [17] | Yes: Springer LNCS [17] | Every accepted paper needs a general (non-student) registration and in-person presentation [17] |

---

## 2. Venue by venue

### 2.1 WOSOC at NDSS 2027 (best topic fit, but no 2027 CFP yet)

What the sources say:

- The 2026 edition was co-located with NDSS 2026 in San Diego and called itself "the premier forum for academic researchers and security operators" on SOC work [9]. Its topics included alert management, incident response, automation and AI integration [7]. The 2025 topic list named "Large Language Models in SOCs" and "datasets" [8].
- 2026 dates: papers due 22 Dec 2025, extended to 29 Dec 2025 (AoE); notification 9 Jan 2026; camera-ready 30 Jan 2026 [7]. 2025: due 15 Dec 2024, extended to 22 Dec 2024; notification 15 Jan 2025 [8].
- Researchers submit short papers "between 4-8 pages excluding references" in the NDSS template (US letter, two columns, Times 10 pt) [7]. Papers may be "emerging research, work-in-progress, and position papers" [7].
- "Academic papers and operational talk abstracts will be published in proceedings" [7]. In 2025 the proceedings were published through the Internet Society [8].
- The CFPs do not state a review model, a registration obligation or fees [7][8]. I could not find either on the NDSS registration pages (both were empty of fees) [30][31].
- The 2026 accepted list had several LLM-in-the-SOC papers, none clearly about alert-triage evaluation [13].
- **2027 status:** the NDSS 2027 symposium (22 to 26 March 2027, Seoul) has an open call for co-located workshop proposals; proposals were due 1 Sep 2026 and acceptance was notified 8 Sep 2026 [10]. The NDSS 2027 submissions and co-located-events pages list no workshop and no WOSOC 2027 CFP [11][12]. The WOSOC 2027 pages I tried were the 2023 and 2024 archives [32][33].

Estimate (not verified): by analogy to 2025 and 2026, a WOSOC 2027 deadline would fall in mid to late December 2026, with a 4 to 8 page limit. This depends on WOSOC being accepted again, which I could not confirm.

### 2.2 ACM CODASPY 2027 (open CFP, earliest deadline)

- All deadlines are Anywhere on Earth. SoK abstract 2 Nov (firm); abstract 16 Nov; research, dataset/tool, BlueSky and SoK papers 23 Nov 2026; rebuttal 18 to 22 Jan 2027; notification 25 Jan 2027; camera-ready 26 Mar 2027 [4][5]. The conference runs 14 to 17 June 2027 [5].
- Research papers: at most 12 pages in double-column ACM sigconf plus up to 2 appendix pages. Dataset/Tool papers: at most 6 pages plus 2, with a "Data/Toolset paper" subtitle [4]. BlueSky and SoK papers are invitation-only [4].
- Research, dataset/tool and SoK papers "must be anonymized and avoid obvious self-references" [4].
- Topics include "Security of AI systems" and "Trustworthy artificial intelligence / machine learning" among many application areas [4]. The home page describes the scope as research at "the data and application layers" [6]. The CFP lists no SOC or alert-triage topic.
- Ethics and Open Science statements are "highly encouraged" [4].
- Concurrent submission: papers "must not substantially overlap with papers that have been published or that are simultaneously submitted to a journal, conference or workshop" [4].
- ACM is fully open access since 1 Jan 2026. For 2027 the CFP quotes subsidized article processing charges of $500 (members) or $750 (non-members) for authors whose institutions are not covered [4]. The CFP states no registration obligation and no fees [4]; the conference is in person with paid registration, pricing pending [5].

### 2.3 ACM AsiaCCS 2027, cycle 2 (open CFP, larger venue)

- Cycle 2: submission 11 Dec 2026 (AoE); early rejection 5 Feb 2027; rebuttal 8 to 12 Mar 2027; notification 31 Mar 2027; camera-ready 7 May 2027 [1].
- Limit: 12 pages of content in ACM sigconf, plus up to 10 additional pages for bibliography and appendices; reviewers need not read appendices [1].
- Double-blind. Preprints on arXiv are allowed, but authors must "refrain from broadly advertising their results" [1].
- Scope warning: "Purely theoretical...submissions are not encouraged. The same applies for submissions focusing primarily on blockchains or machine learning." A separate AI Security track covers "the security and privacy of AI/ML systems" [1]. An LLM-for-SOC evaluation is neither of those tracks' core, so fit is uncertain.
- Required appendices: "Open Science" (max half a page, anonymous link to code and data) and, if ethical concerns arise, "Ethical Considerations" (max half a page) [1].
- "At least one paper author must register for each accepted paper at the appropriate full conference rate." Same ACM open-access charges as above [1]. The 2027 registration page says "To be announced" [2].
- No AsiaCCS 2027 workshops are announced yet ("To be announced later") [3].

### 2.4 AI-SEC 2027 at AINA-2027 (open CFP, lower-tier but archival)

- "The 3rd International Workshop on Artificial Intelligence for Cybersecurity", Polytechnic University of Tirana, hybrid, 24 to 26 March 2027; parent event is the 41st AINA [15].
- Deadlines: submission 10 Dec 2026; notification 10 Jan 2027; final manuscript and registration 25 Jan 2027 [14][15]. Submission is through EDAS [15].
- Maximum 10 pages "including all figures, tables, and references", in the Springer Lecture Notes style [14]. Accepted papers go into a Springer Lecture Notes volume indexed in Scopus [14].
- "Authors of accepted papers, or at least one, are requested to register and present their work at the conference; otherwise, their papers will be removed from the digital library" [14]. The home page says remote presentation is allowed [15].
- Topics listed on the pages I could read: malware and intrusion detection, threat detection and anomalies, web security, IoT and edge security, adversarial robustness [15]. A search-result summary of the call also mentioned "incident response using AI", but I did not find that on a page I opened, so treat it as not verified. SOC alert triage is not named.
- The CFP does not say whether review is blind or what the fee is (not verified). The AINA-2024 registration page charged EUR 400 per paper and required "FULL REGISTRATION" for each paper to appear in the Springer proceedings [16]. The AINA-2025, 2026 and 2027 registration pages returned no fee text when I opened them, so the 2027 amount is an **estimate** from 2024.

### 2.5 DIMVA 2027 (no CFP yet; the topical fit is the best of the Springer venues)

- DIMVA 2026 (Chania, 1 to 3 July 2026): cycle 1 due 10 Dec 2025 (extended), notification 27 Jan 2026; cycle 2 due 18 Feb 2026 (extended), notification 3 Apr 2026; camera-ready 28 May 2026 [17]. (A mirror on the IEEE calendar gives 11 Feb for cycle 2; I used the official page.)
- 25 pages total in Springer LNCS: "a maximum of 18 pages for the main paper content, 5 pages for the bibliography, and 2 pages for appendices" [17].
- Double-blind; poorly anonymized papers "risk being rejected without review" [17].
- "To be included in the proceedings, every accepted paper requires a general registration and in-person presentation" [17]. Registration fees are not in the CFP [17].
- The DIMVA home page shows only the 2026 edition and says nothing about 2027 [18]. **Estimate (not verified):** a 2027 cycle 1 deadline around early to mid December 2026 and cycle 2 around mid February 2027.
- The 2026 CFP as shown on the IEEE-hosted mirror lists intrusion detection among its topics and expects "enough details to enable reproducibility of the experimental results" [17]. I read this on the mirror, not on the official page.

---

## 3. Considered and left out

| Venue | Why it is out | Source |
|---|---|---|
| ESORICS 2027 | No 2027 CFP yet. ESORICS 2026 had a winter cycle (9 Jan 2026) and a spring cycle (21 Apr 2026), so a January 2027 deadline is likely **(estimate)**. 16 pages plus up to 4 for references and appendices, Springer LNCS. The 2026 EasyChair call says "Submissions are not required to be anonymous". Lists "Artificial Intelligence for Security" as a topic. It would be a stretch-goal backup for DIMVA if the project goes well. | [19][20] |
| AAAI-27 workshops | Workshop submissions are due 20 Nov 2026, notification 2 Dec 2026, workshops 22 to 23 Feb 2027 in Montreal. The accepted-workshop list and CFPs are only posted on 16 Oct 2026, so I cannot say yet whether any suits a SOC paper. AAAI "does not archive workshop papers", leaves publishing to organizers, and requires one co-author to present in person. The only AAAI-27 security workshop I found, "LLM Agents Under Threat in Cyberspace", is a proposal about attacks on LLM agents, which does not match. Check again after 16 Oct. | [21] |
| STALA 2027 (NDSS workshop) | Deadline 11 Dec 2026, 8 pages (4 for short papers), NDSS proceedings. But its topics are security testing of LLMs and agents (fuzzing, red teaming, jailbreaks), not LLMs applied to SOC data. Its own site says it is co-located with NDSS 2027; the NDSS co-located-events page did not list it. | [22][12] |
| LAST-X (NDSS workshop) | 2026 edition only: 10 pages, IEEE double-column, double-blind. Topics are LLM-assisted fuzzing, code analysis and hardware security, not SOC. No 2027 CFP found. | [23] |
| ITASEC27 (Siena, 8 to 12 Feb 2027) | Paper deadline is **16 Oct 2026**, before the window (16 pages, CEUR template, single-blind, CEUR-WS proceedings). It also has a "preliminary work" track that is not in proceedings. | [24] |
| ICCWS 2027 (Cape Town, March 2027) | Full paper was due 15 Oct 2026, before the window; fees and review model are not on the CFP. | [25] |
| EICC 2027 (Paris, 2 to 3 Jun 2027) | The CFP page gives no submission deadline yet (12 to 16+ pages, Springer LNCS, double-blind, one author must register). Re-check in November. | [29] |
| RAID 2027, ARES 2027, USENIX Security '27, ICISSP 2027 | Not verified on official CFPs. RAID's 2026 deadline was in April and ARES's was in March, both outside the window; USENIX Security '27 and ICISSP only showed up in search results I did not open. | (not verified) |

---

## 4. arXiv as the fallback

- arXiv requires endorsement before a first submission to a category. An institutional email address speeds this up; without one, an established researcher must endorse you. Endorsement is "not peer review" [26].
- arXiv's 2025 policy for cs papers asks prior peer review for **review articles and position papers**; it does not restrict standard research papers [27]. An empirical evaluation falls outside that rule [27]. A "position paper" framing for the WOSOC short paper would not.
- AsiaCCS explicitly allows preprints under double-blind review, with the caveat on advertising [1]. CODASPY says only that submissions must be anonymized and not simultaneously submitted elsewhere [4].

---

## Takeaways

These are **our interpretation**, not claims from the sources.

1. **Best fit by topic: WOSOC.** It is the only listed venue whose scope names alert management and LLMs in SOCs [7][8]. Its limits are a risk: no 2027 call exists, its deadline is an estimate, and I could not confirm it will run again. Watch the NDSS 2027 co-located-events page through November.
2. **Best fit by firm dates: CODASPY (23 Nov) and AsiaCCS (11 Dec).** Both have open CFPs, are ACM proceedings, and allow 12 content pages. CODASPY comes only about 6.5 weeks after today and the feasibility pilot (ticket 08) and prior-work check (ticket 09) are still open, so 23 Nov is realistic only if both pass quickly. AsiaCCS gives 4 more weeks. AsiaCCS's statement that ML-focused submissions "are not encouraged" is a real fit risk for an LLM-evaluation paper [1]; CODASPY's topic list is broader but also does not name SOC work [4].
3. **AI-SEC and DIMVA are the lower-risk archival backups.** AI-SEC is a low-selectivity Springer workshop with a known date (10 Dec) and a modest cost, but a registration fee is probably due (estimated EUR 400, from AINA-2024 [16]) and the topic list does not name SOC. DIMVA's topic fit (intrusion detection) is good, but its 25-page limit and double-blind rules are demanding for a solo student and the 2027 dates are guesses.
4. **Registration is a real cost for a solo author.** AsiaCCS (Macau) and DIMVA need in-person presentation at the full rate [1][17]; AINA/AI-SEC needs one author to register and present, remotely if hybrid [14][15]. CODASPY and WOSOC CFPs state no obligation [4][7], but I would assume an author must attend. The ACM open-access charge ($500 or $750) applies if the author's institution is not an ACM Open participant [1][4]. I did not check whether an MCA student's institution is covered. Budget before committing.
5. **Page limits should shape the brief's scope.**
   - **Plan the paper as an 8 to 10 page paper with A1 as the spine.** That fits AI-SEC (10 pages including references) and trims to WOSOC's 4 to 8 (A1 only) [14][7]. It also expands comfortably to the 12 content pages of CODASPY and AsiaCCS [4][1].
   - **If A2 is cut to two CATS datasets,** the paper still fits the 10-page target. Do not plan around DIMVA's 18 content pages; that only helps if the project grows.
   - **The brief should say "A1 is the paper; A2 is the extension."** WOSOC's short-paper form is the only venue where A1 alone is the natural scope [7].
6. **Do not submit the same paper to two archival venues at once.** CODASPY forbids simultaneous submission to any "journal, conference or workshop" [4]. I did not check AsiaCCS's, AI-SEC's or WOSOC's rule. Choose one primary venue. CODASPY notifies on 25 Jan 2027 [4] and AsiaCCS on 31 Mar 2027 [1]. Only CODASPY's result arrives before a mid-February DIMVA cycle 2 deadline (an estimate), so CODASPY then DIMVA is the one sequence that works on the dates we have. AI-SEC (10 Dec) and WOSOC (estimated late Dec) close before either result, so they are alternatives to CODASPY and AsiaCCS, not fallbacks after them.
7. **Post to arXiv after review decisions are in** unless the target allows preprints. AsiaCCS allows them with a limit on promotion [1]; CODASPY requires anonymization, so check its policy on preprints before posting [4].
8. **Not verified, and worth re-checking** before the brief is final: the WOSOC 2027 CFP (mid November onward), the DIMVA 2027 and ESORICS 2027 CFPs, the AAAI-27 workshop list after 16 Oct, the AI-SEC 2027 review model and fee, and each venue's rule on preprints and dual submission.

---

## Sources

Fetched on 2026-10-08.

1. ACM AsiaCCS 2027, Call for Papers. https://asiaccs2027.cityu.edu.mo/call-for-papers/
2. ACM AsiaCCS 2027, home page (registration "To be announced"). https://asiaccs2027.cityu.edu.mo/
3. ACM AsiaCCS 2027, Workshops page ("To be announced later"). https://asiaccs2027.cityu.edu.mo/workshops/
4. ACM CODASPY 2027, Call for Papers. https://www.codaspy.org/2027/cfp.html
5. ACM CODASPY 2027, Important Dates. https://www.codaspy.org/2027/important-dates.html
6. ACM CODASPY 2027, home page. https://www.codaspy.org/2027/
7. NDSS Symposium 2026, Call for Papers: Workshop on SOC Operations and Construction (WOSOC) 2026. https://www.ndss-symposium.org/ndss2026/submissions/cfp-wosoc/
8. NDSS Symposium 2025, Call for Papers: WOSOC 2025. https://www.ndss-symposium.org/ndss2025/submissions/cfp-wosoc/
9. NDSS Symposium 2026, WOSOC 2026 workshop page. https://www.ndss-symposium.org/ndss2026/co-located-events/wosoc/
10. NDSS Symposium 2027, Call for Co-located Workshops. https://www.ndss-symposium.org/ndss2027/submissions/call-for-co-located-workshops/
11. NDSS Symposium 2027, Calls for Submissions. https://www.ndss-symposium.org/ndss2027/submissions/
12. NDSS Symposium 2027, Co-located Events (no 2027 workshops listed). https://www.ndss-symposium.org/ndss2027/co-located-events/
13. NDSS Symposium 2026, WOSOC 2026 Accepted Papers. https://www.ndss-symposium.org/ndss2026/co-located-events/wosoc/accepted-papers/
14. AI-SEC 2027, Submission Instructions. https://sites.google.com/community.unipa.it/ai-sec-2027/submission-instructions
15. AI-SEC 2027, workshop home page. https://sites.google.com/community.unipa.it/ai-sec-2027/home
16. AINA-2024, Registration (fees and per-paper registration rule, used as an estimate for 2027). https://voyager.ce.fit.ac.jp/conf/aina/2024/registration.php
17. DIMVA 2026, Call for Papers. https://www.dimva.org/dimva2026/ (the IEEE calendar mirror, https://www.ieee-security.org/Calendar/cfps/cfp-DIMVA2026.html, agrees except for the cycle 2 date)
18. DIMVA home page (no 2027 edition listed). https://www.dimva.org/
19. ESORICS 2026, EasyChair call for papers. https://easychair.org/cfp/ESORICS-2026
20. ESORICS 2026, Call for Papers (Winter Cycle), IEEE TC on Security and Privacy calendar. https://www.ieee-security.org/Calendar/cfps/cfp-ESORICS2026.html
21. AAAI-27, Workshops call and timeline. https://aaai.org/conference/aaai/aaai-27/workshops-call/
22. STALA 2027, Security Testing and Assurance for LLMs and Agents. https://stala-workshop.github.io/
23. NDSS Symposium 2026, Call for Papers: LAST-X 2026. https://www.ndss-symposium.org/ndss2026/submissions/cfp-last-x/
24. ITASEC27, Call for Papers. https://itasec.it/call-for-papers/ (EasyChair page: https://easychair.org/cfp/ITASEC27)
25. ICCWS 2027, Call for Papers. https://www.academic-conferences.org/conferences/iccws/iccws-call-for-papers/
26. arXiv, Endorsement. https://info.arxiv.org/help/endorsement.html
27. arXiv blog, "Attention authors: updated practice for review articles and position papers in arXiv CS category" (2025-10-31). https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/
28. This repo, [Choose the problem](../.scratch/topic-search/issues/06-choose-the-problem.md) (A1 and A2 definitions and kill criteria).
29. EICC 2027, home and call for papers. https://www.fvv.um.si/eicc2027/
30. NDSS Symposium 2026, Registration page (no fees shown). https://www.ndss-symposium.org/ndss2026/attend/registration/
31. NDSS Symposium 2027, Registration page (no fees shown). https://www.ndss-symposium.org/ndss2027/attend/registration/
32. NDSS Symposium 2027 URL `.../ndss2027/co-located-events/wosoc/` (serves the 2024 WOSOC archive, no 2027 content). https://www.ndss-symposium.org/ndss2027/co-located-events/wosoc/
33. NDSS Symposium 2027 URL `.../ndss2027/submissions/cfp-wosoc/` (serves the 2023 WOSOC archive, no 2027 content). https://www.ndss-symposium.org/ndss2027/submissions/cfp-wosoc/
