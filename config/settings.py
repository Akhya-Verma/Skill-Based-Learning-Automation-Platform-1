import pathlib

# AI Models
SPACY_MODEL          = "en_core_web_md"
SENTENCE_TRANSFORMER = "all-MiniLM-L6-v2"

# Skill Matching
SIMILARITY_THRESHOLD = 0.65

# Learning Path
HOURS_PER_WEEK = 5

# File paths
BASE_DIR             = pathlib.Path(__file__).parent.parent
TRAINING_DATA_FILE   = BASE_DIR / "data" / "training_modules.json"
SKILLS_TAXONOMY_FILE = BASE_DIR / "data" / "skills_taxonomy.json"
SAMPLE_ROLES_FILE    = BASE_DIR / "data" / "sample_roles.json"