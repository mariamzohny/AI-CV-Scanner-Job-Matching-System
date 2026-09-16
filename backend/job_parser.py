
import re


# ============================================================
# DEFAULT TECHNICAL SKILLS
# ============================================================

DEFAULT_SKILLS = [

    # Programming Languages
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",
    "PHP",
    "Go",
    "Rust",
    "Kotlin",
    "Swift",
    "R",
    "MATLAB",

    # Data / Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Oracle",
    "Redis",
    "Excel",
    "Power BI",
    "Tableau",
    "Looker",

    # AI / Machine Learning
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Data Analysis",
    "NLP",
    "Natural Language Processing",
    "Computer Vision",
    "Statistics",
    "Predictive Modeling",
    "Feature Engineering",
    "Data Cleaning",

    # ML / Data Libraries
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "SciPy",
    "OpenCV",
    "XGBoost",
    "LightGBM",
    "Matplotlib",

    # Generative AI / NLP
    "Transformers",
    "Hugging Face",
    "LangChain",
    "LangGraph",
    "LangMem",
    "CrewAI",
    "RAG",
    "Retrieval Augmented Generation",
    "LLM",
    "Large Language Models",
    "Prompt Engineering",
    "Embeddings",
    "Vector Database",
    "FAISS",
    "Pinecone",
    "Chroma",
    "OpenAI",

    # Backend / Web
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",
    "Django",
    "Flask",
    "FastAPI",
    "Streamlit",
    "REST API",
    "GraphQL",

    # Cloud / DevOps
    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "GitLab",
    "Linux",
    "CI/CD",
    "Jenkins",

    # Big Data
    "Spark",
    "Apache Spark",
    "Hadoop",
    "Kafka",
    "Airflow",
    "Databricks",
    "Snowflake",

    # Agentic AI
    "n8n",
    "Flowise",
    "AgentOps",

    # General
    "Agile",
    "Scrum",
    "Jira",
    "Project Management",
    "Data Visualization",
    "ETL"
]


# ============================================================
# SKILL ALIASES
# Different ways the same skill can appear
# ============================================================

SKILL_ALIASES = {

    "Machine Learning": [
        "machine learning",
        "ml"
    ],

    "Artificial Intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "Natural Language Processing": [
        "natural language processing",
        "nlp"
    ],

    "Large Language Models": [
        "large language models",
        "large language model",
        "llms",
        "llm"
    ],

    "Retrieval Augmented Generation": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag"
    ],

    "Scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn"
    ],

    "Power BI": [
        "power bi",
        "powerbi"
    ],

    "Node.js": [
        "node.js",
        "nodejs",
        "node js"
    ],

    "Google Cloud": [
        "google cloud",
        "google cloud platform",
        "gcp"
    ],

    "Hugging Face": [
        "hugging face",
        "huggingface"
    ],

    "REST API": [
        "rest api",
        "restful api",
        "restful apis",
        "rest apis"
    ],

    "Computer Vision": [
        "computer vision",
        "cv"
    ]
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# SAFE TERM MATCHING
# Handles:
# Python
# C++
# C#
# Node.js
# etc.
# ============================================================

def contains_term(
    text,
    term
):

    text = str(text)
    term = str(term).strip()

    if not term:
        return False

    pattern = (
        r"(?<![A-Za-z0-9])"
        +
        re.escape(term)
        +
        r"(?![A-Za-z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )
    )


# ============================================================
# JOB TITLE EXTRACTION
# ============================================================

