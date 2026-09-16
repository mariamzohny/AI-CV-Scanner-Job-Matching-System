# AI CV Scanner & Job Matching System

Software application built with **FastAPI, Streamlit, and Sentence Transformers**.

An end-to-end **Hybrid NLP-based Recruitment System** designed for both **individual users and organizations**.

For individuals, the system supports **CV creation, CV analysis, job matching, and job recommendation**.

For recruiters, HR teams, and organizations, it supports **candidate screening, candidate ranking, job dataset analysis, and large-scale candidate-job matching**.

The system combines **Sentence Transformers, NLP, skill matching, experience matching, and education matching** to calculate candidate-job compatibility across multiple recruitment workflows.

Built with **Python, FastAPI, Streamlit, Sentence Transformers, Pandas, and NLP techniques**.

---

## System Architecture

```text
                           AI CV Scanner & Job Matching System
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        │                                   │                                   │
        ▼                                   ▼                                   ▼
  Upload Existing CV                 Build CV from Form                 Upload Dataset(s)
   (PDF / DOCX / TXT)                (No CV Available)                 (Candidates / Jobs)
        │                                   │                                   │
        ▼                                   ▼                                   ▼
    cv_parser.py                      cv_builder.py                    dataset_processor.py
        │                                   │                                   │
        │                                   ├──────────────► Generate CV (.docx)
        │                                   │
        │                                   ▼
        │                          Standard Candidate Format
        │                                   │
        └───────────────────────────┬───────┘
                                    │
                                    ▼
                           Standard Candidate Object
                                    │
                                    │
                     Raw Job Description / Jobs Dataset
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
              job_parser.py                  standardize_jobs()
                    │                               │
                    ▼                               ▼
             Parsed Job Object               Standard Job Object
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                                scanner.py
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
   Skills Matching           Semantic Matching         Experience / Education
        │                           │                           │
        └───────────────┬───────────┴───────────┬──────────────┘
                        │                       │
                        ▼                       ▼
                Final Match Score        Top 3 Matching Skills
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
     Score >= 80%              Score < 80%
            │                       │
            ▼                       ▼
 Passed First Phase          Not Passed
 Qualified for Interview
```

---

# Detailed Workflows

The system supports multiple ways of working with candidates and job requirements.

---

## 1. Existing CV + Job Description

A user who already has a CV can upload it in **PDF, DOCX, or TXT** format and paste a complete Job Description.

```text
Upload CV
   │
   ▼
cv_parser.py
   │
   ├──► Extract Skills
   ├──► Extract Education
   ├──► Estimate Experience
   └──► Extract Full CV Text
   │
   ▼
Standard Candidate
   │
   │
Paste Raw Job Description
   │
   ▼
job_parser.py
   │
   ├──► Job Title
   ├──► Required Skills
   ├──► Experience Requirement
   ├──► Education Requirement
   └──► Full Job Description
   │
   ▼
Standard Job
   │
   ▼
scanner.py
   │
   ▼
Candidate ↔ Job Matching
   │
   ▼
Final Match Score
   │
   ├──► Passed / Not Passed
   ├──► Matched Skills
   ├──► Missing Skills
   └──► Top 3 Matching Skills
```

---

## 2. Build CV + Job Description

If the user does not already have a CV, they can enter their information directly into the system.

The system generates a professional `.docx` CV and can immediately match the candidate with a Job Description.

```text
User Information Form
        │
        ▼
    cv_builder.py
        │
        ├──────────────────────► Generated Professional CV (.docx)
        │
        ▼
Standard Candidate Profile
        │
        │
Paste Job Description
        │
        ▼
   job_parser.py
        │
        ▼
   Standard Job
        │
        ▼
     scanner.py
        │
        ▼
   Match Result
        │
        ├──► Final Score
        ├──► Pass / Fail
        ├──► Matching Skills
        └──► Download Generated CV
```

The CV Builder supports:

- Personal Information
- Professional Summary
- Skills
- Work Experience
- Education
- Projects
- Certifications
- Languages
- LinkedIn
- GitHub

---

## 3. Candidate Dataset + Job Description

Recruiters can upload a complete candidate dataset in **CSV or Excel** format.

The system automatically analyzes the dataset structure and maps its columns into the internal candidate format.

```text
Candidate Dataset
   CSV / Excel
       │
       ▼
dataset_processor.py
       │
       ▼
Automatic Column Detection
       │
       ▼
Column Mapping
       │
       ▼
Standard Candidates
       │
       │
Job Description
       │
       ▼
 job_parser.py
       │
       ▼
   Standard Job
       │
       ▼
    scanner.py
       │
       ▼
Scan All Candidates
       │
       ▼
Candidate Ranking
       │
       ├──► Match Scores
       ├──► Qualified Candidates
       ├──► Matched Skills
       └──► Missing Skills
```

