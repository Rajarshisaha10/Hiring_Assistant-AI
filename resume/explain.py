# explain.py


def generate_explanation(score, data, job_config):

    reasons = []

    matched = list(set(data["skills"]) & set(job_config["skills"]))
    missing = list(set(job_config["skills"]) - set(data["skills"]))

    if matched:
        reasons.append(f"✓ Matched skills: {', '.join(matched)}")

    if missing:
        reasons.append(f"✗ Missing skills: {', '.join(missing)}")

    reasons.append(f"Experience: {data['experience']} years")
    reasons.append(f"Projects detected: {data['projects']}")

    decision = "SHORTLISTED" if score >= 60 else "REJECTED"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons
    }