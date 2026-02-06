import random
import time

# resume modules
from resume.parser import extract_text
from resume.skill_extractor import extract_skills, extract_experience, count_projects
from resume.scorer import score_candidate

# coding modules
from project.question_selector import select_questions
from project.judge import evaluate
from fraud_detector import FraudDetector


# -----------------------------
# CONFIG
# -----------------------------

JOB_CONFIG = {
    "skills": ["python", "fastapi", "sql", "docker"],
    "min_exp": 2
}


# -----------------------------
# RESUME STAGE
# -----------------------------

def evaluate_resume(path):

    text = extract_text(path)

    data = {
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "projects": count_projects(text)
    }

    score = score_candidate(data, JOB_CONFIG)

    return score, data


# -----------------------------
# CODING STAGE
# -----------------------------

def run_coding_round(resume_score):

    detector = FraudDetector()

    random.seed(time.time())

    questions = select_questions(resume_score, 2)
    random.shuffle(questions)

    total_score = 0

    print("\n=== Coding Round Started ===")

    for i, q in enumerate(questions, 1):

        print("\n--------------------------")
        print(f"Question {i}: {q['title']}")
        print("Difficulty:", q["difficulty"])
        print(q["description"])
        print("--------------------------")

        print("\nPaste code (END to finish):")

        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        candidate_code = "\n".join(lines)

        detector.track_code(candidate_code)
        detector.track_submission()

        score = evaluate(candidate_code, q["tests"])
        print("Score:", score)

        total_score += score

    final_score = total_score / len(questions)
    fraud_risk = detector.compute_risk(final_score)

    return final_score, fraud_risk


# -----------------------------
# FINAL DECISION ENGINE
# -----------------------------

def final_decision(resume_score, coding_score, fraud_risk):

    trust = 100 - fraud_risk

    final = (
        resume_score * 0.3 +
        coding_score * 0.5 +
        trust * 0.2
    )

    if final >= 75:
        decision = "SHORTLIST"
    elif final >= 60:
        decision = "INTERVIEW"
    else:
        decision = "REJECT"

    return round(final, 2), decision


# -----------------------------
# MAIN ORCHESTRATOR
# -----------------------------

def run_pipeline(resume_path):

    print("\n==============================")
    print(" 🤖 AI Hiring Orchestrator")
    print("==============================")

    # Resume
    resume_score, _ = evaluate_resume(resume_path)
    print("Resume Score:", resume_score)

    # Coding
    coding_score, fraud_risk = run_coding_round(resume_score)

    print("\nCoding Score:", coding_score)
    print("Fraud Risk:", fraud_risk)

    # Final decision
    final_score, decision = final_decision(
        resume_score,
        coding_score,
        fraud_risk
    )

    print("\n==============================")
    print("FINAL AI SCORE:", final_score)
    print("DECISION:", decision)
    print("==============================\n")


# -----------------------------
# APPLICATION PROCESSOR (FOR WEB)
# -----------------------------

def process_application(resume_path, applicant_data):
    """Process an applicant's application for the web interface."""
    try:
        if not resume_path:
            return {
                "success": False,
                "error": "No resume provided"
            }
        
        # Evaluate resume
        resume_score, resume_data = evaluate_resume(resume_path)
        
        # Select coding questions
        questions = select_questions(resume_score, n=3)
        
        return {
            "success": True,
            "candidate_data": {
                "resume_score": resume_score,
                "resume_data": resume_data,
                "questions": questions
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":

    path = input("Enter resume file path: ")
    run_pipeline(path)
