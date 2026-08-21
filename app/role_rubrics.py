ROLE_RUBRICS = {
    "ML/AI": {
        "name": "ML/AI Intern",
        "max_score": 22,
        "criteria": [
            ("Python", "python", 3),
            ("ML Fundamentals", "ml_fundamentals", 3),
            ("Project Evidence", "project_evidence", 3),
            ("Data Handling", "data_handling", 3),
            ("Model Evaluation", "model_evaluation", 2),
            ("ML Libraries", "ml_libraries", 2),
            ("Git / GitHub", "git_github", 2),
            ("Practical Exposure", "practical_exposure", 2),
            ("Bonus Exposure", "bonus_exposure", 2),
        ],
    },
    "Data Science": {
        "name": "Data Science Intern",
        "max_score": 22,
        "criteria": [
            ("Python", "python", 3),
            ("Statistics / EDA", "statistics_eda", 3),
            ("SQL", "sql", 3),
            ("ML Fundamentals", "ml_fundamentals", 3),
            ("Data Handling", "data_handling", 3),
            ("Visualization", "visualization", 2),
            ("Model Evaluation", "model_evaluation", 2),
            ("Git / GitHub", "git_github", 1),
            ("Practical Exposure", "practical_exposure", 2),
        ],
    },
    "Data Engineering": {
        "name": "Data Engineering Intern",
        "max_score": 22,
        "criteria": [
            ("Python / SQL", "python_sql", 4),
            ("ETL / Data Pipelines", "pipelines_etl", 4),
            ("Databases", "databases", 3),
            ("Data Modeling", "data_modeling", 2),
            ("Warehouse / Cloud", "warehouse_cloud", 2),
            ("Git / GitHub", "git_github", 2),
            ("Project Evidence", "project_evidence", 3),
            ("Practical Exposure", "practical_exposure", 2),
        ],
    },
    "DevOps": {
        "name": "DevOps Intern",
        "max_score": 22,
        "criteria": [
            ("Linux / Scripting", "linux_scripting", 3),
            ("Git / GitHub", "git_github", 2),
            ("Containers", "containers", 4),
            ("CI/CD", "ci_cd", 3),
            ("Cloud", "cloud", 3),
            ("Networking", "networking", 2),
            ("Monitoring / Deployment", "monitoring_deployment", 2),
            ("Project Evidence", "project_evidence", 2),
            ("Practical Exposure", "practical_exposure", 1),
        ],
    },
}

SUPPORTED_ROLES = set(ROLE_RUBRICS)


def get_role_rubric(role):
    return ROLE_RUBRICS.get(str(role).strip())
