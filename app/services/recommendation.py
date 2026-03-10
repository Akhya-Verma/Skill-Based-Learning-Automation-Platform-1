import json
import sys
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import TRAINING_DATA_FILE, SENTENCE_TRANSFORMER

_model = None
_modules_cache = None
_DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(SENTENCE_TRANSFORMER)
    return _model


def _load_modules():
    global _modules_cache
    if _modules_cache is None:
        with open(TRAINING_DATA_FILE) as f:
            _modules_cache = json.load(f)
    return _modules_cache


def recommend_modules(missing_skills, top_n=2):
    all_modules = _load_modules()
    recommendations = {}

    for skill in missing_skills:
        # Try exact match first
        exact = [m for m in all_modules if m["skill"].lower() == skill.lower()]

        if exact:
            modules = exact
        else:
            # Fall back to semantic search
            modules = _semantic_search(skill, all_modules, top_n)

        modules = sorted(modules, key=lambda m: _DIFFICULTY_ORDER.get(m.get("difficulty", "beginner"), 0))
        recommendations[skill] = modules[:top_n]

    return recommendations


def _semantic_search(skill, all_modules, top_n):
    model  = _get_model()
    names  = [m["skill"] for m in all_modules]
    embs   = model.encode(names)
    s_emb  = model.encode([skill])
    sims   = cosine_similarity(s_emb, embs)[0]
    top_idx = np.argsort(sims)[::-1][:top_n]
    return [all_modules[i] for i in top_idx if sims[i] > 0.4]