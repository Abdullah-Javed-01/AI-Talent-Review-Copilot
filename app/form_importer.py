import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


FIELD_ALIASES = {
    "candidate_id": ["candidate id", "candidate_id", "application id", "applicant id"],
    "name": ["name", "full name", "candidate name", "applicant name"],
    "email": ["email", "email address", "e-mail"],
    "phone": ["phone", "phone number", "contact number", "mobile number", "contact"],
    "university": ["university", "university name", "institute", "institution"],
    "semester": ["semester", "current semester", "education status", "academic status"],
    "applied_role": ["applied role", "role", "internship role", "position", "position applied for"],
    "current_city": ["current city", "city", "current location", "location"],
    "lahore_address": ["lahore address", "address in lahore", "address", "current address"],
    "shift_available": [
        "shift available",
        "working hours",
        "5pm-2am availability",
        "5 pm - 2 am availability",
        "5pm to 2am",
        "required shift",
    ],
    "onsite_available": ["onsite available", "onsite availability", "available onsite", "on-site availability"],
    "linkedin_url": ["linkedin", "linkedin url", "linkedin profile", "linkedin profile url"],
    "resume_source": ["resume", "cv", "resume/cv", "resume cv", "upload resume", "upload cv", "resume link"],
}


def normalize_header(value):
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_yes_no(value):
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "available", "1"}:
        return "Yes"
    if text in {"no", "n", "false", "not available", "0"}:
        return "No"
    return str(value).strip()


def is_url(value):
    try:
        parsed = urlparse(str(value).strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def find_column(columns, aliases):
    normalized = {normalize_header(column): column for column in columns}
    for alias in aliases:
        key = normalize_header(alias)
        if key in normalized:
            return normalized[key]
    return None


def import_form_export(input_csv, output_csv):
    input_csv = Path(input_csv)
    output_csv = Path(output_csv)

    raw = pd.read_csv(input_csv)
    normalized = pd.DataFrame(index=raw.index)

    resolved_columns = {}
    for internal_name, aliases in FIELD_ALIASES.items():
        source_column = find_column(raw.columns, aliases)
        resolved_columns[internal_name] = source_column
        normalized[internal_name] = (
            raw[source_column].fillna("").astype(str).str.strip()
            if source_column
            else ""
        )

    if normalized["candidate_id"].eq("").all():
        normalized["candidate_id"] = [
            f"FORM-{index:06d}"
            for index in range(1, len(normalized) + 1)
        ]
    else:
        missing_ids = normalized["candidate_id"].eq("")
        for offset, row_index in enumerate(normalized.index[missing_ids], start=1):
            normalized.loc[row_index, "candidate_id"] = f"FORM-MISSING-{offset:06d}"

    normalized["shift_available"] = normalized["shift_available"].map(normalize_yes_no)
    normalized["onsite_available"] = normalized["onsite_available"].map(normalize_yes_no)

    normalized["resume_filename"] = normalized["resume_source"].map(
        lambda value: "" if not value or is_url(value) else Path(value).name
    )
    normalized["resume_source_type"] = normalized["resume_source"].map(
        lambda value: "remote_url" if is_url(value) else "local_reference" if value else "missing"
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(output_csv, index=False)

    return {
        "rows": len(normalized),
        "output_csv": str(output_csv),
        "resolved_columns": resolved_columns,
        "unresolved_fields": [
            key for key, value in resolved_columns.items()
            if value is None and key != "candidate_id"
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Normalize an exported internship application form into the Talent Review Copilot schema."
    )
    parser.add_argument("input_csv", help="Path to the exported form CSV")
    parser.add_argument(
        "--output",
        default="data/applications/imported_applications.csv",
        help="Normalized CSV output path",
    )
    args = parser.parse_args()

    result = import_form_export(args.input_csv, args.output)

    print(f"Imported {result['rows']} application(s).")
    print(f"Normalized CSV: {result['output_csv']}")

    if result["unresolved_fields"]:
        print("Unresolved optional/form fields:")
        for field in result["unresolved_fields"]:
            print(f"- {field}")

    remote_resume_count = pd.read_csv(result["output_csv"])["resume_source_type"].eq("remote_url").sum()
    if remote_resume_count:
        print(
            f"\n{remote_resume_count} resume reference(s) are remote URLs. "
            "Google Forms file uploads usually require authenticated Drive retrieval before parsing."
        )


if __name__ == "__main__":
    main()
