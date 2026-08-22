import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
ROOT = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from build_profiles import build_profiles
from form_importer import import_form_export

APPLICATION_DIR = ROOT / "data" / "applications"
RESUME_DIR = ROOT / "data" / "resumes"
RAW_FORM_EXPORT = APPLICATION_DIR / "uploaded_form_export.csv"
NORMALIZED_APPLICATIONS = APPLICATION_DIR / "imported_applications.csv"

APPLICATION_DIR.mkdir(parents=True, exist_ok=True)
RESUME_DIR.mkdir(parents=True, exist_ok=True)

st.title("Data Intake")
st.caption(
    "Import application responses and candidate CVs without touching the codebase. "
    "Technical evidence is extracted only after the actual CV file is available."
)

st.info(
    "Current demo workflow: upload a Google Forms/Sheets CSV export plus the corresponding PDF CV files. "
    "A direct Google Drive connection can replace the manual CV upload step once the recruiter authorizes Drive access."
)

with st.expander("How a real Google Form connects", expanded=False):
    st.markdown(
        """
        **Application Form** → name, email, phone, university, semester, role, city/address, shift, onsite, LinkedIn  
        **CV / Resume** → technical skills, projects, tools, model/data/deployment evidence  
        **Role rubric** → deterministic evidence score and review priority  
        **Recruiter** → shortlist, hold, or not selected

        If a Google Form file-upload answer appears as a Drive URL, this app keeps the URL as provenance. "
        "It does not claim to have parsed the CV until the file itself is uploaded or retrieved with authorized Drive access.
        """
    )

st.subheader("1. Upload form responses")
form_file = st.file_uploader(
    "Google Forms / Google Sheets CSV export",
    type=["csv"],
    help="Export the response sheet as CSV and upload it here. Column names do not need to match the internal schema exactly.",
)

st.subheader("2. Upload candidate CV files")
cv_files = st.file_uploader(
    "Candidate CVs (PDF)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload the PDF files collected from the form. Multiple files can be uploaded together.",
)


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _guess_file(candidate_name, filenames):
    name_slug = _slug(candidate_name)
    if not name_slug:
        return None

    for filename in filenames:
        file_slug = _slug(Path(filename).stem)
        if name_slug and name_slug in file_slug:
            return filename

    name_tokens = [token for token in re.findall(r"[a-z0-9]+", str(candidate_name).lower()) if len(token) > 1]
    for filename in filenames:
        file_slug = _slug(Path(filename).stem)
        if name_tokens and all(token in file_slug for token in name_tokens):
            return filename

    return None


if form_file is not None:
    RAW_FORM_EXPORT.write_bytes(form_file.getvalue())

    try:
        result = import_form_export(RAW_FORM_EXPORT, NORMALIZED_APPLICATIONS)
        normalized_df = pd.read_csv(NORMALIZED_APPLICATIONS).fillna("")
    except Exception as exc:
        st.error(f"Could not normalize the form export: {exc}")
        st.stop()

    st.success(f"Imported {result['rows']} application response(s).")

    if result["unresolved_fields"]:
        st.warning(
            "These fields were not matched automatically: "
            + ", ".join(result["unresolved_fields"])
        )

    st.markdown("#### Normalized application preview")
    preview_columns = [
        column
        for column in [
            "candidate_id",
            "name",
            "applied_role",
            "current_city",
            "shift_available",
            "onsite_available",
            "resume_source_type",
        ]
        if column in normalized_df.columns
    ]
    st.dataframe(normalized_df[preview_columns], width="stretch", hide_index=True)

    uploaded_names = []
    uploaded_bytes = {}
    for uploaded_cv in cv_files or []:
        safe_name = Path(uploaded_cv.name).name
        uploaded_names.append(safe_name)
        uploaded_bytes[safe_name] = uploaded_cv.getvalue()
        (RESUME_DIR / safe_name).write_bytes(uploaded_cv.getvalue())

    st.subheader("3. Match CVs to candidates")

    working_df = normalized_df.copy()
    mapping = {}

    for row_index, row in working_df.iterrows():
        candidate_id = str(row.get("candidate_id", "")).strip()
        candidate_name = str(row.get("name", "")).strip()
        current_filename = str(row.get("resume_filename", "")).strip()
        source_type = str(row.get("resume_source_type", "")).strip()

        options = ["— No CV selected —"] + uploaded_names
        default_index = 0

        if current_filename in uploaded_names:
            default_index = options.index(current_filename)
        elif len(working_df) == 1 and len(uploaded_names) == 1:
            default_index = 1
        else:
            guessed = _guess_file(candidate_name, uploaded_names)
            if guessed:
                default_index = options.index(guessed)

        selected_file = st.selectbox(
            f"{candidate_name or candidate_id} · {candidate_id}",
            options,
            index=default_index,
            key=f"cv_map_{candidate_id}_{row_index}",
            help=(
                "A Drive URL may be present in the form export. Choose the corresponding uploaded PDF here. "
                "The original Drive URL is retained as source provenance."
                if source_type == "remote_url"
                else None
            ),
        )

        if selected_file != "— No CV selected —":
            mapping[row_index] = selected_file

    mapped_count = len(mapping)
    st.caption(f"{mapped_count} of {len(working_df)} application(s) currently have a CV mapped for parsing.")

    if st.button("Process applications", type="primary", width="stretch"):
        for row_index, filename in mapping.items():
            working_df.loc[row_index, "resume_filename"] = filename
            working_df.loc[row_index, "resume_source_type"] = "local_reference"

        working_df.to_csv(NORMALIZED_APPLICATIONS, index=False)

        try:
            build_profiles(NORMALIZED_APPLICATIONS)
            st.cache_data.clear()
            st.success(
                "Processing complete. Candidate profiles have been rebuilt from the imported form data and mapped CV files."
            )
            st.page_link("dashboard.py", label="Open Review Dashboard", icon="📋")
        except SystemExit:
            st.error(
                "Application validation failed. Check unsupported roles, missing required fields, or invalid Yes/No values above."
            )
        except Exception as exc:
            st.error(f"Processing failed: {exc}")
else:
    st.caption("Upload a CSV export to start the intake workflow.")

st.divider()
st.markdown("### Direct Google Forms → Drive automation")
st.write(
    "For a production recruiter workflow, the next integration is Google OAuth. The recruiter would sign in once, "
    "authorize access to the response Sheet and the Form uploads folder, and the app would retrieve new CV files directly "
    "from Google Drive before running this same parsing and scoring pipeline."
)
st.caption(
    "This requires authorization from the account that owns or can access the Form uploads. "
    "The prototype intentionally does not bypass Google Drive permissions."
)
