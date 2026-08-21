def score_candidate(evidence, application):
    workflow = evidence["machine_learning"]["workflow"]

    workflow_depth = sum(
        bool(value)
        for value in workflow.values()
    )

    # -------------------------------------------------
    # Python: 0-3
    # -------------------------------------------------

    python_data = evidence["python"]

    if not python_data["mentioned"]:
        python_score = 0

    elif (
        workflow_depth >= 4
        and (
            python_data["explicit_use"]
            or python_data["ecosystem_used"]
        )
    ):
        python_score = 3

    elif (
        workflow_depth >= 2
        and (
            python_data["explicit_use"]
            or python_data["ecosystem_used"]
        )
    ):
        python_score = 2

    else:
        python_score = 1

    # -------------------------------------------------
    # ML fundamentals: 0-3
    # -------------------------------------------------

    model_training = workflow["model_training"]
    train_test = workflow["train_test"]
    evaluation = workflow["evaluation"]

    if not model_training:
        if evidence["machine_learning"]["models_found"]:
            ml_score = 1
        else:
            ml_score = 0

    elif (
        train_test
        and evaluation
        and (
            workflow["model_comparison"]
            or workflow["feature_work"]
            or workflow["evaluation_reasoning"]
        )
    ):
        ml_score = 3

    elif train_test or evaluation:
        ml_score = 2

    else:
        ml_score = 1

    # -------------------------------------------------
    # Project depth: 0-3
    # -------------------------------------------------

    project_depth_signals = [
        any(evidence["data_handling"].values()),
        workflow["model_training"],
        workflow["evaluation"],
        workflow["model_comparison"],
        workflow["evaluation_reasoning"],
        workflow["interface_or_deployment"],
    ]

    project_depth = sum(
        bool(value)
        for value in project_depth_signals
    )

    if project_depth >= 4:
        project_score = 3

    elif project_depth >= 2:
        project_score = 2

    elif (
        workflow["model_training"]
        or evidence["machine_learning"]["models_found"]
    ):
        project_score = 1

    else:
        project_score = 0

    # -------------------------------------------------
    # Data handling: 0-3
    # -------------------------------------------------

    data_signals = sum(
        bool(value)
        for value in evidence["data_handling"].values()
    )

    if data_signals >= 3:
        data_score = 3

    elif data_signals == 2:
        data_score = 2

    elif data_signals == 1:
        data_score = 1

    else:
        data_score = 0

    # -------------------------------------------------
    # Model evaluation: 0-2
    # -------------------------------------------------

    evaluation_data = evidence["evaluation"]

    if (
        len(evaluation_data["metrics"]) >= 3
        or evaluation_data["confusion_matrix"]
        or evaluation_data["classification_report"]
        or evaluation_data["reasoning"]
    ):
        evaluation_score = 2

    elif (
        len(evaluation_data["metrics"]) > 0
        or workflow["evaluation"]
    ):
        evaluation_score = 1

    else:
        evaluation_score = 0

    # -------------------------------------------------
    # ML libraries: 0-2
    # -------------------------------------------------

    libraries = evidence["ml_libraries"]

    if not libraries["found"]:
        library_score = 0

    elif (
        libraries["used_in_body"]
        and workflow_depth >= 3
    ):
        library_score = 2

    elif workflow_depth >= 4:
        # Library appears in skills, but the resume also
        # demonstrates a strong ML workflow.
        library_score = 2

    else:
        library_score = 1

    # -------------------------------------------------
    # Git/GitHub: 0-2
    # -------------------------------------------------

    git = evidence["git_github"]

    if git["demonstrated"]:
        git_score = 2

    elif git["mentioned"]:
        git_score = 1

    else:
        git_score = 0

    # -------------------------------------------------
    # Practical exposure: 0-2
    # -------------------------------------------------

    practical = evidence["practical_exposure"]

    if practical["strong"]:
        practical_score = 2

    elif practical["light"]:
        practical_score = 1

    else:
        practical_score = 0

    # -------------------------------------------------
    # Bonus exposure: 0-2
    # -------------------------------------------------

    bonus = evidence["bonus"]

    if len(bonus["demonstrated"]) >= 3:
        bonus_score = 2

    elif bonus["mentioned"]:
        bonus_score = 1

    else:
        bonus_score = 0

    scores = {
        "python": python_score,
        "ml_fundamentals": ml_score,
        "project_evidence": project_score,
        "data_handling": data_score,
        "model_evaluation": evaluation_score,
        "ml_libraries": library_score,
        "git_github": git_score,
        "practical_exposure": practical_score,
        "bonus_exposure": bonus_score,
    }

    total = sum(scores.values())

    # -------------------------------------------------
    # Operational fit
    # -------------------------------------------------

    onsite = str(
        application["onsite_available"]
    ).strip().lower()

    shift = str(
        application["shift_available"]
    ).strip().lower()

    city = str(
        application["current_city"]
    ).strip().lower()

    if onsite != "yes":
        operational_status = "REQUIREMENT_MISMATCH"
        operational_reason = (
            "Candidate is not available for onsite work."
        )

    elif shift != "yes":
        operational_status = "REQUIREMENT_MISMATCH"
        operational_reason = (
            "Candidate is not available for the required shift."
        )

    elif city == "lahore":
        operational_status = "READY"
        operational_reason = (
            "Lahore-based and available for onsite work "
            "and the required shift."
        )

    else:
        operational_status = "CONFIRM_LOCATION"
        operational_reason = (
            "Candidate is outside Lahore but indicated "
            "onsite availability."
        )

    # -------------------------------------------------
    # Technical review priority
    # These are MVP thresholds and can be tuned later.
    # -------------------------------------------------

    if total >= 17:
        review_priority = "PRIORITY_REVIEW"

    elif total >= 11:
        review_priority = "GOOD_POTENTIAL"

    elif total >= 6:
        review_priority = "DEVELOPING_PROFILE"

    else:
        review_priority = "INSUFFICIENT_EVIDENCE"

    return {
        "scores": scores,
        "total_score": total,
        "max_score": 22,
        "technical_review_priority": review_priority,
        "operational_status": operational_status,
        "operational_reason": operational_reason,
    }