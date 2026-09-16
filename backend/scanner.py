
import ast
import re
import numpy as np

from functools import lru_cache
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_WEIGHTS = {
    "skills": 0.60,
    "semantic": 0.20,
    "experience": 0.10,
    "education": 0.10
}

DEFAULT_THRESHOLD = 80


SKILL_ALIASES = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "powerbi": "power bi",
    "power-bi": "power bi",
    "sklearn": "scikit learn",
    "scikit-learn": "scikit learn",
    "tf": "tensorflow",
    "js": "javascript",
    "nodejs": "node.js",
    "node js": "node.js",
    "reactjs": "react",
    "react js": "react",

    "nlp": "natural language processing",
    "natural language processing": "natural language processing",

    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",

    "ml": "machine learning",
    "machine learning": "machine learning",

    "llm": "large language models",
    "llms": "large language models",
    "large language model": "large language models",
    "large language models": "large language models",

    "rag": "retrieval augmented generation",
    "retrieval augmented generation": "retrieval augmented generation",

    "huggingface": "hugging face",
    "hugging face": "hugging face",

    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "google cloud": "google cloud",

    "powerbi": "power bi",
    "power bi": "power bi",

    "sklearn": "scikit learn",
    "scikit-learn": "scikit learn",
    "scikit learn": "scikit learn"
}


# ============================================================
# LOAD TRANSFORMER MODEL
# Loads once and is reused
# ============================================================

@lru_cache(maxsize=1)
def get_model():

    return SentenceTransformer(
        MODEL_NAME
    )


# ============================================================
# BASIC HELPERS
# ============================================================

def parse_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    text = str(value).strip()

    if not text:
        return []

    try:

        parsed = ast.literal_eval(text)

        if isinstance(parsed, (list, tuple, set)):
            return list(parsed)

    except:
        pass

    return [
        part.strip()
        for part in re.split(
            r"[\n,;]+",
            text
        )
        if part.strip()
    ]


def normalize_skill(skill):

    skill = str(skill).lower().strip()

    skill = skill.replace(
        "_",
        " "
    )

    skill = skill.replace(
        "-",
        " "
    )

    skill = re.sub(
        r"[^a-z0-9+#. ]",
        " ",
        skill
    )

    skill = re.sub(
        r"\s+",
        " ",
        skill
    ).strip()

    return SKILL_ALIASES.get(
        skill,
        skill
    )


def unique_skills(skills):

    result = []
    seen = set()

    for skill in skills:

        clean_skill = str(
            skill
        ).strip()

        if not clean_skill:
            continue

        normalized = normalize_skill(
            clean_skill
        )

        if normalized not in seen:

            seen.add(
                normalized
            )

            result.append(
                clean_skill
            )

    return result


# ============================================================
# SKILL MATCHING
# ============================================================

def compare_skills(
    candidate_skills,
    required_skills
):

    candidate_skills = unique_skills(
        parse_list(
            candidate_skills
        )
    )

    required_skills = unique_skills(
        parse_list(
            required_skills
        )
    )

    if len(required_skills) == 0:

        return 100.0, [], []

    matches = []
    missing = []

    candidate_normalized = [
        normalize_skill(skill)
        for skill in candidate_skills
    ]

    for required_skill in required_skills:

        required_normalized = normalize_skill(
            required_skill
        )

        best_score = 0
        best_candidate_skill = None

        for original_skill, candidate_normalized_skill in zip(
            candidate_skills,
            candidate_normalized
        ):

            if len(required_normalized) <= 2:

                score = (
                    100
                    if required_normalized
                    == candidate_normalized_skill
                    else 0
                )

            else:

                score = fuzz.token_set_ratio(
                    required_normalized,
                    candidate_normalized_skill
                )

            if score > best_score:

                best_score = score
                best_candidate_skill = original_skill

        if best_score >= 80:

            matches.append({
                "required_skill":
                    required_skill,

                "candidate_skill":
                    best_candidate_skill,

                "score":
                    round(
                        float(best_score),
                        2
                    )
            })

        else:

            missing.append(
                required_skill
            )

    skill_score = (
        len(matches)
        /
        len(required_skills)
        *
        100
    )

    return (
        round(
            skill_score,
            2
        ),
        matches,
        missing
    )


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def extract_required_experience(
    text
):

    text = str(
        text
    ).lower().strip()

    if not text:

        return None

    if any(
        word in text
        for word in [
            "fresher",
            "fresh graduate",
            "no experience"
        ]
    ):

        return 0

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        text
    )

    if not numbers:

        return None

    return float(
        numbers[0]
    )


