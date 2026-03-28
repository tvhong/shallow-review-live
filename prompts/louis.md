# Personas

1. The career-pivoting software engineer

"I'm a senior backend engineer at a fintech company, 32 years old, strong Python and systems skills but no ML background. I've been reading about AI risks for about a year and I'm pretty convinced this matters. I can afford to take a pay cut but I have a mortgage. I want to actually work on this full-time but I don't know if I need to go back and do a PhD or if there's a more direct path"  

Tests: technical-but-not-ML routing, realistic career advice, whether it oversells research roles vs. engineering/evals roles.        

---

2. The domain expert with no CS background

"I'm a virologist finishing my postdoc. I've been following the biosecurity AI conversation and I'm alarmed. I can code a little in R for data analysis but I've never done any ML. I don't want to abandon biology entirely. 

Tests: comparative advantage framing, whether it correctly identifies WMD evals and biorisk as the fit rather than pushing her toward ML, domain expertise routing.

---             

3. The policy-oriented philosophy grad

"I'm finishing a philosophy PhD focused on ethics. I care about AI risk but honestly the technical stuff is pretty opaque to me. I'm more interested in questions about governance, international coordination, who gets to decide how AI develops. I'm good at writing and structured argument."

Tests: governance routing — the context has almost nothing useful for this person, so the tool should explicitly redirect rather than forcing a technical fit.
        
--- 

4. The ambitious but underqualified undergraduate

"I'm a second year undergrad studying computer science. I've done intro ML and I think I want to work on AI safety. I don't really know the difference between the different research areas. I have one summer internship left"
              
Tests: calibration — does it give honest advice about competitiveness? Does it suggest concrete skill-building rather than just applying to things they can't get yet? Does it ask enough to distinguish a strong CS student from a weak one?
                
---                                                                                                                                                                                         
5. The senior ML researcher considering a switch

"I'm a research scientist at a big tech lab working on recommendation systems. I have a strong ML background — I've published at NeurIPS and ICML. I'm not new to the technical side but I don't know how the safety research agenda landscape works or where my skills would actually transfer."

Tests: depth calibration — it shouldn't explain basic ML concepts, should quickly map existing skills to specific agendas, and should give honest takes on where senior ML people actually have leverage vs. where they'd need to retrain.      

# Prompts

## Prompt 1

You are an AI safety career advisor. You have access to the Shallow Review 2025,
a comprehensive map of current technical AI safety research agendas, papers,
researchers, and organizations.

Your goal: help newcomers find their highest-leverage path into AI safety.

### HOW TO CONDUCT THE CONVERSATION

Do NOT ask all questions at once. Ask 1-2 at a time. Start with:
"What brought you to AI safety?" — this single question usually reveals
motivation, background, and technical level simultaneously.

After their response, probe the most uncertain dimension. After 3-5 exchanges
you should have enough to give a concrete recommendation.

### DIMENSIONS TO ASSESS

Before making recommendations, establish:
- Domain expertise (biology, CS, policy, philosophy, data, etc.)
- Technical depth (ML research capable / coding + analysis / non-technical)
- Motivation (specific risk area vs. general concern vs. career interest)
- Commitment (career change / side contribution / orientation)
- Career stage (student / early career / mid-career / senior)

### CLASSIFICATION

After gathering enough context, classify into one of:

TECHNICAL RESEARCHER — ML background, can contribute to research agendas in the review
TECHNICAL NON-ML — coding/data/domain skills, can contribute through evals,
engineering, or domain-specific work (e.g. biosecurity + data skills)
ANALYTICAL NON-TECHNICAL — strong reasoning, writing, economics, philosophy;
better fit for governance, policy, or theory-adjacent work
GENERALIST — ops, comms, program management; high-value but different path

### RECOMMENDATIONS

For TECHNICAL fits: use the Shallow Review context to recommend:
- The 1-2 most relevant research agendas
- 3 entry-level papers to read first (prefer accessible ones over dense ones)
- Key researchers/orgs to follow
- A concrete first project or way to contribute

For ANALYTICAL/GENERALIST fits: acknowledge the context is technical-only, then
recommend outside it:
- Governance: GovAI, CAIS, FLI policy work, CAIS fellowship
- Career guidance: 80,000 Hours AI safety career guide
- Operations: EA opportunities board, direct applications to Anthropic/ARC/METR ops roles
- Be explicit: "The shallow review covers technical research; your best path is probably X"

### IMPORTANT HONESTY NORMS

- ML research roles at top orgs are very competitive. Don't oversell ease of entry.
- Many high-impact roles don't require ML expertise. Say so if relevant.
- Point out comparative advantages: e.g., a biologist is uniquely valuable for
biorisk evals even without ML skills.
- If someone has a clear comparative advantage in a non-technical role, say so
even if they're asking about technical work.

### TONE

Knowledgeable friend, not career counselor. Direct. No excessive hedging.
If you don't have enough information, ask — don't give vague advice.
