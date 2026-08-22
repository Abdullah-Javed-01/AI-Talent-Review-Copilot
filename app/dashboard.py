import json
from pathlib import Path

import pandas as pd
import streamlit as st

from decision_store import get_decision, load_decisions, save_decision
from role_rubrics import get_role_rubric

ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILE = ROOT / "data" / "processed" / "candidate_profiles.json"

st.set_page_config(
    page_title="Talent Review Copilot",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ab-bg: #050b18;
        --ab-panel: #0d1628;
        --ab-panel-2: #111c31;
        --ab-primary: #2258f5;
        --ab-primary-2: #3f7dff;
        --ab-cyan: #6bd5ff;
        --ab-border: rgba(92, 137, 255, 0.22);
        --ab-text: #f7f9ff;
        --ab-muted: #aab6d0;
    }

    .stApp {
        background:
            radial-gradient(circle at 78% -10%, rgba(54, 110, 255, 0.18), transparent 32%),
            radial-gradient(circle at 10% 12%, rgba(53, 157, 255, 0.10), transparent 28%),
            linear-gradient(180deg, #07101f 0%, var(--ab-bg) 62%, #040914 100%);
        color: var(--ab-text);
    }

    header[data-testid="stHeader"] {
        height: 38px !important;
        min-height: 38px !important;
        background: transparent !important;
        box-shadow: none !important;
        overflow: visible !important;
    }

    div[data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 1000000 !important;
        background: rgba(13, 22, 40, 0.92) !important;
        border: 1px solid rgba(92, 137, 255, 0.28) !important;
        border-radius: 9px !important;
        padding: 2px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18) !important;
        backdrop-filter: blur(8px);
    }

    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(34,88,245,0.16) 0%, rgba(13,22,40,0.98) 18%, rgba(6,12,24,0.99) 100%);
        border-right: 1px solid var(--ab-border);
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(105, 141, 255, 0.18);
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: var(--ab-text);
    }

    .ab-hero {
        position: relative;
        overflow: hidden;
        padding: 1.45rem 1.6rem 1.35rem;
        border-radius: 18px;
        border: 1px solid rgba(111, 153, 255, 0.30);
        background:
            radial-gradient(circle at 82% 15%, rgba(107,213,255,0.20), transparent 24%),
            linear-gradient(112deg, rgba(34,88,245,0.96), rgba(24,70,185,0.82) 46%, rgba(11,25,59,0.94));
        box-shadow: 0 18px 45px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }

    .ab-hero::after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -90px;
        top: -120px;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 50%;
        box-shadow:
            0 0 0 34px rgba(255,255,255,0.025),
            0 0 0 70px rgba(255,255,255,0.018);
        pointer-events: none;
    }

    .ab-eyebrow {
        font-size: 0.76rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 750;
        color: rgba(236,244,255,0.80);
        margin-bottom: 0.55rem;
    }

    .ab-title {
        margin: 0;
        font-size: clamp(2rem, 4vw, 3.25rem);
        line-height: 1.02;
        font-weight: 850;
        color: #ffffff;
    }

    .ab-subtitle {
        margin-top: 0.65rem;
        max-width: 760px;
        font-size: 1rem;
        color: rgba(240,246,255,0.86);
    }

    .ab-chip {
        display: inline-block;
        margin-top: 0.9rem;
        padding: 0.34rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.20);
        background: rgba(255,255,255,0.08);
        color: #ffffff;
        font-size: 0.76rem;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(180deg, rgba(18,30,52,0.96), rgba(10,18,33,0.97));
        border: 1px solid var(--ab-border);
        padding: 16px 18px;
        border-radius: 14px;
        box-shadow: 0 10px 26px rgba(0,0,0,0.12);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--ab-muted);
        font-size: 0.82rem;
        font-weight: 650;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid var(--ab-border);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid rgba(80,127,255,0.55);
        background: linear-gradient(180deg, rgba(34,88,245,0.95), rgba(24,69,198,0.95));
        color: #ffffff;
        box-shadow: 0 8px 20px rgba(34,88,245,0.14);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: rgba(107,213,255,0.85);
        background: linear-gradient(180deg, #2f69ff, #1d50de);
        color: #ffffff;
    }

    button[data-baseweb="tab"] {
        font-weight: 700;
        color: var(--ab-muted);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #7fb5ff;
    }

    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {
        background: rgba(7,14,28,0.92) !important;
        border: 1px solid rgba(88,128,235,0.26) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 13px;
        border: 1px solid rgba(85,136,255,0.26);
        background: rgba(20,53,104,0.40);
    }

    details {
        border-radius: 11px !important;
        border-color: rgba(88,128,235,0.20) !important;
        background: rgba(8,15,29,0.62) !important;
    }

    .candidate-kicker {
        font-size: .86rem;
        color: var(--ab-muted);
        margin-top: -.35rem;
        margin-bottom: .8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def pretty_label(value):
    if value is None:
        return "—"
    try:
        if pd.isna(value):
            return "—"
    except (TypeError, ValueError):
        pass
    return str(value).replace("_", " ").title()


def render_bullets(items, empty_message):
    if not items:
        st.caption(empty_message)
        return
    for item in items:
        st.write(f"• {pretty_label(item)}")


@st.cache_data
def load_profiles():
    with open(PROFILE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


profiles = load_profiles()
decisions = load_decisions()

rows = []
for profile in profiles:
    assessment = profile.get("assessment") or {}
    rows.append(
        {
            "Candidate ID": profile.get("candidate_id", "UNKNOWN"),
            "Name": profile.get("name", "Unknown candidate"),
            "Role": profile.get("applied_role", "—"),
            "Evidence": assessment.get("total_score"),
            "Max Score": assessment.get("max_score", 22),
            "Priority": assessment.get("technical_review_priority", "MANUAL_REVIEW"),
            "Operational": assessment.get("operational_status", "MANUAL_REVIEW"),
            "Manual Review": profile.get("manual_review_required", False),
            "Decision": decisions.get(profile.get("candidate_id"), "PENDING"),
        }
    )

df = pd.DataFrame(rows)

with st.sidebar:
    st.markdown("## Review Filters")
    st.caption("Narrow the queue without changing candidate assessments.")

    search_query = st.text_input("Search", placeholder="Name or candidate ID")

    role_options = ["All"] + sorted(df["Role"].dropna().astype(str).unique().tolist())
    selected_role = st.selectbox("Internship role", role_options)

    selected_priority = st.selectbox(
        "Technical priority",
        [
            "All",
            "PRIORITY_REVIEW",
            "GOOD_POTENTIAL",
            "DEVELOPING_PROFILE",
            "INSUFFICIENT_EVIDENCE",
            "MANUAL_REVIEW",
        ],
        format_func=pretty_label,
    )
    selected_operational = st.selectbox(
        "Operational status",
        ["All", "READY", "CONFIRM_LOCATION", "REQUIREMENT_MISMATCH", "MANUAL_REVIEW"],
        format_func=pretty_label,
    )
    selected_decision = st.selectbox(
        "Recruiter decision",
        ["All", "PENDING", "SHORTLISTED", "HOLD", "NOT_SELECTED"],
        format_func=pretty_label,
    )
    minimum_score = st.slider("Minimum evidence score", 0, 22, 0)

    st.divider()
    st.caption("Technical evidence and operational fit are intentionally separated.")

filtered_df = df.copy()

if selected_role != "All":
    filtered_df = filtered_df[filtered_df["Role"] == selected_role]
if selected_priority != "All":
    filtered_df = filtered_df[filtered_df["Priority"] == selected_priority]
if selected_operational != "All":
    filtered_df = filtered_df[filtered_df["Operational"] == selected_operational]
if selected_decision != "All":
    filtered_df = filtered_df[filtered_df["Decision"] == selected_decision]

filtered_df = filtered_df[filtered_df["Evidence"].fillna(0) >= minimum_score]

if search_query:
    query = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["Candidate ID"].astype(str).str.lower().str.contains(query, regex=False)
        | filtered_df["Name"].astype(str).str.lower().str.contains(query, regex=False)
    ]

st.markdown(
    """
    <div class="ab-hero">
        <div class="ab-eyebrow">Alphabridge-inspired · Independent prototype</div>
        <div class="ab-title">Talent Review Copilot</div>
        <div class="ab-subtitle">
            Evidence-first candidate prioritization for high-volume internship hiring.
        </div>
        <div class="ab-chip">Synthetic demo data · Human decision remains final</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("Demo environment · 100% synthetic candidate data · No real applicant information is used.")
st.caption("Inspired by a public high-volume hiring use case. This is not an official Alphabridge product.")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Applications", len(df))
m2.metric("Priority Review", int((df["Priority"] == "PRIORITY_REVIEW").sum()))
m3.metric("Good Potential", int((df["Priority"] == "GOOD_POTENTIAL").sum()))
m4.metric("Operationally Ready", int((df["Operational"] == "READY").sum()))
m5.metric("Manual Review", int(df["Manual Review"].sum()))

st.divider()

queue_tab, candidate_tab, shortlist_tab = st.tabs(
    ["Review Queue", "Candidate Profile", "Shortlist"]
)

with queue_tab:
    header_col, count_col = st.columns([4, 1])
    with header_col:
        st.subheader("Candidate Review Queue")
        st.caption("Review, filter, and prioritize internship applicants using role-specific evidence and operational fit.")
    with count_col:
        st.metric("Visible Candidates", len(filtered_df))

    if filtered_df.empty:
        st.warning("No candidates match the current filters.")
    else:
        display_df = filtered_df[
            ["Candidate ID", "Name", "Role", "Evidence", "Max Score", "Priority", "Operational", "Decision"]
        ].copy()
        display_df["Evidence"] = display_df.apply(
            lambda row: f"{int(row['Evidence'])}/{int(row['Max Score'])}"
            if pd.notna(row["Evidence"])
            else "Manual",
            axis=1,
        )
        display_df = display_df.drop(columns=["Max Score"])
        for column in ["Priority", "Operational", "Decision"]:
            display_df[column] = display_df[column].map(pretty_label)

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Export current review queue",
            data=filtered_df[
                ["Candidate ID", "Name", "Role", "Evidence", "Max Score", "Priority", "Operational", "Decision"]
            ].to_csv(index=False).encode("utf-8"),
            file_name="candidate_review_queue.csv",
            mime="text/csv",
        )

with candidate_tab:
    available_candidates = filtered_df["Candidate ID"].tolist()

    if not available_candidates:
        st.warning("No candidates match the current filters. Adjust the sidebar filters.")
    else:
        labels = {
            row["Candidate ID"]: f"{row['Name']} · {row['Role']} · {row['Candidate ID']}"
            for _, row in filtered_df.iterrows()
        }

        selected_candidate_id = st.selectbox(
            "Select candidate",
            available_candidates,
            format_func=lambda candidate_id: labels.get(candidate_id, candidate_id),
        )

        selected_profile = next(
            profile
            for profile in profiles
            if profile.get("candidate_id") == selected_candidate_id
        )

        role = selected_profile.get("applied_role", "—")
        assessment = selected_profile.get("assessment") or {}
        operational = selected_profile.get("operational") or {}
        evidence = selected_profile.get("evidence") or {}
        current_decision = get_decision(selected_candidate_id)

        manual_review = bool(
            selected_profile.get("manual_review_required")
            or not assessment
            or "technical_review_priority" not in assessment
        )

        evidence_score = assessment.get("total_score")
        max_score = assessment.get("max_score", 22)
        review_priority = assessment.get("technical_review_priority", "MANUAL_REVIEW")
        operational_status = assessment.get("operational_status", "MANUAL_REVIEW")
        operational_reason = assessment.get(
            "operational_reason",
            "This profile requires recruiter review before automated prioritization can be trusted.",
        )
        rubric_name = assessment.get("rubric_name") or (get_role_rubric(role) or {}).get("name", role)
        criteria = assessment.get("criteria") or (get_role_rubric(role) or {}).get("criteria", [])

        c1, c2, c3 = st.columns([3, 1, 2])
        with c1:
            st.subheader(selected_profile.get("name", "Unknown candidate"))
            st.markdown(
                f'<div class="candidate-kicker">{selected_profile.get("candidate_id", "—")} · '
                f'{role} · Rubric: {rubric_name}</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.metric(
                "Evidence",
                f"{evidence_score}/{max_score}" if evidence_score is not None else "Manual",
            )
        with c3:
            st.metric("Review Priority", pretty_label(review_priority))

        if manual_review:
            st.error(
                "Manual review required: "
                + selected_profile.get(
                    "manual_review_reason",
                    "The profile is missing a complete automated assessment.",
                )
            )
            resume = selected_profile.get("resume") or {}
            r1, r2, r3 = st.columns(3)
            r1.metric("Resume Status", pretty_label(resume.get("parse_status")))
            r2.metric("Current City", operational.get("current_city", "—"))
            r3.metric("Decision", pretty_label(current_decision))
        else:
            o1, o2, o3, o4 = st.columns(4)
            o1.metric("Location", operational.get("current_city", "—"))
            o2.metric("Onsite", operational.get("onsite_available", "—"))
            o3.metric("Required Shift", operational.get("shift_available", "—"))
            o4.metric("Operational", pretty_label(operational_status))
            st.caption(operational_reason)

            scores = assessment.get("scores") or {}
            score_df = pd.DataFrame(
                [
                    {
                        "Criterion": label,
                        "Score": scores.get(key, 0),
                        "Maximum": maximum,
                    }
                    for label, key, maximum in criteria
                ]
            )

            st.markdown("### Why this candidate surfaced")

            if role == "ML/AI":
                workflow = (evidence.get("machine_learning") or {}).get("workflow") or {}
                python_data = evidence.get("python") or {}
                surfaced_items = []

                if python_data.get("mentioned") and python_data.get("ecosystem_used"):
                    surfaced_items.append("Python is supported by practical project evidence.")
                elif python_data.get("mentioned"):
                    surfaced_items.append("Python is mentioned, but supporting project evidence is limited.")
                if workflow.get("model_training"):
                    surfaced_items.append("Model training evidence is present.")
                if workflow.get("model_comparison"):
                    surfaced_items.append("Model comparison evidence is present.")
                if workflow.get("evaluation"):
                    surfaced_items.append("Model evaluation evidence is present.")
                if workflow.get("evaluation_reasoning"):
                    surfaced_items.append("Evaluation reasoning is demonstrated.")
            else:
                signals = evidence.get("signals") or {}
                snippets = evidence.get("snippets") or {}
                surfaced_items = []
                for label, key, _ in criteria:
                    if snippets.get(key):
                        surfaced_items.append(f"{label} is demonstrated with contextual resume evidence.")
                    elif signals.get(key):
                        surfaced_items.append(f"{label} is mentioned, but supporting context is limited.")

            if surfaced_items:
                left, right = st.columns(2)
                midpoint = (len(surfaced_items) + 1) // 2
                with left:
                    for item in surfaced_items[:midpoint]:
                        st.write(f"✅ {item}")
                with right:
                    for item in surfaced_items[midpoint:]:
                        st.write(f"✅ {item}")
            else:
                st.caption("The resume contains limited supporting evidence for this role-specific rubric.")

            with st.expander("Role-specific evidence score breakdown"):
                st.caption(f"Rubric: {rubric_name}")
                st.dataframe(score_df, use_container_width=True, hide_index=True)

            st.markdown("### Evidence at a glance")

            if role == "ML/AI":
                e1, e2 = st.columns(2)
                machine_learning = evidence.get("machine_learning") or {}
                evaluation = evidence.get("evaluation") or {}
                ml_libraries = evidence.get("ml_libraries") or {}
                bonus = evidence.get("bonus") or {}

                with e1:
                    st.markdown("**ML Models**")
                    render_bullets(machine_learning.get("models_found", []), "No demonstrated models found.")
                    st.markdown("**Evaluation Metrics**")
                    render_bullets(evaluation.get("metrics", []), "No evaluation metrics found.")

                with e2:
                    st.markdown("**ML Libraries**")
                    render_bullets(ml_libraries.get("found", []), "No ML libraries found.")
                    st.markdown("**Additional Technologies**")
                    render_bullets(
                        bonus.get("demonstrated", []),
                        "No demonstrated additional technologies found.",
                    )
            else:
                signals = evidence.get("signals") or {}
                left, right = st.columns(2)
                for index, (label, key, _) in enumerate(criteria):
                    target = left if index % 2 == 0 else right
                    with target:
                        st.markdown(f"**{label}**")
                        render_bullets(signals.get(key, []), "No matching evidence found.")

            st.markdown("### Supporting Resume Evidence")
            st.caption(
                "These excerpts come directly from the candidate's resume. "
                "Skills and certificate lists are excluded from strong evidence excerpts."
            )

            if role == "ML/AI":
                snippets = evidence.get("snippets") or {}
                snippet_sections = [
                    ("python", "Python / Technical Usage"),
                    ("ml_workflow", "Machine Learning Workflow"),
                    ("data_handling", "Data Handling"),
                    ("evaluation", "Model Evaluation"),
                    ("git_github", "Git / GitHub"),
                    ("additional_technology", "Additional Technologies"),
                ]
            else:
                snippets = evidence.get("snippets") or {}
                snippet_sections = [(key, label) for label, key, _ in criteria]

            for key, label in snippet_sections:
                items = snippets.get(key, [])
                with st.expander(
                    f"{label} · {len(items)} evidence item(s)",
                    expanded=len(items) > 0 and key in {"ml_workflow", "evaluation", "pipelines_etl", "containers", "statistics_eda"},
                ):
                    if not items:
                        st.caption("No supporting resume evidence found.")
                    else:
                        for item in items:
                            st.markdown(f"> {item}")

        st.divider()
        st.markdown("### Recruiter Decision")

        if current_decision == "SHORTLISTED":
            st.success("This candidate is currently shortlisted.")
        elif current_decision == "HOLD":
            st.warning("This candidate is currently on hold.")
        elif current_decision == "NOT_SELECTED":
            st.info("This candidate is currently marked not selected.")
        else:
            st.caption(
                "The system organizes evidence and review priority; "
                "the final decision remains with the recruiter."
            )

        st.caption(f"Current status: {pretty_label(current_decision)}")

        d1, d2, d3 = st.columns(3)
        if d1.button(
            "Shortlist",
            key=f"shortlist_{selected_candidate_id}",
            use_container_width=True,
        ):
            save_decision(selected_candidate_id, "SHORTLISTED")
            st.rerun()

        if d2.button(
            "Hold",
            key=f"hold_{selected_candidate_id}",
            use_container_width=True,
        ):
            save_decision(selected_candidate_id, "HOLD")
            st.rerun()

        if d3.button(
            "Not Selected",
            key=f"not_selected_{selected_candidate_id}",
            use_container_width=True,
        ):
            save_decision(selected_candidate_id, "NOT_SELECTED")
            st.rerun()

with shortlist_tab:
    shortlisted = df[df["Decision"] == "SHORTLISTED"].copy()

    s1, s2 = st.columns([4, 1])
    with s1:
        st.subheader("Shortlisted Candidates")
        st.caption("A focused handoff queue for recruiter follow-up or the next interview stage.")
    with s2:
        st.metric("Shortlisted", len(shortlisted))

    if shortlisted.empty:
        st.info(
            "No candidates have been shortlisted yet. "
            "Use the Candidate Profile tab to add candidates."
        )
    else:
        shortlist_display = shortlisted[
            ["Candidate ID", "Name", "Role", "Evidence", "Max Score", "Priority", "Operational"]
        ].copy()
        shortlist_display["Evidence"] = shortlist_display.apply(
            lambda row: f"{int(row['Evidence'])}/{int(row['Max Score'])}"
            if pd.notna(row["Evidence"])
            else "Manual",
            axis=1,
        )
        shortlist_display = shortlist_display.drop(columns=["Max Score"])
        shortlist_display["Priority"] = shortlist_display["Priority"].map(pretty_label)
        shortlist_display["Operational"] = shortlist_display["Operational"].map(pretty_label)

        st.dataframe(shortlist_display, use_container_width=True, hide_index=True)

        st.download_button(
            "Export shortlist",
            data=shortlist_display.to_csv(index=False).encode("utf-8"),
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
        )