def experience_score(
    candidate_years,
    requirement
):

    try:

        candidate_years = float(
            candidate_years
        )

    except:

        candidate_years = 0


    required_years = extract_required_experience(
        requirement
    )

    if required_years is None:

        return 100.0

    if required_years == 0:

        return 100.0

    score = (
        candidate_years
        /
        required_years
        *
        100
    )

    return round(
        min(
            score,
            100
        ),
        2
    )


# ============================================================
# EDUCATION MATCHING
# ============================================================

def get_education_level(
    text
):

    text = str(
        text
    ).lower()

    if any(
        word in text
        for word in [
            "phd",
            "ph.d",
            "doctorate"
        ]
    ):

        return 4

    if any(
        word in text
        for word in [
            "master",
            "msc",
            "m.sc",
            "mba",
            "m.tech",
            "mtech"
        ]
    ):

        return 3

    if any(
        word in text
        for word in [
            "bachelor",
            "bsc",
            "b.sc",
            "b.tech",
            "btech",
            "b.e",
            "undergraduate"
        ]
    ):

        return 2

    if "diploma" in text:

        return 1

    return None


def education_score(
    candidate_education,
    job_requirement
):

    job_requirement = str(
        job_requirement
    ).strip()

    if not job_requirement:

        return 100.0

    candidate_level = get_education_level(
        candidate_education
    )

    required_level = get_education_level(
        job_requirement
    )

    if required_level is None:

        return 100.0

    if candidate_level is None:

        return 0.0

    if candidate_level >= required_level:

        return 100.0

    return round(
        (
            candidate_level
            /
            required_level
        )
        *
        100,
        2
    )


# ============================================================
# TOP 3 MATCHING SKILLS
# ============================================================

def get_top_3_skills(
    matches
):

    if not matches:

        return []

    sorted_matches = sorted(
        matches,
        key=lambda x:
            x["score"],
        reverse=True
    )

    result = []
    seen = set()

    for match in sorted_matches:

        skill = match[
            "candidate_skill"
        ]

        normalized = normalize_skill(
            skill
        )

        if normalized not in seen:

            seen.add(
                normalized
            )

            result.append(
                skill
            )

        if len(result) == 3:
            break

    return result


# ============================================================
# BUILD STANDARD TEXT
# ============================================================

def build_candidate_text(
    candidate
):

    if candidate.get(
        "candidate_text"
    ):

        return str(
            candidate[
                "candidate_text"
            ]
        )

    skills = ", ".join(
        parse_list(
            candidate.get(
                "skills",
                []
            )
        )
    )

    education = str(
        candidate.get(
            "education",
            ""
        )
    )

    positions = ", ".join(
        parse_list(
            candidate.get(
                "positions",
                []
            )
        )
    )

    summary = str(
        candidate.get(
            "summary",
            ""
        )
    )

    return f"""
Candidate Profile

Summary:
{summary}

Skills:
{skills}

Education:
{education}

Previous Positions:
{positions}
""".strip()


def build_job_text(
    job
):

    if job.get(
        "job_text"
    ):

        return str(
            job[
                "job_text"
            ]
        )

    required_skills = ", ".join(
        parse_list(
            job.get(
                "required_skills",
                []
            )
        )
    )

    job_title = str(
        job.get(
            "job_title",
            ""
        )
    )

    responsibilities = str(
        job.get(
            "responsibilities",
            ""
        )
    )

    education_requirement = str(
        job.get(
            "education_requirement",
            ""
        )
    )

    experience_requirement = str(
        job.get(
            "experience_requirement",
            ""
        )
    )

    return f"""
Job Title:
{job_title}

Required Skills:
{required_skills}

Responsibilities:
{responsibilities}

Education Requirement:
{education_requirement}

Experience Requirement:
{experience_requirement}
""".strip()


