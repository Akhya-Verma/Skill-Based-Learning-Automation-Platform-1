import sys
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import SENTENCE_TRANSFORMER, SIMILARITY_THRESHOLD

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(SENTENCE_TRANSFORMER)
    return _model


def match_skills(employee_skills, required_skills, optional_skills):
    model = _get_model()

    emp_embeddings = model.encode(employee_skills) if employee_skills else np.array([])

    def _check(role_skills):
        matched, missing = [], []
        for rs in role_skills:
            if not employee_skills:
                missing.append(rs)
                continue
            rs_emb = model.encode([rs])
            sims   = cosine_similarity(rs_emb, emp_embeddings)[0]
            best_i = int(np.argmax(sims))
            best_s = float(sims[best_i])
            if best_s >= SIMILARITY_THRESHOLD:
                matched.append({
                    "role_skill":     rs,
                    "employee_skill": employee_skills[best_i],
                    "similarity":     round(best_s, 3),
                })
            else:
                missing.append(rs)
        return matched, missing

    matched_req, missing_req = _check(required_skills)
    matched_opt, missing_opt = _check(optional_skills)

    req_coverage = len(matched_req) / len(required_skills) if required_skills else 1.0
    opt_coverage = len(matched_opt) / len(optional_skills) if optional_skills else 1.0

    final_score = (req_coverage * 0.85 + opt_coverage * 0.15) if optional_skills else req_coverage

    return {
        "match_score":       round(final_score, 4),
        "matched":           matched_req,
        "missing":           missing_req,
        "optional_matched":  matched_opt,
        "optional_gaps":     missing_opt,
        "required_coverage": round(req_coverage, 4),
        "optional_coverage": round(opt_coverage, 4),
    }