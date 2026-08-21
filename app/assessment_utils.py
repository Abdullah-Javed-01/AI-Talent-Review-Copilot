def get_operational_fit(application):
    onsite = str(application["onsite_available"]).strip().lower()
    shift = str(application["shift_available"]).strip().lower()
    city = str(application["current_city"]).strip().lower()

    if onsite != "yes":
        return (
            "REQUIREMENT_MISMATCH",
            "Candidate is not available for onsite work.",
        )

    if shift != "yes":
        return (
            "REQUIREMENT_MISMATCH",
            "Candidate is not available for the required shift.",
        )

    if city == "lahore":
        return (
            "READY",
            "Lahore-based and available for onsite work and the required shift.",
        )

    return (
        "CONFIRM_LOCATION",
        "Candidate is outside Lahore but indicated onsite availability.",
    )


def get_review_priority(total, max_score=22):
    # Thresholds are expressed as proportions so future rubrics can use other maxima.
    ratio = total / max_score if max_score else 0

    if ratio >= 17 / 22:
        return "PRIORITY_REVIEW"
    if ratio >= 11 / 22:
        return "GOOD_POTENTIAL"
    if ratio >= 6 / 22:
        return "DEVELOPING_PROFILE"
    return "INSUFFICIENT_EVIDENCE"