def extract_job_title(
    job_description
):

    text = normalize_text(
        job_description
    )

    if not text:
        return "Unknown Job"


    lines = [

        line.strip()

        for line
        in text.splitlines()

        if line.strip()
    ]


    # --------------------------------------------------------
    # Explicit title fields
    # --------------------------------------------------------

    explicit_patterns = [

        r"^(?:job\s*title)\s*[:\-]\s*(.+)$",

        r"^(?:position)\s*[:\-]\s*(.+)$",

        r"^(?:role)\s*[:\-]\s*(.+)$",

        r"^(?:vacancy)\s*[:\-]\s*(.+)$",

        r"^(?:المسمى\s*الوظيفي)\s*[:\-]\s*(.+)$",

        r"^(?:الوظيفة)\s*[:\-]\s*(.+)$"
    ]


    for line in lines[:20]:

        for pattern in explicit_patterns:

            match = re.search(
                pattern,
                line,
                flags=re.IGNORECASE
            )

            if match:

                title = (
                    match
                    .group(1)
                    .strip()
                )

                if title:

                    return title[:120]


    # --------------------------------------------------------
    # We are looking for an AI Engineer...
    # Hiring a Data Scientist...
    # --------------------------------------------------------

    sentence_patterns = [

        (
            r"(?:we\s+are\s+)?"
            r"looking\s+for\s+"
            r"(?:an?\s+)?"
            r"([A-Za-z][A-Za-z0-9 /&+\-]{2,70}?)"
            r"(?=\s+(?:to|who|with|for)\s+|[.,\n])"
        ),

        (
            r"(?:we\s+are\s+)?"
            r"hiring\s+"
            r"(?:an?\s+)?"
            r"([A-Za-z][A-Za-z0-9 /&+\-]{2,70}?)"
            r"(?=\s+(?:to|who|with|for)\s+|[.,\n])"
        ),

        (
            r"seeking\s+"
            r"(?:an?\s+)?"
            r"([A-Za-z][A-Za-z0-9 /&+\-]{2,70}?)"
            r"(?=\s+(?:to|who|with|for)\s+|[.,\n])"
        )
    ]


    for pattern in sentence_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            title = (
                match
                .group(1)
                .strip()
            )

            if title:

                return title


    # --------------------------------------------------------
    # First line heuristic
    # Example:
    # AI Engineer
    # ----------------
    # We are looking for...
    # --------------------------------------------------------

    if lines:

        first_line = lines[0]

        bad_first_lines = [
            "job description",
            "job overview",
            "about the role",
            "about us",
            "description"
        ]

        if (
            len(first_line) <= 100
            and
            len(first_line.split()) <= 12
            and
            first_line.lower()
            not in bad_first_lines
            and
            not first_line.endswith(".")
        ):

            return first_line


    return "Unknown Job"


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_required_skills(
    job_description,
    custom_skill_vocabulary=None
):

    text = normalize_text(
        job_description
    )

    if not text:
        return []


    found_skills = []
    seen = set()


    # --------------------------------------------------------
    # 1. Search aliases
    # --------------------------------------------------------

    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            if contains_term(
                text,
                alias
            ):

                normalized = (
                    canonical_skill
                    .lower()
                    .strip()
                )

                if normalized not in seen:

                    seen.add(
                        normalized
                    )

                    found_skills.append(
                        canonical_skill
                    )

                break


    # --------------------------------------------------------
    # 2. Search default vocabulary
    # --------------------------------------------------------

    vocabulary = list(
        DEFAULT_SKILLS
    )


    if custom_skill_vocabulary:

        vocabulary.extend(
            custom_skill_vocabulary
        )


    for skill in vocabulary:

        skill = str(
            skill
        ).strip()

        if not skill:
            continue


        if contains_term(
            text,
            skill
        ):

            normalized = (
                skill
                .lower()
                .strip()
            )


            # ------------------------------------------------
            # Avoid adding aliases after canonical concept
            # ------------------------------------------------

            skip = False

            for canonical_skill, aliases in SKILL_ALIASES.items():

                if (
                    normalized
                    ==
                    canonical_skill.lower()
                ):

                    if (
                        canonical_skill.lower()
                        in seen
                    ):

                        skip = True

                        break


                alias_names = [
                    alias.lower()
                    for alias in aliases
                ]


                if normalized in alias_names:

                    if (
                        canonical_skill.lower()
                        in seen
                    ):

                        skip = True

                        break


            if skip:
                continue


            if normalized not in seen:

                seen.add(
                    normalized
                )

                found_skills.append(
                    skill
                )


    # --------------------------------------------------------
    # Remove concept duplicates
    # --------------------------------------------------------

    concept_duplicates = {

        "Natural Language Processing": [
            "NLP"
        ],

        "Artificial Intelligence": [
            "AI"
        ],

        "Machine Learning": [
            "ML"
        ],

        "Large Language Models": [
            "LLM"
        ],

        "Retrieval Augmented Generation": [
            "RAG"
        ],

        "Google Cloud": [
            "GCP"
        ],

        "Apache Spark": [
            "Spark"
        ]
    }


    final_skills = list(
        found_skills
    )


    for canonical, duplicates in concept_duplicates.items():

        if canonical in final_skills:

            final_skills = [

                skill

                for skill
                in final_skills

                if (
                    skill == canonical
                    or
                    skill not in duplicates
                )
            ]


    return final_skills


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience_requirement(
    job_description
):

    text = normalize_text(
        job_description
    ).lower()


    if not text:
        return ""


    # --------------------------------------------------------
    # Fresh Graduate / Entry Level
    # --------------------------------------------------------

    fresher_phrases = [

        "fresh graduate",
        "fresh graduates",
        "fresher",
        "no experience required",
        "no prior experience",
        "entry level",
        "entry-level"
    ]


    if any(
        phrase in text
        for phrase in fresher_phrases
    ):

        return "0 years"


    # --------------------------------------------------------
    # Experience range:
    # 3-5 years
    # 2 to 4 years
    #
    # Use minimum required number
    # --------------------------------------------------------

    range_patterns = [

        (
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:-|–|—|to)\s*"
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:years?|yrs?)"
        ),

        (
            r"between\s+"
            r"(\d+(?:\.\d+)?)"
            r"\s+and\s+"
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:years?|yrs?)"
        )
    ]


    for pattern in range_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            minimum = float(
                match.group(1)
            )

            return (
                f"At least "
                f"{minimum:g} years"
            )


    # --------------------------------------------------------
    # Single requirement:
    # at least 2 years
    # minimum 3 years
    # 2+ years
    # 4 years of experience
    # --------------------------------------------------------

    single_patterns = [

        (
            r"(?:at\s+least|minimum(?:\s+of)?|min\.?)"
            r"\s*(\d+(?:\.\d+)?)"
            r"\s*\+?"
            r"\s*(?:years?|yrs?)"
        ),

        (
            r"(\d+(?:\.\d+)?)"
            r"\s*\+\s*"
            r"(?:years?|yrs?)"
        ),

        (
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:years?|yrs?)"
            r"\s+(?:of\s+)?"
            r"(?:relevant\s+)?"
            r"(?:professional\s+)?"
            r"experience"
        ),

        (
            r"experience"
            r"\s*(?:of)?\s*"
            r"(\d+(?:\.\d+)?)"
            r"\s*\+?"
            r"\s*(?:years?|yrs?)"
        )
    ]


    for pattern in single_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            years = float(
                match.group(1)
            )

            return (
                f"At least "
                f"{years:g} years"
            )


    # --------------------------------------------------------
    # Basic Arabic Support
    # Examples:
    # خبرة سنتين
    # 3 سنوات خبرة
    # --------------------------------------------------------

    arabic_patterns = [

        (
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:سنة|سنوات)"
            r"\s*(?:من\s+)?"
            r"(?:الخبرة|خبرة)?"
        ),

        (
            r"(?:خبرة|الخبرة)"
            r"\s*(?:لا\s+تقل\s+عن\s*)?"
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:سنة|سنوات)"
        )
    ]


    for pattern in arabic_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            years = float(
                match.group(1)
            )

            return (
                f"At least "
                f"{years:g} years"
            )


    return ""


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education_requirement(
    job_description
):

    text = normalize_text(
        job_description
    ).lower()


    if not text:
        return ""


    levels_found = []


    # --------------------------------------------------------
    # Diploma
    # --------------------------------------------------------

    diploma_keywords = [

        "diploma",
        "associate degree",
        "دبلوم"
    ]


    if any(
        keyword in text
        for keyword in diploma_keywords
    ):

        levels_found.append(
            (
                1,
                "Diploma"
            )
        )


    # --------------------------------------------------------
    # Bachelor
    # --------------------------------------------------------

    bachelor_keywords = [

        "bachelor",
        "bachelor's",
        "bachelors",
        "bsc",
        "b.sc",
        "b.tech",
        "btech",
        "b.e",
        "undergraduate degree",
        "undergraduate",
        "بكالوريوس"
    ]


    if any(
        keyword in text
        for keyword in bachelor_keywords
    ):

        levels_found.append(
            (
                2,
                "Bachelor degree"
            )
        )


    # --------------------------------------------------------
    # Master
    # --------------------------------------------------------

    master_keywords = [

        "master",
        "master's",
        "masters",
        "msc",
        "m.sc",
        "mba",
        "mtech",
        "m.tech",
        "ماجستير"
    ]


    if any(
        keyword in text
        for keyword in master_keywords
    ):

        levels_found.append(
            (
                3,
                "Master degree"
            )
        )


    # --------------------------------------------------------
    # PhD
    # --------------------------------------------------------

    phd_keywords = [

        "phd",
        "ph.d",
        "doctorate",
        "doctoral degree",
        "دكتوراه"
    ]


    if any(
        keyword in text
        for keyword in phd_keywords
    ):

        levels_found.append(
            (
                4,
                "PhD"
            )
        )


    if not levels_found:

        return ""


    # --------------------------------------------------------
    # Example:
    # "Bachelor's or Master's degree"
    #
    # Minimum acceptable education = Bachelor
    # --------------------------------------------------------

    levels_found.sort(
        key=lambda item:
            item[0]
    )


    return levels_found[0][1]


