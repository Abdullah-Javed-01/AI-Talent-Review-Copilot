import json
from pathlib import Path

import pandas as pd

from evidence_extractor import extract_evidence
from resume_parser import parse_resume
from score_engine import score_candidate
from validator import validate_applications


ROOT = Path(__file__).resolve().parents[1]

APPLICATION_FILE = (
    ROOT
    / "data"
    / "applications"
    / "synthetic_applications.csv"
)

RESUME_DIR = ROOT / "data" / "resumes"

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "candidate_profiles.json"


applications = pd.read_csv(APPLICATION_FILE)

issues = validate_applications(applications)

if not issues.empty:
    print("\nApplication validation failed:\n")
    print(issues.to_string(index=False))
    raise SystemExit(1)


profiles = []


print(
    f"\nProcessing {len(applications)} candidates...\n"
)


for _, application in applications.iterrows():

    candidate_id = application["candidate_id"]

    resume_path = (
        RESUME_DIR
        / application["resume_filename"]
    )

    parsed_resume = parse_resume(resume_path)

    profile = {
        "candidate_id": candidate_id,
        "name": application["name"],
        "applied_role": application["applied_role"],

        "operational": {
            "current_city": application["current_city"],
            "onsite_available": application[
                "onsite_available"
            ],
            "shift_available": application[
                "shift_available"
            ],
        },

        "resume": {
            "filename": application["resume_filename"],
            "parse_status": parsed_resume["status"],
            "pages": parsed_resume["pages"],
        },
    }

    if parsed_resume["status"] != "success":

        profile["manual_review_required"] = True

        profile["manual_review_reason"] = (
            parsed_resume["error"]
        )

        profiles.append(profile)

        print(
            f"{candidate_id}: MANUAL REVIEW "
            f"({parsed_resume['error']})"
        )

        continue

    evidence = extract_evidence(
        parsed_resume["text"]
    )

    result = score_candidate(
        evidence,
        application,
    )

    profile["manual_review_required"] = False

    profile["evidence"] = evidence

    profile["assessment"] = result

    profiles.append(profile)

    print(
        f"{candidate_id}: "
        f"{result['total_score']}/22 | "
        f"{result['technical_review_priority']} | "
        f"{result['operational_status']}"
    )


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        profiles,
        file,
        indent=2,
        ensure_ascii=False,
    )


print(
    f"\nSaved candidate profiles to:\n"
    f"{OUTPUT_FILE}"
)