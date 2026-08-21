import re


def _normalize(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def _sentences(text):
    lines = []
    for raw in str(text).splitlines():
        cleaned = raw.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered.startswith("skills:") or lowered.startswith("certificates:"):
            continue
        lines.append(cleaned)

    body = re.sub(r"\s+", " ", " ".join(lines)).strip()
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+", body) if item.strip()]


def _find_terms(text, terms):
    lowered = _normalize(text)
    return sorted({term for term in terms if term in lowered})


def _snippets(text, terms, limit=4):
    action_terms = [
        "built", "developed", "created", "implemented", "used", "worked",
        "designed", "deployed", "configured", "automated", "managed",
        "analyzed", "cleaned", "queried", "modeled", "visualized",
        "orchestrated", "monitored", "containerized", "published",
    ]
    matches = []
    for sentence in _sentences(text):
        lowered = sentence.lower()
        if any(term in lowered for term in terms) and any(action in lowered for action in action_terms):
            matches.append(sentence)
        if len(matches) >= limit:
            break
    return matches


def extract_role_evidence(resume_text, role):
    role = str(role).strip()
    normalized = _normalize(resume_text)

    shared = {
        "python": _find_terms(normalized, ["python", "pandas", "numpy"]),
        "sql": _find_terms(normalized, ["sql", "mysql", "postgresql", "postgres", "sqlite"]),
        "git": _find_terms(normalized, ["git", "github", "gitlab"]),
        "project": _find_terms(normalized, ["project", "system", "application", "dashboard", "pipeline"]),
        "practical": _find_terms(
            normalized,
            ["internship", "intern", "research", "client", "freelance", "team", "competition", "coursework"],
        ),
    }

    if role == "Data Science":
        groups = {
            "python": ["python", "pandas", "numpy"],
            "statistics_eda": ["statistics", "statistical", "eda", "exploratory data analysis", "correlation", "distribution", "hypothesis"],
            "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
            "ml_fundamentals": ["machine learning", "classification", "regression", "random forest", "decision tree", "scikit-learn", "sklearn", "train-test"],
            "data_handling": ["cleaned", "preprocessed", "missing values", "null values", "feature engineering", "encoding", "outlier", "transformed"],
            "visualization": ["matplotlib", "seaborn", "plotly", "power bi", "tableau", "visualization", "dashboard"],
            "model_evaluation": ["accuracy", "precision", "recall", "f1", "roc-auc", "confusion matrix", "evaluated"],
            "git_github": ["git", "github", "gitlab"],
            "practical_exposure": ["internship", "intern", "research", "client", "team", "competition", "coursework"],
        }
    elif role == "Data Engineering":
        groups = {
            "python_sql": ["python", "sql", "pandas", "postgresql", "postgres", "mysql"],
            "pipelines_etl": ["etl", "elt", "pipeline", "data pipeline", "airflow", "spark", "kafka", "ingestion", "orchestration"],
            "databases": ["postgresql", "postgres", "mysql", "sql server", "mongodb", "sqlite", "database"],
            "data_modeling": ["data model", "data modeling", "schema", "star schema", "snowflake schema", "normalization", "dimensional"],
            "warehouse_cloud": ["data warehouse", "warehouse", "bigquery", "snowflake", "redshift", "aws", "azure", "gcp", "cloud"],
            "git_github": ["git", "github", "gitlab"],
            "project_evidence": ["project", "pipeline", "etl", "warehouse", "database", "ingestion"],
            "practical_exposure": ["internship", "intern", "research", "client", "team", "competition", "coursework"],
        }
    elif role == "DevOps":
        groups = {
            "linux_scripting": ["linux", "ubuntu", "bash", "shell", "powershell", "python script", "scripting"],
            "git_github": ["git", "github", "gitlab"],
            "containers": ["docker", "container", "docker compose", "kubernetes", "k8s"],
            "ci_cd": ["ci/cd", "ci cd", "github actions", "gitlab ci", "jenkins", "pipeline"],
            "cloud": ["aws", "azure", "gcp", "cloud", "ec2", "s3"],
            "networking": ["networking", "dns", "tcp", "http", "https", "nginx", "reverse proxy", "load balancer"],
            "monitoring_deployment": ["monitoring", "prometheus", "grafana", "logging", "deployed", "deployment", "uptime"],
            "project_evidence": ["project", "deployed", "containerized", "automated", "configured"],
            "practical_exposure": ["internship", "intern", "client", "team", "competition", "coursework"],
        }
    else:
        return {"role": role, "signals": {}, "snippets": {}}

    signals = {key: _find_terms(normalized, terms) for key, terms in groups.items()}
    snippets = {key: _snippets(resume_text, terms) for key, terms in groups.items()}

    return {
        "role": role,
        "shared": shared,
        "signals": signals,
        "snippets": snippets,
    }
