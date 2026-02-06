"""
Hiring Orchestrator - Main Pipeline Coordinator

Coordinates the complete hiring pipeline:
1. Resume Analysis
2. Coding Assessment
3. Fraud Detection
4. Final Decision
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from resume.parser import extract_text
from resume.skill_extractor import extract_skills, extract_experience, count_projects
from resume.scorer import score_candidate
from resume.explain import generate_explanation
from project.question_selector import select_questions
from project.judge import score_coding_answers, execute_code
from fraud_detector import run_fraud_detection
from decision_engine import make_final_decision


def run_resume_analysis(resume_path: str, job_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Complete resume processing pipeline.
    
    Args:
        resume_path: Path to resume file
        job_config: Optional job requirements
    
    Returns:
        Resume analysis results
    """
    if job_config is None:
        job_config = {
            "skills": ["python", "fastapi", "sql", "docker", "aws"],
            "min_exp": 1
        }
    
    try:
        # Extract text from resume
        resume_text = extract_text(resume_path)
        
        # Extract information
        skills = extract_skills(resume_text)
        experience = extract_experience(resume_text)
        projects = count_projects(resume_text)
        
        # Prepare data
        data = {
            "skills": skills,
            "experience": experience,
            "projects": projects
        }
        
        # Calculate score
        score = score_candidate(data, job_config)
        
        # Generate explanation
        explanation = generate_explanation(score, data, job_config)
        
        return {
            "success": True,
            "resume_score": int(score),
            "skills": skills,
            "experience": experience,
            "projects": projects,
            "explanation": explanation,
            "resume_text_length": len(resume_text)
        }
        
    except Exception as e:
        return {
            "success": False,
            "resume_score": 0,
            "error": str(e),
            "skills": [],
            "experience": 0,
            "projects": 0
        }