# ============================================================
# SEMANTIC MATCHING
# ============================================================

def semantic_score(
    candidate_text,
    job_text
):

    model = get_model()

    embeddings = model.encode(
        [
            candidate_text,
            job_text
        ],
        normalize_embeddings=True
    )

    similarity = float(
        embeddings[0]
        @
        embeddings[1]
    )

    score = np.clip(
        similarity * 100,
        0,
        100
    )

    return round(
        float(score),
        2
    )


# ============================================================
# MAIN SCANNER
# ============================================================

def scan_candidate(
    candidate,
    job,
    threshold=DEFAULT_THRESHOLD,
    weights=None
):

    if weights is None:

        weights = DEFAULT_WEIGHTS


    candidate_skills = candidate.get(
        "skills",
        []
    )

    required_skills = job.get(
        "required_skills",
        []
    )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skill_score, matches, missing = compare_skills(
        candidate_skills,
        required_skills
    )


    # --------------------------------------------------------
    # Semantic Transformer Score
    # --------------------------------------------------------

    candidate_text = build_candidate_text(
        candidate
    )

    job_text = build_job_text(
        job
    )

    semantic_match_score = semantic_score(
        candidate_text,
        job_text
    )


    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    exp_score = experience_score(

        candidate.get(
            "experience_years",
            0
        ),

        job.get(
            "experience_requirement",
            ""
        )
    )


    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    edu_score = education_score(

        candidate.get(
            "education",
            ""
        ),

        job.get(
            "education_requirement",
            ""
        )
    )


    # --------------------------------------------------------
    # Final Score
    # --------------------------------------------------------

    final_score = (

        skill_score
        *
        weights[
            "skills"
        ]

        +

        semantic_match_score
        *
        weights[
            "semantic"
        ]

        +

        exp_score
        *
        weights[
            "experience"
        ]

        +

        edu_score
        *
        weights[
            "education"
        ]
    )


    final_score = round(
        float(final_score),
        2
    )


    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    passed = (
        final_score
        >=
        threshold
    )


    if passed:

        status = (
            "Passed First Phase - "
            "Qualified for Actual Interview"
        )

        top_skills = get_top_3_skills(
            matches
        )

    else:

        status = "Not Passed"

        top_skills = []


    # --------------------------------------------------------
    # Final Result
    # --------------------------------------------------------

    return {

        "candidate_id":
            candidate.get(
                "candidate_id",
                "UNKNOWN"
            ),

        "job_title":
            job.get(
                "job_title",
                ""
            ),

        "final_match_score":
            final_score,

        "passed":
            passed,

        "status":
            status,

        "top_3_skills":
            top_skills,

        "skill_score":
            skill_score,

        "semantic_score":
            semantic_match_score,

        "experience_score":
            exp_score,

        "education_score":
            edu_score,

        "matched_skills": [
            match[
                "candidate_skill"
            ]
            for match in matches
        ],

        "missing_skills":
            missing
    }


# ============================================================
# ONE CANDIDATE AGAINST ALL JOBS
# ============================================================

def rank_candidate_against_jobs(
    candidate,
    jobs,
    threshold=DEFAULT_THRESHOLD
):

    results = []

    for job in jobs:

        result = scan_candidate(
            candidate,
            job,
            threshold
        )

        results.append(
            result
        )

    results = sorted(
        results,
        key=lambda x:
            x[
                "final_match_score"
            ],
        reverse=True
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        result[
            "job_rank"
        ] = rank

    return results


# ============================================================
# MANY CANDIDATES AGAINST ONE JOB
# ============================================================

def rank_candidates_for_job(
    candidates,
    job,
    threshold=DEFAULT_THRESHOLD
):

    results = []

    for candidate in candidates:

        result = scan_candidate(
            candidate,
            job,
            threshold
        )

        results.append(
            result
        )

    results = sorted(
        results,
        key=lambda x:
            x[
                "final_match_score"
            ],
        reverse=True
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        result[
            "candidate_rank"
        ] = rank

    return results
