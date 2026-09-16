
import os
import json
import requests
import pandas as pd
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="AI CV Scanner",
    page_icon="📄",
    layout="wide"
)


API_BASE_URL = os.getenv(
    "CV_SCANNER_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 30px;
    }

    .result-box {
        padding: 16px;
        border-radius: 10px;
        margin-top: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPERS
# ============================================================

def upload_file_tuple(file):

    return (
        file.name,
        file.getvalue(),
        file.type or "application/octet-stream"
    )


def api_health():

    try:

        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=3
        )

        return (
            response.status_code == 200
        )

    except Exception:

        return False


def api_post(
    endpoint,
    data=None,
    files=None,
    timeout=600
):

    try:

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            data=data,
            files=files,
            timeout=timeout
        )

    except requests.RequestException as e:

        st.error(
            f"Could not connect to backend: {e}"
        )

        return None


    if not response.ok:

        try:

            detail = response.json().get(
                "detail",
                response.text
            )

        except Exception:

            detail = response.text


        st.error(
            f"Backend Error: {detail}"
        )

        return None


    try:

        return response.json()

    except Exception:

        st.error(
            "Backend returned an invalid response."
        )

        return None


def score_text(value):

    if value is None:

        return "N/A"

    try:

        return f"{float(value):.2f}%"

    except Exception:

        return str(value)


def show_job_info(job):

    if not job:

        return


    with st.expander(
        "Parsed Job Description",
        expanded=False
    ):

        st.write(
            "**Job Title:**",
            job.get(
                "job_title",
                ""
            )
        )

        st.write(
            "**Required Skills:**",
            ", ".join(
                job.get(
                    "required_skills",
                    []
                )
            )
            or
            "Not detected"
        )

        st.write(
            "**Experience:**",
            job.get(
                "experience_requirement"
            )
            or
            "Not detected"
        )

        st.write(
            "**Education:**",
            job.get(
                "education_requirement"
            )
            or
            "Not detected"
        )


        warnings = job.get(
            "parser_warnings",
            []
        )


        if warnings:

            st.warning(
                "\n".join(
                    warnings
                )
            )


def show_match_result(result):

    if not result:

        return


    st.divider()

    st.subheader(
        "Matching Result"
    )


    final_score = result.get(
        "final_match_score",
        0
    )


    if result.get(
        "passed"
    ):

        st.success(
            "Passed First Phase - Qualified for Actual Interview"
        )

    else:

        st.error(
            "Not Passed"
        )


    c1, c2, c3, c4, c5 = st.columns(
        5
    )


    c1.metric(
        "Final Match",
        score_text(
            final_score
        )
    )


    c2.metric(
        "Skills",
        score_text(
            result.get(
                "skill_score"
            )
        )
    )


    c3.metric(
        "Semantic",
        score_text(
            result.get(
                "semantic_score"
            )
        )
    )


    c4.metric(
        "Experience",
        score_text(
            result.get(
                "experience_score"
            )
        )
    )


    c5.metric(
        "Education",
        score_text(
            result.get(
                "education_score"
            )
        )
    )


    top_skills = result.get(
        "top_3_skills",
        []
    )


    if top_skills:

        st.markdown(
            "### Top 3 Matching Skills"
        )

        st.write(
            " • ".join(
                top_skills
            )
        )


    matched = result.get(
        "matched_skills",
        []
    )


    missing = result.get(
        "missing_skills",
        []
    )


    col1, col2 = st.columns(
        2
    )


    with col1:

        st.markdown(
            "#### Matched Skills"
        )

        if matched:

            st.write(
                ", ".join(
                    matched
                )
            )

        else:

            st.write(
                "No matched skills."
            )


    with col2:

        st.markdown(
            "#### Missing Skills"
        )

        if missing:

            st.write(
                ", ".join(
                    missing
                )
            )

        else:

            st.write(
                "No missing skills."
            )


