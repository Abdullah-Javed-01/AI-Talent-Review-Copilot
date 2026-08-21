from role_rubrics import get_role_rubric


def _criterion_score(terms, snippets, maximum):
    """Evidence-weighted score: mentions earn partial credit; demonstrated use earns more."""
    term_count = len(terms or [])
    snippet_count = len(snippets or [])

    if term_count == 0:
        return 0

    if snippet_count >= 2:
        return maximum

    if snippet_count == 1:
        return max(1, maximum - 1)

    # Keyword/skills-list evidence only. Never award more than ~40%.
    if maximum >= 4:
        return 2
    return 1


def score_role_evidence(role_evidence, role):
    rubric = get_role_rubric(role)
    if not rubric:
        raise ValueError(f"No rubric configured for role: {role}")

    signals = role_evidence.get("signals", {})
    snippets = role_evidence.get("snippets", {})

    scores = {}
    for _, key, maximum in rubric["criteria"]:
        scores[key] = _criterion_score(
            signals.get(key, []),
            snippets.get(key, []),
            maximum,
        )

    return {
        "scores": scores,
        "total_score": sum(scores.values()),
        "max_score": rubric["max_score"],
        "rubric_name": rubric["name"],
    }
