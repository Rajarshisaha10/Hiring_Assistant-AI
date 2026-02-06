import json
import os
import random


BASE_DIR = os.path.dirname(__file__)
QUESTIONS_PATH = os.path.join(BASE_DIR, "questions.json")


def _load_questions():
    """Load coding questions from the local JSON file."""
    if not os.path.exists(QUESTIONS_PATH):
        return []

    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


QUESTIONS = _load_questions()


def select_questions(score, n=3):
    """
    Select a small set of coding questions based on a resume score.

    - score: 0–100
    - n: number of questions to return
    """
    if not QUESTIONS:
        return []

    if score >= 70:
        level = "hard"
    elif score >= 40:
        level = "medium"
    else:
        level = "easy"

    pool = [q for q in QUESTIONS if q.get("difficulty") == level]

    if not pool:
        pool = QUESTIONS

    chosen = random.sample(pool, min(n, len(pool)))
    random.shuffle(chosen)
    return chosen