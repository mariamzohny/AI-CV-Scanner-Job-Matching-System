
import os
import re
import json
import shutil
import uuid

from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


# ============================================================
# PROJECT MODULES
# ============================================================

from .scanner import (
    scan_candidate,
    rank_candidate_against_jobs,
    rank_candidates_for_job
)

from .dataset_processor import (
    read_dataset,
    suggest_mapping,
    standardize_candidates,
    standardize_jobs
)

from .cv_parser import (
    parse_cv
)

from .job_parser import (
    parse_job_description,
    DEFAULT_SKILLS
)

from .cv_builder import (
    build_candidate_from_profile,
    generate_cv_docx
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(

    title="AI CV Scanner & Job Matching API",

    description=(
        "AI-powered CV screening, job matching, "
        "candidate ranking and CV generation system."
    ),

    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# PROJECT PATHS
# ============================================================

BACKEND_DIR = Path(
    __file__
).resolve().parent


PROJECT_ROOT = (
    BACKEND_DIR.parent
)


UPLOAD_FOLDER = (
    PROJECT_ROOT
    /
    "uploads"
)


OUTPUT_FOLDER = (
    PROJECT_ROOT
    /
    "outputs"
)


UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPERS
# ============================================================

def save_uploaded_file(
    uploaded_file
):

    original_name = (
        uploaded_file.filename
        or
        "uploaded_file"
    )

    extension = Path(
        original_name
    ).suffix.lower()


    unique_name = (
        uuid.uuid4().hex
        +
        extension
    )


    file_path = (
        UPLOAD_FOLDER
        /
        unique_name
    )


    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            uploaded_file.file,
            buffer
        )


    return file_path


def delete_temp_file(
    file_path
):

    try:

        if (
            file_path
            and
            Path(
                file_path
            ).exists()
        ):

            Path(
                file_path
            ).unlink()

    except Exception:

        pass


def parse_skills_text(
    skills_text
):

    if not skills_text:

        return []


    parts = re.split(
        r"[,;\n]+",
        str(
            skills_text
        )
    )


    return [

        skill.strip()

        for skill
        in parts

        if skill.strip()
    ]


def parse_json_form(
    json_text,
    field_name="JSON"
):

    try:

        data = json.loads(
            json_text
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                f"{field_name} must be valid JSON."
            )
        )


    if not isinstance(
        data,
        dict
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"{field_name} must contain a JSON object."
            )
        )


    return data


def create_cv_filename(
    full_name
):

    full_name = str(
        full_name
        or
        "Generated_CV"
    ).strip()


    safe_name = re.sub(
        r"[^A-Za-z0-9_\-]+",
        "_",
        full_name
    )


    safe_name = (
        safe_name.strip("_")
        or
        "Generated_CV"
    )


    unique_id = (
        uuid.uuid4()
        .hex[:8]
    )


    return (
        f"{safe_name}_"
        f"{unique_id}_CV.docx"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "project":
            "AI CV Scanner & Job Matching System",

        "status":
            "API is running",

        "version":
            "2.0.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status":
            "healthy"
    }


# ============================================================
# PARSE RAW JOB DESCRIPTION
# ============================================================

@app.post("/parse-job-description")
async def parse_job(

    job_description:
        str = Form(...)
):

    try:

        result = (
            parse_job_description(
                job_description
            )
        )

        return result


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# INSPECT DATASET + AUTO COLUMN MAPPING
# ============================================================

