"""Evaluation for the AI Safety Career Advisor (vy.md) prompt.

Three scoring dimensions:
1. Conversation quality — rubric-scored by the persona (NPS 0-10)
2. Information freshness — checks if recommendations are up-to-date using trusted sources
3. Coverage — checks if the advisor missed highly relevant resources for the persona
"""

import json
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

TRUSTED_SOURCES = json.loads(
    (Path(__file__).parent / "trusted_sources.json").read_text()
)
TRUSTED_DOMAINS_LIST = "\n".join(
    f"- {s['name']} ({s['domain']}): {s['description']}"
    for s in TRUSTED_SOURCES["domains"]
)

# ---------------------------------------------------------------------------
# Persona system prompt (unchanged)
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
# Scoring prompt templates
# ---------------------------------------------------------------------------

QUALITY_SCORING_TEMPLATE = """\
You just finished a career advising conversation. You are still in character as:

{persona_description}

Here is the full conversation you had with the career advisor:

{conversation}

Rate the career advisor on a scale from 0 to 10 (Net Promoter Score), where:
- 0-6: Detractor (would not recommend)
- 7-8: Passive (satisfied but not enthusiastic)
- 9-10: Promoter (would enthusiastically recommend)

Evaluate each of these criteria carefully. For EACH criterion, note whether the \
advisor succeeded or failed, then use those judgments to determine your overall score.

CRITERIA:
1. Discovery before advice — Did the advisor ask questions to understand your \
situation BEFORE giving recommendations? Or did they jump straight to generic advice?
2. Tailored recommendations — Were the specific resources, programs, and paths \
recommended clearly chosen for YOUR background and constraints? Or could the same \
advice have been given to anyone?
3. Structured roadmap — Did the advisor break recommendations into clear phases \
(short-term, medium-term, long-term)? Or was it an unstructured list?
4. Right depth — Did the advisor match their level of explanation to your expertise? \
(e.g., not explaining basic ML to an ML engineer, not drowning a newcomer in jargon)
5. Actionability — Could you actually act on the advice right now? Were there \
specific links, programs, or next steps, or was it vague ("learn more about X")?
6. Honesty — Was the advisor realistic about difficulty, competitiveness, and \
timelines? Or did they make everything sound easy?
7. Human advisor option — Did the advisor mention the option of talking to a human \
career advisor (e.g., AISafety.com advisors) at any point?

IMPORTANT: Be a tough grader. A score of 7-8 means "good but not exceptional." \
Reserve 9-10 for advice that genuinely impressed you. A score of 5-6 means \
"okay but had clear gaps." Below 5 means the advice was unhelpful or generic.

Respond in EXACTLY this format:
CRITERIA_RESULTS:
1. Discovery: PASS/FAIL — <brief note>
2. Tailored: PASS/FAIL — <brief note>
3. Roadmap: PASS/FAIL — <brief note>
4. Depth: PASS/FAIL — <brief note>
5. Actionability: PASS/FAIL — <brief note>
6. Honesty: PASS/FAIL — <brief note>
7. Human advisor: PASS/FAIL — <brief note>
SCORE: <number 0-10>
FEEDBACK: <2-3 sentences explaining your rating, in character>"""

FRESHNESS_SCORING_TEMPLATE = """\
You are an evaluator checking whether a career advisor gave up-to-date information.

Here is the conversation between a persona and the advisor:

{conversation}

Your task: Extract every specific resource the advisor recommended (courses, \
programs, organizations, guides, job boards, etc.) and evaluate whether each one \
is current and appropriate.

For each resource, check:
1. Is it still active and available? (Not shut down, moved, or deprecated)
2. Is the description accurate? (e.g., if the advisor says "4-week bootcamp" but \
it's now 6 weeks, that's inaccurate)
3. Is there a newer or better alternative from a trusted source that the advisor \
should have recommended instead?

You may ONLY check resources from these trusted sources:
{trusted_domains}

For each resource mentioned, assess whether it appears current based on your \
knowledge. Flag anything that seems potentially outdated or where you know a \
better alternative exists.

Rate the overall freshness on a scale from 0 to 10:
- 0-3: Multiple outdated or broken resources recommended
- 4-6: Some resources may be outdated or better alternatives exist
- 7-8: Most resources appear current, minor gaps
- 9-10: All resources are current and well-chosen

Respond in EXACTLY this format:
RESOURCES_CHECKED:
- <resource name> (<url if given>): CURRENT / POSSIBLY_OUTDATED / OUTDATED — <note>
...
SCORE: <number 0-10>
FEEDBACK: <2-3 sentences summarizing freshness assessment>"""

