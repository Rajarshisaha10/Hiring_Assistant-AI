from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Set third-party library logging levels
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
logging.getLogger('transformers').setLevel(logging.WARNING)
logging.getLogger('torch').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from project.question_selector import select_questions
from project.hr_selector import select_hr_questions
from project.judge import score_resume, score_coding_answers


app = FastAPI(title="AI Hiring Assistant API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'resume')
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logger.info("FastAPI initialized")


# =========================================================
# PYDANTIC MODELS
# =========================================================

class AdminLoginRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class CodingAnswer(BaseModel):
    question_id: int
    answer: str

class CodingSubmission(BaseModel):
    answers: List[CodingAnswer]

class HRAnswer(BaseModel):
    question_id: int
    answer: str

class HRSubmission(BaseModel):
    answers: List[HRAnswer]


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


def compute_final_score(resume_score: int, coding_score: Optional[int], hr_score: Optional[int]) -> tuple[int, str]:
    """
    Calculate final score based on 3 phases:
    - Resume Score: 30%
    - Coding Score: 40%
    - HR Score: 30%
    """
    scores = []
    weights = []
    
    if resume_score is not None:
        scores.append(resume_score)
        weights.append(0.30)
    
    if coding_score is not None:
        scores.append(coding_score)
        weights.append(0.40)
    
    if hr_score is not None:
        scores.append(hr_score)
        weights.append(0.30)
    
    # Normalize weights if not all phases are complete
    if weights:
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        final_score = sum(s * w for s, w in zip(scores, weights))
    else:
        final_score = 0
    
    final_score = int(final_score)
    
    if final_score >= 80:
        verdict = "Strong match - highly recommended"
    elif final_score >= 65:
        verdict = "Good match - recommended"
    elif final_score >= 50:
        verdict = "Moderate match - consider"
    elif final_score >= 40:
        verdict = "Below average - manual review"
    else:
        verdict = "Poor match - not recommended"
    
    return final_score, verdict


def get_candidate_by_id(cid):
    for c in CANDIDATES_DB:
        if c["id"] == cid:
            return c
    return None


def format_questions_for_ui(questions):
    """Transform questions from storage format to UI format"""
    formatted = []
    for q in questions:
        formatted_q = {
            "id": q.get("id"),
            "question": q.get("description") or q.get("title"),  # Use description, fallback to title
            "title": q.get("title"),
            "difficulty": q.get("difficulty"),
            "function_signature": q.get("function_signature"),
            "topic": q.get("topic")
        }
        formatted.append(formatted_q)
    return formatted


# =========================================================
# API ROUTES
# =========================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}


# =========================================================
# ADMIN API
# =========================================================

@app.post("/api/auth/admin")
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    return {"success": True, "role": "admin"}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total = len(CANDIDATES_DB)

    stats = {
        "total": total,
        "approved": len([c for c in CANDIDATES_DB if c.get("status") == "approved"]),
        "rejected": len([c for c in CANDIDATES_DB if c.get("status") == "rejected"]),
        "pending": len([c for c in CANDIDATES_DB if c.get("status") == "pending"]),
        "avg_score": round(sum([c.get("ai_score", 0) for c in CANDIDATES_DB]) / total, 1)
        if total else 0
    }

    return {
        "stats": stats,
        "candidates": CANDIDATES_DB
    }


# =========================================================
# APPLICANT API
# =========================================================

@app.post("/api/applicant/submit")
async def submit_application(
    name: str = Form(...),
    email: str = Form(...),
    resume: Optional[UploadFile] = File(None)
):
    """Submit applicant application with resume"""
    try:
        resume_path = None
        filename = None

        if resume:
            filename = resume.filename
            resume_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save uploaded file
            with open(resume_path, "wb") as buffer:
                content = await resume.read()
                buffer.write(content)

        # Use hiring orchestrator for complete pipeline
        try:
            from hiring_orchestrator import process_application
            
            applicant_data = {
                "name": name,
                "email": email
            }
            
            pipeline_result = process_application(resume_path, applicant_data)
            
            if not pipeline_result["success"]:
                # Fallback to basic processing
                resume_score = score_resume(resume_path) if resume_path else 50
                ai_score, verdict = compute_ai_score_and_verdict(resume_score, None)
                questions = select_questions(resume_score, n=3)
            else:
                candidate_data = pipeline_result["candidate_data"]
                resume_score = candidate_data["resume_score"]
                ai_score, verdict = compute_ai_score_and_verdict(resume_score, None)
                questions = candidate_data["questions"]
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            resume_score = score_resume(resume_path) if resume_path else 50
            ai_score, verdict = compute_ai_score_and_verdict(resume_score, None)
            questions = select_questions(resume_score, n=3)

        applicant_id = len(APPLICANTS_DB) + 1

        # Store complete applicant data
        applicant_record = {
            "id": applicant_id,
            "name": name,
            "email": email,
            "resume_score": resume_score,
            "ai_score": ai_score,
            "ai_verdict": verdict,
            "status": "pending",
            "stage": "Coding Assessment",
            "resume_filename": filename
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
            "coding_test_results": [],
            "hr_questions": select_hr_questions(n=4),
            "hr_score": None,
            "hr_answers": {},
            "ai_score": ai_score,
            "final_score": None,
            "candidate_id": candidate_id,
            "assessment_stage": "coding"  # Track which phase: coding, hr, completed
        }

        return {
            "success": True,
            "applicant_id": applicant_id,
            "applicant": applicant_record
        }

    except Exception as e:
        logger.error(f"Application submission error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applicant/{applicant_id}")
async def get_applicant(applicant_id: int):
    """Get applicant data"""
    applicant = next((a for a in APPLICANTS_DB if a["id"] == applicant_id), None)
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    return applicant


@app.get("/api/applicant/{applicant_id}/coding")
async def get_coding_questions(applicant_id: int):
    """Get coding questions for applicant"""
    session_state = CODING_SESSIONS.get(applicant_id)

    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")

    formatted_questions = format_questions_for_ui(session_state["questions"])

    return {
        "questions": formatted_questions,
        "resume_score": session_state["resume_score"],
        "coding_score": session_state["coding_score"],
        "ai_score": session_state["ai_score"],
        "test_results": session_state["coding_test_results"],
        "assessment_stage": session_state["assessment_stage"]
    }


@app.post("/api/applicant/{applicant_id}/coding")
async def submit_coding_answers(applicant_id: int, submission: CodingSubmission):
    """Submit coding answers"""
    session_state = CODING_SESSIONS.get(applicant_id)

    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")

    # Convert Pydantic models to dict format expected by judge
    answers = [{"question_id": ans.question_id, "answer": ans.answer} 
               for ans in submission.answers]

    questions = session_state["questions"]

    result = score_coding_answers(questions, answers)

    if isinstance(result, tuple):
        coding_score, test_details = result
    else:
        coding_score = result
        test_details = []

    # Store results
    session_state["coding_score"] = coding_score
    session_state["coding_test_results"] = test_details
    session_state["assessment_stage"] = "hr"

    # Update candidate
    candidate = get_candidate_by_id(session_state["candidate_id"])

    if candidate:
        candidate["coding_score"] = coding_score

    hr_questions = [
        {
            "id": q.get("id"),
            "question": q.get("question"),
            "category": q.get("category"),
            "type": q.get("type")
        }
        for q in session_state["hr_questions"]
    ]

    return {
        "success": True,
        "coding_score": coding_score,
        "test_results": test_details,
        "next_stage": "hr",
        "hr_questions": hr_questions
    }


@app.get("/api/applicant/{applicant_id}/hr")
async def get_hr_questions(applicant_id: int):
    """Get HR questions for applicant"""
    session_state = CODING_SESSIONS.get(applicant_id)

    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")

    hr_questions = [
        {
            "id": q.get("id"),
            "question": q.get("question"),
            "category": q.get("category"),
            "type": q.get("type")
        }
        for q in session_state["hr_questions"]
    ]

    return {
        "hr_questions": hr_questions,
        "coding_score": session_state["coding_score"],
        "assessment_stage": session_state["assessment_stage"]
    }


@app.post("/api/applicant/{applicant_id}/hr")
async def submit_hr_answers(applicant_id: int, submission: HRSubmission):
    """Submit HR answers and generate final score"""
    session_state = CODING_SESSIONS.get(applicant_id)

    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")

    # Convert answers to dict format
    hr_answers = {ans.question_id: ans.answer for ans in submission.answers}
    session_state["hr_answers"] = hr_answers

    # Calculate HR score based on response quality/length (0-100)
    # This is a simple heuristic - in production you'd use NLP/ML
    hr_score = calculate_hr_score(hr_answers)
    session_state["hr_score"] = hr_score

    # Calculate final score using all 3 phases
    final_score, final_verdict = compute_final_score(
        session_state["resume_score"],
        session_state["coding_score"],
        hr_score
    )

    session_state["final_score"] = final_score
    session_state["assessment_stage"] = "completed"

    # Update candidate with final results
    candidate = get_candidate_by_id(session_state["candidate_id"])
    if candidate:
        candidate["hr_score"] = hr_score
        candidate["final_score"] = final_score
        candidate["status"] = "completed"

    return {
        "success": True,
        "hr_score": hr_score,
        "final_score": final_score,
        "final_verdict": final_verdict,
        "breakdown": {
            "resume_score": session_state["resume_score"],
            "coding_score": session_state["coding_score"],
            "hr_score": hr_score,
            "final_score": final_score
        }
    }


def calculate_hr_score(hr_answers: dict) -> int:
    """
    Calculate HR score based on response quality.
    This is a simplified heuristic - in production use NLP/ML models.
    
    Scoring criteria:
    - Response length (more detailed = higher score)
    - Number of responses provided
    """
    if not hr_answers:
        return 0

    total_score = 0
    num_answers = 0

    for question_id, answer in hr_answers.items():
        if answer and isinstance(answer, str):
            num_answers += 1
            # Award points based on response length
            word_count = len(answer.split())
            
            if word_count >= 50:
                score = 100
            elif word_count >= 30:
                score = 85
            elif word_count >= 15:
                score = 70
            elif word_count >= 5:
                score = 50
            else:
                score = 20
            
            total_score += score

    if num_answers == 0:
        return 0

    hr_score = int(total_score / num_answers)
    return min(max(hr_score, 0), 100)


# =========================================================
# CANDIDATE MANAGEMENT API
# =========================================================

@app.get("/api/candidates")
async def get_candidates():
    """Get all candidates"""
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
    
    return all_candidates


@app.get("/api/candidate/{candidate_id}")
async def get_candidate_detail(candidate_id: int):
    """Get individual candidate details"""
    candidate = get_candidate_by_id(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
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
    
    return full_profile


@app.get("/api/assessments")
async def get_assessments():
    """Get all assessments"""
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
    
    return assessments_data


@app.get("/api/jobs")
async def get_jobs():
    """Get all jobs"""
    return JOBS_DB


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Hiring Assistant API with FastAPI")
    uvicorn.run(
        app,
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 5000)),
        log_level="info"
    )