"""Evaluation for the AI Safety Career Advisor (vy.md) prompt.

Simulates multi-turn conversations between diverse personas and the advisor,
then scores the advisor on a unified rubric covering conversation quality,
resource relevance, and coverage.
"""

import re
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import json_dataset
from inspect_ai.model import (
    ChatMessageSystem,
    ChatMessageUser,
    get_model,
)
from inspect_ai.scorer import Score, mean, scorer, stderr
from inspect_ai.solver import Generate, TaskState, solver

ADVISOR_SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "vy.md").read_text()

DATA_SOURCES = (Path(__file__).parent.parent / "prompts" / "data_sources.md").read_text()

# ---------------------------------------------------------------------------
# Persona system prompt
# ---------------------------------------------------------------------------

PERSONA_SYSTEM_TEMPLATE = """\
You are roleplaying as the following person who is seeking AI safety career advice. \
Stay in character throughout the conversation. Be natural and realistic — \
ask questions, respond to advice, share concerns, and follow up on things \
that interest you. Do NOT break character or mention that you are an AI.

Your persona:
{persona_description}

Start the conversation by introducing yourself and explaining why you're \
seeking career advice. Keep your messages concise (2-4 sentences typically)."""

# ---------------------------------------------------------------------------
# Scoring prompt
# ---------------------------------------------------------------------------

SCORING_TEMPLATE = """\
You are an expert evaluator assessing an AI safety career advisor. You will \
score the advisor on a 0-10 scale using the rubric below.

## Persona
{persona_description}

## Conversation
{conversation}

## Reference: Known High-Value Data Sources
Use this as ground truth for what good recommendations look like. The advisor \
doesn't need to mention everything here, but recommendations should draw from \
these sources and be appropriate for the persona.

{data_sources}

---

## Scoring Rubric

Evaluate EACH criterion independently. For each, assign PASS, PARTIAL, or FAIL.

### A. Conversation Process

1. **Discovery before advice** — Did the advisor ask questions to understand the \
persona's situation BEFORE giving recommendations? Jumping straight to advice is \
a FAIL.

2. **Right depth** — Did the advisor match explanation level to the persona's \
expertise? (Not explaining basic ML to an ML engineer. Not using jargon with a \
newcomer.) Misjudging depth is a FAIL.

3. **Structured roadmap** — Did the advisor organize recommendations into clear \
phases (short-term, medium-term, long-term) rather than an unstructured dump of \
links?

### B. Recommendation Quality

4. **Tailored to persona** — Were the specific resources chosen for THIS person's \
background, constraints, and interests? Or could the same advice have been given \
to anyone? Generic advice is a FAIL.

5. **Actionable and specific** — Did the advisor give concrete next steps with \
specific resources (names, links, programs)? Vague advice like "learn more about \
alignment" is a FAIL.

6. **Correct routing** — Did the advisor direct the persona toward the right area \
of the field? (e.g., not pushing a policy person toward technical research, not \
sending an ML engineer to governance courses, correctly identifying domain-specific \
niches like biorisk evals for a biologist). Use the data sources reference to \
judge whether the routing makes sense.

7. **Resource quality** — Are the specific resources recommended actually among \
the best available for this persona? Check against the data sources reference. \
Flag if the advisor recommended weak or generic resources when clearly better \
ones exist in the reference material.

### C. Coverage and Honesty

8. **No major misses** — Did the advisor fail to mention a resource or path that \
would be CLEARLY valuable for this persona? Check the data sources reference for \
what's available. Only flag genuine misses that are obviously relevant — not \
tangential resources.

9. **Honest calibration** — Was the advisor realistic about difficulty, \
competitiveness, and timelines? Did they flag comparative advantages honestly? \
(e.g., telling an ops person that the field desperately needs ops talent, being \
honest with an undergrad about how competitive research roles are)

10. **Human advisor option** — Did the advisor mention the option of talking to \
a human career advisor (e.g., AISafety.com advisors directory) at any point?

---

## Scoring Guide

Count the results:
- 9-10 PASS with 0 FAILs → Score 9-10
- 7-8 PASS, at most 1 FAIL → Score 7-8
- 5-6 PASS, 2-3 FAILs → Score 5-6
- Fewer than 5 PASS or 4+ FAILs → Score 0-4

Be a tough grader. PARTIAL counts as half. If the advisor gave generic advice \
that could apply to anyone, that alone caps the score at 6.

Respond in EXACTLY this format:

CRITERIA_RESULTS:
1. Discovery: PASS/PARTIAL/FAIL — <brief note>
2. Right depth: PASS/PARTIAL/FAIL — <brief note>
3. Structured roadmap: PASS/PARTIAL/FAIL — <brief note>
4. Tailored to persona: PASS/PARTIAL/FAIL — <brief note>
5. Actionable and specific: PASS/PARTIAL/FAIL — <brief note>
6. Correct routing: PASS/PARTIAL/FAIL — <brief note>
7. Resource quality: PASS/PARTIAL/FAIL — <brief note>
8. No major misses: PASS/PARTIAL/FAIL — <brief note>
9. Honest calibration: PASS/PARTIAL/FAIL — <brief note>
10. Human advisor: PASS/PARTIAL/FAIL — <brief note>
SCORE: <number 0-10>
FEEDBACK: <2-3 sentences summarizing the key strengths and weaknesses>"""

