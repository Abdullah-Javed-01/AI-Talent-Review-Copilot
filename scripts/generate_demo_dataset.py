from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]

APPLICATION_FILE = (
    ROOT
    / "data"
    / "applications"
    / "synthetic_applications.csv"
)

RESUME_DIR = ROOT / "data" / "resumes"

RESUME_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


styles = getSampleStyleSheet()


NAMES = [
    "Ayesha Khan",
    "Hamza Ali",
    "Sara Ahmed",
    "Usman Raza",
    "Hira Malik",
    "Bilal Ahmad",
    "Zainab Noor",
    "Ali Hassan",
    "Fatima Shah",
    "Daniyal Khan",
    "Maham Tariq",
    "Saad Ahmed",
    "Iqra Aslam",
    "Ahmed Raza",
    "Maryam Noor",
    "Talha Khan",
    "Anam Fatima",
    "Hassan Ali",
    "Mehwish Tariq",
    "Umer Farooq",
    "Sana Khalid",
    "Abbas Raza",
    "Areeba Khan",
    "Huzaifa Ali",
    "Laiba Ahmed",
    "Taha Malik",
    "Muneeb Hassan",
    "Amna Tariq",
    "Rafay Ahmed",
    "Noor Fatima",
]


UNIVERSITIES = [
    "University A",
    "University B",
    "University C",
    "University D",
]


def strong_resume():
    return [
        "Skills: Python, Pandas, NumPy, Scikit-learn, SQL, Git, GitHub, Streamlit",
        "Customer Churn Prediction.",
        (
            "Using Python, Pandas and NumPy, cleaned and preprocessed "
            "customer data, handled missing values and categorical "
            "variables, and performed feature engineering."
        ),
        (
            "Cleaned and preprocessed customer data, handled missing "
            "values and categorical variables, and performed feature "
            "engineering."
        ),
        (
            "Trained Logistic Regression and Random Forest models "
            "using a train-test split and compared their performance."
        ),
        (
            "Evaluated models using accuracy, precision, recall, "
            "F1-score and ROC-AUC and selected the final model based "
            "on evaluation results."
        ),
        (
            "Built a Streamlit prediction interface and published "
            "the project to GitHub with documentation."
        ),
        "Completed relevant university and personal projects.",
    ]


def deep_project_resume():
    return [
        "Skills: Python, Pandas, NumPy, Scikit-learn, Git, GitHub, SQL",
        "Loan Default Prediction System.",
        (
            "Using Python and Pandas, worked with approximately 8000 "
            "records, inspected missing values and class imbalance, "
            "encoded categorical variables and performed feature selection."
        ),
        (
            "Worked with approximately 8000 records, inspected "
            "missing values and class imbalance, encoded categorical "
            "variables and performed feature selection."
        ),
        (
            "Compared Logistic Regression, Decision Tree and Random "
            "Forest using a train-test split."
        ),
        (
            "Evaluated models using precision, recall, F1-score and "
            "ROC-AUC. Recall was prioritized because false negatives "
            "were more costly for the problem."
        ),
        (
            "Published the project to GitHub with a detailed README."
        ),
    ]


def good_resume():
    return [
        "Skills: Python, Pandas, Scikit-learn, Git, SQL",
        "Student Performance Prediction.",
        (
            "Using Python and Pandas, preprocessed student data and trained "
            "a Logistic Regression classification model using Scikit-learn."
        ),
        (
            "Preprocessed student data and trained a Logistic "
            "Regression classification model using Scikit-learn."
        ),
        (
            "Used a train-test split and evaluated the model using "
            "accuracy and a confusion matrix."
        ),
        "Completed machine learning coursework and university projects.",
    ]


def keyword_resume():
    return [
        (
            "Skills: Python, Machine Learning, TensorFlow, PyTorch, "
            "LangChain, RAG, AI Agents, AWS, Docker, SQL, Git, GitHub"
        ),
        (
            "Certificates: Machine Learning Fundamentals, Generative "
            "AI, Prompt Engineering, AWS Fundamentals"
        ),
        "AI Chatbot.",
        "Developed an AI chatbot using Python and AI technologies.",
        "Machine Learning Prediction System.",
        "Built a machine learning model for prediction.",
    ]