def run_coding_assessment(
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete coding assessment with fraud detection.
    
    Args:
        questions: List of coding questions
        answers: List of submitted answers
        metadata: Optional timing and other metadata
    
    Returns:
        Coding assessment results with fraud analysis
    """
    if metadata is None:
        metadata = {}
    
    try:
        # Score the coding answers
        coding_score, test_results = score_coding_answers(questions, answers)
        
        # Prepare code submissions for fraud detection
        code_submissions = []
        for answer in answers:
            question = next((q for q in questions if q["id"] == answer["question_id"]), None)
            if question:
                code_submissions.append({
                    "question_id": answer["question_id"],
                    "code": answer["answer"],
                    "difficulty": question.get("difficulty", "medium")
                })
        
        # Run fraud detection
        fraud_analysis = run_fraud_detection(
            code_submissions=code_submissions,
            resume_data=metadata.get("resume_data", {}),
            timing_data=metadata.get("timing_data")
        )
        
        return {
            "success": True,
            "coding_score": coding_score,
            "test_results": test_results,
            "fraud_analysis": fraud_analysis,
            "total_tests": len(test_results),
            "passed_tests": sum(1 for r in test_results if r.get("passed")),
            "failed_tests": sum(1 for r in test_results if not r.get("passed"))
        }
        
    except Exception as e:
        return {
            "success": False,
            "coding_score": 0,
            "error": str(e),
            "test_results": [],
            "fraud_analysis": {"fraud_score": 0, "risk_level": "UNKNOWN"}
        }


def run_final_decision(all_data: Dict[str, Any], job_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate final hiring decision.
    
    Args:
        all_data: Complete candidate data
        job_config: Optional job requirements
    
    Returns:
        Final decision and recommendation
    """
    try:
        # Prepare candidate data for decision engine
        candidate_data = {
            "resume_score": all_data.get("resume_score", 0),
            "coding_score": all_data.get("coding_score"),
            "fraud_score": all_data.get("fraud_score", 0),
            "current_stage": all_data.get("current_stage", "Coding Assessment"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add job config with candidate skills
        if job_config:
            job_config["candidate_skills"] = all_data.get("skills", [])
        
        # Make final decision
        decision = make_final_decision(candidate_data, job_config)
        
        return {
            "success": True,
            "decision": decision
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "decision": None
        }


def process_application(
    resume_path: str,
    applicant_data: Dict[str, Any],
    job_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main orchestrator - runs complete hiring pipeline.
    
    This is the primary entry point for processing a new application.
    
    Args:
        resume_path: Path to uploaded resume
        applicant_data: Basic applicant info (name, email, etc.)
        job_config: Optional job requirements
    
    Returns:
        Complete pipeline results
    """
    pipeline_start = datetime.now()
    
    # Stage 1: Resume Analysis
    print(f"[ORCHESTRATOR] Stage 1: Analyzing resume from {resume_path}")
    resume_results = run_resume_analysis(resume_path, job_config)
    
    if not resume_results["success"]:
        return {
            "success": False,
            "stage": "Resume Analysis",
            "error": resume_results.get("error", "Resume analysis failed"),
            "resume_results": resume_results
        }
    
    resume_score = resume_results["resume_score"]
    print(f"[ORCHESTRATOR] Resume score: {resume_score}/100")
    
    # Stage 2: Question Selection
    print(f"[ORCHESTRATOR] Stage 2: Selecting coding questions based on score")
    questions = select_questions(resume_score, n=3)
    print(f"[ORCHESTRATOR] Selected {len(questions)} questions")
    
    # Prepare initial candidate data
    candidate_data = {
        "name": applicant_data.get("name"),
        "email": applicant_data.get("email"),
        "resume_score": resume_score,
        "skills": resume_results.get("skills", []),
        "experience": resume_results.get("experience", 0),
        "projects": resume_results.get("projects", 0),
        "questions": questions,
        "stage": "Coding Assessment",
        "status": "pending",
        "resume_filename": os.path.basename(resume_path),
        "resume_explanation": resume_results.get("explanation", {}),
        "pipeline_start_time": pipeline_start.isoformat()
    }
    
    return {
        "success": True,
        "stage": "Resume Analysis Complete",
        "candidate_data": candidate_data,
        "resume_results": resume_results,
        "questions": questions
    }


def complete_coding_assessment(
    candidate_data: Dict[str, Any],
    answers: List[Dict[str, Any]],
    submission_time: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Complete the coding assessment stage and generate final decision.
    
    Args:
        candidate_data: Existing candidate data from resume stage
        answers: Submitted coding answers
        submission_time: When the coding was submitted
    
    Returns:
        Complete assessment results with final decision
    """
    print(f"[ORCHESTRATOR] Stage 3: Evaluating coding submissions")
    
    # Prepare metadata for fraud detection
    metadata = {
        "resume_data": {
            "skills": candidate_data.get("skills", []),
            "experience": candidate_data.get("experience", 0),
            "projects": candidate_data.get("projects", 0)
        },
        "timing_data": {
            "start_time": datetime.fromisoformat(candidate_data.get("pipeline_start_time", datetime.now().isoformat())),
            "end_time": submission_time or datetime.now(),
            "difficulty": "medium",  # Could be calculated from questions
            "num_questions": len(candidate_data.get("questions", []))
        }
    }
    
    # Run coding assessment
    coding_results = run_coding_assessment(
        candidate_data.get("questions", []),
        answers,
        metadata
    )
    
    if not coding_results["success"]:
        return {
            "success": False,
            "stage": "Coding Assessment",
            "error": coding_results.get("error", "Coding assessment failed"),
            "coding_results": coding_results
        }
    
    coding_score = coding_results["coding_score"]
    fraud_score = coding_results["fraud_analysis"]["fraud_score"]
    
    print(f"[ORCHESTRATOR] Coding score: {coding_score}/100")
    print(f"[ORCHESTRATOR] Fraud risk score: {fraud_score}/100")
    
    # Stage 4: Final Decision
    print(f"[ORCHESTRATOR] Stage 4: Making final hiring decision")
    
    all_data = {
        "resume_score": candidate_data.get("resume_score", 0),
        "coding_score": coding_score,
        "fraud_score": fraud_score,
        "skills": candidate_data.get("skills", []),
        "current_stage": "Coding Assessment"
    }
    
    decision_results = run_final_decision(all_data)
    
    if not decision_results["success"]:
        return {
            "success": False,
            "stage": "Final Decision",
            "error": decision_results.get("error", "Decision making failed"),
            "decision_results": decision_results
        }
    
    print(f"[ORCHESTRATOR] Final decision: {decision_results['decision']['recommendation']['decision']}")
    
    # Combine all results
    return {
        "success": True,
        "stage": "Complete",
        "coding_results": coding_results,
        "decision_results": decision_results,
        "final_scores": {
            "resume_score": candidate_data.get("resume_score", 0),
            "coding_score": coding_score,
            "fraud_score": fraud_score,
            "final_score": decision_results["decision"]["final_score"]
        }
    }


def get_pipeline_status(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current status of a candidate in the pipeline.
    
    Args:
        candidate_data: Candidate information
    
    Returns:
        Current status and next steps
    """
    return {
        "current_stage": candidate_data.get("stage", "Unknown"),
        "status": candidate_data.get("status", "Unknown"),
        "resume_score": candidate_data.get("resume_score"),
        "coding_score": candidate_data.get("coding_score"),
        "next_step": "Complete coding assessment" if candidate_data.get("coding_score") is None else "Review results"
    }
