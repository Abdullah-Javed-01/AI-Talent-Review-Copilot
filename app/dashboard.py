import json
from pathlib import Path

import pandas as pd
import streamlit as st

from decision_store import (
    get_decision,
    load_decisions,
    save_decision,
)


ROOT = Path(__file__).resolve().parents[1]

PROFILE_FILE = (
    ROOT
    / "data"
    / "processed"
    / "candidate_profiles.json"
)


st.set_page_config(
    page_title="Talent Review Copilot",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data
def load_profiles():
    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


profiles = load_profiles()
decisions = load_decisions()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("Talent Review Copilot")

st.caption(
    "Evidence-based applicant review for high-volume internship hiring."
)

st.info(
    "Demo environment — all candidates and application data shown here "
    "are synthetic."
)

st.caption(
    "Independent prototype inspired by a public high-volume hiring use case. "
    "Not an official Alphabridge product and no real applicant data is used."
)

# --------------------------------------------------
# Convert profiles to table
# --------------------------------------------------

rows = []

for profile in profiles:

    assessment = profile.get("assessment", {})

    rows.append(
        {
            "Candidate ID": profile["candidate_id"],
            "Name": profile["name"],
            "Role": profile["applied_role"],
            "Score": assessment.get("total_score"),
            "Priority": assessment.get(
                "technical_review_priority",
                "MANUAL_REVIEW",
            ),
            "Operational": assessment.get(
                "operational_status",
                "MANUAL_REVIEW",
            ),
            "Manual Review": profile.get(
                "manual_review_required",
                False,
            ),
            "Decision": decisions.get(
                profile["candidate_id"],
                "PENDING",
            ),
        }
    )


df = pd.DataFrame(rows)


# --------------------------------------------------
# Top metrics
# --------------------------------------------------

total_candidates = len(df)

priority_count = (
    df["Priority"] == "PRIORITY_REVIEW"
).sum()

good_potential_count = (
    df["Priority"] == "GOOD_POTENTIAL"
).sum()

manual_review_count = df["Manual Review"].sum()

ready_count = (
    df["Operational"] == "READY"
).sum()


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Applications",
    total_candidates,
)

col2.metric(
    "Priority Review",
    int(priority_count),
)

col3.metric(
    "Good Potential",
    int(good_potential_count),
)

col4.metric(
    "Operationally Ready",
    int(ready_count),
)

col5.metric(
    "Manual Review",
    int(manual_review_count),
)


st.divider()


# --------------------------------------------------
# Filters
# --------------------------------------------------

st.subheader("Candidate Review Queue")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)


with filter_col1:

    priority_options = [
        "All",
        "PRIORITY_REVIEW",
        "GOOD_POTENTIAL",
        "DEVELOPING_PROFILE",
        "INSUFFICIENT_EVIDENCE",
        "MANUAL_REVIEW",
    ]

    selected_priority = st.selectbox(
        "Review priority",
        priority_options,
    )


with filter_col2:

    operational_options = [
        "All",
        "READY",
        "CONFIRM_LOCATION",
        "REQUIREMENT_MISMATCH",
        "MANUAL_REVIEW",
    ]

    selected_operational = st.selectbox(
        "Operational status",
        operational_options,
    )


with filter_col3:

    minimum_score = st.slider(
        "Minimum evidence score",
        min_value=0,
        max_value=22,
        value=0,
    )

with filter_col4:
    selected_decision = st.selectbox(
    "Recruiter decision",
    [
        "All",
        "PENDING",
        "SHORTLISTED",
        "HOLD",
        "NOT_SELECTED",
    ],
)

filtered_df = df.copy()


if selected_priority != "All":

    filtered_df = filtered_df[
        filtered_df["Priority"]
        == selected_priority
    ]


if selected_operational != "All":

    filtered_df = filtered_df[
        filtered_df["Operational"]
        == selected_operational
    ]
    
if selected_decision != "All":
    filtered_df = filtered_df[
        filtered_df["Decision"]
        == selected_decision
    ]


filtered_df = filtered_df[
    (
        filtered_df["Score"].fillna(0)
        >= minimum_score
    )
]

search_query = st.text_input(
    "Search candidate",
    placeholder="Search by candidate ID or name...",
)

if search_query:
    query = search_query.strip().lower()

    filtered_df = filtered_df[
        filtered_df["Candidate ID"]
        .str.lower()
        .str.contains(query)
        |
        filtered_df["Name"]
        .str.lower()
        .str.contains(query)
    ]

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Export filtered queue
# --------------------------------------------------

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "Export current review queue",
    data=csv_data,
    file_name="candidate_review_queue.csv",
    mime="text/csv",
)


