"""Run deterministic chatbot-search checks without making an OpenAI API call."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.chatbot_evals import CASES, run_chatbot_evaluations


def main() -> None:
    failures = run_chatbot_evaluations()
    failed_cases = {failure["case"] for failure in failures}
    for description, _, _, _ in CASES:
        print(f"{'FAIL' if description in failed_cases else 'PASS'}: {description}")

    if failures:
        raise SystemExit(f"{len(failures)} chatbot evaluation(s) failed: {failures}")
    print(f"All {len(CASES)} chatbot evaluations passed.")


if __name__ == "__main__":
    main()
