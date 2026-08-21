import pandas as pd

from role_rubrics import SUPPORTED_ROLES


YES_NO_VALUES = {"Yes", "No"}

REQUIRED_COLUMNS = [
    "candidate_id",
    "name",
    "email",
    "phone",
    "university",
    "semester",
    "applied_role",
    "current_city",
    "lahore_address",
    "shift_available",
    "onsite_available",
    "linkedin_url",
    "resume_filename",
]


def is_blank(series):
    return series.isna() | series.astype(str).str.strip().eq("")


def validate_applications(applications):
    issues = []

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in applications.columns
    ]

    for column in missing_columns:
        issues.append(
            {
                "row": "-",
                "candidate_id": "-",
                "field": column,
                "message": f"Required column '{column}' is missing.",
            }
        )

    if missing_columns:
        return pd.DataFrame(issues)

    candidate_ids = applications["candidate_id"].astype("string").str.strip()
    roles = applications["applied_role"].astype("string").str.strip()
    shifts = applications["shift_available"].astype("string").str.strip()
    onsite = applications["onsite_available"].astype("string").str.strip()

    def add_issues(mask, field, message):
        for index in applications.index[mask]:
            candidate_id = candidate_ids.loc[index]

            if pd.isna(candidate_id) or not candidate_id:
                candidate_id = "(missing)"

            issues.append(
                {
                    "row": index + 2,
                    "candidate_id": candidate_id,
                    "field": field,
                    "message": message,
                }
            )

    missing_id = is_blank(applications["candidate_id"])
    add_issues(missing_id, "candidate_id", "Candidate ID is missing.")

    duplicate_id = candidate_ids.duplicated(keep=False) & ~missing_id
    add_issues(duplicate_id, "candidate_id", "Duplicate candidate ID.")

    invalid_role = (
        ~roles.isin(SUPPORTED_ROLES)
        & ~is_blank(applications["applied_role"])
    )
    add_issues(
        invalid_role,
        "applied_role",
        "Unsupported internship role.",
    )

    invalid_shift = (
        ~shifts.isin(YES_NO_VALUES)
        & ~is_blank(applications["shift_available"])
    )
    add_issues(
        invalid_shift,
        "shift_available",
        "Shift availability must be Yes or No.",
    )

    invalid_onsite = (
        ~onsite.isin(YES_NO_VALUES)
        & ~is_blank(applications["onsite_available"])
    )
    add_issues(
        invalid_onsite,
        "onsite_available",
        "Onsite availability must be Yes or No.",
    )

    missing_resume = is_blank(applications["resume_filename"])
    add_issues(
        missing_resume,
        "resume_filename",
        "Resume filename is missing.",
    )

    return pd.DataFrame(
        issues,
        columns=["row", "candidate_id", "field", "message"],
    )