def show_ranking(
    results,
    title="Ranking"
):

    if not results:

        st.warning(
            "No results were returned."
        )

        return


    df = pd.DataFrame(
        results
    )


    if "top_3_skills" in df.columns:

        df[
            "top_3_skills"
        ] = df[
            "top_3_skills"
        ].apply(

            lambda x:
                ", ".join(x)

            if isinstance(
                x,
                list
            )

            else x
        )


    if "matched_skills" in df.columns:

        df[
            "matched_skills"
        ] = df[
            "matched_skills"
        ].apply(

            lambda x:
                ", ".join(x)

            if isinstance(
                x,
                list
            )

            else x
        )


    if "missing_skills" in df.columns:

        df[
            "missing_skills"
        ] = df[
            "missing_skills"
        ].apply(

            lambda x:
                ", ".join(x)

            if isinstance(
                x,
                list
            )

            else x
        )


    st.subheader(
        title
    )


    preferred_columns = [

        "candidate_rank",
        "job_rank",

        "candidate_id",
        "job_title",

        "final_match_score",
        "status",

        "top_3_skills",

        "skill_score",
        "semantic_score",
        "experience_score",
        "education_score",

        "matched_skills",
        "missing_skills"
    ]


    available_columns = [

        column

        for column
        in preferred_columns

        if column
        in df.columns
    ]


    st.dataframe(

        df[
            available_columns
        ],

        use_container_width=True,

        hide_index=True
    )


def inspect_dataset(
    uploaded_file,
    dataset_type
):

    return api_post(

        "/inspect-dataset",

        data={
            "dataset_type":
                dataset_type
        },

        files={
            "dataset":
                upload_file_tuple(
                    uploaded_file
                )
        }
    )


# ============================================================
# COLUMN MAPPING
# ============================================================

CANDIDATE_FIELDS = [

    (
        "candidate_id",
        "Candidate ID / Name"
    ),

    (
        "skills",
        "Skills *"
    ),

    (
        "education",
        "Education"
    ),

    (
        "experience_years",
        "Experience Years"
    ),

    (
        "positions",
        "Position / Role"
    ),

    (
        "summary",
        "Summary"
    )
]


JOB_FIELDS = [

    (
        "job_title",
        "Job Title *"
    ),

    (
        "required_skills",
        "Required Skills *"
    ),

    (
        "education_requirement",
        "Education Requirement"
    ),

    (
        "experience_requirement",
        "Experience Requirement"
    ),

    (
        "responsibilities",
        "Responsibilities"
    )
]


def render_mapping(
    columns,
    suggested,
    fields,
    prefix
):

    mapping = {}

    options = [
        "-- Not Mapped --"
    ] + list(
        columns
    )


    for standard_field, label in fields:

        suggested_column = (
            suggested.get(
                standard_field
            )
            if suggested
            else None
        )


        if suggested_column in options:

            index = options.index(
                suggested_column
            )

        else:

            index = 0


        selected = st.selectbox(

            label,

            options,

            index=index,

            key=(
                f"{prefix}_"
                f"{standard_field}"
            )
        )


        if selected == "-- Not Mapped --":

            mapping[
                standard_field
            ] = None

        else:

            mapping[
                standard_field
            ] = selected


    return mapping


