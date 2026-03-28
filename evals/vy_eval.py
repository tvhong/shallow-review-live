"""NPS evaluation for the AI Safety Career Advisor (vy.md) prompt.

Simulates multi-turn conversations between diverse personas and the advisor,
then has each persona rate the advisor on an NPS scale (0-10).
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

PERSONA_SYSTEM_TEMPLATE = """\
You are roleplaying as the following person who is seeking AI safety career advice. \
Stay in character throughout the conversation. Be natural and realistic — \
ask questions, respond to advice, share concerns, and follow up on things \
that interest you. Do NOT break character or mention that you are an AI.

Your persona:
{persona_description}

Start the conversation by introducing yourself and explaining why you're \
seeking career advice. Keep your messages concise (2-4 sentences typically)."""

NPS_SCORING_TEMPLATE = """\
You just finished a career advising conversation. You are still in character as:

{persona_description}

Here is the full conversation you had with the career advisor:

{conversation}

Now, step back and rate the career advisor on a scale from 0 to 10 \
(Net Promoter Score), where:
- 0-6: Detractor (would not recommend)
- 7-8: Passive (satisfied but not enthusiastic)
- 9-10: Promoter (would enthusiastically recommend)

Consider:
1. Did the advisor understand your specific situation and needs?
2. Were the recommendations concrete and actionable (not generic)?
3. Did the advisor tailor advice to your background and constraints?
4. Did you learn something useful you didn't know before?
5. Would you recommend this advisor to a friend in a similar situation?

Respond in EXACTLY this format:
SCORE: <number 0-10>
FEEDBACK: <2-3 sentences explaining your rating, in character>"""


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
            advisor_message = state.output.completion

            if _turn < turns - 1:
                # Persona responds to the advisor
                # Build the persona's view of the conversation
                persona_history = [ChatMessageSystem(content=persona_prompt)]
                for msg in state.messages[1:]:  # skip advisor system prompt
                    if msg.role == "user":
                        persona_history.append(
                            ChatMessageSystem(
                                content=f"[Your previous message]: {msg.content}"
                            )
                        )
                    elif msg.role == "assistant":
                        persona_history.append(
                            ChatMessageUser(
                                content=f"The career advisor said: {msg.content}"
                            )
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


def _format_conversation(state: TaskState) -> str:
    """Format the conversation history for the scoring prompt."""
    lines = []
    for msg in state.messages:
        if msg.role == "system":
            continue
        role = "You" if msg.role == "user" else "Career Advisor"
        lines.append(f"{role}: {msg.content}")
    return "\n\n".join(lines)


@scorer(metrics=[mean(), stderr()])
def nps_scorer():
    """Have the persona rate the advisor on NPS (0-10)."""

    async def score(state: TaskState, target) -> Score:
        persona_model = get_model(role="persona")
        persona_description = state.input_text
        conversation = _format_conversation(state)

        scoring_prompt = NPS_SCORING_TEMPLATE.format(
            persona_description=persona_description,
            conversation=conversation,
        )

        response = await persona_model.generate(
            [ChatMessageUser(content=scoring_prompt)]
        )
        response_text = response.completion

        # Parse the score
        score_match = re.search(r"SCORE:\s*(\d+)", response_text)
        nps_score = int(score_match.group(1)) if score_match else 5

        # Parse the feedback
        feedback_match = re.search(
            r"FEEDBACK:\s*(.+)", response_text, re.DOTALL
        )
        feedback = (
            feedback_match.group(1).strip() if feedback_match else response_text
        )

        return Score(
            value=nps_score,
            explanation=feedback,
        )

    return score


@task
def vy_advisor_eval():
    """Evaluate the AI Safety Career Advisor prompt via persona-based NPS scoring."""
    return Task(
        dataset=json_dataset(str(Path(__file__).parent / "personas.json")),
        solver=conversation_sim(turns=10),
        scorer=nps_scorer(),
        model_roles={"persona": "anthropic/claude-sonnet-4-6"},
    )
