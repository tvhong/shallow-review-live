---
name: improve-prompt
description: Run the advisor eval, analyze results, and improve prompts/vy.md based on eval feedback. Use when user wants to evaluate or improve the career advisor prompt.
user-invocable: true
disable-model-invocation: false
allowed-tools: Bash(inspect eval *), Bash(.venv/bin/python evals/*), Bash(python evals/*), Bash(uv run python evals/*), Read, Edit, Grep, Glob, Bash(git *)
---

# Improve Prompt Skill

You are running the eval-driven improvement loop for the AI Safety Career Advisor prompt (`prompts/vy.md`). Follow these steps precisely.

## Important warnings

- Each eval run costs ~$15-25 in API calls and takes 10-20 minutes. Confirm with the user before running.
- Do NOT rewrite the whole prompt. Make only targeted, minimal edits.
- Preserve ALL existing URLs in `prompts/vy.md`. Do NOT add URLs that are not in `prompts/data_sources.md`.

## Step 1: Run the eval

Run the eval using the inspect-ai framework:

```
inspect eval evals/advisor_eval.py
```

The eval simulates multi-turn conversations between 8 diverse personas and the advisor, then scores on a 10-criterion rubric. Model roles (`persona` and `scorer`) default to `claude-sonnet-4-6`. The advisor model can be overridden with `--model`.

## Step 2: Read the results

Read the most recent eval log:

```
.venv/bin/python evals/read_eval_log.py
```

This prints per-sample scores, criteria results, and feedback. No arguments needed for the most recent log.

## Step 3: Extract criteria results

For each sample, find the CRITERIA_RESULTS block and extract the PASS/PARTIAL/FAIL verdict for each of the 10 criteria:

### A. Conversation Process
1. **Discovery before advice** — Did the advisor ask questions before giving recommendations?
2. **Right depth** — Did the advisor match explanation level to persona expertise?
3. **Structured roadmap** — Were recommendations organized into clear phases?

### B. Recommendation Quality
4. **Tailored to persona** — Were resources chosen for THIS person's background?
5. **Actionable and specific** — Were there concrete next steps with specific resources?
6. **Correct routing** — Was the persona directed toward the right area of the field?
7. **Resource quality** — Are recommended resources among the best available?

### C. Coverage and Honesty
8. **No major misses** — Were clearly valuable resources/paths omitted?
9. **Honest calibration** — Was the advisor realistic about difficulty and timelines?
10. **Human advisor option** — Did the advisor mention human career advisors (e.g., AISafety.com)?

## Step 4: Identify patterns

Build a tally across all samples. For example:
- "6/8 samples: FAIL on Discovery before advice"
- "5/8 samples: PARTIAL on Structured roadmap"
- "4/8 samples: FAIL on Human advisor option"

Focus on criteria that are FAIL or PARTIAL in 50%+ of samples. These are the recurring weaknesses.

## Step 5: Propose edits

For each of the top 2-3 recurring weaknesses, propose a specific, minimal edit to `prompts/vy.md`. Examples:
- If "Discovery before advice" is weak: add explicit instruction to ask clarifying questions before giving advice
- If "Human advisor option" is weak: add a section about recommending human advisors
- If "Structured roadmap" is weak: add instruction to organize advice into phases

Read `prompts/vy.md` and `prompts/data_sources.md` before proposing edits.

## Step 6: Apply edits

Use the Edit tool to make targeted changes to `prompts/vy.md`. Keep changes minimal and focused on addressing the identified weaknesses.

## Step 7: Present summary

Present a summary to the user:

1. **Before scores**: Mean score and per-sample breakdown
2. **Weaknesses identified**: The top 2-3 recurring FAIL/PARTIAL patterns with tallies
3. **Changes made**: What was edited in `prompts/vy.md` and why
4. **Next step**: Suggest re-running the eval to verify improvement (`/improve-prompt` again)

After presenting, offer to commit the changes.
