
import os
import re
import pandas as pd


# ============================================================
# IMPORT HELPERS FROM SCANNER
# ============================================================

try:
    from .scanner import parse_list, unique_skills
except ImportError:
    from scanner import parse_list, unique_skills


# ============================================================
# COLUMN NAME SUGGESTIONS
# ============================================================

CANDIDATE_COLUMN_ALIASES = {

    "candidate_id": [
        "candidate_id",
        "candidate",
        "candidate_name",
        "name",
        "applicant",
        "applicant_name",
        "id"
    ],

    "skills": [
        "skills",
        "skill",
        "skill_set",
        "skillset",
        "technical_skills",
        "candidate_skills",
        "competencies"
    ],

    "education": [
        "education",
        "degree",
        "degree_names",
        "qualification",
        "educational_qualification",
        "academic_background"
    ],

    "experience_years": [
        "experience",
        "experience_years",
        "years_experience",
        "years_of_experience",
        "yearsworked",
        "work_experience"
    ],

    "positions": [
        "positions",
        "position",
        "job_title",
        "current_role",
        "current_position",
        "previous_role",
        "previous_positions"
    ],

    "summary": [
        "summary",
        "profile",
        "career_objective",
        "objective",
        "professional_summary",
        "about"
    ]
}


JOB_COLUMN_ALIASES = {

    "job_title": [
        "job_title",
        "job_position",
        "job_position_name",
        "position",
        "role",
        "title"
    ],

    "required_skills": [
        "required_skills",
        "skills_required",
        "skills",
        "technical_skills",
        "requirements"
    ],

    "education_requirement": [
        "education_requirement",
        "education_requirements",
        "education",
        "degree_requirement",
        "qualification"
    ],

    "experience_requirement": [
        "experience_requirement",
        "experience_requirements",
        "experience",
        "required_experience",
        "years_experience"
    ],

    "responsibilities": [
        "responsibilities",
        "job_responsibilities",
        "description",
        "job_description",
        "duties"
    ]
}


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_column_name(name):

    name = str(name).strip()

    # Convert CamelCase to snake_case
    name = re.sub(
        r"(?<=[a-z0-9])(?=[A-Z])",
        "_",
        name
    )

    name = name.lower()

    name = name.replace(
        "-",
        "_"
    )

    name = name.replace(
        " ",
        "_"
    )

    name = re.sub(
        r"[^a-z0-9_]+",
        "",
        name
    )

    name = re.sub(
        r"_+",
        "_",
        name
    )

    return name.strip("_")


def extract_years(value):

    if value is None:
        return 0.0

    if isinstance(
        value,
        (int, float)
    ):

        if pd.isna(value):
            return 0.0

        return float(value)

    text = str(value).lower().strip()

    if not text:
        return 0.0

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        text
    )

    if not numbers:
        return 0.0

    try:
        return float(
            numbers[0]
        )

    except:
        return 0.0


# ============================================================
# READ DATASET
# ============================================================

