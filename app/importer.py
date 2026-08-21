from pathlib import Path

import pandas as pd

from validator import validate_applications


CSV_PATH = Path(
    "data/applications/synthetic_applications.csv"
)

DISPLAY_COLUMNS = [
    "candidate_id",
    "applied_role",
    "current_city",
    "shift_available",
    "onsite_available",
    "resume_filename",
]


applications = pd.read_csv(CSV_PATH)

print(f"\nTotal number of applications: {len(applications)}\n")

print(
    applications[DISPLAY_COLUMNS].to_string(index=False)
)

issues = validate_applications(applications)

print("\n--- Validation ---")

if issues.empty:
    print("Validation passed. No application issues found.")
else:
    print(f"Validation found {len(issues)} issue(s):\n")
    print(issues.to_string(index=False))