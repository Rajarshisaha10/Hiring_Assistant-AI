from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.utils import secure_filename
from datetime import datetime
from typing import Optional
import os
import logging

# Import configuration
from config import CONFIG, setup_logging

# Setup logging
logger = setup_logging()

from project.question_selector import select_questions
from project.judge import score_resume, score_coding_answers


app = Flask(__name__)
app.config.from_object(CONFIG)

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

logger.info(f"Flask app initialized with {os.getenv('FLASK_ENV', 'development')} configuration")


# =========================================================
# MOCK DATABASES
# =========================================================

CANDIDATES_DB = []
APPLICANTS_DB = []
CODING_SESSIONS = {}

JOBS_DB = {
    "default": {
        "role": "Senior Backend Engineer",
        "level": "Senior",
        "skills": ["python", "fastapi", "sql", "docker"],
        "pipeline": ["Resume", "Coding", "System Design", "Behavioral", "Final"],
        "risk_tolerance": 50
    }
}


# =========================================================
# HELPERS
# =========================================================

def compute_ai_score_and_verdict(resume_score: int,
                                 coding_score: Optional[int]) -> tuple[int, str]:

    if coding_score is None:
        ai_score = resume_score
    else:
        ai_score = int((resume_score + coding_score) / 2)

    if ai_score >= 80:
        verdict = "Strong match - highly recommended"
    elif ai_score >= 60:
        verdict = "Promising profile"
    elif ai_score >= 40:
        verdict = "Borderline - manual review"
    else:
        verdict = "Below threshold"

    return ai_score, verdict


def get_candidate_by_id(cid):
    for c in CANDIDATES_DB:
        if c["id"] == cid:
            return c
    return None


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def role_selection():
    return render_template("login.html")


# =========================================================
# ADMIN
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        session["role"] = "admin"
        return redirect(url_for("dashboard"))

    return render_template("admin_login.html")


@app.route("/dashboard")
def dashboard():

    total = len(CANDIDATES_DB)

    stats = {
        "total": total,
        "approved": len([c for c in CANDIDATES_DB if c.get("status") == "approved"]),
        "rejected": len([c for c in CANDIDATES_DB if c.get("status") == "rejected"]),
        "pending": len([c for c in CANDIDATES_DB if c.get("status") == "pending"]),
        "avg_score": round(sum([c.get("ai_score", 0) for c in CANDIDATES_DB]) / total, 1)
        if total else 0
    }

    return render_template("dashboard.html", stats=stats, candidates=CANDIDATES_DB)


# =========================================================
# APPLICANT PORTAL
# =========================================================

@app.route("/applicant", methods=["GET", "POST"])
def applicant_portal():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        resume_file = request.files.get("resume")

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        resume_path = None

        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            resume_file.save(resume_path)

        # Use hiring orchestrator for complete pipeline
        from hiring_orchestrator import process_application
        
        applicant_data = {
            "name": name,
            "email": email
        }
        
        pipeline_result = process_application(resume_path, applicant_data)
        
        if not pipeline_result["success"]:
            # Fallback to basic processing if orchestrator fails
            resume_score = score_resume(resume_path) if resume_path else 50
            ai_score, verdict = compute_ai_score_and_verdict(resume_score, None)
            questions = select_questions(resume_score, n=3)
        else:
            candidate_data = pipeline_result["candidate_data"]
            resume_score = candidate_data["resume_score"]
            ai_score, verdict = compute_ai_score_and_verdict(resume_score, None)
            questions = candidate_data["questions"]

        applicant_id = len(APPLICANTS_DB) + 1

        # Store complete applicant data with all required fields
        applicant_record = {
            "id": applicant_id,
            "name": name,
            "email": email,
            "resume_score": resume_score,
            "ai_score": ai_score,
            "ai_verdict": verdict,
            "status": "pending",
            "stage": "Coding Assessment",
            "resume_filename": filename if resume_file and resume_file.filename else None
        }
        
        APPLICANTS_DB.append(applicant_record)

        candidate_id = len(CANDIDATES_DB) + 1

        CANDIDATES_DB.append({
            "id": candidate_id,
            "name": name,
            "email": email,
            "resume_score": resume_score,
            "coding_score": None,
            "ai_score": ai_score,
            "status": "pending"
        })

        CODING_SESSIONS[applicant_id] = {
            "questions": questions,
            "resume_score": resume_score,
            "coding_score": None,
            "ai_score": ai_score,
            "test_results": [],
            "candidate_id": candidate_id
        }

        # Render the portal with application data instead of redirecting
        return render_template("applicant_portal.html", application=applicant_record, applicant_id=applicant_id)

    return render_template("applicant_portal.html")


# =========================================================
# CODING ROUND  (FIXED VERSION)
# =========================================================

