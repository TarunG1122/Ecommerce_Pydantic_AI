"""No-cost regression checks for the chatbot's server-side search guardrails."""

from typing import Any


CASES = [
    (
        "white shirt excludes a black shirt",
        {"name": "Classic Black Shirt", "category": "men", "color": ["Black"], "price": 1200},
        {"keyword": "shirt", "color": "white"},
        False,
    ),
    (
        "white shirt includes a white shirt",
        {"name": "Classic White Shirt", "category": "men", "color": ["White"], "price": 1200},
        {"keyword": "shirt", "color": "white"},
        True,
    ),
    (
        "budget is enforced after AI extraction",
        {"name": "White Shirt", "category": "men", "color": ["White"], "price": 2200},
        {"keyword": "shirt", "color": "white", "max_price": 2000},
        False,
    ),
]


def run_chatbot_evaluations() -> list[dict[str, Any]]:
    """Validate strict catalog guardrails without sending OpenAI requests."""
    from .routes.chabot import product_matches

    failures = []
    for description, product, filters, expected in CASES:
        actual = product_matches(product, **filters)
        if actual != expected:
            failures.append({"case": description, "expected": expected, "actual": actual})
    return failures
