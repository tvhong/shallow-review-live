# High-Value Data Sources

Key pages from 80,000 Hours, AISafety.com, and ShallowReview.ai that we can feed to a model for AI safety field navigation.

---

## 80,000 Hours (80000hours.org)

**Search URL pattern:** `https://80000hours.org/?s={query}` (WordPress standard)

### Career Reviews (structured profiles with skills, paths, pros/cons)

- https://80000hours.org/career-reviews/ai-safety-researcher/ — Technical AI safety research, skill requirements, empirical vs theoretical paths
- https://80000hours.org/career-reviews/ai-policy-and-strategy/ — AI governance and policy, 6 career pathway categories
- https://80000hours.org/career-reviews/working-at-an-ai-lab/ — Working at frontier AI labs
- https://80000hours.org/career-reviews/china-related-ai-safety-and-governance-paths/ — China-focused AI safety careers
- https://80000hours.org/career-reviews/information-security/ — InfoSec careers relevant to AI safety
- https://80000hours.org/career-reviews/alignment-data-expert/ — Alignment data specialist roles
- https://80000hours.org/career-reviews/machine-learning-phd/ — ML PhD as a career path
- https://80000hours.org/career-reviews/become-an-expert-in-ai-hardware/ — AI hardware expertise
- https://80000hours.org/career-reviews/formal-verification-expert/ — Formal verification for AI safety
- https://80000hours.org/career-reviews/software-engineering/ — Software engineering (feeder path)

### Guides & Transition Resources

- https://80000hours.org/articles/ai-policy-guide/ — Comprehensive AI policy career guide, researcher vs practitioner tracks
- https://80000hours.org/articles/ml-engineering-career-transition-guide/ — SWE-to-ML-engineer transition, phased timeline (200+ hours)
- https://80000hours.org/articles/us-ai-policy/ — US government AI policy roles
- https://80000hours.org/articles/ai-safety-syllabus/ — Curated reading list for technical AI safety (partially dated, 2016 with 2024 update)
- https://80000hours.org/2025/06/technical-ai-safety-upskilling-resources/ — 67 curated upskilling resources: courses, fellowships (MATS, ARENA, Anthropic), research orgs, newsletters

### AI-Specific Guide Pages

- https://80000hours.org/ai/ — Main AI landing page: career paths, job board (700+ positions), resource hub. **Best single entry point.**
- https://80000hours.org/ai/guide/skills-ai-makes-valuable/ — Skills increasing in value as AI advances

### Problem Profiles (theory of change / why this matters)

- https://80000hours.org/problem-profiles/artificial-intelligence/ — Master AI problem profile, 5-part risk framework
- https://80000hours.org/problem-profiles/risks-from-power-seeking-ai/ — Power-seeking AI risk analysis
- https://80000hours.org/problem-profiles/extreme-power-concentration/ — Extreme power concentration from AI
- https://80000hours.org/problem-profiles/catastrophic-ai-misuse/ — Catastrophic AI misuse scenarios
- https://80000hours.org/problem-profiles/gradual-disempowerment/ — Gradual human disempowerment by AI

### Skill Development Pages

- https://80000hours.org/skills/software-tech/
- https://80000hours.org/skills/research/
- https://80000hours.org/skills/political-bureaucratic/
- https://80000hours.org/skills/communication/
- https://80000hours.org/skills/organisation-building/
- https://80000hours.org/skills/specialist-knowledge/
- https://80000hours.org/skills/engineering/
- https://80000hours.org/skills/emerging-power/

### Sitemaps (for deeper scraping)

- `80000hours.org/sitemap_index.xml` — index with sub-sitemaps:
  - `career_profile-sitemap.xml` — 65 career reviews
  - `article-sitemap.xml` — 120+ articles
  - `problem_profile-sitemap.xml` — 37 problem profiles
  - `skill_set-sitemap.xml` — 8 skill guides
  - `ai_career_guide_page-sitemap.xml` — 3 AI-specific guide pages

---

## AISafety.com

**No linkable search URL** — uses client-side JavaScript filtering (Finsweet/Airtable). All filtering is in-browser.

### Key Pages

