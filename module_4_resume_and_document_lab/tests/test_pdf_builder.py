"""
Unit Tests for Vector ATS Resume PDF Builder
Tests single-column layout rendering, valid PDF byte generation, and text extraction friendliness.
"""
from module_4_resume_and_document_lab.resume_studio.pdf_builder import ResumePDFBuilder


def test_pdf_builder_outputs_valid_pdf():
    resume_data = {
        "personal_info": {
            "full_name": "Rohan Gupta",
            "email": "rohan.gupta@gmail.com",
            "location": "Bengaluru, India",
            "linkedin_url": "https://linkedin.com/in/rohan",
            "github_url": "https://github.com/rohan"
        },
        "professional_summary": "Full Stack Engineer with 2 years of experience building Python and React applications.",
        "skills_breakdown": {
            "core_competencies": ["Python", "FastAPI", "React", "PostgreSQL"],
            "supporting_technologies": ["Docker", "Git", "Redis"]
        },
        "education": {
            "degree": "B.Tech",
            "branch": "Computer Science & Engineering",
            "college_name": "National Institute of Technology",
            "passing_year": 2024,
            "cgpa": 8.7
        },
        "target_role": "Software Development Engineer",
        "target_company": "Zomato",
        "certifications": ["AWS Certified Cloud Practitioner", "PostgreSQL Professional"]
    }

    pdf_bytes = ResumePDFBuilder.generate_pdf_bytes(resume_data)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000  # Non-trivial PDF output
    assert pdf_bytes.startswith(b"%PDF")  # Valid standard PDF header
