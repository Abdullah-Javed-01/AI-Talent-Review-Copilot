from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
APPLICATION_FILE = ROOT / "data" / "applications" / "synthetic_applications.csv"
RESUME_DIR = ROOT / "data" / "resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()

NAMES = [
    "Ayesha Khan", "Hamza Ali", "Sara Ahmed", "Usman Raza", "Hira Malik",
    "Bilal Ahmad", "Zainab Noor", "Ali Hassan", "Fatima Shah", "Daniyal Khan",
    "Maham Tariq", "Saad Ahmed", "Iqra Aslam", "Ahmed Raza", "Maryam Noor",
    "Talha Khan", "Anam Fatima", "Hassan Ali", "Mehwish Tariq", "Umer Farooq",
    "Sana Khalid", "Abbas Raza", "Areeba Khan", "Huzaifa Ali", "Laiba Ahmed",
    "Taha Malik", "Muneeb Hassan", "Amna Tariq", "Rafay Ahmed", "Noor Fatima",
]

UNIVERSITIES = ["University A", "University B", "University C", "University D"]


def ml_strong():
    return [
        "Skills: Python, Pandas, NumPy, Scikit-learn, SQL, Git, GitHub, Streamlit",
        "Customer Churn Prediction.",
        "Using Python, Pandas and NumPy, cleaned and preprocessed customer data, handled missing values and categorical variables, and performed feature engineering.",
        "Trained Logistic Regression and Random Forest models using a train-test split and compared their performance.",
        "Evaluated models using accuracy, precision, recall, F1-score and ROC-AUC and selected the final model based on evaluation results.",
        "Built a Streamlit prediction interface and published the project to GitHub with documentation.",
    ]


def ml_good():
    return [
        "Skills: Python, Pandas, Scikit-learn, Git, SQL",
        "Student Performance Prediction.",
        "Using Python and Pandas, preprocessed student data and trained a Logistic Regression model using Scikit-learn.",
        "Used a train-test split and evaluated the model using accuracy and a confusion matrix.",
        "Completed machine learning coursework and university projects.",
    ]


def ml_weak():
    return [
        "Skills: Python, Machine Learning, TensorFlow, PyTorch, LangChain, RAG, AWS, Docker, SQL, Git, GitHub",
        "Certificates: Machine Learning Fundamentals, Generative AI, Prompt Engineering",
        "AI Chatbot.",
        "Developed an AI chatbot using Python and AI technologies.",
    ]


def ds_strong():
    return [
        "Skills: Python, Pandas, NumPy, SQL, Scikit-learn, Matplotlib, Seaborn, Git",
        "Retail Customer Analytics Project.",
        "Used Python and SQL to query, clean and analyze customer transaction data with missing values and outliers.",
        "Performed exploratory data analysis, correlation analysis and statistical summaries before feature engineering.",
        "Built and evaluated classification models using accuracy, precision, recall and F1-score.",
        "Created visualizations and an interactive dashboard using Matplotlib and Plotly.",
        "Published the project to GitHub with documentation.",
    ]


def ds_good():
    return [
        "Skills: Python, Pandas, SQL, Matplotlib, Scikit-learn",
        "Sales Analysis Project.",
        "Used Python and Pandas to clean sales data and performed exploratory data analysis.",
        "Queried records using SQL and created visualizations with Matplotlib.",
        "Built a regression model and evaluated it using common metrics.",
    ]


def ds_weak():
    return [
        "Skills: Python, Data Science, Pandas, SQL, Tableau, Machine Learning",
        "Certificates: Data Science Foundations, SQL Basics",
        "Completed beginner exercises in Python and data analysis.",
    ]


def de_strong():
    return [
        "Skills: Python, SQL, PostgreSQL, Airflow, Docker, AWS, Git, GitHub",
        "Batch Data Pipeline Project.",
        "Built a Python ETL pipeline that ingested CSV and API data into PostgreSQL.",
        "Designed normalized database schemas and implemented data validation before loading records.",
        "Orchestrated scheduled pipeline jobs with Airflow and containerized the workflow with Docker.",
        "Used AWS cloud storage for pipeline inputs and documented the project on GitHub.",
    ]


def de_good():
    return [
        "Skills: Python, SQL, PostgreSQL, Git, Docker",
        "Data Ingestion Project.",
        "Built a Python pipeline to extract and transform CSV data before loading it into PostgreSQL.",
        "Designed a relational schema and queried the database using SQL.",
        "Published the project to GitHub.",
    ]


def de_weak():
    return [
        "Skills: Python, SQL, Database, AWS, Spark, Airflow",
        "Certificates: SQL Fundamentals, Cloud Basics",
        "Completed coursework covering databases and data engineering concepts.",
    ]