- https://www.aisafety.com/map — Interactive field map, hundreds of orgs in 16 categories (Advocacy, Research, Funding, Governance, Career Support, Training, Forecasting). **Highest density of structured org data.**
- https://aisafety.com/courses — Curated self-study directory linking to:
  - alignmentforum.org/library (Curated Sequences)
  - bluedot.org (Technical & Governance courses)
  - aisafetybook.com/curriculum (AISES Curriculum)
  - ai-safety-atlas.com/read (AI Safety Atlas)
  - course.mlsafety.org/about (Intro to ML Safety)
  - arena.education/curriculum (ARENA)
  - cooperativeai.com/curriculum (Cooperative AI)
- https://www.aisafety.com/events-and-training — Dynamic database of upcoming programs
- https://www.aisafety.com/advisors — Directory of free career mentors/advisors (80K Hours, Successif, Probably Good, etc.)
- https://www.aisafety.com/jobs — Job board filterable by skill set, experience level, role type
- https://www.aisafety.com/communities — Directory of online/in-person AI safety communities worldwide
- https://www.aisafety.com/funding — Directory of funders (grants, fellowships, incubators, VC)
- https://www.aisafety.com/projects — Volunteer project directory
- https://www.aisafety.com/media-channels — Podcasts, newsletters, blogs

### Architecture Note

All directory pages are Airtable-backed databases on Webflow. Data may be accessible via Airtable if we can find the base ID.

---

## ShallowReview.ai

**No search function.** Static Next.js site on GitHub Pages. Navigation is structure-based.

**Canonical domain:** `https://shallowreview.ai` (no www)

### What It Is

Third annual shallow review of technical AI safety, covering **800+ papers across 80+ research agendas**. Created by Arb Research (Gavin Leech et al.), website by QURI/Quantified Uncertainty.

### Top-Level Pages

- https://shallowreview.ai/overview — Full taxonomy of all 80+ agendas in 8 sections. **Best entry point.**
- https://shallowreview.ai/table — Spreadsheet view: Name, Section, Summary, Paper count, FTEs, Target Case, Approaches, Problems, Funders, Researchers. **Richest structured data.**
- https://shallowreview.ai/similarity — Interactive network graph of 1,465 connections between agendas
- https://shallowreview.ai/methodology — Data sources, processing pipeline, scope
- https://shallowreview.ai/about — Authors, links to GitHub repo and Google Sheets

### Classification Framework

- https://shallowreview.ai/orthodox-problems — 13 core AI safety challenges mapped to agendas
- https://shallowreview.ai/target-cases — 3 target cases: Average (25 agendas), Pessimistic (19), Worst Case (18)
- https://shallowreview.ai/broad-approaches — 3 approaches: Engineering (17), Behavioral (15), Cognitive (25)

### Section Pages (8 sections, ~80 agenda subpages)

| Section | URL | Agendas |
|---------|-----|---------|
| Labs | /Labs | 6 (OpenAI, DeepMind, Anthropic, xAI, Meta, China) |
| Black Box Safety | /Black_box_safety | 25 (control, steering, model psychology, data quality, goal robustness) |
| White Box Safety | /White_box_safety | 14 (interpretability, sparse coding, causal abstractions, activation engineering) |
| Safety by Construction | /Safety_by_construction | 3 (Guaranteed Safe AI, Scientist AI, Brainlike AGI Safety) |
| Make AI Solve It | /Make_AI_solve_it | 5 (weak-to-strong, debate, AI explanations) |
| Theory | /Theory | 9 (agent foundations, natural abstractions, corrigibility) |
| Multi-Agent First | /Multi_agent_first | 6 (social contract alignment, multi-AI theory) |
| Evals | /Evals | 12 eval types (capability, deception, scheming, WMD, autonomy) |

### Agenda Page URL Pattern

`https://shallowreview.ai/{Section}/{Agenda_Name}` (underscores for spaces)

Each page has: summary, classification, FTE estimates, key researchers, paper list, critiques.

### External Data Sources

- GitHub: https://github.com/arb-consulting/shallow-review-2025
- Google Sheets (linked from /about)
- LessWrong full text: https://www.lesswrong.com/posts/Wti4Wr7Cf5ma3FGWa/shallow-review-of-technical-ai-safety-2025-2