def beginner_resume():
    return [
        "Skills: Python, Machine Learning, Pandas",
        "Python Practice Projects.",
        (
            "Completed beginner Python exercises and learned basic "
            "data analysis using Pandas."
        ),
        (
            "Currently learning machine learning classification "
            "concepts."
        ),
    ]


def genai_resume():
    return [
        (
            "Skills: Python, Pandas, Scikit-learn, LangChain, RAG, "
            "FastAPI, Git, GitHub"
        ),
        "Document Question Answering Assistant.",
        (
            "Built a Python RAG application that retrieves document "
            "chunks and generates grounded answers."
        ),
        (
            "Also trained a Logistic Regression classifier and "
            "evaluated it using accuracy and F1-score."
        ),
        (
            "Built a FastAPI endpoint and published project code to "
            "GitHub."
        ),
    ]


ARCHETYPES = [
    strong_resume,
    strong_resume,
    deep_project_resume,
    good_resume,
    good_resume,
    keyword_resume,
    beginner_resume,
    genai_resume,
]


applications = []


for index, name in enumerate(NAMES, start=1):

    candidate_id = f"DEMO-{index:03d}"

    archetype = ARCHETYPES[
        (index - 1) % len(ARCHETYPES)
    ]

    city = "Lahore"
    onsite = "Yes"
    shift = "Yes"

    # Some operational edge cases
    if index in {8, 16, 24}:
        city = "Islamabad"

    if index in {10, 20}:
        city = "Rawalpindi"

    if index in {12, 26}:
        onsite = "No"

    if index in {18, 28}:
        shift = "No"

    semester = (
        "7th Semester"
        if index % 3 == 1
        else "8th Semester"
        if index % 3 == 2
        else "Graduated"
    )

    resume_filename = (
        f"demo_{index:03d}_resume.pdf"
    )

    # Candidate 30 intentionally points to a missing
    # resume to demonstrate manual-review handling.
    if index == 30:
        resume_filename = (
            "demo_030_missing_resume.pdf"
        )

    applications.append(
        {
            "candidate_id": candidate_id,
            "name": name,
            "email": (
                f"demo{index:03d}@example.com"
            ),
            "phone": (
                f"0300{index:07d}"
            ),
            "university": UNIVERSITIES[
                (index - 1)
                % len(UNIVERSITIES)
            ],
            "semester": semester,
            "applied_role": "ML/AI",
            "current_city": city,
            "lahore_address": (
                "Demo Lahore Address"
                if city == "Lahore"
                else ""
            ),
            "shift_available": shift,
            "onsite_available": onsite,
            "linkedin_url": (
                "https://linkedin.com/in/"
                f"demo-{index:03d}"
            ),
            "resume_filename": resume_filename,
        }
    )

    if index == 30:
        continue

    resume_path = (
        RESUME_DIR
        / resume_filename
    )

    document = SimpleDocTemplate(
        str(resume_path),
        pagesize=A4,
    )

    story = [
        Paragraph(
            name,
            styles["Title"],
        ),
        Spacer(1, 12),
        Paragraph(
            f"BS Student - {semester}",
            styles["BodyText"],
        ),
        Spacer(1, 8),
    ]

    for paragraph in archetype():

        story.append(
            Paragraph(
                paragraph,
                styles["BodyText"],
            )
        )

        story.append(
            Spacer(1, 8)
        )

    document.build(story)


df = pd.DataFrame(applications)

df.to_csv(
    APPLICATION_FILE,
    index=False,
)


print(
    f"Created {len(df)} synthetic applications."
)

print(
    f"Application CSV: {APPLICATION_FILE}"
)

print(
    f"Resume directory: {RESUME_DIR}"
)

print(
    "Candidate DEMO-030 intentionally has a "
    "missing resume for manual-review testing."
)