Example automatic mapping:

```text
Applicant         → candidate_id
TechnicalSkills   → skills
Degree            → education
YearsWorked       → experience_years
CurrentRole       → positions
Profile           → summary
```

---

## 4. CV + Jobs Dataset

A candidate can upload one CV and compare it against multiple jobs.

This works as a **Job Recommendation System**.

```text
Candidate CV
    │
    ▼
cv_parser.py
    │
    ▼
Standard Candidate
    │
    │
Jobs Dataset
CSV / Excel
    │
    ▼
dataset_processor.py
    │
    ▼
Standard Jobs
    │
    ▼
scanner.py
    │
    ▼
Candidate vs All Jobs
    │
    ▼
Job Ranking
    │
    ├──► Best Matching Jobs
    ├──► Match Score per Job
    ├──► Qualified Jobs
    └──► Missing / Matching Skills
```

---

## 5. Candidates Dataset + Jobs Dataset

The system can also process multiple candidates against multiple jobs.

```text
Candidates Dataset
        │
        ▼
dataset_processor.py
        │
        ▼
Standard Candidates
        │
        │
        ├───────────────────────┐
        │                       │
        │                       │
Jobs Dataset                    │
        │                       │
        ▼                       │
dataset_processor.py            │
        │                       │
        ▼                       │
Standard Jobs ──────────────────┘
        │
        ▼
     scanner.py
        │
        ▼
All Candidate × Job Comparisons
        │
        ▼
Ranking & Qualification
        │
        ├──► Best Candidate per Job
        ├──► Best Jobs per Candidate
        ├──► Qualified Matches
        └──► Match Scores
```

Example:

```text
100 Candidates
       ×
20 Jobs
       ↓
2,000 Candidate-Job Comparisons
```

---

# Matching Engine

The hybrid matching engine combines four components:

```text
Candidate + Job
      │
      ▼
  scanner.py
      │
      ├────────► Skills Matching
      │              │
      │              ▼
      │           60%
      │
      ├────────► Semantic Matching
      │              │
      │              ▼
      │           20%
      │
      ├────────► Experience Matching
      │              │
      │              ▼
      │           10%
      │
      └────────► Education Matching
                     │
                     ▼
                  10%
                     │
                     ▼
              Final Match Score
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
           >= 80%         < 80%
              │             │
              ▼             ▼
           Passed       Not Passed
```

### Scoring Weights

| Component | Weight |
|---|---:|
| Skills Matching | 60% |
| Semantic Matching | 20% |
| Experience Matching | 10% |
| Education Matching | 10% |

---

## Semantic Matching

Semantic similarity is calculated using the pretrained Sentence Transformer:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Instead of comparing only keywords, the Transformer compares the semantic meaning of the candidate profile and the Job Description.

```text
Full CV / Candidate Profile
            │
            ▼
    Sentence Transformer
            ▲
            │
   Full Job Description
            │
            ▼
     Semantic Score
```

---

## Qualification Logic

The default qualification threshold is:

```text
80%
```

```text
Final Match Score
        │
        ▼
   Score >= 80%?
      /      \
    Yes       No
     │         │
     ▼         ▼
   Passed   Not Passed
     │
     ▼
Qualified for
Actual Interview
     │
     ▼
Top 3 Matching Skills
```

The qualification threshold can also be adjusted from the application interface.

---

## Technology Stack

```text
Frontend
   └── Streamlit

Backend
   └── FastAPI

NLP / AI
   ├── Sentence Transformers
   ├── Hugging Face
   ├── RapidFuzz
   └── NLP Text Processing

Data Processing
   ├── Pandas
   └── NumPy

Document Processing
   ├── PyPDF
   └── python-docx

Model
   └── all-MiniLM-L6-v2
```

---

## Project Structure

```text
CV_Scanner_Project/
│
├── backend/
│   ├── __init__.py
│   ├── scanner.py
│   ├── dataset_processor.py
│   ├── cv_parser.py
│   ├── job_parser.py
│   ├── cv_builder.py
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── data/
│
├── notebooks/
│   └── 01_CV_Scanner_Core_Engine.ipynb
│
├── outputs/
├── uploads/
│
├── requirements.txt
└── README.md
```

---

## Important Note

This system is designed as an **AI-assisted recruitment screening and decision-support system**.

The generated match score is intended to help organize and prioritize candidate-job matches and should not replace human recruiter review.
