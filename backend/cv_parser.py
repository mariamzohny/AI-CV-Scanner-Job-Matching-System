
import os
import re

from pypdf import PdfReader
from docx import Document


# ============================================================
# EXTRACT RAW TEXT
# ============================================================

def extract_text_from_pdf(file_path):

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages).strip()


def extract_text_from_docx(file_path):

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs).strip()


def extract_cv_text(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    elif extension == ".docx":

        return extract_text_from_docx(
            file_path
        )

    elif extension == ".txt":

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return file.read().strip()

    else:

        raise ValueError(
            "Supported CV formats: PDF, DOCX, TXT."
        )


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(
    cv_text,
    skill_vocabulary
):

    text = cv_text.lower()

    text = text.replace(
        "-",
        " "
    )

    text = text.replace(
        "_",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    found_skills = []

    seen = set()

    for skill in skill_vocabulary:

        original_skill = str(
            skill
        ).strip()

        if not original_skill:
            continue

        normalized_skill = (
            original_skill
            .lower()
            .replace("-", " ")
            .replace("_", " ")
            .strip()
        )

        pattern = (
            r"(?<![a-zA-Z0-9])"
            +
            re.escape(
                normalized_skill
            )
            +
            r"(?![a-zA-Z0-9])"
        )

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            key = normalized_skill

            if key not in seen:

                seen.add(key)

                found_skills.append(
                    original_skill
                )

    return found_skills


# ============================================================
# ESTIMATE EXPERIENCE
# ============================================================

def extract_experience_years(
    cv_text
):

    text = cv_text.lower()

    # Explicit:
    # "3 years of experience"
    patterns = [

        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",

        r"(\d+(?:\.\d+)?)\+?\s*yrs?\s+(?:of\s+)?experience",

        r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*years?"
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        for match in matches:

            try:
                values.append(
                    float(match)
                )
            except:
                pass

    if values:

        return max(values)


    # --------------------------------------------------------
    # Fallback: date ranges
    # 2021 - 2024
    # 2022 - Present
    # --------------------------------------------------------

    current_year = 2026

    date_pattern = (
        r"\b((?:19|20)\d{2})\b"
        r"\s*(?:-|–|—|to)\s*"
        r"(present|current|now|(?:19|20)\d{2})"
    )

    matches = re.findall(
        date_pattern,
        text
    )

    intervals = []

    for start, end in matches:

        start_year = int(start)

        if end in [
            "present",
            "current",
            "now"
        ]:

            end_year = current_year

        else:

            end_year = int(end)

        if (
            end_year >= start_year
            and
            end_year - start_year <= 30
        ):

            intervals.append(
                (
                    start_year,
                    end_year
                )
            )

    if not intervals:

        return 0.0

    intervals.sort()

    merged = [
        list(intervals[0])
    ]

    for start, end in intervals[1:]:

        last = merged[-1]

        if start <= last[1]:

            last[1] = max(
                last[1],
                end
            )

        else:

            merged.append(
                [
                    start,
                    end
                ]
            )

    total_years = sum(
        end - start
        for start, end in merged
    )

    return float(
        total_years
    )


# ============================================================
# DETECT EDUCATION
# ============================================================

def extract_education(
    cv_text
):

    text = cv_text.lower()

    education_patterns = [

        (
            "PhD",
            [
                "phd",
                "ph.d",
                "doctorate"
            ]
        ),

        (
            "Master",
            [
                "master",
                "msc",
                "m.sc",
                "mba",
                "m.tech",
                "mtech"
            ]
        ),

        (
            "Bachelor",
            [
                "bachelor",
                "bsc",
                "b.sc",
                "b.tech",
                "btech",
                "b.e"
            ]
        ),

        (
            "Diploma",
            [
                "diploma"
            ]
        )
    ]

    for level, keywords in education_patterns:

        if any(
            keyword in text
            for keyword in keywords
        ):

            return level

    return ""


# ============================================================
# BUILD STANDARD CANDIDATE
# ============================================================

def parse_cv(
    file_path,
    skill_vocabulary,
    candidate_id="UPLOADED_CV"
):

    cv_text = extract_cv_text(
        file_path
    )

    if not cv_text:

        raise ValueError(
            "No readable text was found in the CV."
        )

    skills = extract_skills(
        cv_text,
        skill_vocabulary
    )

    experience_years = (
        extract_experience_years(
            cv_text
        )
    )

    education = extract_education(
        cv_text
    )

    return {

        "candidate_id":
            candidate_id,

        "skills":
            skills,

        "education":
            education,

        "experience_years":
            experience_years,

        "positions":
            [],

        "summary":
            cv_text,

        "candidate_text":
            cv_text
    }
