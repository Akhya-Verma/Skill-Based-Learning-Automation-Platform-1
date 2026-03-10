import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import SPACY_MODEL, SKILLS_TAXONOMY_FILE

_nlp = None
_all_skills = []
_skills_lower_map = {}

# Project keywords that map to skills
PROJECT_SKILL_MAP = {
    "neural network":        "Deep Learning",
    "deep neural":           "Deep Learning",
    "convolutional":         "Deep Learning",
    "computer vision":       "Deep Learning",
    "image classification":  "Deep Learning",
    "object detection":      "Deep Learning",
    "recommendation engine": "Machine Learning",
    "recommendation system": "Machine Learning",
    "fraud detection":       "Machine Learning",
    "predictive model":      "Machine Learning",
    "classification model":  "Machine Learning",
    "regression model":      "Machine Learning",
    "clustering":            "Machine Learning",
    "natural language":      "NLP",
    "text classification":   "NLP",
    "sentiment analysis":    "NLP",
    "chatbot":               "NLP",
    "named entity":          "NLP",
    "data pipeline":         "Spark",
    "etl pipeline":          "Spark",
    "batch processing":      "Spark",
    "stream processing":     "Kafka",
    "event driven":          "Kafka",
    "message queue":         "Kafka",
    "microservice":          "Docker",
    "containerized":         "Docker",
    "rest api":              "FastAPI",
    "restful api":           "FastAPI",
    "web scraping":          "Python",
    "data scraping":         "Python",
    "automation script":     "Python",
    "dashboard":             "Tableau",
    "data visualization":    "Tableau",
    "cloud deployment":      "AWS",
    "deployed on cloud":     "AWS",
    "infrastructure":        "Terraform",
    "version control":       "Git",
    "source control":        "Git",
    "relational database":   "SQL",
    "database design":       "SQL",
    "data warehouse":        "SQL",
    "statistical analysis":  "Statistics",
    "hypothesis testing":    "Statistics",
    "a/b testing":           "Statistics",
    "data analysis":         "Data Analysis",
    "exploratory analysis":  "Data Analysis",
    "agile methodology":     "Agile",
    "scrum methodology":     "Agile",
    "sprint planning":       "Agile",
}


def _load_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load(SPACY_MODEL)
    return _nlp


def _load_taxonomy():
    global _all_skills, _skills_lower_map
    if not _all_skills:
        with open(SKILLS_TAXONOMY_FILE) as f:
            taxonomy = json.load(f)
        for skill_list in taxonomy.values():
            for skill in skill_list:
                _all_skills.append(skill)
                _skills_lower_map[skill.lower()] = skill
    return _all_skills


def extract_project_section(resume_text):
    """Extract the projects section from resume text."""
    lines      = resume_text.splitlines()
    collecting = False
    project_lines = []

    project_headers = [
        "project", "projects", "personal projects",
        "academic projects", "work projects", "key projects"
    ]
    stop_headers = [
        "education", "experience", "skills", "certifications",
        "awards", "publications", "references", "languages"
    ]

    for line in lines:
        line_lower = line.strip().lower()

        # Start collecting when we hit a projects section
        if any(line_lower == h or line_lower.startswith(h) for h in project_headers):
            collecting = True
            continue

        # Stop collecting when we hit another section
        if collecting and any(line_lower == h or line_lower.startswith(h) for h in stop_headers):
            break

        if collecting and line.strip():
            project_lines.append(line.strip())

    return "\n".join(project_lines)


def extract_skills_from_projects(project_text):
    """Infer skills from project descriptions using keyword mapping."""
    found = {}
    text_lower = project_text.lower()

    for keyword, skill in PROJECT_SKILL_MAP.items():
        if keyword in text_lower:
            if skill not in found:
                found[skill] = {
                    "skill":      skill,
                    "confidence": 0.8,
                    "method":     "project_inference"
                }

    return found


def extract_skills(resume_text):
    _load_taxonomy()
    nlp = _load_nlp()

    found = {}
    text_lower = resume_text.lower()

    # Pass 1 - Exact match against taxonomy
    for skill in _all_skills:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found[skill] = {
                "skill":      skill,
                "confidence": 1.0,
                "method":     "exact_match"
            }

    # Pass 2 - spaCy NLP
    doc = nlp(resume_text)

    for ent in doc.ents:
        canonical = _skills_lower_map.get(ent.text.lower().strip())
        if canonical and canonical not in found:
            found[canonical] = {
                "skill":      canonical,
                "confidence": 0.9,
                "method":     "ner"
            }

    for chunk in doc.noun_chunks:
        canonical = _skills_lower_map.get(chunk.text.lower().strip())
        if canonical and canonical not in found:
            found[canonical] = {
                "skill":      canonical,
                "confidence": 0.9,
                "method":     "noun_chunk"
            }

    for token in doc:
        canonical = _skills_lower_map.get(token.lemma_.lower())
        if canonical and canonical not in found:
            found[canonical] = {
                "skill":      canonical,
                "confidence": 0.85,
                "method":     "lemma"
            }

    # Pass 3 - Project section inference
    project_text = extract_project_section(resume_text)
    if project_text:
        project_skills = extract_skills_from_projects(project_text)
        for skill, data in project_skills.items():
            if skill not in found:
                found[skill] = data

    # Pass 4 - Full text project inference
    # catches projects even if not under a Projects heading
    full_text_skills = extract_skills_from_projects(resume_text)
    for skill, data in full_text_skills.items():
        if skill not in found:
            found[skill] = data

    return sorted(found.values(), key=lambda x: x["skill"])


def extract_skill_names(resume_text):
    return [s["skill"] for s in extract_skills(resume_text)]