@app.route("/applicant/<int:applicant_id>/coding", methods=["GET", "POST"])
def applicant_coding(applicant_id):

    session_state = CODING_SESSIONS.get(applicant_id)

    if not session_state:
        return redirect(url_for("applicant_portal"))

    questions = session_state["questions"]

    # ---------------- POST ----------------

    if request.method == "POST":

        answers = []

        for q in questions:
            ans = request.form.get(f"answer_{q['id']}", "")
            answers.append({"question_id": q["id"], "answer": ans})

        result = score_coding_answers(questions, answers)

        if isinstance(result, tuple):
            coding_score, test_details = result
        else:
            coding_score = result
            test_details = []

        # store
        session_state["coding_score"] = coding_score
        session_state["test_results"] = test_details

        # recompute AI score  ✅ FIX
        ai_score, verdict = compute_ai_score_and_verdict(
            session_state["resume_score"], coding_score
        )

        session_state["ai_score"] = ai_score

        # update candidate
        candidate = get_candidate_by_id(session_state["candidate_id"])

        if candidate:
            candidate["coding_score"] = coding_score
            candidate["ai_score"] = ai_score

    # ---------------- RENDER ----------------

    return render_template(
        "applicant_coding.html",
        questions=session_state["questions"],
        resume_score=session_state["resume_score"],
        coding_score=session_state["coding_score"],
        ai_score=session_state["ai_score"],
        test_results=session_state["test_results"]
    )


# =========================================================
# ADMIN PANEL ROUTES
# =========================================================

@app.route("/jobs")
def jobs():
    """Jobs management page"""
    return render_template("jobs.html", jobs=JOBS_DB)


@app.route("/candidates")
def candidates():
    """All candidates list page"""
    # Combine data from CANDIDATES_DB and APPLICANTS_DB for complete view
    all_candidates = []
    
    for candidate in CANDIDATES_DB:
        # Find matching applicant data
        applicant = next((a for a in APPLICANTS_DB if a.get("name") == candidate.get("name")), None)
        
        # Merge data
        merged = {
            **candidate,
            "stage": applicant.get("stage", "Unknown") if applicant else "Unknown",
            "ai_verdict": applicant.get("ai_verdict", "N/A") if applicant else "N/A"
        }
        all_candidates.append(merged)
    
    return render_template("candidate.html", candidates=all_candidates)


@app.route("/candidate/<int:candidate_id>")
def candidate_detail(candidate_id):
    """Individual candidate detail page"""
    candidate = get_candidate_by_id(candidate_id)
    
    if not candidate:
        return "Candidate not found", 404
    
    # Find matching applicant data
    applicant = next((a for a in APPLICANTS_DB if a.get("name") == candidate.get("name")), None)
    
    # Find coding session if exists
    coding_session = None
    for app_id, session in CODING_SESSIONS.items():
        if session.get("candidate_id") == candidate_id:
            coding_session = session
            break
    
    # Merge all data
    full_profile = {
        **candidate,
        "stage": applicant.get("stage", "Unknown") if applicant else "Unknown",
        "ai_verdict": applicant.get("ai_verdict", "N/A") if applicant else "N/A",
        "resume_filename": applicant.get("resume_filename") if applicant else None,
        "coding_session": coding_session
    }
    
    return render_template("candidate_detail.html", candidate=full_profile)


@app.route("/assessments")
def assessments():
    """Assessments overview page"""
    # Prepare assessment data
    assessments_data = []
    
    for app_id, session in CODING_SESSIONS.items():
        candidate = get_candidate_by_id(session.get("candidate_id"))
        if candidate:
            assessments_data.append({
                "applicant_id": app_id,
                "candidate_name": candidate.get("name"),
                "candidate_email": candidate.get("email"),
                "resume_score": session.get("resume_score", 0),
                "coding_score": session.get("coding_score"),
                "ai_score": session.get("ai_score", 0),
                "num_questions": len(session.get("questions", [])),
                "completed": session.get("coding_score") is not None
            })
    
    return render_template("assessment.html", assessments=assessments_data)


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(400)
def bad_request(e):
    logger.warning(f"Bad request: {e}")
    return render_template('error.html', error="Bad Request", message="Invalid request"), 400


@app.errorhandler(404)
def not_found(e):
    logger.warning(f"Page not found: {request.path}")
    return render_template('error.html', error="Not Found", message="The requested page does not exist"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}", exc_info=True)
    if CONFIG.DEBUG:
        return f"Server Error: {e}", 500
    return render_template('error.html', error="Server Error", message="An unexpected error occurred"), 500


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    logger.info("Starting Hiring Assistant Application")
    app.run(
        host=CONFIG.HOST,
        port=CONFIG.PORT,
        debug=CONFIG.DEBUG,
        use_reloader=True
    )