st.divider()


# --------------------------------------------------
# Candidate detail
# --------------------------------------------------

st.subheader("Candidate Evidence")

available_candidates = (
    filtered_df["Candidate ID"].tolist()
)


if not available_candidates:

    st.warning(
        "No candidates match the current filters."
    )

else:

    selected_candidate_id = st.selectbox(
        "Select candidate",
        available_candidates,
    )


    selected_profile = next(
        profile
        for profile in profiles
        if profile["candidate_id"]
        == selected_candidate_id
    )


    assessment = selected_profile.get(
        "assessment"
    )


    if selected_profile.get(
        "manual_review_required"
    ):

        st.error(
            "Manual review required: "
            + selected_profile.get(
                "manual_review_reason",
                "Resume could not be processed.",
            )
        )

    else:

        # ------------------------------------------
        # Candidate summary
        # ------------------------------------------

        name_col, score_col, priority_col = st.columns(
            [2, 1, 2]
        )


        with name_col:

            st.markdown(
                f"### {selected_profile['name']}"
            )

            st.write(
                f"**Candidate ID:** "
                f"{selected_profile['candidate_id']}"
            )

            st.write(
                f"**Applied Role:** "
                f"{selected_profile['applied_role']}"
            )


        with score_col:

            st.metric(
                "Evidence Score",
                f"{assessment['total_score']}/22",
            )


        with priority_col:

            st.write("**Review Priority**")

            st.success(
                assessment[
                    "technical_review_priority"
                ].replace("_", " ")
            )


        # ------------------------------------------
        # Operational status
        # ------------------------------------------

        st.markdown("#### Operational Fit")

        operational = selected_profile[
            "operational"
        ]


        op_col1, op_col2, op_col3 = st.columns(3)

        op_col1.write(
            f"**Current City:** "
            f"{operational['current_city']}"
        )

        op_col2.write(
            f"**Onsite:** "
            f"{operational['onsite_available']}"
        )

        op_col3.write(
            f"**Required Shift:** "
            f"{operational['shift_available']}"
        )


        st.write(
            f"**Status:** "
            f"{assessment['operational_status']}"
        )

        st.caption(
            assessment["operational_reason"]
        )


        # ------------------------------------------
        # Score breakdown
        # ------------------------------------------

        st.markdown("#### Technical Evidence")

        scores = assessment["scores"]


        score_rows = [
            {
                "Criterion": "Python",
                "Score": scores["python"],
                "Maximum": 3,
            },
            {
                "Criterion": "ML Fundamentals",
                "Score": scores[
                    "ml_fundamentals"
                ],
                "Maximum": 3,
            },
            {
                "Criterion": "Project Evidence",
                "Score": scores[
                    "project_evidence"
                ],
                "Maximum": 3,
            },
            {
                "Criterion": "Data Handling",
                "Score": scores[
                    "data_handling"
                ],
                "Maximum": 3,
            },
            {
                "Criterion": "Model Evaluation",
                "Score": scores[
                    "model_evaluation"
                ],
                "Maximum": 2,
            },
            {
                "Criterion": "ML Libraries",
                "Score": scores[
                    "ml_libraries"
                ],
                "Maximum": 2,
            },
            {
                "Criterion": "Git / GitHub",
                "Score": scores[
                    "git_github"
                ],
                "Maximum": 2,
            },
            {
                "Criterion": "Practical Exposure",
                "Score": scores[
                    "practical_exposure"
                ],
                "Maximum": 2,
            },
            {
                "Criterion": "Bonus Exposure",
                "Score": scores[
                    "bonus_exposure"
                ],
                "Maximum": 2,
            },
        ]


        score_df = pd.DataFrame(
            score_rows
        )


        st.dataframe(
            score_df,
            use_container_width=True,
            hide_index=True,
        )


        # ------------------------------------------
        # Evidence
        # ------------------------------------------

        evidence = selected_profile["evidence"]


        st.markdown("#### Evidence Found")


        evidence_col1, evidence_col2 = st.columns(2)


        with evidence_col1:

            st.write("**ML Models**")

            models = evidence[
                "machine_learning"
            ]["models_found"]

            if models:
                for model in models:
                    st.write(f"- {model}")
            else:
                st.write(
                    "No demonstrated models found."
                )


            st.write("**Evaluation Metrics**")

            metrics = evidence[
                "evaluation"
            ]["metrics"]

            if metrics:
                for metric in metrics:
                    st.write(f"- {metric}")
            else:
                st.write(
                    "No evaluation metrics found."
                )


        with evidence_col2:

            st.write("**ML Libraries**")

            libraries = evidence[
                "ml_libraries"
            ]["found"]

            if libraries:
                for library in libraries:
                    st.write(f"- {library}")
            else:
                st.write(
                    "No ML libraries found."
                )


            st.write("**Additional Technologies**")

            bonus = evidence[
                "bonus"
            ]["demonstrated"]

            if bonus:
                for technology in bonus:
                    st.write(
                        f"- {technology}"
                    )
            else:
                st.write(
                    "No demonstrated bonus "
                    "technologies found."
                )
                
        st.markdown("#### Supporting Resume Evidence")

        st.caption(
            "These excerpts come directly from the candidate's resume. "
            "Skills and certificate lists are excluded from strong evidence excerpts."
        )


        snippets = evidence.get(
            "snippets",
            {},
        )


        snippet_sections = [
            (
                "python",
                "Python / Technical Usage",
            ),
            (
                "ml_workflow",
                "Machine Learning Workflow",
            ),
            (
                "data_handling",
                "Data Handling",
            ),
            (
                "evaluation",
                "Model Evaluation",
            ),
            (
                "git_github",
                "Git / GitHub",
            ),
            (
                "additional_technology",
                "Additional Technologies",
            ),
        ]


        for key, label in snippet_sections:

            items = snippets.get(
                key,
                [],
            )

            with st.expander(
                f"{label} ({len(items)} evidence item(s))",
                expanded=key in [
                    "ml_workflow",
                    "evaluation",
                ],
            ):

                if not items:

                    st.write(
                        "No supporting resume evidence found."
                    )

                else:

                    for item in items:

                        st.markdown(
                            f"> {item}"
                        )

        # ------------------------------------------
        # Evidence strength
        # ------------------------------------------

        st.markdown(
            "#### Evidence Interpretation"
        )


        python_data = evidence["python"]

        if (
            python_data["mentioned"]
            and python_data["ecosystem_used"]
        ):
            st.write(
                "✅ Python is supported by "
                "practical project evidence."
            )

        elif python_data["mentioned"]:
            st.write(
                "⚠️ Python is mentioned but "
                "has limited supporting evidence."
            )

        else:
            st.write(
                "❌ No Python evidence found."
            )


        workflow = evidence[
            "machine_learning"
        ]["workflow"]


        if workflow["model_training"]:
            st.write(
                "✅ Model training evidence found."
            )

        if workflow["model_comparison"]:
            st.write(
                "✅ Model comparison evidence found."
            )

        if workflow["evaluation"]:
            st.write(
                "✅ Model evaluation evidence found."
            )

        if workflow["evaluation_reasoning"]:
            st.write(
                "✅ Evaluation reasoning found."
            )


        # ------------------------------------------
        # Human decision placeholder
        # ------------------------------------------

        st.markdown("#### Recruiter Decision")

        st.caption(
            "AI organizes evidence and review priority. "
            "The final decision remains with the recruiter."
        )

        decision_col1, decision_col2, decision_col3 = (
            st.columns(3)
        )

        current_decision = get_decision(
            selected_candidate_id
        )

        st.write(
            f"**Current Decision:** "
            f"{current_decision.replace('_', ' ').title()}"
        )


        decision_col1, decision_col2, decision_col3 = (
            st.columns(3)
        )


        if decision_col1.button(
            "Shortlist",
            key=f"shortlist_{selected_candidate_id}",
            use_container_width=True,
        ):

            save_decision(
                selected_candidate_id,
                "SHORTLISTED",
            )

            st.success(
                "Candidate moved to Shortlist."
            )

            st.rerun()


        if decision_col2.button(
            "Hold",
            key=f"hold_{selected_candidate_id}",
            use_container_width=True,
        ):

            save_decision(
                selected_candidate_id,
                "HOLD",
            )

            st.info(
                "Candidate placed on Hold."
            )

            st.rerun()


        if decision_col3.button(
            "Not Selected",
            key=f"reject_{selected_candidate_id}",
            use_container_width=True,
        ):

            save_decision(
                selected_candidate_id,
                "NOT_SELECTED",
            )

            st.warning(
                "Candidate marked Not Selected."
            )

            st.rerun()