"""Read and summarize eval log results.

Usage:
    .venv/bin/python evals/read_eval_log.py <path-to-eval-file>
    .venv/bin/python evals/read_eval_log.py  # reads most recent log
"""

import sys
from pathlib import Path

from inspect_ai.log import read_eval_log, list_eval_logs


def print_eval_summary(log_path: str | None = None) -> None:
    if log_path:
        log = read_eval_log(log_path)
    else:
        logs = list_eval_logs("logs/")
        if not logs:
            print("No eval logs found in logs/")
            return
        log = read_eval_log(logs[0].name)

    print(f"Task: {log.eval.task}")
    print(f"Model: {log.eval.model}")
    print(f"Status: {log.status}")
    print(f"Samples: {len(log.samples)}")
    print()

    scores = []
    for i, sample in enumerate(log.samples):
        score_obj = sample.scores.get("advisor_scorer")
        if not score_obj:
            continue

        # Extract persona name from input
        input_text = sample.input if isinstance(sample.input, str) else str(sample.input)
        first_line = input_text[:120]

        print(f"{'='*60}")
        print(f"Sample {i} | Score: {score_obj.value}/10")
        print(f"Persona: {first_line}...")
        print(f"\nFeedback: {score_obj.explanation}")
        scores.append(score_obj.value)

        # Find full criteria from ModelEvent
        for ev in sample.events:
            if type(ev).__name__ == "ModelEvent":
                out = getattr(ev, "output", None)
                if out:
                    comp = getattr(out, "completion", "")
                    if "CRITERIA_RESULTS" in comp:
                        print(f"\nFull Criteria:\n{comp}")
                        break
        print()

    if scores:
        print(f"{'='*60}")
        print(f"Mean score: {sum(scores)/len(scores):.1f}/10")
        print(f"Min: {min(scores)}, Max: {max(scores)}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    print_eval_summary(path)
