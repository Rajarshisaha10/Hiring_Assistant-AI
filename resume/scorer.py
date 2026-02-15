# scorer.py

import logging
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

# Lazy load the model to avoid loading issues in production
_model = None


def get_model():
    """Lazy load the model on first use"""
    global _model
    if _model is None:
        try:
            logger.info("Loading sentence transformer model...")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    return _model


def semantic_similarity(candidate_skills, required_skills):
    try:
        if not candidate_skills:
            return 0

        model = get_model()
        cand_embed = model.encode(" ".join(candidate_skills), convert_to_tensor=True)
        req_embed = model.encode(" ".join(required_skills), convert_to_tensor=True)

        score = util.cos_sim(cand_embed, req_embed).item()

        return max(score, 0)
    except Exception as e:
        logger.error(f"Error computing semantic similarity: {e}")
        return 0


def score_candidate(data, job_config):
    """
    Score a candidate based on their profile

    data = {
        skills,
        experience,
        projects
    }
    """
    try:
        skill_sim = semantic_similarity(data["skills"], job_config["skills"])

        skill_score = skill_sim * 50

        exp_score = min(data["experience"] / job_config["min_exp"], 1) * 25

        project_score = min(data["projects"], 5) / 5 * 15

        final = skill_score + exp_score + project_score

        return round(final, 2)
    except Exception as e:
        logger.error(f"Error scoring candidate: {e}")
        return 0