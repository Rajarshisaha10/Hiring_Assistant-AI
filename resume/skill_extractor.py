# skill_extractor.py

import re

# Extend this list anytime
KNOWN_SKILLS = [
    "python", "django", "fastapi", "flask",
    "sql", "postgresql", "mysql",
    "docker", "kubernetes",
    "aws", "gcp",
    "react", "node", "api", "rest",
    "machine learning", "pandas", "numpy"
]


def extract_skills(text: str):
    found = []

    for skill in KNOWN_SKILLS:
        if skill in text:
            found.append(skill)

    return list(set(found))


def extract_experience(text: str):
    """
    Matches:
    3 years
    2+ years
    5 yrs
    """
    matches = re.findall(r'(\d+)\s*\+?\s*(years|yrs)', text)

    if not matches:
        return 0

    years = [int(m[0]) for m in matches]
    return max(years)


def count_projects(text: str):
    keywords = ["project", "built", "developed", "created"]
    return sum(text.count(k) for k in keywords)