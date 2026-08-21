import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DECISION_FILE = (
    ROOT
    / "data"
    / "processed"
    / "recruiter_decisions.json"
)


def load_decisions():
    if not DECISION_FILE.exists():
        return {}

    try:
        with open(
            DECISION_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_decision(candidate_id, decision):
    decisions = load_decisions()

    decisions[candidate_id] = decision

    DECISION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        DECISION_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            decisions,
            file,
            indent=2,
        )


def get_decision(candidate_id):
    decisions = load_decisions()

    return decisions.get(
        candidate_id,
        "PENDING",
    )