# ---------------------------------------------------------------------------
# Solver (conversation simulation)
# ---------------------------------------------------------------------------


@solver
def conversation_sim(turns: int = 10):
    """Simulate a multi-turn conversation between a persona and the advisor."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        persona_description = state.input_text
        persona_model = get_model(role="persona")

        # Set up the advisor's system prompt
        state.messages = [ChatMessageSystem(content=ADVISOR_SYSTEM_PROMPT)]

        # Generate the persona's opening message
        persona_prompt = PERSONA_SYSTEM_TEMPLATE.format(
            persona_description=persona_description
        )
        persona_response = await persona_model.generate(
            [
                ChatMessageSystem(content=persona_prompt),
                ChatMessageUser(content="Begin the conversation now."),
            ]
        )
        persona_message = persona_response.completion
        state.messages.append(ChatMessageUser(content=persona_message))

        for _turn in range(turns):
            # Advisor responds
            state = await generate(state)

            if _turn < turns - 1:
                # Persona responds to the advisor
                persona_history = [ChatMessageSystem(content=persona_prompt)]
                for msg in state.messages[1:]:  # skip advisor system prompt
                    if msg.role == "user":
                        persona_history.append(
                            ChatMessageSystem(content=f"[You]: {msg.content}")
                        )
                    elif msg.role == "assistant":
                        persona_history.append(
                            ChatMessageUser(content=f"[Advisor]: {msg.content}")
                        )
                persona_history.append(
                    ChatMessageUser(
                        content="Continue the conversation naturally. "
                        "Respond to what the advisor just said. "
                        "Ask follow-up questions if you have them."
                    )
                )
                persona_response = await persona_model.generate(persona_history)
                persona_message = persona_response.completion
                state.messages.append(ChatMessageUser(content=persona_message))

        return state

    return solve


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_conversation(state: TaskState) -> str:
    """Format the conversation history for the scoring prompt."""
    lines = []
    for msg in state.messages:
        if msg.role == "system":
            continue
        role = "You" if msg.role == "user" else "Career Advisor"
        lines.append(f"{role}: {msg.content}")
    return "\n\n".join(lines)


def _parse_score(response_text: str, default: int = 5) -> tuple[int, str]:
    """Extract SCORE and full explanation (criteria + feedback) from a scorer response."""
    score_match = re.search(r"SCORE:\s*(\d+)", response_text)
    score_val = int(score_match.group(1)) if score_match else default

    # Include everything from CRITERIA_RESULTS onward as the explanation
    criteria_match = re.search(r"CRITERIA_RESULTS:\s*\n(.+)", response_text, re.DOTALL)
    explanation = (
        criteria_match.group(1).strip() if criteria_match else response_text
    )
    return score_val, explanation


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


@scorer(metrics=[mean(), stderr()])
def advisor_scorer():
    """Score the advisor on a unified 10-criterion rubric."""

    async def score(state: TaskState, target) -> Score:
        scorer_model = get_model(role="scorer")
        persona_description = state.input_text
        conversation = _format_conversation(state)

        scoring_prompt = SCORING_TEMPLATE.format(
            persona_description=persona_description,
            conversation=conversation,
            data_sources=DATA_SOURCES,
        )

        response = await scorer_model.generate(
            [ChatMessageUser(content=scoring_prompt)]
        )
        score_val, feedback = _parse_score(response.completion)

        return Score(value=score_val, explanation=feedback)

    return score


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


@task
def advisor_eval():
    """Evaluate the AI Safety Career Advisor via persona simulation and rubric scoring."""
    return Task(
        dataset=json_dataset(str(Path(__file__).parent / "personas.json")),
        solver=conversation_sim(turns=10),
        scorer=advisor_scorer(),
        model_roles={
            "persona": "anthropic/claude-sonnet-4-6",
            "scorer": "anthropic/claude-sonnet-4-6",
        },
    )
