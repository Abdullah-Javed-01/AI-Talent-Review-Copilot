import json
from pathlib import Path

import pandas as pd
import streamlit as st

from decision_store import get_decision, load_decisions, save_decision

ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILE = ROOT / "data" / "processed" / "candidate_profiles.json"

st.set_page_config(
    page_title="Talent Review Copilot",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '''
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1480px;}
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.035);
        border: 1px solid rgba(128,128,128,.22);
        padding: 15px 17px;
        border-radius: 12px;
    }
    div[data-testid="stDataFrame"] {border-radius: 12px; overflow: hidden;}
    .stButton > button, .stDownloadButton > button {
        border-radius: 9px;
        min-height: 42px;
        font-weight: 600;
    }
    button[data-baseweb="tab"] {font-weight: 650;}
    section[data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.18);}
    .prototype-chip {
        display:inline-block; padding:.28rem .62rem;
        border:1px solid rgba(128,128,128,.32);
        border-radius:999px; font-size:.78rem; font-weight:650; opacity:.82;
        margin-top:.35rem;
    }
    .candidate-kicker {font-size:.86rem; opacity:.72; margin-top:-.35rem; margin-bottom:.8rem;}
    </style>
    ''',
    unsafe_allow_html=True,
)


def pretty_label(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
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
    assessment = profile.get("assessment", {})
    rows.append(
        {
            "Candidate ID": profile["candidate_id"],
            "Name": profile["name"],
            "Role": profile["applied_role"],
            "Evidence": assessment.get("total_score"),
            "Priority": assessment.get("technical_review_priority", "MANUAL_REVIEW"),
            "Operational": assessment.get("operational_status", "MANUAL_REVIEW"),
            "Manual Review": profile.get("manual_review_required", False),
            "Decision": decisions.get(profile["candidate_id"], "PENDING"),
        }
    )

df = pd.DataFrame(rows)

with st.sidebar:
    st.markdown("## Review Filters")
    st.caption("Narrow the queue without changing candidate assessments.")

    search_query = st.text_input("Search candidates", placeholder="Name or candidate ID")
    selected_priority = st.selectbox(
        "Technical priority",
        ["All", "PRIORITY_REVIEW", "GOOD_POTENTIAL", "DEVELOPING_PROFILE",
         "INSUFFICIENT_EVIDENCE", "MANUAL_REVIEW"],
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
    st.caption(
        "Technical evidence and operational fit are intentionally separated."
    )

filtered_df = df.copy()

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
        filtered_df["Candidate ID"].str.lower().str.contains(query, regex=False)
        | filtered_df["Name"].str.lower().str.contains(query, regex=False)
    ]

title_col, badge_col = st.columns([5, 1])

with title_col:
    st.title("Talent Review Copilot")
    st.caption("Evidence-first candidate prioritization for high-volume internship hiring.")

with badge_col:
    st.markdown(
        '<div class="prototype-chip">Independent Prototype</div>',
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
        st.caption("Prioritize strong evidence matches, then verify the supporting resume evidence.")
    with count_col:
        st.metric("Visible Candidates", len(filtered_df))

    if filtered_df.empty:
        st.warning("No candidates match the current filters.")
    else:
        display_df = filtered_df[
            ["Candidate ID", "Name", "Role", "Evidence", "Priority", "Operational", "Decision"]
        ].copy()
        display_df["Evidence"] = display_df["Evidence"].apply(
            lambda value: f"{int(value)}/22" if pd.notna(value) else "Manual"
        )
        for column in ["Priority", "Operational", "Decision"]:
            display_df[column] = display_df[column].map(pretty_label)

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Export current review queue",
            data=filtered_df[
                ["Candidate ID", "Name", "Role", "Evidence", "Priority", "Operational", "Decision"]
            ].to_csv(index=False).encode("utf-8"),
            file_name="candidate_review_queue.csv",
            mime="text/csv",
        )

with candidate_tab:
    available_candidates = filtered_df["Candidate ID"].tolist()

    if not available_candidates:
        st.warning("No candidates match the current filters. Adjust the filters in the sidebar.")
    else:
        labels = {
            row["Candidate ID"]: f"{row['Name']} · {row['Candidate ID']}"
            for _, row in filtered_df.iterrows()
        }
        selected_candidate_id = st.selectbox(
            "Select candidate",
            available_candidates,
            format_func=lambda candidate_id: labels[candidate_id],
        )

        selected_profile = next(
            profile for profile in profiles
            if profile["candidate_id"] == selected_candidate_id
        )
        assessment = selected_profile.get("assessment")
        operational = selected_profile.get("operational", {})
        current_decision = get_decision(selected_candidate_id)

        c1, c2, c3 = st.columns([3, 1, 2])
        with c1:
            st.subheader(selected_profile["name"])
            st.markdown(
                f'<div class="candidate-kicker">{selected_profile["candidate_id"]} · '
                f'{selected_profile["applied_role"]} Intern</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.metric("Evidence", f"{assessment['total_score']}/22" if assessment else "Manual")
        with c3:
            st.metric(
                "Review Priority",
                pretty_label(assessment["technical_review_priority"]) if assessment else "Manual Review",
            )

        if selected_profile.get("manual_review_required"):
            st.error(
                "Manual review required: "
                + selected_profile.get("manual_review_reason", "Resume could not be processed.")
            )
            resume = selected_profile.get("resume", {})
            r1, r2, r3 = st.columns(3)
            r1.metric("Resume Status", pretty_label(resume.get("parse_status")))
            r2.metric("Current City", operational.get("current_city", "—"))
            r3.metric("Decision", pretty_label(current_decision))
        else:
            o1, o2, o3, o4 = st.columns(4)
            o1.metric("Location", operational.get("current_city", "—"))
            o2.metric("Onsite", operational.get("onsite_available", "—"))
            o3.metric("Required Shift", operational.get("shift_available", "—"))
            o4.metric("Operational", pretty_label(assessment["operational_status"]))
            st.caption(assessment["operational_reason"])

            evidence = selected_profile["evidence"]
            workflow = evidence["machine_learning"]["workflow"]
            python_data = evidence["python"]

            st.markdown("### Why this candidate surfaced")
            surfaced_items = []

            if python_data["mentioned"] and python_data["ecosystem_used"]:
                surfaced_items.append("Python is supported by practical project evidence.")
            elif python_data["mentioned"]:
                surfaced_items.append("Python is mentioned, but supporting project evidence is limited.")
            if workflow["model_training"]:
                surfaced_items.append("Model training evidence is present.")
            if workflow["model_comparison"]:
                surfaced_items.append("Model comparison evidence is present.")
            if workflow["evaluation"]:
                surfaced_items.append("Model evaluation evidence is present.")
            if workflow["evaluation_reasoning"]:
                surfaced_items.append("Evaluation reasoning is demonstrated.")

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
                st.caption("The resume contains limited supporting evidence for this rubric.")

            scores = assessment["scores"]
            score_df = pd.DataFrame(
                [
                    {"Criterion": "Python", "Score": scores["python"], "Maximum": 3},
                    {"Criterion": "ML Fundamentals", "Score": scores["ml_fundamentals"], "Maximum": 3},
                    {"Criterion": "Project Evidence", "Score": scores["project_evidence"], "Maximum": 3},
                    {"Criterion": "Data Handling", "Score": scores["data_handling"], "Maximum": 3},
                    {"Criterion": "Model Evaluation", "Score": scores["model_evaluation"], "Maximum": 2},
                    {"Criterion": "ML Libraries", "Score": scores["ml_libraries"], "Maximum": 2},
                    {"Criterion": "Git / GitHub", "Score": scores["git_github"], "Maximum": 2},
                    {"Criterion": "Practical Exposure", "Score": scores["practical_exposure"], "Maximum": 2},
                    {"Criterion": "Bonus Exposure", "Score": scores["bonus_exposure"], "Maximum": 2},
                ]
            )

            with st.expander("Evidence score breakdown"):
                st.dataframe(score_df, use_container_width=True, hide_index=True)

            st.markdown("### Evidence at a glance")
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("**ML Models**")
                render_bullets(
                    evidence["machine_learning"]["models_found"],
                    "No demonstrated models found.",
                )
                st.markdown("**Evaluation Metrics**")
                render_bullets(
                    evidence["evaluation"]["metrics"],
                    "No evaluation metrics found.",
                )
            with e2:
                st.markdown("**ML Libraries**")
                render_bullets(evidence["ml_libraries"]["found"], "No ML libraries found.")
                st.markdown("**Additional Technologies**")
                render_bullets(
                    evidence["bonus"]["demonstrated"],
                    "No demonstrated additional technologies found.",
                )

            st.markdown("### Supporting Resume Evidence")
            st.caption(
                "These excerpts come directly from the candidate's resume. "
                "Skills and certificate lists are excluded from strong evidence excerpts."
            )

            snippets = evidence.get("snippets", {})
            snippet_sections = [
                ("python", "Python / Technical Usage"),
                ("ml_workflow", "Machine Learning Workflow"),
                ("data_handling", "Data Handling"),
                ("evaluation", "Model Evaluation"),
                ("git_github", "Git / GitHub"),
                ("additional_technology", "Additional Technologies"),
            ]

            for key, label in snippet_sections:
                items = snippets.get(key, [])
                with st.expander(
                    f"{label} · {len(items)} evidence item(s)",
                    expanded=key in {"ml_workflow", "evaluation"},
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

        st.caption(f"Current status: **{pretty_label(current_decision)}**")

        d1, d2, d3 = st.columns(3)
        if d1.button("Shortlist", key=f"shortlist_{selected_candidate_id}", use_container_width=True):
            save_decision(selected_candidate_id, "SHORTLISTED")
            st.rerun()
        if d2.button("Hold", key=f"hold_{selected_candidate_id}", use_container_width=True):
            save_decision(selected_candidate_id, "HOLD")
            st.rerun()
        if d3.button("Not Selected", key=f"not_selected_{selected_candidate_id}", use_container_width=True):
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
            ["Candidate ID", "Name", "Role", "Evidence", "Priority", "Operational"]
        ].copy()
        shortlist_display["Evidence"] = shortlist_display["Evidence"].apply(
            lambda value: f"{int(value)}/22" if pd.notna(value) else "Manual"
        )
        shortlist_display["Priority"] = shortlist_display["Priority"].map(pretty_label)
        shortlist_display["Operational"] = shortlist_display["Operational"].map(pretty_label)

        st.dataframe(shortlist_display, use_container_width=True, hide_index=True)

        st.download_button(
            "Export shortlist",
            data=shortlist_display.to_csv(index=False).encode("utf-8"),
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
        )