COVERAGE_SCORING_TEMPLATE = """\
You are an evaluator checking whether a career advisor missed important resources \
or paths for a specific person.

Here is the persona:
{persona_description}

Here is the conversation:
{conversation}

The advisor has access to resources from these trusted sources:
{trusted_domains}

Your task: Based on the persona's background, interests, and constraints, identify \
any HIGHLY RELEVANT resources or career paths that the advisor failed to mention.

Only flag genuine misses — resources that would have been clearly valuable for this \
specific person. Do NOT flag resources that are tangentially related or that would \
only matter in edge cases.

Consider:
1. Did the advisor miss an obvious career path that fits this persona's background?
2. Did the advisor fail to mention a key organization or program that directly \
matches what this person is looking for?
3. Did the advisor miss a community, job board, or funding source that would be \
highly relevant?
4. For technical personas: did the advisor fail to connect them to specific \
research agendas from the Shallow Review that match their skills?

Rate coverage on a scale from 0 to 10:
- 0-3: Major relevant paths or resources were missed
- 4-6: Some notable gaps in coverage
- 7-8: Good coverage with minor misses
- 9-10: Comprehensive — all highly relevant resources were mentioned

Respond in EXACTLY this format:
MISSED_RESOURCES:
- <resource or path>: <why it's relevant for this persona>
...
(Write "None identified" if coverage was comprehensive)
SCORE: <number 0-10>
FEEDBACK: <2-3 sentences summarizing coverage assessment>"""

# ---------------------------------------------------------------------------
# Solver (conversation simulation) — unchanged
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
# Helper
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
    """Extract SCORE and FEEDBACK from a scorer response."""
    score_match = re.search(r"SCORE:\s*(\d+)", response_text)
    score_val = int(score_match.group(1)) if score_match else default

    feedback_match = re.search(r"FEEDBACK:\s*(.+)", response_text, re.DOTALL)
    feedback = (
        feedback_match.group(1).strip() if feedback_match else response_text
    )
    return score_val, feedback


# ---------------------------------------------------------------------------
# Scorer 1: Conversation quality (rubric-based NPS)
# ---------------------------------------------------------------------------


@scorer(metrics=[mean(), stderr()])
def quality_scorer():
    """Rate the advisor on conversation quality using a detailed rubric."""

    async def score(state: TaskState, target) -> Score:
        scorer_model = get_model(role="scorer")
        persona_description = state.input_text
        conversation = _format_conversation(state)

        scoring_prompt = QUALITY_SCORING_TEMPLATE.format(
            persona_description=persona_description,
            conversation=conversation,
        )

        response = await scorer_model.generate(
            [ChatMessageUser(content=scoring_prompt)]
        )
        score_val, feedback = _parse_score(response.completion)

        return Score(value=score_val, explanation=feedback)

    return score


# ---------------------------------------------------------------------------
# Scorer 2: Information freshness
# ---------------------------------------------------------------------------


@scorer(metrics=[mean(), stderr()])
def freshness_scorer():
    """Check if recommended resources are up-to-date."""

    async def score(state: TaskState, target) -> Score:
        scorer_model = get_model(role="scorer")
        conversation = _format_conversation(state)

        scoring_prompt = FRESHNESS_SCORING_TEMPLATE.format(
            conversation=conversation,
            trusted_domains=TRUSTED_DOMAINS_LIST,
        )

        response = await scorer_model.generate(
            [ChatMessageUser(content=scoring_prompt)]
        )
        score_val, feedback = _parse_score(response.completion)

        return Score(value=score_val, explanation=feedback)

    return score


# ---------------------------------------------------------------------------
# Scorer 3: Coverage
# ---------------------------------------------------------------------------


@scorer(metrics=[mean(), stderr()])
def coverage_scorer():
    """Check if the advisor missed highly relevant resources for the persona."""

    async def score(state: TaskState, target) -> Score:
        scorer_model = get_model(role="scorer")
        persona_description = state.input_text
        conversation = _format_conversation(state)

        scoring_prompt = COVERAGE_SCORING_TEMPLATE.format(
            persona_description=persona_description,
            conversation=conversation,
            trusted_domains=TRUSTED_DOMAINS_LIST,
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
    """Evaluate the AI Safety Career Advisor across quality, freshness, and coverage."""
    return Task(
        dataset=json_dataset(str(Path(__file__).parent / "personas.json")),
        solver=conversation_sim(turns=10),
        scorer=[
            quality_scorer(),
            # freshness_scorer(),  # TODO: needs live web fetching to be useful
            coverage_scorer(),
        ],
        model_roles={
            "persona": "anthropic/claude-sonnet-4-6",
            "scorer": "anthropic/claude-sonnet-4-6",
        },
    )