def devops_strong():
    return [
        "Skills: Linux, Bash, Git, GitHub, Docker, Kubernetes, GitHub Actions, AWS, Nginx, Prometheus, Grafana",
        "Containerized Deployment Project.",
        "Containerized a web application with Docker and configured Docker Compose for local services.",
        "Created a GitHub Actions CI/CD pipeline to run tests and automate deployment.",
        "Deployed the application to AWS, configured Nginx as a reverse proxy, and used HTTPS.",
        "Monitored application metrics with Prometheus and Grafana and documented the project on GitHub.",
    ]


def devops_good():
    return [
        "Skills: Linux, Bash, Git, Docker, GitHub Actions, AWS",
        "Deployment Automation Project.",
        "Used Linux and Bash scripts to automate application setup.",
        "Containerized the application with Docker and created a GitHub Actions pipeline.",
        "Deployed the project to an AWS virtual machine and published configuration to GitHub.",
    ]


def devops_weak():
    return [
        "Skills: Linux, Docker, AWS, Kubernetes, Git, Jenkins",
        "Certificates: DevOps Fundamentals, AWS Cloud Basics",
        "Completed beginner Linux and Docker coursework.",
    ]


ROLE_PLAN = [
    ("ML/AI", ml_strong), ("ML/AI", ml_strong), ("ML/AI", ml_good),
    ("ML/AI", ml_good), ("ML/AI", ml_weak), ("ML/AI", ml_weak),
    ("ML/AI", ml_strong), ("ML/AI", ml_good),

    ("Data Science", ds_strong), ("Data Science", ds_strong),
    ("Data Science", ds_good), ("Data Science", ds_good),
    ("Data Science", ds_weak), ("Data Science", ds_strong),
    ("Data Science", ds_good), ("Data Science", ds_weak),

    ("Data Engineering", de_strong), ("Data Engineering", de_strong),
    ("Data Engineering", de_good), ("Data Engineering", de_good),
    ("Data Engineering", de_weak), ("Data Engineering", de_strong),
    ("Data Engineering", de_good),

    ("DevOps", devops_strong), ("DevOps", devops_strong),
    ("DevOps", devops_good), ("DevOps", devops_good),
    ("DevOps", devops_weak), ("DevOps", devops_strong),
    ("DevOps", devops_good),
]

applications = []

for index, name in enumerate(NAMES, start=1):
    candidate_id = f"DEMO-{index:03d}"
    role, archetype = ROLE_PLAN[index - 1]

    city = "Lahore"
    onsite = "Yes"
    shift = "Yes"

    if index in {8, 16, 24}:
        city = "Islamabad"
    if index in {10, 20}:
        city = "Rawalpindi"
    if index in {12, 26}:
        onsite = "No"
    if index in {18, 28}:
        shift = "No"

    semester = (
        "7th Semester" if index % 3 == 1
        else "8th Semester" if index % 3 == 2
        else "Graduated"
    )

    resume_filename = f"demo_{index:03d}_resume.pdf"
    if index == 30:
        resume_filename = "demo_030_missing_resume.pdf"

    applications.append(
        {
            "candidate_id": candidate_id,
            "name": name,
            "email": f"demo{index:03d}@example.com",
            "phone": f"0300{index:07d}",
            "university": UNIVERSITIES[(index - 1) % len(UNIVERSITIES)],
            "semester": semester,
            "applied_role": role,
            "current_city": city,
            "lahore_address": "Demo Lahore Address" if city == "Lahore" else "",
            "shift_available": shift,
            "onsite_available": onsite,
            "linkedin_url": f"https://linkedin.com/in/demo-{index:03d}",
            "resume_filename": resume_filename,
        }
    )

    if index == 30:
        continue

    resume_path = RESUME_DIR / resume_filename
    document = SimpleDocTemplate(str(resume_path), pagesize=A4)
    story = [
        Paragraph(name, styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Applicant for {role} Intern · {semester}", styles["BodyText"]),
        Spacer(1, 8),
    ]

    for paragraph in archetype():
        story.append(Paragraph(paragraph, styles["BodyText"]))
        story.append(Spacer(1, 8))

    document.build(story)

pd.DataFrame(applications).to_csv(APPLICATION_FILE, index=False)

print(f"Created {len(applications)} synthetic applications across 4 technical tracks.")
print("Tracks: ML/AI, Data Science, Data Engineering, DevOps")
print(f"Application CSV: {APPLICATION_FILE}")
print(f"Resume directory: {RESUME_DIR}")
print("Candidate DEMO-030 intentionally has a missing resume for manual-review testing.")
