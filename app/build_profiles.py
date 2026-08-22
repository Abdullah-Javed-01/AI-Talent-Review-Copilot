import argparse
import json
from pathlib import Path

import pandas as pd

from assessment_utils import get_operational_fit, get_review_priority
from evidence_extractor import extract_evidence
from resume_parser import parse_resume
from role_evidence import extract_role_evidence
from role_rubrics import get_role_rubric
from role_score_engine import score_role_evidence
from score_engine import score_candidate
from validator import validate_applications


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APPLICATION_FILE = ROOT / "data" / "applications" / "synthetic_applications.csv"
RESUME_DIR = ROOT / "data" / "resumes"
OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "candidate_profiles.json"


def _clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def build_profiles(application_file):
    applications = pd.read_csv(application_file)
    issues = validate_applications(applications)

    if not issues.empty:
        print("\nApplication validation failed:\n")
        print(issues.to_string(index=False))
        raise SystemExit(1)

    profiles = []
    print(f"\nProcessing {len(applications)} candidates...\n")

    for _, application in applications.iterrows():
        candidate_id = _clean(application.get("candidate_id"))
        role = _clean(application.get("applied_role"))
        resume_filename = _clean(application.get("resume_filename"))
        resume_source = _clean(application.get("resume_source")) or resume_filename
        resume_source_type = _clean(application.get("resume_source_type")) or (
            "local_reference" if resume_filename else "remote_url" if resume_source else "missing"
        )

        application_info = {
            "name": _clean(application.get("name")),
            "email": _clean(application.get("email")),
            "phone": _clean(application.get("phone")),
            "university": _clean(application.get("university")),
            "semester": _clean(application.get("semester")),
            "applied_role": role,
            "linkedin_url": _clean(application.get("linkedin_url")),
            "source": "application_form",
        }

        operational = {
            "current_city": _clean(application.get("current_city")),
            "lahore_address": _clean(application.get("lahore_address")),
            "onsite_available": _clean(application.get("onsite_available")),
            "shift_available": _clean(application.get("shift_available")),
            "source": "application_form",
        }

        profile = {
            "candidate_id": candidate_id,
            "name": application_info["name"],
            "applied_role": role,
            "application": application_info,
            "operational": operational,
            "provenance": {
                "application_fields": "application_form",
                "technical_evidence": "resume_cv",
                "assessment": "deterministic_role_rubric",
                "recruiter_decision": "human_recruiter",
            },
        }

        if resume_source_type == "remote_url" and not resume_filename:
            profile["resume"] = {
                "source": resume_source,
                "source_type": resume_source_type,
                "filename": "",
                "parse_status": "pending_retrieval",
                "pages": 0,
            }
            profile["manual_review_required"] = True
            profile["manual_review_reason"] = (
                "Resume is referenced by a remote URL and must be retrieved with authorized file access before parsing."
            )
            profiles.append(profile)
            print(f"{candidate_id}: MANUAL REVIEW (remote resume retrieval required)")
            continue

        resume_path = RESUME_DIR / resume_filename
        parsed_resume = parse_resume(resume_path)

        profile["resume"] = {
            "source": resume_source,
            "source_type": resume_source_type,
            "filename": resume_filename,
            "parse_status": parsed_resume["status"],
            "pages": parsed_resume["pages"],
        }

        if parsed_resume["status"] != "success":
            profile["manual_review_required"] = True
            profile["manual_review_reason"] = parsed_resume["error"]
            profiles.append(profile)
            print(f"{candidate_id}: MANUAL REVIEW ({parsed_resume['error']})")
            continue

        if role == "ML/AI":
            evidence = extract_evidence(parsed_resume["text"])
            result = score_candidate(evidence, application)
            rubric = get_role_rubric(role)
            result["rubric_name"] = rubric["name"]
            result["criteria"] = rubric["criteria"]
        else:
            evidence = extract_role_evidence(parsed_resume["text"], role)
            result = score_role_evidence(evidence, role)
            operational_status, operational_reason = get_operational_fit(application)
            result["operational_status"] = operational_status
            result["operational_reason"] = operational_reason
            result["technical_review_priority"] = get_review_priority(
                result["total_score"],
                result["max_score"],
            )
            result["criteria"] = get_role_rubric(role)["criteria"]

        result["source"] = "deterministic_role_rubric"
        evidence["source"] = "resume_cv"

        profile["manual_review_required"] = False
        profile["evidence"] = evidence
        profile["assessment"] = result
        profiles.append(profile)

        print(
            f"{candidate_id}: {role} | "
            f"{result['total_score']}/{result['max_score']} | "
            f"{result['technical_review_priority']} | "
            f"{result['operational_status']}"
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(profiles, file, indent=2, ensure_ascii=False)

    print(f"\nSaved candidate profiles to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build recruiter-ready candidate profiles.")
    parser.add_argument(
        "--applications",
        default=str(DEFAULT_APPLICATION_FILE),
        help="Path to a normalized application CSV.",
    )
    args = parser.parse_args()
    build_profiles(Path(args.applications))
