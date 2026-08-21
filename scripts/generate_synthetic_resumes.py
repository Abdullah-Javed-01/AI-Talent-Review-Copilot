from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


ROOT = Path(__file__).resolve().parents[1]
RESUME_DIR = ROOT / "data" / "resumes"

RESUME_DIR.mkdir(parents=True, exist_ok=True)


resumes = {
    "syn001_resume.pdf": {
        "name": "Ayesha Khan",
        "content": [
            "BS Computer Science - 7th Semester",
            "Skills: Python, Pandas, NumPy, Scikit-learn, Matplotlib, Git, GitHub, SQL",
            "Customer Churn Prediction",
            (
                "Cleaned and preprocessed customer data, handled missing values "
                "and categorical variables, trained Logistic Regression and "
                "Random Forest models, and evaluated them using accuracy, "
                "precision, recall and F1-score."
            ),
            "Student Performance Predictor",
            (
                "Performed exploratory data analysis and feature engineering, "
                "trained classification models using Scikit-learn, created a "
                "confusion matrix and classification report, and built a "
                "Streamlit prediction interface."
            ),
            "Sales Analysis",
            (
                "Used Pandas and NumPy for data cleaning and analysis, SQL for "
                "queries, and Matplotlib for visualizations."
            ),
            "Uses Git and GitHub for university and personal projects.",
        ],
    },

    "syn002_resume.pdf": {
        "name": "Hamza Ali",
        "content": [
            "BS Artificial Intelligence - 8th Semester",
            (
                "Skills: Python, Machine Learning, Deep Learning, TensorFlow, "
                "PyTorch, NLP, Computer Vision, Generative AI, LangChain, RAG, "
                "AI Agents, Hugging Face, Docker, AWS, SQL, Git, GitHub"
            ),
            "Certificates: Machine Learning, Generative AI Fundamentals, Deep Learning Basics, Prompt Engineering, AWS Fundamentals",
            "AI Chatbot",
            "Developed an AI chatbot using Python and AI technologies.",
            "Machine Learning Prediction System",
            "Built a machine learning model for prediction.",
            "Deep Learning Project",
            "Used TensorFlow to create a deep learning application.",
        ],
    },

    "syn003_resume.pdf": {
        "name": "Sara Ahmed",
        "content": [
            "BS Computer Science - 7th Semester",
            "Skills: Python, Pandas, NumPy, Scikit-learn, Matplotlib, SQL, Git, GitHub, Streamlit",
            "Loan Default Prediction System",
            (
                "Worked with approximately 8000 records. Inspected missing "
                "values and class imbalance, cleaned and transformed the data, "
                "encoded categorical variables, and performed feature selection."
            ),
            (
                "Compared Logistic Regression, Decision Tree and Random Forest "
                "using a train-test split."
            ),
            (
                "Evaluated models using accuracy, precision, recall, F1-score "
                "and ROC-AUC. Recall was prioritized because false negatives "
                "were more costly for the problem."
            ),
            (
                "Built a Streamlit interface and published the project to "
                "GitHub with documentation."
            ),
        ],
    },
}


styles = getSampleStyleSheet()


for filename, resume in resumes.items():
    path = RESUME_DIR / filename

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
    )

    story = [
        Paragraph(resume["name"], styles["Title"]),
        Spacer(1, 12),
    ]

    for item in resume["content"]:
        story.append(Paragraph(item, styles["BodyText"]))
        story.append(Spacer(1, 8))

    document.build(story)

    print(f"Created: {path.name}")