def dataset_mapping_section(
    uploaded_file,
    dataset_type,
    key_prefix
):

    if uploaded_file is None:

        return None


    state_key = (
        f"{key_prefix}_"
        f"inspection"
    )


    previous = st.session_state.get(
        state_key
    )


    if (
        previous
        and
        previous.get(
            "file_name"
        )
        !=
        uploaded_file.name
    ):

        st.session_state.pop(
            state_key,
            None
        )


    if st.button(
        "Analyze Dataset Columns",
        key=f"{key_prefix}_analyze"
    ):

        with st.spinner(
            "Analyzing dataset..."
        ):

            info = inspect_dataset(
                uploaded_file,
                dataset_type
            )


        if info:

            st.session_state[
                state_key
            ] = info


    info = st.session_state.get(
        state_key
    )


    if not info:

        st.info(
            "Click 'Analyze Dataset Columns' first."
        )

        return None


    st.write(
        f"Rows: **{info['rows']}**"
        f" | Columns: "
        f"**{info['columns_count']}**"
    )


    preview = info.get(
        "preview",
        []
    )


    if preview:

        with st.expander(
            "Dataset Preview"
        ):

            st.dataframe(
                pd.DataFrame(
                    preview
                ),
                use_container_width=True,
                hide_index=True
            )


    if dataset_type == "candidate":

        fields = CANDIDATE_FIELDS

    else:

        fields = JOB_FIELDS


    st.markdown(
        "#### Column Mapping"
    )


    mapping = render_mapping(

        columns=
            info[
                "columns"
            ],

        suggested=
            info.get(
                "suggested_mapping",
                {}
            ),

        fields=
            fields,

        prefix=
            key_prefix
    )


    return mapping


# ============================================================
# DOWNLOAD GENERATED CV
# ============================================================

def render_cv_download(
    download_url,
    filename,
    key
):

    if not download_url:

        return


    try:

        response = requests.get(

            f"{API_BASE_URL}"
            f"{download_url}",

            timeout=60
        )


        if response.ok:

            st.download_button(

                "Download Generated CV",

                data=
                    response.content,

                file_name=
                    filename,

                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),

                key=key
            )

        else:

            st.warning(
                "Could not download generated CV."
            )


    except Exception as e:

        st.warning(
            f"Download error: {e}"
        )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    'AI CV Scanner & Job Matching System'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="subtitle">'
    'CV Screening • NLP Matching • Candidate Ranking • '
    'Job Recommendation • CV Builder'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# API STATUS
# ============================================================

if api_health():

    st.sidebar.success(
        "Backend Connected"
    )

else:

    st.sidebar.error(
        "Backend Offline"
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "System Mode"
)


mode = st.sidebar.radio(

    "Choose Mode",

    [

        "Upload CV + Job Description",

        "Build CV + Job Description",

        "Candidate Dataset + Job Description",

        "CV + Jobs Dataset",

        "Candidates Dataset + Jobs Dataset"
    ]
)


threshold = st.sidebar.slider(

    "Qualification Threshold",

    min_value=0,

    max_value=100,

    value=80,

    step=1
)


st.sidebar.caption(
    "Default project threshold: 80%"
)


# ============================================================
# MODE 1
# UPLOAD CV + RAW JD
# ============================================================

if mode == "Upload CV + Job Description":

    st.header(
        "Upload CV + Job Description"
    )


    cv_file = st.file_uploader(

        "Upload CV",

        type=[
            "pdf",
            "docx",
            "txt"
        ],

        key="personal_cv"
    )


    job_description = st.text_area(

        "Paste Job Description",

        height=300,

        placeholder=(
            "Paste the complete job description here..."
        )
    )


    if st.button(
        "Scan CV",
        type="primary"
    ):

        if cv_file is None:

            st.error(
                "Please upload a CV."
            )

        elif not job_description.strip():

            st.error(
                "Please enter a Job Description."
            )

        else:

            with st.spinner(
                "Parsing CV and matching..."
            ):

                data = api_post(

                    "/scan-cv-jd",

                    data={

                        "job_description":
                            job_description,

                        "threshold":
                            threshold
                    },

                    files={

                        "cv":
                            upload_file_tuple(
                                cv_file
                            )
                    }
                )


            if data:

                candidate = data.get(
                    "candidate",
                    {}
                )


                st.subheader(
                    "Extracted Candidate Data"
                )


                c1, c2, c3 = st.columns(
                    3
                )


                c1.write(
                    "**Candidate:** "
                    +
                    str(
                        candidate.get(
                            "candidate_id",
                            ""
                        )
                    )
                )


                c2.write(
                    "**Experience:** "
                    +
                    str(
                        candidate.get(
                            "estimated_experience_years",
                            0
                        )
                    )
                    +
                    " years"
                )


                c3.write(
                    "**Education:** "
                    +
                    str(
                        candidate.get(
                            "detected_education",
                            ""
                        )
                        or
                        "Not detected"
                    )
                )


                st.write(
                    "**Extracted Skills:**",
                    ", ".join(
                        candidate.get(
                            "extracted_skills",
                            []
                        )
                    )
                    or
                    "No skills detected"
                )


                show_job_info(
                    data.get(
                        "parsed_job"
                    )
                )


                show_match_result(
                    data.get(
                        "match_result"
                    )
                )


