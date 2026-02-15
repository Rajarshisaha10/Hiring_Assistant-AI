import json
import os
import random


BASE_DIR = os.path.dirname(__file__)
HR_QUESTIONS_PATH = os.path.join(BASE_DIR, "hr_questions.json")


def _load_hr_questions():
    """Load HR questions from the local JSON file."""
    if not os.path.exists(HR_QUESTIONS_PATH):
        return []

    with open(HR_QUESTIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


HR_QUESTIONS = _load_hr_questions()


def select_hr_questions(n=4):
    """
    Select HR questions randomly.
    
    Args:
        n: number of questions to return (default: 4)
    
    Returns:
        List of selected HR questions
    """
    if not HR_QUESTIONS:
        return []

    chosen = random.sample(HR_QUESTIONS, min(n, len(HR_QUESTIONS)))
    random.shuffle(chosen)
    return chosen
