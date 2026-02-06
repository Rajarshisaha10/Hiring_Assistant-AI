"""
Decision Engine for Hiring Pipeline

Makes final hiring decisions based on:
- Resume score
- Coding score
- Fraud score
- Job requirements
"""

from typing import Dict, Any, List, Optional


def calculate_final_score(
    resume_score: int,
    coding_score: Optional[int],
    fraud_score: int,
    weights: Optional[Dict[str, float]] = None
) -> int:
    """
    Calculate weighted final score.
    
    Default weights:
    - Resume: 30%
    - Coding: 50%
    - Fraud (inverted): 20%
    
    Args:
        resume_score: 0-100
        coding_score: 0-100 or None
        fraud_score: 0-100 (higher = more fraudulent)
        weights: Optional custom weights
    
    Returns:
        Final score (0-100)
    """
    if weights is None:
        weights = {
            "resume": 0.3,
            "coding": 0.5,
            "fraud": 0.2
        }
    
    # If no coding score yet, adjust weights
    if coding_score is None:
        final_score = (
            resume_score * 0.7 +
            (100 - fraud_score) * 0.3
        )
    else:
        final_score = (
            resume_score * weights["resume"] +
            coding_score * weights["coding"] +
            (100 - fraud_score) * weights["fraud"]
        )
    
    return int(min(max(final_score, 0), 100))


def determine_next_stage(
    current_stage: str,
    scores: Dict[str, int],
    fraud_score: int
) -> str:
    """
    Determine next pipeline stage based on scores.
    
    Pipeline stages:
    1. Resume Screening
    2. Coding Assessment
    3. Technical Interview
    4. Behavioral Interview
    5. Final Decision
    
    Args:
        current_stage: Current pipeline stage
        scores: Dict with resume_score, coding_score, final_score
        fraud_score: Fraud risk score
    
    Returns:
        Next stage name
    """
    # Auto-reject if high fraud risk
    if fraud_score > 70:
        return "REJECTED - Fraud Risk"
    
    final_score = scores.get("final_score", 0)
    resume_score = scores.get("resume_score", 0)
    coding_score = scores.get("coding_score")
    
    if current_stage == "Resume Screening":
        if resume_score < 40:
            return "REJECTED - Low Resume Score"
        else:
            return "Coding Assessment"
    
    elif current_stage == "Coding Assessment":
        if coding_score is None:
            return "Coding Assessment"  # Still in progress
        elif coding_score < 30:
            return "REJECTED - Failed Coding"
        elif final_score >= 75:
            return "Technical Interview"
        elif final_score >= 60:
            return "Manual Review"
        else:
            return "REJECTED - Low Overall Score"
    
    elif current_stage == "Technical Interview":
        return "Behavioral Interview"
    
    elif current_stage == "Behavioral Interview":
        return "Final Decision"
    
    else:
        return "Unknown Stage"