def read_dataset(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()


    if extension == ".csv":

        try:

            df = pd.read_csv(
                file_path
            )

        except UnicodeDecodeError:

            df = pd.read_csv(
                file_path,
                encoding="latin1"
            )


    elif extension in [
        ".xlsx",
        ".xls"
    ]:

        df = pd.read_excel(
            file_path
        )


    else:

        raise ValueError(
            "Supported dataset formats are CSV, XLSX and XLS."
        )


    if df.empty:

        raise ValueError(
            "The uploaded dataset is empty."
        )


    # Remove hidden BOM / whitespace
    df.columns = [
        str(column)
        .replace("\ufeff", "")
        .strip()

        for column
        in df.columns
    ]


    return df


# ============================================================
# GET DATASET INFO
# ============================================================

def get_dataset_info(file_path):

    df = read_dataset(
        file_path
    )


    return {

        "rows":
            len(df),

        "columns_count":
            len(df.columns),

        "columns":
            df.columns.tolist(),

        "preview":
            df.head(5)
    }


# ============================================================
# AUTOMATIC COLUMN MAPPING SUGGESTION
# ============================================================

def suggest_mapping(
    columns,
    dataset_type="candidate"
):

    cleaned_columns = {}

    compact_columns = {}

    for column in columns:

        cleaned = clean_column_name(
            column
        )

        compact = cleaned.replace(
            "_",
            ""
        )

        cleaned_columns[
            cleaned
        ] = column

        compact_columns[
            compact
        ] = column


    if dataset_type == "candidate":

        aliases = (
            CANDIDATE_COLUMN_ALIASES
        )

    elif dataset_type == "job":

        aliases = (
            JOB_COLUMN_ALIASES
        )

    else:

        raise ValueError(
            "dataset_type must be 'candidate' or 'job'."
        )


    mapping = {}


    for standard_name, possible_names in aliases.items():

        mapping[
            standard_name
        ] = None


        for possible_name in possible_names:

            cleaned_possible = (
                clean_column_name(
                    possible_name
                )
            )

            compact_possible = (
                cleaned_possible.replace(
                    "_",
                    ""
                )
            )


            # Exact normalized match
            if cleaned_possible in cleaned_columns:

                mapping[
                    standard_name
                ] = (
                    cleaned_columns[
                        cleaned_possible
                    ]
                )

                break


            # Flexible match:
            # TechnicalSkills == technical_skills
            elif compact_possible in compact_columns:

                mapping[
                    standard_name
                ] = (
                    compact_columns[
                        compact_possible
                    ]
                )

                break


    return mapping


# ============================================================
# VALIDATE MAPPING
# ============================================================

def validate_mapping(
    df,
    mapping,
    dataset_type
):

    if dataset_type == "candidate":

        required_fields = [
            "skills"
        ]

    elif dataset_type == "job":

        required_fields = [
            "job_title",
            "required_skills"
        ]

    else:

        raise ValueError(
            "dataset_type must be 'candidate' or 'job'."
        )


    missing_required = []


    for field in required_fields:

        column = mapping.get(
            field
        )


        if not column:

            missing_required.append(
                field
            )

        elif column not in df.columns:

            raise ValueError(
                f"Mapped column '{column}' does not exist."
            )


    if missing_required:

        raise ValueError(
            "Missing required mapping fields: "
            +
            ", ".join(
                missing_required
            )
        )


    for standard_field, dataset_column in mapping.items():

        if (
            dataset_column is not None
            and
            dataset_column not in df.columns
        ):

            raise ValueError(
                f"Column '{dataset_column}' "
                f"mapped to '{standard_field}' "
                "was not found in the dataset."
            )


    return True


# ============================================================
# STANDARDIZE CANDIDATE DATASET
# ============================================================

def standardize_candidates(
    df,
    mapping
):

    validate_mapping(
        df,
        mapping,
        "candidate"
    )


    candidates = []


    for index, row in df.iterrows():


        # ----------------------------------------------------
        # Candidate ID
        # ----------------------------------------------------

        id_column = mapping.get(
            "candidate_id"
        )


        if id_column:

            candidate_id = str(
                row[
                    id_column
                ]
            ).strip()

        else:

            candidate_id = (
                f"CAND_{index + 1:04d}"
            )


        if (
            not candidate_id
            or
            candidate_id.lower()
            in [
                "nan",
                "none"
            ]
        ):

            candidate_id = (
                f"CAND_{index + 1:04d}"
            )


        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        skills_column = mapping.get(
            "skills"
        )


        skills = unique_skills(
            parse_list(
                row[
                    skills_column
                ]
            )
        )


        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        education_column = mapping.get(
            "education"
        )


        if education_column:

            education = str(
                row[
                    education_column
                ]
            ).strip()

        else:

            education = ""


        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        experience_column = mapping.get(
            "experience_years"
        )


        if experience_column:

            experience_years = (
                extract_years(
                    row[
                        experience_column
                    ]
                )
            )

        else:

            experience_years = 0.0


        # ----------------------------------------------------
        # Positions
        # ----------------------------------------------------

        positions_column = mapping.get(
            "positions"
        )


        if positions_column:

            positions = parse_list(
                row[
                    positions_column
                ]
            )

        else:

            positions = []


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        summary_column = mapping.get(
            "summary"
        )


        if summary_column:

            summary = str(
                row[
                    summary_column
                ]
            ).strip()

        else:

            summary = ""


        # ----------------------------------------------------
        # Standard Candidate
        # ----------------------------------------------------

        candidates.append({

            "candidate_id":
                candidate_id,

            "skills":
                skills,

            "education":
                education,

            "experience_years":
                experience_years,

            "positions":
                positions,

            "summary":
                summary
        })


    return candidates


# ============================================================
# STANDARDIZE JOB DATASET
# ============================================================

def standardize_jobs(
    df,
    mapping
):

    validate_mapping(
        df,
        mapping,
        "job"
    )


    jobs = []


    for _, row in df.iterrows():


        # ----------------------------------------------------
        # Job title
        # ----------------------------------------------------

        job_title_column = mapping[
            "job_title"
        ]


        job_title = str(
            row[
                job_title_column
            ]
        ).strip()


        if (
            not job_title
            or
            job_title.lower()
            in [
                "nan",
                "none"
            ]
        ):

            continue


        # ----------------------------------------------------
        # Required skills
        # ----------------------------------------------------

        skills_column = mapping[
            "required_skills"
        ]


        required_skills = unique_skills(
            parse_list(
                row[
                    skills_column
                ]
            )
        )


        # ----------------------------------------------------
        # Education Requirement
        # ----------------------------------------------------

        education_column = mapping.get(
            "education_requirement"
        )


        if education_column:

            education_requirement = str(
                row[
                    education_column
                ]
            ).strip()

        else:

            education_requirement = ""


        # ----------------------------------------------------
        # Experience Requirement
        # ----------------------------------------------------

        experience_column = mapping.get(
            "experience_requirement"
        )


        if experience_column:

            experience_requirement = str(
                row[
                    experience_column
                ]
            ).strip()

        else:

            experience_requirement = ""


        # ----------------------------------------------------
        # Responsibilities
        # ----------------------------------------------------

        responsibilities_column = mapping.get(
            "responsibilities"
        )


        if responsibilities_column:

            responsibilities = str(
                row[
                    responsibilities_column
                ]
            ).strip()

        else:

            responsibilities = ""


        # ----------------------------------------------------
        # Standard Job
        # ----------------------------------------------------

        jobs.append({

            "job_title":
                job_title,

            "required_skills":
                required_skills,

            "education_requirement":
                education_requirement,

            "experience_requirement":
                experience_requirement,

            "responsibilities":
                responsibilities
        })


    return jobs


# ============================================================
# LOAD + STANDARDIZE CANDIDATES
# ============================================================

def load_candidates(
    file_path,
    mapping
):

    df = read_dataset(
        file_path
    )

    return standardize_candidates(
        df,
        mapping
    )


# ============================================================
# LOAD + STANDARDIZE JOBS
# ============================================================

def load_jobs(
    file_path,
    mapping
):

    df = read_dataset(
        file_path
    )

    return standardize_jobs(
        df,
        mapping
    )