# ============================================================
# MODE 2
# BUILD CV
# ============================================================

elif mode == "Build CV + Job Description":

    st.header(
        "Build Professional CV"
    )


    st.caption(
        "Enter your information and the system "
        "will generate a CV and match it with the job."
    )


    col1, col2 = st.columns(
        2
    )


    with col1:

        full_name = st.text_input(
            "Full Name *"
        )

        email = st.text_input(
            "Email"
        )

        phone = st.text_input(
            "Phone"
        )


    with col2:

        location = st.text_input(
            "Location"
        )

        linkedin = st.text_input(
            "LinkedIn"
        )

        github = st.text_input(
            "GitHub"
        )


    summary = st.text_area(

        "Professional Summary",

        height=120
    )


    skills_text = st.text_area(

        "Skills *",

        placeholder=(
            "Python, SQL, Machine Learning, "
            "TensorFlow, FastAPI"
        )
    )


    experience_years = st.number_input(

        "Total Experience Years",

        min_value=0.0,

        max_value=60.0,

        value=0.0,

        step=0.5
    )


    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    st.subheader(
        "Professional Experience"
    )


    experience_count = st.number_input(

        "Number of Experience Entries",

        min_value=0,

        max_value=5,

        value=1,

        step=1
    )


    experience_entries = []


    for i in range(
        int(
            experience_count
        )
    ):

        with st.expander(
            f"Experience {i + 1}",
            expanded=(
                i == 0
            )
        ):

            position = st.text_input(

                "Position",

                key=f"exp_position_{i}"
            )


            company = st.text_input(

                "Company",

                key=f"exp_company_{i}"
            )


            e1, e2 = st.columns(
                2
            )


            with e1:

                start_date = st.text_input(

                    "Start Date",

                    key=f"exp_start_{i}"
                )


            with e2:

                end_date = st.text_input(

                    "End Date",

                    key=f"exp_end_{i}"
                )


            description = st.text_area(

                "Responsibilities / Achievements",

                key=f"exp_desc_{i}"
            )


            if any(
                [
                    position,
                    company,
                    description
                ]
            ):

                experience_entries.append(
                    {

                        "position":
                            position,

                        "company":
                            company,

                        "start_date":
                            start_date,

                        "end_date":
                            end_date,

                        "description":
                            description
                    }
                )


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    st.subheader(
        "Education"
    )


    education_count = st.number_input(

        "Number of Education Entries",

        min_value=0,

        max_value=5,

        value=1,

        step=1
    )


    education_entries = []


    for i in range(
        int(
            education_count
        )
    ):

        with st.expander(
            f"Education {i + 1}",
            expanded=(
                i == 0
            )
        ):

            degree = st.text_input(

                "Degree",

                key=f"edu_degree_{i}"
            )


            field = st.text_input(

                "Field of Study",

                key=f"edu_field_{i}"
            )


            institution = st.text_input(

                "Institution",

                key=f"edu_institution_{i}"
            )


            year = st.text_input(

                "Year",

                key=f"edu_year_{i}"
            )


            if any(
                [
                    degree,
                    field,
                    institution
                ]
            ):

                education_entries.append(
                    {

                        "degree":
                            degree,

                        "field":
                            field,

                        "institution":
                            institution,

                        "year":
                            year
                    }
                )


    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    st.subheader(
        "Projects"
    )


    project_count = st.number_input(

        "Number of Projects",

        min_value=0,

        max_value=5,

        value=1,

        step=1
    )


    projects = []


    for i in range(
        int(
            project_count
        )
    ):

        with st.expander(
            f"Project {i + 1}"
        ):

            project_name = st.text_input(

                "Project Name",

                key=f"project_name_{i}"
            )


            project_description = st.text_area(

                "Project Description",

                key=f"project_desc_{i}"
            )


            if (
                project_name
                or
                project_description
            ):

                projects.append(
                    {

                        "name":
                            project_name,

                        "description":
                            project_description
                    }
                )


    certifications_text = st.text_area(

        "Certifications",

        placeholder=(
            "Certification 1, Certification 2"
        )
    )


    languages_text = st.text_input(

        "Languages",

        placeholder=(
            "Arabic, English"
        )
    )


    st.subheader(
        "Job Description"
    )


    job_description = st.text_area(

        "Paste Job Description",

        height=250,

        key="builder_jd"
    )


    profile = {

        "full_name":
            full_name,

        "email":
            email,

        "phone":
            phone,

        "location":
            location,

        "linkedin":
            linkedin,

        "github":
            github,

        "professional_summary":
            summary,

        "skills":
            skills_text,

        "experience_years":
            experience_years,

        "experience":
            experience_entries,

        "education":
            education_entries,

        "projects":
            projects,

        "certifications":
            certifications_text,

        "languages":
            languages_text
    }


    b1, b2 = st.columns(
        2
    )


    with b1:

        generate_only = st.button(
            "Generate CV"
        )


    with b2:

        generate_match = st.button(
            "Generate CV & Match",
            type="primary"
        )


    if generate_only:

        if not full_name.strip():

            st.error(
                "Please enter your full name."
            )

        elif not skills_text.strip():

            st.error(
                "Please enter your skills."
            )

        else:

            with st.spinner(
                "Generating CV..."
            ):

                data = api_post(

                    "/build-cv",

                    data={

                        "profile_json":
                            json.dumps(
                                profile
                            )
                    }
                )


            if data:

                st.success(
                    "CV generated successfully."
                )


                render_cv_download(

                    data.get(
                        "download_url"
                    ),

                    data.get(
                        "filename",
                        "Generated_CV.docx"
                    ),

                    key="download_cv_only"
                )


    if generate_match:

        if not full_name.strip():

            st.error(
                "Please enter your full name."
            )

        elif not skills_text.strip():

            st.error(
                "Please enter your skills."
            )

        elif not job_description.strip():

            st.error(
                "Please enter a Job Description."
            )

        else:

            with st.spinner(
                "Generating CV and matching..."
            ):

                data = api_post(

                    "/build-cv-and-match",

                    data={

                        "profile_json":
                            json.dumps(
                                profile
                            ),

                        "job_description":
                            job_description,

                        "threshold":
                            threshold
                    }
                )


            if data:

                show_job_info(
                    data.get(
                        "parsed_job"
                    )
                )


                show_match_result(
                    data.get(
                        "match_result"
                    )
                )


                generated_cv = data.get(
                    "generated_cv",
                    {}
                )


                render_cv_download(

                    generated_cv.get(
                        "download_url"
                    ),

                    generated_cv.get(
                        "filename",
                        "Generated_CV.docx"
                    ),

                    key="download_cv_match"
                )