@app.post("/inspect-dataset")
async def inspect_dataset(

    dataset:
        UploadFile = File(...),

    dataset_type:
        str = Form("candidate")
):

    file_path = None

    try:

        if dataset_type not in [
            "candidate",
            "job"
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    "dataset_type must be "
                    "'candidate' or 'job'."
                )
            )


        file_path = save_uploaded_file(
            dataset
        )


        df = read_dataset(
            file_path
        )


        mapping = suggest_mapping(

            df.columns,

            dataset_type=
                dataset_type
        )


        preview = (

            df
            .head(5)
            .fillna("")
            .astype(str)
            .to_dict(
                orient="records"
            )
        )


        return {

            "file_name":
                dataset.filename,

            "dataset_type":
                dataset_type,

            "rows":
                len(df),

            "columns_count":
                len(
                    df.columns
                ),

            "columns":
                df.columns.tolist(),

            "suggested_mapping":
                mapping,

            "preview":
                preview
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        delete_temp_file(
            file_path
        )


# ============================================================
# OLD MODE:
# CV + MANUAL JOB FIELDS
# ============================================================

@app.post("/scan-cv")
async def scan_cv(

    cv:
        UploadFile = File(...),

    job_title:
        str = Form(...),

    required_skills:
        str = Form(...),

    education_requirement:
        str = Form(""),

    experience_requirement:
        str = Form(""),

    responsibilities:
        str = Form(""),

    threshold:
        float = Form(80)
):

    file_path = None

    try:

        required_skills_list = (
            parse_skills_text(
                required_skills
            )
        )


        file_path = save_uploaded_file(
            cv
        )


        skill_vocabulary = list(
            dict.fromkeys(

                DEFAULT_SKILLS
                +
                required_skills_list
            )
        )


        candidate = parse_cv(

            file_path=str(
                file_path
            ),

            skill_vocabulary=
                skill_vocabulary,

            candidate_id=
                Path(
                    cv.filename
                    or
                    "UPLOADED_CV"
                ).stem
        )


        job = {

            "job_title":
                job_title,

            "required_skills":
                required_skills_list,

            "education_requirement":
                education_requirement,

            "experience_requirement":
                experience_requirement,

            "responsibilities":
                responsibilities
        }


        result = scan_candidate(

            candidate=
                candidate,

            job=
                job,

            threshold=
                threshold
        )


        return {

            "candidate":
                {

                    "candidate_id":
                        candidate[
                            "candidate_id"
                        ],

                    "extracted_skills":
                        candidate[
                            "skills"
                        ],

                    "experience_years":
                        candidate[
                            "experience_years"
                        ],

                    "education":
                        candidate[
                            "education"
                        ]
                },

            "job":
                job,

            "match_result":
                result
        }


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        delete_temp_file(
            file_path
        )


# ============================================================
# NEW MODE:
# CV + RAW JOB DESCRIPTION
# ============================================================

@app.post("/scan-cv-jd")
async def scan_cv_job_description(

    cv:
        UploadFile = File(...),

    job_description:
        str = Form(...),

    threshold:
        float = Form(80)
):

    cv_path = None

    try:

        # ----------------------------------------------------
        # Parse Job Description
        # ----------------------------------------------------

        parsed_job = (
            parse_job_description(
                job_description
            )
        )


        # ----------------------------------------------------
        # Build a broad skill vocabulary
        # ----------------------------------------------------

        skill_vocabulary = list(
            dict.fromkeys(

                DEFAULT_SKILLS
                +
                parsed_job[
                    "required_skills"
                ]
            )
        )


        # ----------------------------------------------------
        # Save + Parse CV
        # ----------------------------------------------------

        cv_path = save_uploaded_file(
            cv
        )


        candidate = parse_cv(

            file_path=str(
                cv_path
            ),

            skill_vocabulary=
                skill_vocabulary,

            candidate_id=
                Path(
                    cv.filename
                    or
                    "UPLOADED_CV"
                ).stem
        )


        # ----------------------------------------------------
        # Match
        # ----------------------------------------------------

        result = scan_candidate(

            candidate=
                candidate,

            job=
                parsed_job,

            threshold=
                threshold
        )


        return {

            "candidate":
                {

                    "candidate_id":
                        candidate[
                            "candidate_id"
                        ],

                    "extracted_skills":
                        candidate[
                            "skills"
                        ],

                    "estimated_experience_years":
                        candidate[
                            "experience_years"
                        ],

                    "detected_education":
                        candidate[
                            "education"
                        ]
                },

            "parsed_job":
                parsed_job,

            "match_result":
                result
        }


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        delete_temp_file(
            cv_path
        )


# ============================================================
# DATASET + MANUAL JOB
# ============================================================

@app.post("/scan-dataset")
async def scan_dataset(

    dataset:
        UploadFile = File(...),

    mapping_json:
        str = Form(...),

    job_title:
        str = Form(...),

    required_skills:
        str = Form(...),

    education_requirement:
        str = Form(""),

    experience_requirement:
        str = Form(""),

    responsibilities:
        str = Form(""),

    threshold:
        float = Form(80)
):

    file_path = None

    try:

        mapping = parse_json_form(

            mapping_json,

            "mapping_json"
        )


        file_path = save_uploaded_file(
            dataset
        )


        df = read_dataset(
            file_path
        )


        candidates = (
            standardize_candidates(
                df,
                mapping
            )
        )


        job = {

            "job_title":
                job_title,

            "required_skills":
                parse_skills_text(
                    required_skills
                ),

            "education_requirement":
                education_requirement,

            "experience_requirement":
                experience_requirement,

            "responsibilities":
                responsibilities
        }


        results = (
            rank_candidates_for_job(

                candidates=
                    candidates,

                job=
                    job,

                threshold=
                    threshold
            )
        )


        qualified = [

            result

            for result
            in results

            if result[
                "passed"
            ]
        ]


        return {

            "job_title":
                job_title,

            "total_candidates":
                len(
                    candidates
                ),

            "qualified_candidates":
                len(
                    qualified
                ),

            "threshold":
                threshold,

            "results":
                results
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        delete_temp_file(
            file_path
        )


# ============================================================
# CV + JOB DATASET
# JOB RECOMMENDATION
# ============================================================

@app.post("/recommend-jobs")
async def recommend_jobs(

    cv:
        UploadFile = File(...),

    jobs_dataset:
        UploadFile = File(...),

    jobs_mapping_json:
        str = Form(...),

    threshold:
        float = Form(80)
):

    cv_path = None
    jobs_path = None

    try:

        jobs_mapping = (
            parse_json_form(

                jobs_mapping_json,

                "jobs_mapping_json"
            )
        )


        # ----------------------------------------------------
        # Jobs
        # ----------------------------------------------------

        jobs_path = save_uploaded_file(
            jobs_dataset
        )


        jobs_df = read_dataset(
            jobs_path
        )


        jobs = standardize_jobs(

            jobs_df,

            jobs_mapping
        )


        if not jobs:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid jobs were found."
                )
            )


        # ----------------------------------------------------
        # Skill vocabulary from all jobs
        # ----------------------------------------------------

        skill_vocabulary = list(
            DEFAULT_SKILLS
        )


        for job in jobs:

            skill_vocabulary.extend(
                job[
                    "required_skills"
                ]
            )


        skill_vocabulary = list(
            dict.fromkeys(
                skill_vocabulary
            )
        )


        # ----------------------------------------------------
        # CV
        # ----------------------------------------------------

        cv_path = save_uploaded_file(
            cv
        )


        candidate = parse_cv(

            file_path=str(
                cv_path
            ),

            skill_vocabulary=
                skill_vocabulary,

            candidate_id=
                Path(
                    cv.filename
                    or
                    "UPLOADED_CV"
                ).stem
        )


        # ----------------------------------------------------
        # Rank Jobs
        # ----------------------------------------------------

        results = (
            rank_candidate_against_jobs(

                candidate=
                    candidate,

                jobs=
                    jobs,

                threshold=
                    threshold
            )
        )


        qualified_jobs = [

            result

            for result
            in results

            if result[
                "passed"
            ]
        ]


        return {

            "candidate_id":
                candidate[
                    "candidate_id"
                ],

            "extracted_skills":
                candidate[
                    "skills"
                ],

            "total_jobs":
                len(
                    jobs
                ),

            "qualified_jobs":
                len(
                    qualified_jobs
                ),

            "results":
                results
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        delete_temp_file(
            cv_path
        )

        delete_temp_file(
            jobs_path
        )


# ============================================================
# CANDIDATE DATASET x JOB DATASET
# ============================================================

@app.post("/scan-all")
async def scan_all(

    candidates_dataset:
        UploadFile = File(...),

    jobs_dataset:
        UploadFile = File(...),

    candidates_mapping_json:
        str = Form(...),

    jobs_mapping_json:
        str = Form(...),

    threshold:
        float = Form(80)
):

    candidates_path = None
    jobs_path = None

    try:

        candidates_mapping = (
            parse_json_form(

                candidates_mapping_json,

                "candidates_mapping_json"
            )
        )


        jobs_mapping = (
            parse_json_form(

                jobs_mapping_json,

                "jobs_mapping_json"
            )
        )


        # ----------------------------------------------------
        # Candidates
        # ----------------------------------------------------

        candidates_path = (
            save_uploaded_file(
                candidates_dataset
            )
        )


        candidates_df = (
            read_dataset(
                candidates_path
            )
        )


        candidates = (
            standardize_candidates(

                candidates_df,

                candidates_mapping
            )
        )


        # ----------------------------------------------------
        # Jobs
        # ----------------------------------------------------

        jobs_path = (
            save_uploaded_file(
                jobs_dataset
            )
        )


        jobs_df = (
            read_dataset(
                jobs_path
            )
        )


        jobs = standardize_jobs(

            jobs_df,

            jobs_mapping
        )


        # ----------------------------------------------------
        # All Comparisons
        # ----------------------------------------------------

        all_results = []


        for job in jobs:

            results = (
                rank_candidates_for_job(

                    candidates=
                        candidates,

                    job=
                        job,

                    threshold=
                        threshold
                )
            )


            all_results.extend(
                results
            )


        qualified = [

            result

            for result
            in all_results

            if result[
                "passed"
            ]
        ]


        return {

            "total_candidates":
                len(
                    candidates
                ),

            "total_jobs":
                len(
                    jobs
                ),

            "total_comparisons":
                len(
                    all_results
                ),

            "qualified_matches":
                len(
                    qualified
                ),

            "results":
                all_results
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        delete_temp_file(
            candidates_path
        )

        delete_temp_file(
            jobs_path
        )


# ============================================================
# BUILD CV ONLY
# User does NOT already have a CV
# ============================================================

@app.post("/build-cv")
async def build_cv(

    profile_json:
        str = Form(...)
):

    try:

        profile = parse_json_form(

            profile_json,

            "profile_json"
        )


        filename = create_cv_filename(

            profile.get(
                "full_name"
            )
        )


        generated_path = (
            generate_cv_docx(

                profile=
                    profile,

                output_directory=
                    OUTPUT_FOLDER,

                filename=
                    filename
            )
        )


        return {

            "status":
                "CV generated successfully",

            "filename":
                Path(
                    generated_path
                ).name,

            "download_url":
                (
                    "/download-cv/"
                    +
                    Path(
                        generated_path
                    ).name
                )
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# BUILD CV FROM FORM + RAW JD + MATCH
# ============================================================

@app.post("/build-cv-and-match")
async def build_cv_and_match(

    profile_json:
        str = Form(...),

    job_description:
        str = Form(...),

    threshold:
        float = Form(80)
):

    try:

        # ----------------------------------------------------
        # User Profile
        # ----------------------------------------------------

        profile = parse_json_form(

            profile_json,

            "profile_json"
        )


        # ----------------------------------------------------
        # Convert profile to standard candidate
        # ----------------------------------------------------

        candidate = (
            build_candidate_from_profile(
                profile
            )
        )


        # ----------------------------------------------------
        # Parse Job Description
        # ----------------------------------------------------

        parsed_job = (
            parse_job_description(
                job_description
            )
        )


        # ----------------------------------------------------
        # Matching
        # ----------------------------------------------------

        result = scan_candidate(

            candidate=
                candidate,

            job=
                parsed_job,

            threshold=
                threshold
        )


        # ----------------------------------------------------
        # Generate DOCX CV
        # ----------------------------------------------------

        filename = create_cv_filename(

            profile.get(
                "full_name"
            )
        )


        generated_path = (
            generate_cv_docx(

                profile=
                    profile,

                output_directory=
                    OUTPUT_FOLDER,

                filename=
                    filename
            )
        )


        return {

            "candidate":
                {

                    "candidate_id":
                        candidate[
                            "candidate_id"
                        ],

                    "skills":
                        candidate[
                            "skills"
                        ],

                    "education":
                        candidate[
                            "education"
                        ],

                    "experience_years":
                        candidate[
                            "experience_years"
                        ]
                },

            "parsed_job":
                parsed_job,

            "match_result":
                result,

            "generated_cv":
                {

                    "filename":
                        Path(
                            generated_path
                        ).name,

                    "download_url":
                        (
                            "/download-cv/"
                            +
                            Path(
                                generated_path
                            ).name
                        )
                }
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# DOWNLOAD GENERATED CV
# ============================================================

@app.get("/download-cv/{filename}")
def download_cv(
    filename: str
):

    # Prevent path traversal
    safe_filename = (
        Path(
            filename
        ).name
    )


    file_path = (
        OUTPUT_FOLDER
        /
        safe_filename
    )


    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="CV file not found."
        )


    return FileResponse(

        path=str(
            file_path
        ),

        filename=
            safe_filename,

        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )
