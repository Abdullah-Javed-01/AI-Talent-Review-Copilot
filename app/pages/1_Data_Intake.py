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
RAW_FORM_EXPORT = APPLICATION_DIR / "uploaded_form_export"
NORMALIZED_APPLICATIONS = APPLICATION_DIR / "imported_applications.csv"

APPLICATION_DIR.mkdir(parents=True, exist_ok=True)
RESUME_DIR.mkdir(parents=True, exist_ok=True)

st.title("Data Intake")
st.caption(
    "Import application responses and candidate CVs without touching the codebase. "
    "Technical evidence is extracted only after the actual CV file is available."
)

st.info(
    "Upload a Google Forms/Sheets export plus the corresponding PDF CV files. "
    "XLSX is preferred because it can preserve the original Google Drive file link as provenance."
)

with st.expander("How a real Google Form connects", expanded=False):
    st.markdown(
        """
        **Application Form** → name, email, phone, university, semester, role, city/address, shift, onsite, LinkedIn  
        **CV / Resume** → technical skills, projects, tools, model/data/deployment evidence  
        **Role rubric** → deterministic evidence score and review priority  
        **Recruiter** → shortlist, hold, or not selected

        If a Google Form file-upload answer points to Google Drive, the app preserves that link as provenance. It only parses the CV after the actual file is uploaded here or later retrieved through authorized Drive access.
        """
    )

st.subheader("1. Upload form responses")
form_file = st.file_uploader(
    "Google Forms / Google Sheets export",
    type=["csv", "xlsx"],
    help=(
        "Upload either CSV or XLSX. XLSX is recommended for Google Forms because "
        "the underlying Drive hyperlink can be preserved."
    ),
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


def _guess_file(candidate_name, form_resume_name, filenames):
    if not filenames:
        return None

    # Strongest match: the filename displayed by Google Forms/Sheets.
    form_slug = _slug(Path(str(form_resume_name)).stem) if form_resume_name else ""
    if form_slug:
        for filename in filenames:
            upload_slug = _slug(Path(filename).stem)
            if form_slug == upload_slug or form_slug in upload_slug or upload_slug in form_slug:
                return filename

    # Next: candidate name appears in the uploaded filename.
    name_slug = _slug(candidate_name)
    if name_slug:
        for filename in filenames:
            file_slug = _slug(Path(filename).stem)
            if name_slug in file_slug:
                return filename

    # Safe convenience for the single-candidate real-world test case.
    if len(filenames) == 1:
        return filenames[0]

    return None


if form_file is not None:
    suffix = Path(form_file.name).suffix.lower() or ".csv"
    raw_export_path = RAW_FORM_EXPORT.with_suffix(suffix)
    raw_export_path.write_bytes(form_file.getvalue())

    try:
        result = import_form_export(raw_export_path, NORMALIZED_APPLICATIONS)
        normalized_df = pd.read_csv(NORMALIZED_APPLICATIONS, dtype=str, keep_default_na=False)
    except Exception as exc:
        st.error(f"Could not normalize the form export: {exc}")
        st.stop()

    st.success(f"Imported {result['rows']} application response(s).")

    if result["unresolved_fields"]:
        st.warning(
            "These fields were not matched automatically: "
            + ", ".join(result["unresolved_fields"])
        )
    else:
        st.success("All expected application fields were matched automatically.")

    if result.get("drive_links_preserved", 0):
        st.caption(
            f"Preserved {result['drive_links_preserved']} Google Drive resume link(s) as source provenance."
        )

    st.markdown("#### Normalized application preview")
    preview_columns = [
        column
        for column in [
            "candidate_id",
            "name",
            "semester",
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
    for uploaded_cv in cv_files or []:
        safe_name = Path(uploaded_cv.name).name
        uploaded_names.append(safe_name)
        (RESUME_DIR / safe_name).write_bytes(uploaded_cv.getvalue())

    st.subheader("3. Match CVs to candidates")

    working_df = normalized_df.copy()
    mapping = {}

    for row_index, row in working_df.iterrows():
        candidate_id = str(row.get("candidate_id", "")).strip()
        candidate_name = str(row.get("name", "")).strip()
        form_resume_name = str(row.get("resume_display_name", "")).strip()
        current_filename = str(row.get("resume_filename", "")).strip()
        source_type = str(row.get("resume_source_type", "")).strip()

        guessed = None
        if current_filename in uploaded_names:
            guessed = current_filename
        else:
            guessed = _guess_file(candidate_name, form_resume_name, uploaded_names)

        # For an unambiguous single match, make the workflow automatic and
        # avoid stale selectbox state from a previous rerun.
        if guessed and (len(uploaded_names) == 1 or current_filename in uploaded_names):
            mapping[row_index] = guessed
            st.success(f"{candidate_name or candidate_id} → {guessed}")
            continue

        options = ["— No CV selected —"] + uploaded_names
        default_index = options.index(guessed) if guessed in uploaded_names else 0

        selected_file = st.selectbox(
            f"{candidate_name or candidate_id} · {candidate_id}",
            options,
            index=default_index,
            key=f"cv_map_{candidate_id}_{row_index}_{len(uploaded_names)}",
            help=(
                "A Drive URL is present in the form export. Choose the corresponding uploaded PDF here. "
                "The original Drive URL is retained as source provenance."
                if source_type == "remote_url"
                else None
            ),
        )

        if selected_file != "— No CV selected —":
            mapping[row_index] = selected_file

    mapped_count = len(mapping)
    st.caption(f"{mapped_count} of {len(working_df)} application(s) currently have a CV mapped for parsing.")

    can_process = mapped_count > 0
    if st.button(
        "Process applications",
        type="primary",
        width="stretch",
        disabled=not can_process,
    ):
        for row_index, filename in mapping.items():
            working_df.loc[row_index, "resume_filename"] = filename
            # Keep resume_source itself untouched so XLSX Drive provenance is preserved.
            working_df.loc[row_index, "resume_source_type"] = "local_reference"

        working_df.to_csv(NORMALIZED_APPLICATIONS, index=False)

        try:
            build_profiles(NORMALIZED_APPLICATIONS)
            st.cache_data.clear()
            st.success(
                "Processing complete. Candidate profiles were rebuilt from the imported form data and actual CV files."
            )
            st.page_link("dashboard.py", label="Open Review Dashboard", icon="📋")
        except SystemExit:
            st.error(
                "Application validation failed. Review unsupported roles, missing required fields, or invalid Yes/No values above."
            )
        except Exception as exc:
            st.error(f"Processing failed: {exc}")
else:
    st.caption("Upload a CSV or XLSX export to start the intake workflow.")

st.divider()
st.markdown("### Direct Google Forms → Drive automation")
st.write(
    "For production use, the next integration is Google OAuth. The recruiter would authorize the response Sheet "
    "and Form uploads folder once, allowing this app to retrieve CVs directly from Drive before running the same parsing and scoring pipeline."
)
st.caption(
    "The prototype does not bypass Google Drive permissions. Direct retrieval requires authorization from the account that owns or can access the Form uploads."
)