# ============================================================
# MODE 3
# CANDIDATE DATASET + RAW JD
# ============================================================

elif mode == "Candidate Dataset + Job Description":

    st.header(
        "Candidate Dataset Screening"
    )


    candidate_dataset = st.file_uploader(

        "Upload Candidate Dataset",

        type=[
            "csv",
            "xlsx",
            "xls"
        ],

        key="candidate_dataset"
    )


    candidate_mapping = (
        dataset_mapping_section(

            candidate_dataset,

            "candidate",

            "candidate_dataset_mode"
        )
    )


    job_description = st.text_area(

        "Paste Job Description",

        height=250,

        key="dataset_jd"
    )


    if st.button(
        "Scan Candidates",
        type="primary"
    ):

        if candidate_dataset is None:

            st.error(
                "Please upload a candidate dataset."
            )

        elif candidate_mapping is None:

            st.error(
                "Please analyze and map the dataset first."
            )

        elif not candidate_mapping.get(
            "skills"
        ):

            st.error(
                "Skills column is required."
            )

        elif not job_description.strip():

            st.error(
                "Please enter a Job Description."
            )

        else:

            with st.spinner(
                "Parsing job description..."
            ):

                parsed_job = api_post(

                    "/parse-job-description",

                    data={

                        "job_description":
                            job_description
                    }
                )


            if parsed_job:

                show_job_info(
                    parsed_job
                )


                with st.spinner(
                    "Scanning and ranking candidates..."
                ):

                    data = api_post(

                        "/scan-dataset",

                        data={

                            "mapping_json":
                                json.dumps(
                                    candidate_mapping
                                ),

                            "job_title":
                                parsed_job.get(
                                    "job_title",
                                    "Unknown Job"
                                ),

                            "required_skills":
                                ", ".join(
                                    parsed_job.get(
                                        "required_skills",
                                        []
                                    )
                                ),

                            "education_requirement":
                                parsed_job.get(
                                    "education_requirement",
                                    ""
                                ),

                            "experience_requirement":
                                parsed_job.get(
                                    "experience_requirement",
                                    ""
                                ),

                            "responsibilities":
                                parsed_job.get(
                                    "responsibilities",
                                    job_description
                                ),

                            "threshold":
                                threshold
                        },

                        files={

                            "dataset":
                                upload_file_tuple(
                                    candidate_dataset
                                )
                        }
                    )


                if data:

                    m1, m2 = st.columns(
                        2
                    )


                    m1.metric(
                        "Total Candidates",

                        data.get(
                            "total_candidates",
                            0
                        )
                    )


                    m2.metric(
                        "Qualified Candidates",

                        data.get(
                            "qualified_candidates",
                            0
                        )
                    )


                    show_ranking(

                        data.get(
                            "results",
                            []
                        ),

                        "Candidate Ranking"
                    )


