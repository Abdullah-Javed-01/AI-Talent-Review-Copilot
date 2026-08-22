import re


MODEL_NAMES = [
    "logistic regression",
    "decision tree",
    "random forest",
    "svm",
    "support vector machine",
    "naive bayes",
    "knn",
    "linear regression",
    "xgboost",
]

METRICS = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "f1-score",
    "roc-auc",
    "roc auc",
]

ML_LIBRARIES = [
    "scikit-learn",
    "sklearn",
    "tensorflow",
    "pytorch",
    "keras",
]

BONUS_TECH = [
    "sql",
    "streamlit",
    "fastapi",
    "flask",
    "docker",
    "aws",
    "azure",
    "gcp",
    "cloud",
    "generative ai",
    "genai",
    "rag",
    "langchain",
    "hugging face",
]

# Section headings that should never count as demonstrated evidence by
# themselves. Terms in these sections can still count as resume mentions via
# the full normalized text, but they are excluded from contextual/body proof.
EXCLUDED_SECTION_HEADINGS = {
    "skills",
    "technical skills",
    "core skills",
    "technologies",
    "tools",
    "certifications",
    "certificates",
    "licenses & certifications",
    "licenses and certifications",
}

# Common headings used to tell the parser when an excluded section has ended.
BODY_SECTION_HEADINGS = {
    "professional summary",
    "summary",
    "profile",
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "projects",
    "selected projects",
    "project experience",
    "education",
    "leadership",
    "leadership & awards",
    "leadership and awards",
    "awards",
    "achievements",
    "research",
    "publications",
    "volunteering",
}


def contains_any(text, terms):
    return any(term in text for term in terms)


def _normalized_heading(line):
    heading = re.sub(r"[^a-z0-9& ]+", "", line.lower()).strip()
    return re.sub(r"\s+", " ", heading)


def _is_heading(line, candidates):
    normalized = _normalized_heading(line)
    return normalized in candidates


def split_resume_sections(text):
    skills_lines = []
    certificate_lines = []
    body_lines = []
    excluded_section = None

    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        lowered = cleaned.lower()

        # Inline forms such as "Skills: Python, SQL" remain supported.
        if lowered.startswith("skills:") or lowered.startswith("technical skills:"):
            skills_lines.append(lowered)
            excluded_section = None
            continue

        if lowered.startswith("certificates:") or lowered.startswith("certifications:"):
            certificate_lines.append(lowered)
            excluded_section = None
            continue

        if _is_heading(cleaned, EXCLUDED_SECTION_HEADINGS):
            normalized_heading = _normalized_heading(cleaned)
            excluded_section = "certificates" if "certif" in normalized_heading or "license" in normalized_heading else "skills"
            continue

        if _is_heading(cleaned, BODY_SECTION_HEADINGS):
            excluded_section = None
            body_lines.append(lowered)
            continue

        if excluded_section == "skills":
            skills_lines.append(lowered)
            continue

        if excluded_section == "certificates":
            certificate_lines.append(lowered)
            continue

        body_lines.append(lowered)

    return {
        "skills": " ".join(skills_lines).strip(),
        "certificates": " ".join(certificate_lines).strip(),
        "body": " ".join(body_lines),
    }


def extract_body_sentences(text):
    # Reuse the same section-aware body filtering used for scoring so evidence
    # snippets cannot accidentally come from a skills or certification list.
    body_text = split_resume_sections(text)["body"]

    body_text = re.sub(
        r"\s+",
        " ",
        body_text,
    ).strip()

    sentences = re.split(
        r"(?<=[.!?])\s+",
        body_text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def find_evidence_snippets(
    sentences,
    terms,
    limit=4,
):
    matches = []

    action_terms = [
        "built",
        "developed",
        "trained",
        "used",
        "cleaned",
        "preprocessed",
        "performed",
        "compared",
        "evaluated",
        "implemented",
        "created",
        "published",
        "worked",
        "encoded",
        "selected",
        "designed",
        "deployed",
        "analyzed",
    ]

    for sentence in sentences:
        lowered = sentence.lower()

        has_topic = any(
            term in lowered
            for term in terms
        )

        has_action = any(
            action in lowered
            for action in action_terms
        )

        if has_topic and has_action:
            matches.append(sentence)

        if len(matches) >= limit:
            break

    return matches


def extract_evidence(resume_text):
    normalized = re.sub(
        r"\s+",
        " ",
        resume_text.lower(),
    ).strip()

    sections = split_resume_sections(resume_text)

    sentences = extract_body_sentences(
        resume_text
    )

    skills = sections["skills"]
    certificates = sections["certificates"]
    body = sections["body"]

    models_found = [
        model
        for model in MODEL_NAMES
        if model in normalized
    ]

    metrics_found = sorted(
        {
            metric
            for metric in METRICS
            if metric in normalized
        }
    )

    # Avoid counting f1 and f1-score separately.
    if "f1-score" in metrics_found and "f1" in metrics_found:
        metrics_found.remove("f1")

    libraries_found = sorted(
        {
            library
            for library in ML_LIBRARIES
            if library in normalized
        }
    )

    data_handling = {
        "cleaning_or_preprocessing": contains_any(
            body,
            [
                "cleaned",
                "cleaning",
                "preprocessed",
                "preprocessing",
                "transformed the data",
            ],
        ),

        "missing_values": contains_any(
            body,
            [
                "missing values",
                "null values",
            ],
        ),

        "categorical_encoding": contains_any(
            body,
            [
                "categorical variables",
                "encoded categorical",
                "encoding",
            ],
        ),

        "feature_work": contains_any(
            body,
            [
                "feature engineering",
                "feature selection",
            ],
        ),

        "eda": contains_any(
            body,
            [
                "exploratory data analysis",
                "eda",
            ],
        ),

        "class_imbalance": contains_any(
            body,
            [
                "class imbalance",
                "class weighting",
                "imbalanced",
            ],
        ),
    }

    model_training = contains_any(
        body,
        [
            "trained logistic",
            "trained random",
            "trained classification",
            "trained models",
            "trained a model",
            "built a machine learning model",
            "using a train-test split",
        ],
    )

    # Comparing named models is also clear evidence
    # that models were actually used.
    if len(models_found) >= 2 and "compared" in body:
        model_training = True

    train_test = contains_any(
        body,
        [
            "train-test",
            "train test",
            "train/test",
            "training and testing",
            "train-test split",
        ],
    )

    model_comparison = (
        "compared" in body
        or len(models_found) >= 2
    )

    evaluation_present = (
        len(metrics_found) > 0
        or contains_any(
            body,
            [
                "confusion matrix",
                "classification report",
                "evaluated models",
                "evaluated them",
            ],
        )
    )

    evaluation_reasoning = contains_any(
        body,
        [
            "prioritized because",
            "because false negatives",
            "selected the better-performing",
            "selected the final model",
        ],
    )

    interface_or_deployment = contains_any(
        body,
        [
            "streamlit",
            "fastapi",
            "flask",
            "api endpoint",
            "deployed",
        ],
    )

    python_mentioned = "python" in normalized

    python_explicit_use = contains_any(
        body,
        [
            "using python",
            "with python",
            "python application",
            "python script",
        ],
    )

    python_ecosystem_used = contains_any(
        body,
        [
            "pandas",
            "numpy",
            "scikit-learn",
            "sklearn",
            "streamlit",
        ],
    )

    library_used_in_body = any(
        library in body
        for library in ML_LIBRARIES
    )

    git_mentioned = contains_any(
        normalized,
        [
            "git",
            "github",
        ],
    )

    git_demonstrated = contains_any(
        body,
        [
            "published the project to github",
            "uses git and github",
            "github with documentation",
            "github repository",
        ],
    )

    strong_practical_exposure = contains_any(
        body,
        [
            "internship",
            "research assistant",
            "research project",
            "client project",
            "professional experience",
            "worked with a team",
        ],
    )

    light_practical_exposure = contains_any(
        body,
        [
            "competition",
            "coursework",
            "university project",
            "university and personal projects",
        ],
    )

    bonus_mentioned = sorted(
        {
            technology
            for technology in BONUS_TECH
            if technology in normalized
        }
    )

    bonus_demonstrated = sorted(
        {
            technology
            for technology in BONUS_TECH
            if technology in body
        }
    )

    workflow = {
        "model_training": model_training,
        "train_test": train_test,
        "model_comparison": model_comparison,
        "feature_work": data_handling["feature_work"],
        "evaluation": evaluation_present,
        "evaluation_reasoning": evaluation_reasoning,
        "interface_or_deployment": interface_or_deployment,
    }

    snippets = {
        "python": find_evidence_snippets(
            sentences,
            [
                "python",
                "pandas",
                "numpy",
                "scikit-learn",
                "sklearn",
            ],
        ),

        "ml_workflow": find_evidence_snippets(
            sentences,
            MODEL_NAMES
            + [
                "trained",
                "training",
                "train-test",
                "train test",
                "classification",
                "compared",
                "prediction",
            ],
        ),

        "data_handling": find_evidence_snippets(
            sentences,
            [
                "cleaned",
                "preprocessed",
                "missing values",
                "categorical",
                "feature engineering",
                "feature selection",
                "exploratory data analysis",
                "class imbalance",
            ],
        ),

        "evaluation": find_evidence_snippets(
            sentences,
            [
                "accuracy",
                "precision",
                "recall",
                "f1",
                "roc-auc",
                "confusion matrix",
                "classification report",
                "evaluated",
            ],
        ),

        "git_github": find_evidence_snippets(
            sentences,
            [
                "git",
                "github",
                "repository",
            ],
        ),

        "additional_technology": find_evidence_snippets(
            sentences,
            BONUS_TECH,
        ),
    }

    return {
        "python": {
            "mentioned": python_mentioned,
            "explicit_use": python_explicit_use,
            "ecosystem_used": python_ecosystem_used,
        },

        "machine_learning": {
            "models_found": models_found,
            "workflow": workflow,
        },

        "data_handling": data_handling,

        "evaluation": {
            "metrics": metrics_found,
            "confusion_matrix": "confusion matrix" in body,
            "classification_report": "classification report" in body,
            "reasoning": evaluation_reasoning,
        },

        "ml_libraries": {
            "found": libraries_found,
            "used_in_body": library_used_in_body,
        },

        "git_github": {
            "mentioned": git_mentioned,
            "demonstrated": git_demonstrated,
        },

        "practical_exposure": {
            "strong": strong_practical_exposure,
            "light": light_practical_exposure,
        },

        "bonus": {
            "mentioned": bonus_mentioned,
            "demonstrated": bonus_demonstrated,
        },

        "snippets": snippets,
    }
