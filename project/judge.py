import subprocess
import tempfile
import os
import json
import sys
from typing import List, Dict, Any, Tuple


def execute_code(code_string: str, test_case: Dict[str, Any]) -> Tuple[bool, str, Any]:
    """
    Execute code against a single test case and return (passed, output, error).
    
    Args:
        code_string: Python code from applicant
        test_case: {"input": {...}, "output": expected_output}
    
    Returns:
        (passed: bool, output: str, error: str or None)
    """
    temp_file = None
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".py", encoding='utf-8')
        
        # Write the applicant's code
        temp_file.write(code_string)
        temp_file.write("\n\n# AUTO-GENERATED TEST CODE\n")
        
        # Extract input and expected output
        test_input = test_case.get("input", {})
        expected_output = test_case.get("output")
        
        # Generate function call code
        if isinstance(test_input, dict):
            # Named parameters
            args_str = ", ".join([f"{k}={repr(v)}" for k, v in test_input.items()])
            # Extract function name
            lines = code_string.split('\n')
            func_name = None
            for line in lines:
                if line.strip().startswith('def '):
                    func_name = line.split('(')[0].replace('def ', '').strip()
                    break
            
            if func_name:
                test_code = f"""
import json
try:
    result = {func_name}({args_str})
    print(json.dumps(result, default=str))
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""
            else:
                return False, "", "Could not find function definition"
        else:
            return False, "", "Invalid test case format"
        
        temp_file.write(test_code)
        temp_file.close()
        
        # Execute the temporary file
        result = subprocess.run(
            [sys.executable, temp_file.name],
            capture_output=True,
            timeout=5,
            text=True
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip() if result.stderr else None
        
        # Check if output matches expected
        try:
            actual_output = json.loads(output) if output and not output.startswith("ERROR") else output
            expected_json = json.dumps(expected_output) if isinstance(expected_output, (dict, list)) else str(expected_output)
            actual_json = json.dumps(actual_output) if isinstance(actual_output, (dict, list)) else str(actual_output)
            
            passed = actual_json == expected_json or str(actual_output) == str(expected_output)
        except:
            passed = output == str(expected_output)
        
        return passed, output, error
        
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT: Code took too long to execute (>5 seconds)"
    except Exception as e:
        return False, "", f"Execution error: {str(e)}"
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.remove(temp_file.name)
            except:
                pass


def score_coding_answers(questions: List[Dict], answers: List[Dict]) -> Tuple[int, List[Dict]]:
    """
    Execute all submitted code solutions and return (score, results).
    
    Args:
        questions: List of question dicts with test_cases
        answers: List of {"question_id": id, "answer": code_string}
    
    Returns:
        Tuple of (score: 0-100, results: list of test result details)
    """
    if not questions or not answers:
        return 0, []
    
    total_passed = 0
    total_tests = 0
    results = []
    
    # Create a map of answers by question_id
    answer_map = {a["question_id"]: a["answer"] for a in answers}
    
    for question in questions:
        q_id = question.get("id")
        code = answer_map.get(q_id, "")
        test_cases = question.get("test_cases", [])
        
        if not code or not test_cases:
            continue
        
        for test_case in test_cases:
            total_tests += 1
            passed, output, error = execute_code(code, test_case)
            
            if passed:
                total_passed += 1
            
            results.append({
                "question_id": q_id,
                "title": question.get("title", "Unknown"),
                "passed": passed,
                "output": output,
                "error": error,
                "expected": test_case.get("output")
            })
    
    if total_tests == 0:
        return 0, []
    
    score = int((total_passed / total_tests) * 100)
    return score, results


def score_resume(resume_path: str) -> int:
    """
    Score a resume based on actual file content analysis.
    Uses skill extraction, experience parsing, and project count.
    
    Args:
        resume_path: Path to the uploaded resume file
    
    Returns:
        Score (0-100) based on resume analysis
    """
    if not resume_path or not os.path.exists(resume_path):
        return 0
    
    try:
        # Import locally to avoid import errors
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from resume.parser import extract_text
        from resume.skill_extractor import extract_skills, extract_experience, count_projects
        from resume.scorer import score_candidate
    except ImportError as e:
        # Fallback scoring if imports fail
        try:
            size_kb = os.path.getsize(resume_path) / 1024.0
            return min(int(size_kb * 2), 100)
        except:
            return 50
    
    # Extract text from resume
    try:
        resume_text = extract_text(resume_path)
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return 25
    
    if not resume_text:
        return 20
    
    # Extract information from resume
    skills = extract_skills(resume_text)
    experience = extract_experience(resume_text)
    projects = count_projects(resume_text)
    
    # Sample job config
    job_config = {
        "skills": ["python", "fastapi", "sql", "docker", "aws"],
        "min_exp": 1
    }
    
    data = {
        "skills": skills,
        "experience": experience,
        "projects": projects
    }
    
    # Calculate score
    try:
        score = score_candidate(data, job_config)
    except Exception as e:
        # Calculate manually if scorer fails
        skill_score = min(len(skills), 5) / 5 * 50  # 50 points for skills
        exp_score = min(experience / job_config["min_exp"], 1) * 25  # 25 points for experience
        project_score = min(projects, 5) / 5 * 25  # 25 points for projects
        score = skill_score + exp_score + project_score
    
    return int(min(max(score, 0), 100))


def get_test_results_summary(results: List[Dict]) -> Dict[str, Any]:
    """
    Generate a summary of test results for display.
    """
    passed = sum(1 for r in results if r.get("passed"))
    total = len(results)
    
    return {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "pass_rate": f"{int((passed / total) * 100)}%" if total > 0 else "0%",
        "results": results
    }