# ============================================================
# MODE 4
# PERSONAL CV + JOBS DATASET
# ============================================================

elif mode == "CV + Jobs Dataset":

    st.header(
        "Job Recommendation"
    )


    cv_file = st.file_uploader(

        "Upload CV",

        type=[
            "pdf",
            "docx",
            "txt"
        ],

        key="recommend_cv"
    )


    jobs_dataset = st.file_uploader(

        "Upload Jobs Dataset",

        type=[
            "csv",
            "xlsx",
            "xls"
        ],

        key="jobs_dataset_recommend"
    )


    jobs_mapping = (
        dataset_mapping_section(

            jobs_dataset,

            "job",

            "jobs_recommend"
        )
    )


    if st.button(
        "Recommend Best Jobs",
        type="primary"
    ):

        if cv_file is None:

            st.error(
                "Please upload a CV."
            )

        elif jobs_dataset is None:

            st.error(
                "Please upload a jobs dataset."
            )

        elif jobs_mapping is None:

            st.error(
                "Please analyze and map the jobs dataset first."
            )

        elif not jobs_mapping.get(
            "job_title"
        ):

            st.error(
                "Job Title column is required."
            )

        elif not jobs_mapping.get(
            "required_skills"
        ):

            st.error(
                "Required Skills column is required."
            )

        else:

            with st.spinner(
                "Comparing CV with all jobs..."
            ):

                data = api_post(

                    "/recommend-jobs",

                    data={

                        "jobs_mapping_json":
                            json.dumps(
                                jobs_mapping
                            ),

                        "threshold":
                            threshold
                    },

                    files={

                        "cv":
                            upload_file_tuple(
                                cv_file
                            ),

                        "jobs_dataset":
                            upload_file_tuple(
                                jobs_dataset
                            )
                    }
                )


            if data:

                m1, m2 = st.columns(
                    2
                )


                m1.metric(
                    "Total Jobs",

                    data.get(
                        "total_jobs",
                        0
                    )
                )


                m2.metric(
                    "Qualified Jobs",

                    data.get(
                        "qualified_jobs",
                        0
                    )
                )


                show_ranking(

                    data.get(
                        "results",
                        []
                    ),

                    "Recommended Jobs"
                )


# ============================================================
# MODE 5
# CANDIDATE DATASET x JOB DATASET
# ============================================================

elif mode == "Candidates Dataset + Jobs Dataset":

    st.header(
        "Candidates × Jobs Matching"
    )


    col1, col2 = st.columns(
        2
    )


    with col1:

        candidates_dataset = (
            st.file_uploader(

                "Upload Candidates Dataset",

                type=[
                    "csv",
                    "xlsx",
                    "xls"
                ],

                key="all_candidates"
            )
        )


        candidates_mapping = (
            dataset_mapping_section(

                candidates_dataset,

                "candidate",

                "all_candidate_mapping"
            )
        )


    with col2:

        jobs_dataset = (
            st.file_uploader(

                "Upload Jobs Dataset",

                type=[
                    "csv",
                    "xlsx",
                    "xls"
                ],

                key="all_jobs"
            )
        )


        jobs_mapping = (
            dataset_mapping_section(

                jobs_dataset,

                "job",

                "all_job_mapping"
            )
        )


    if st.button(
        "Run Full Matching",
        type="primary"
    ):

        if (
            candidates_dataset
            is None
            or
            jobs_dataset
            is None
        ):

            st.error(
                "Please upload both datasets."
            )

        elif (
            candidates_mapping
            is None
            or
            jobs_mapping
            is None
        ):

            st.error(
                "Please analyze and map both datasets."
            )

        elif not candidates_mapping.get(
            "skills"
        ):

            st.error(
                "Candidate Skills column is required."
            )

        elif not jobs_mapping.get(
            "job_title"
        ):

            st.error(
                "Job Title column is required."
            )

        elif not jobs_mapping.get(
            "required_skills"
        ):

            st.error(
                "Required Skills column is required."
            )

        else:

            with st.spinner(
                "Running all candidate-job comparisons..."
            ):

                data = api_post(

                    "/scan-all",

                    data={

                        "candidates_mapping_json":
                            json.dumps(
                                candidates_mapping
                            ),

                        "jobs_mapping_json":
                            json.dumps(
                                jobs_mapping
                            ),

                        "threshold":
                            threshold
                    },

                    files={

                        "candidates_dataset":
                            upload_file_tuple(
                                candidates_dataset
                            ),

                        "jobs_dataset":
                            upload_file_tuple(
                                jobs_dataset
                            )
                    }
                )


            if data:

                m1, m2, m3, m4 = st.columns(
                    4
                )


                m1.metric(
                    "Candidates",

                    data.get(
                        "total_candidates",
                        0
                    )
                )


                m2.metric(
                    "Jobs",

                    data.get(
                        "total_jobs",
                        0
                    )
                )


                m3.metric(
                    "Comparisons",

                    data.get(
                        "total_comparisons",
                        0
                    )
                )


                m4.metric(
                    "Qualified Matches",

                    data.get(
                        "qualified_matches",
                        0
                    )
                )


                show_ranking(

                    data.get(
                        "results",
                        []
                    ),

                    "All Candidate-Job Matches"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Hybrid NLP CV Screening System • "
    "Sentence Transformers • FastAPI • Streamlit"
)