# ============================================================
# OPTIONAL RESPONSIBILITY SECTION EXTRACTION
# ============================================================

def extract_responsibilities(
    job_description
):

    text = normalize_text(
        job_description
    )


    section_patterns = [

        r"(?:responsibilities|key responsibilities|duties)"
        r"\s*[:\-]?\s*(.+)",

        r"(?:what you will do)"
        r"\s*[:\-]?\s*(.+)",

        r"(?:المسؤوليات|المهام)"
        r"\s*[:\-]?\s*(.+)"
    ]


    for pattern in section_patterns:

        match = re.search(
            pattern,
            text,
            flags=(
                re.IGNORECASE
                |
                re.DOTALL
            )
        )

        if match:

            extracted = (
                match
                .group(1)
                .strip()
            )

            if extracted:

                return extracted


    # If a clear section cannot be detected,
    # keep the full Job Description.
    return text


# ============================================================
# MAIN PARSER
# ============================================================

def parse_job_description(
    job_description,
    custom_skill_vocabulary=None
):

    if not job_description:

        raise ValueError(
            "Job description cannot be empty."
        )


    clean_description = normalize_text(
        job_description
    )


    if not clean_description:

        raise ValueError(
            "Job description cannot be empty."
        )


    # --------------------------------------------------------
    # Extract Job Information
    # --------------------------------------------------------

    job_title = extract_job_title(
        clean_description
    )


    required_skills = (
        extract_required_skills(

            clean_description,

            custom_skill_vocabulary=
                custom_skill_vocabulary
        )
    )


    experience_requirement = (
        extract_experience_requirement(
            clean_description
        )
    )


    education_requirement = (
        extract_education_requirement(
            clean_description
        )
    )


    responsibilities = (
        extract_responsibilities(
            clean_description
        )
    )


    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    warnings = []


    if job_title == "Unknown Job":

        warnings.append(
            "Job title could not be detected automatically."
        )


    if not required_skills:

        warnings.append(
            "No known technical skills were detected automatically."
        )


    if not experience_requirement:

        warnings.append(
            "Experience requirement was not detected."
        )


    if not education_requirement:

        warnings.append(
            "Education requirement was not detected."
        )


    # --------------------------------------------------------
    # Standard Job Format
    #
    # This format is directly compatible with scanner.py
    # --------------------------------------------------------

    return {

        "job_title":
            job_title,

        "required_skills":
            required_skills,

        "education_requirement":
            education_requirement,

        "experience_requirement":
            experience_requirement,

        "responsibilities":
            responsibilities,

        # Full raw JD is kept for Transformer semantic matching
        "job_text":
            clean_description,

        "parser_warnings":
            warnings
    }
