"""
Fraud Detection System for Hiring Pipeline

Detects suspicious patterns in candidate submissions including:
- Code plagiarism
- Timing anomalies
- Resume inconsistencies
"""

import difflib
from datetime import datetime
from typing import Dict, List, Any, Optional


# Known solution patterns for plagiarism detection
KNOWN_PATTERNS = {
    1: ["def twoSum(nums, target):", "seen = {}", "for i, num in enumerate(nums):"],
    2: ["def isValid(s):", "stack = []", "mapping = {"],
    3: ["def mergeTwoLists(list1, list2):", "result = []", "while list1 and list2:"],
}


def normalize_code(code: str) -> str:
    """Remove whitespace and comments for comparison."""
    lines = []
    for line in code.split('\n'):
        # Remove comments
        if '#' in line:
            line = line[:line.index('#')]
        # Remove whitespace
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def detect_code_plagiarism(code: str, question_id: int) -> Dict[str, Any]:
    """
    Check if code is suspiciously similar to known patterns.
    
    Returns:
        dict with 'is_suspicious', 'similarity_score', 'reason'
    """
    if not code or question_id not in KNOWN_PATTERNS:
        return {
            "is_suspicious": False,
            "similarity_score": 0,
            "reason": "No patterns available for comparison"
        }
    
    normalized = normalize_code(code)
    patterns = KNOWN_PATTERNS[question_id]
    
    # Check how many known patterns appear in the code
    matches = sum(1 for pattern in patterns if pattern in normalized)
    similarity = (matches / len(patterns)) * 100
    
    is_suspicious = similarity > 80
    
    return {
        "is_suspicious": is_suspicious,
        "similarity_score": round(similarity, 2),
        "reason": f"Code matches {matches}/{len(patterns)} known patterns" if is_suspicious else "Code appears original"
    }


def analyze_submission_timing(
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    question_difficulty: str,
    num_questions: int
) -> Dict[str, Any]:
    """
    Detect suspiciously fast submissions.
    
    Expected times (minutes):
    - easy: 5-15 min per question
    - medium: 10-25 min per question
    - hard: 20-40 min per question
    """
    if not start_time or not end_time:
        return {
            "is_suspicious": False,
            "time_taken_minutes": 0,
            "reason": "Timing data not available"
        }
    
    time_taken = (end_time - start_time).total_seconds() / 60  # minutes
    
    # Expected minimum time based on difficulty
    min_expected = {
        "easy": 5 * num_questions,
        "medium": 10 * num_questions,
        "hard": 20 * num_questions
    }.get(question_difficulty, 10 * num_questions)
    
    # Suspicious if completed in less than 20% of expected time
    threshold = min_expected * 0.2
    is_suspicious = time_taken < threshold
    
    return {
        "is_suspicious": is_suspicious,
        "time_taken_minutes": round(time_taken, 2),
        "expected_minimum_minutes": min_expected,
        "reason": f"Completed in {round(time_taken, 1)}min (expected minimum: {min_expected}min)" if is_suspicious else "Timing appears normal"
    }


def check_resume_authenticity(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate resume claims for inconsistencies.
    
    Checks:
    - Unrealistic experience (e.g., 20+ years for entry level)
    - Keyword stuffing (too many skills)
    - Suspicious patterns
    """
    skills = resume_data.get("skills", [])
    experience = resume_data.get("experience", 0)
    projects = resume_data.get("projects", 0)
    
    issues = []
    
    # Check for excessive skills (keyword stuffing)
    if len(skills) > 15:
        issues.append(f"Excessive skills listed ({len(skills)})")
    
    # Check for unrealistic experience
    if experience > 30:
        issues.append(f"Unrealistic experience claim ({experience} years)")
    
    # Check for inconsistency: high experience but no projects
    if experience > 5 and projects < 2:
        issues.append("High experience but few projects mentioned")
    
    is_suspicious = len(issues) > 0
    
    return {
        "is_suspicious": is_suspicious,
        "issues": issues,
        "reason": "; ".join(issues) if issues else "Resume appears authentic"
    }


def calculate_fraud_score(checks: List[Dict[str, Any]]) -> int:
    """
    Calculate overall fraud risk score (0-100).
    Higher score = higher fraud risk.
    
    Args:
        checks: List of fraud check results
    
    Returns:
        Fraud score (0-100)
    """
    if not checks:
        return 0
    
    suspicious_count = sum(1 for check in checks if check.get("is_suspicious", False))
    total_checks = len(checks)
    
    # Base score on percentage of suspicious checks
    base_score = (suspicious_count / total_checks) * 100
    
    # Weight by severity (if plagiarism detected, increase score)
    for check in checks:
        if check.get("is_suspicious") and "plagiarism" in check.get("reason", "").lower():
            base_score = min(base_score + 20, 100)
    
    return int(base_score)


def run_fraud_detection(
    code_submissions: List[Dict[str, Any]],
    resume_data: Dict[str, Any],
    timing_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run complete fraud detection pipeline.
    
    Args:
        code_submissions: List of {question_id, code, difficulty}
        resume_data: Resume information
        timing_data: Optional timing information
    
    Returns:
        Complete fraud analysis report
    """
    checks = []
    
    # Check resume authenticity
    resume_check = check_resume_authenticity(resume_data)
    checks.append(resume_check)
    
    # Check code plagiarism for each submission
    for submission in code_submissions:
        plagiarism_check = detect_code_plagiarism(
            submission.get("code", ""),
            submission.get("question_id", 0)
        )
        checks.append(plagiarism_check)
    
    # Check submission timing if available
    if timing_data:
        timing_check = analyze_submission_timing(
            timing_data.get("start_time"),
            timing_data.get("end_time"),
            timing_data.get("difficulty", "medium"),
            len(code_submissions)
        )
        checks.append(timing_check)
    
    # Calculate overall fraud score
    fraud_score = calculate_fraud_score(checks)
    
    return {
        "fraud_score": fraud_score,
        "risk_level": "HIGH" if fraud_score > 70 else "MEDIUM" if fraud_score > 40 else "LOW",
        "checks": checks,
        "summary": f"Fraud risk: {fraud_score}/100 - {len([c for c in checks if c.get('is_suspicious')])} suspicious indicators found"
    }