def generate_recommendation(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate hiring recommendation with detailed reasoning.
    
    Args:
        candidate_data: Complete candidate information
    
    Returns:
        Recommendation dict with decision, reasoning, and next steps
    """
    resume_score = candidate_data.get("resume_score", 0)
    coding_score = candidate_data.get("coding_score")
    fraud_score = candidate_data.get("fraud_score", 0)
    final_score = candidate_data.get("final_score", 0)
    
    reasons = []
    strengths = []
    weaknesses = []
    
    # Analyze resume
    if resume_score >= 70:
        strengths.append(f"Strong resume (score: {resume_score}/100)")
    elif resume_score >= 50:
        reasons.append(f"Decent resume (score: {resume_score}/100)")
    else:
        weaknesses.append(f"Weak resume (score: {resume_score}/100)")
    
    # Analyze coding
    if coding_score is not None:
        if coding_score >= 70:
            strengths.append(f"Excellent coding skills (score: {coding_score}/100)")
        elif coding_score >= 50:
            reasons.append(f"Adequate coding skills (score: {coding_score}/100)")
        else:
            weaknesses.append(f"Poor coding performance (score: {coding_score}/100)")
    
    # Analyze fraud risk
    if fraud_score > 70:
        weaknesses.append(f"HIGH fraud risk (score: {fraud_score}/100)")
    elif fraud_score > 40:
        reasons.append(f"MEDIUM fraud risk (score: {fraud_score}/100)")
    else:
        strengths.append(f"Low fraud risk (score: {fraud_score}/100)")
    
    # Make decision
    if fraud_score > 70:
        decision = "REJECT"
        verdict = "High fraud risk detected"
        next_steps = ["Flag for manual review", "Do not proceed with interview"]
    elif final_score >= 75:
        decision = "STRONG HIRE"
        verdict = "Excellent candidate - highly recommended"
        next_steps = ["Schedule technical interview", "Fast-track to hiring manager"]
    elif final_score >= 60:
        decision = "PROCEED WITH CAUTION"
        verdict = "Borderline candidate - requires manual review"
        next_steps = ["Manual review by senior engineer", "Additional screening may be needed"]
    elif final_score >= 40:
        decision = "WEAK CANDIDATE"
        verdict = "Below threshold but not auto-rejected"
        next_steps = ["Consider for junior positions", "May need additional training"]
    else:
        decision = "REJECT"
        verdict = "Does not meet minimum requirements"
        next_steps = ["Send rejection email", "Keep in talent pool for future opportunities"]
    
    return {
        "decision": decision,
        "verdict": verdict,
        "final_score": final_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "reasons": reasons,
        "next_steps": next_steps,
        "recommendation_summary": f"{decision}: {verdict} (Final Score: {final_score}/100)"
    }


def apply_job_requirements(
    scores: Dict[str, int],
    job_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Match candidate against specific job requirements.
    
    Args:
        scores: Candidate scores
        job_config: Job requirements and thresholds
    
    Returns:
        Match analysis
    """
    required_skills = job_config.get("skills", [])
    candidate_skills = job_config.get("candidate_skills", [])
    min_score = job_config.get("min_score", 60)
    risk_tolerance = job_config.get("risk_tolerance", 50)
    
    # Calculate skill match
    matched_skills = list(set(required_skills) & set(candidate_skills))
    missing_skills = list(set(required_skills) - set(candidate_skills))
    skill_match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 100
    
    # Check if meets minimum requirements
    final_score = scores.get("final_score", 0)
    fraud_score = scores.get("fraud_score", 0)
    
    meets_requirements = (
        final_score >= min_score and
        fraud_score <= risk_tolerance and
        skill_match_percentage >= 50
    )
    
    return {
        "meets_requirements": meets_requirements,
        "skill_match_percentage": round(skill_match_percentage, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "score_vs_minimum": f"{final_score}/{min_score}",
        "fraud_vs_tolerance": f"{fraud_score}/{risk_tolerance}"
    }


def make_final_decision(candidate_data: Dict[str, Any], job_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main decision function - combines all analysis.
    
    Args:
        candidate_data: Complete candidate information
        job_config: Optional job-specific requirements
    
    Returns:
        Complete decision report
    """
    # Calculate final score
    final_score = calculate_final_score(
        candidate_data.get("resume_score", 0),
        candidate_data.get("coding_score"),
        candidate_data.get("fraud_score", 0)
    )
    
    candidate_data["final_score"] = final_score
    
    # Generate recommendation
    recommendation = generate_recommendation(candidate_data)
    
    # Determine next stage
    next_stage = determine_next_stage(
        candidate_data.get("current_stage", "Resume Screening"),
        {
            "resume_score": candidate_data.get("resume_score", 0),
            "coding_score": candidate_data.get("coding_score"),
            "final_score": final_score
        },
        candidate_data.get("fraud_score", 0)
    )
    
    # Apply job requirements if provided
    job_match = None
    if job_config:
        job_match = apply_job_requirements(
            {
                "final_score": final_score,
                "fraud_score": candidate_data.get("fraud_score", 0)
            },
            job_config
        )
    
    return {
        "final_score": final_score,
        "recommendation": recommendation,
        "next_stage": next_stage,
        "job_match": job_match,
        "timestamp": candidate_data.get("timestamp", "N/A")
    }
