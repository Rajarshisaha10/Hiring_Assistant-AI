# scorer.py

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(candidate_skills, required_skills):
    if not candidate_skills:
        return 0

    cand_embed = model.encode(" ".join(candidate_skills), convert_to_tensor=True)
    req_embed = model.encode(" ".join(required_skills), convert_to_tensor=True)

    score = util.cos_sim(cand_embed, req_embed).item()

    return max(score, 0)


def score_candidate(data, job_config):
    """
    data = {
        skills,
        experience,
        projects
    }
    """

    skill_sim = semantic_similarity(data["skills"], job_config["skills"])

    skill_score = skill_sim * 50

    exp_score = min(data["experience"] / job_config["min_exp"], 1) * 25

    project_score = min(data["projects"], 5) / 5 * 15

    final = skill_score + exp_score + project_score

    return round(final, 2)