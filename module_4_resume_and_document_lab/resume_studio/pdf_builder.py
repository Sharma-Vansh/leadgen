"""
Vector ATS Resume PDF Builder
Generates single-column, ATS-parseable vector PDF documents using ReportLab.
Guarantees clean OCR/text extraction for Workday, Greenhouse, Lever, and Taleo.
"""
import io
from typing import Any, Dict, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ResumePDFBuilder:
    """Builds clean, single-column, ATS-friendly PDF documents."""

    @classmethod
    def generate_pdf_bytes(cls, resume_data: Dict[str, Any]) -> bytes:
        """
        Renders resume data into an in-memory PDF byte stream.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,   # 0.5 inch
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom ATS Typography Styles
        name_style = ParagraphStyle(
            "ATS_Name",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1A1A1A")
        )

        contact_style = ParagraphStyle(
            "ATS_Contact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4A4A4A")
        )

        section_heading_style = ParagraphStyle(
            "ATS_SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=8,
            spaceAfter=3
        )

        body_style = ParagraphStyle(
            "ATS_Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#262626")
        )

        subheading_style = ParagraphStyle(
            "ATS_Subheading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1E293B")
        )

        story = []

        # 1. Header (Candidate Name & Contact Info)
        personal = resume_data.get("personal_info") or {}
        name = personal.get("full_name") or "Candidate"
        story.append(Paragraph(name.upper(), name_style))
        story.append(Spacer(1, 4))

        contact_parts = []
        if personal.get("email"):
            contact_parts.append(personal.get("email"))
        if personal.get("location"):
            contact_parts.append(personal.get("location"))
        if personal.get("linkedin_url"):
            contact_parts.append(personal.get("linkedin_url"))
        if personal.get("github_url"):
            contact_parts.append(personal.get("github_url"))

        contact_line = " | ".join(contact_parts)
        story.append(Paragraph(contact_line, contact_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceBefore=0, spaceAfter=8))

        # 2. Professional Summary
        summary = resume_data.get("professional_summary")
        if summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceBefore=0, spaceAfter=4))
            story.append(Paragraph(summary, body_style))
            story.append(Spacer(1, 8))

        # 3. Technical Skills
        skills_breakdown = resume_data.get("skills_breakdown") or {}
        core_skills = skills_breakdown.get("core_competencies") or []
        supporting = skills_breakdown.get("supporting_technologies") or []
        all_skills = skills_breakdown.get("all_skills") or (core_skills + supporting)

        if all_skills:
            story.append(Paragraph("TECHNICAL COMPETENCIES", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceBefore=0, spaceAfter=4))

            if core_skills:
                story.append(Paragraph(f"<b>Core Stack:</b> {', '.join(core_skills)}", body_style))
            if supporting:
                story.append(Paragraph(f"<b>Supporting Tools & Technologies:</b> {', '.join(supporting)}", body_style))
            elif not core_skills:
                story.append(Paragraph(f"<b>Skills:</b> {', '.join(all_skills)}", body_style))

            story.append(Spacer(1, 8))

        # 4. Education
        edu = resume_data.get("education") or {}
        if edu.get("degree"):
            story.append(Paragraph("EDUCATION", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceBefore=0, spaceAfter=4))

            edu_line_1 = f"{edu.get('degree')} in {edu.get('branch', 'Engineering')}"
            story.append(Paragraph(f"<b>{edu_line_1}</b>", subheading_style))

            edu_details = []
            if edu.get("college_name"):
                edu_details.append(edu.get("college_name"))
            if edu.get("passing_year"):
                edu_details.append(f"Graduation: {edu.get('passing_year')}")
            if edu.get("cgpa"):
                edu_details.append(f"CGPA: {edu.get('cgpa')}/10.0")

            if edu_details:
                story.append(Paragraph(" | ".join(edu_details), body_style))

            story.append(Spacer(1, 8))

        # 5. Target Role Alignment & Projects
        target_role = resume_data.get("target_role")
        target_company = resume_data.get("target_company")
        if target_role:
            story.append(Paragraph("TARGET ROLE ALIGNMENT", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceBefore=0, spaceAfter=4))
            align_text = (
                f"Curated for the <b>{target_role}</b> opening at <b>{target_company}</b>. "
                "Highlights proven project experience and relevant technical toolchains directly applicable to the team."
            )
            story.append(Paragraph(align_text, body_style))
            story.append(Spacer(1, 8))

        # 6. Certifications
        certs = resume_data.get("certifications") or []
        if certs:
            story.append(Paragraph("CERTIFICATIONS & CREDENTIALS", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceBefore=0, spaceAfter=4))
            for cert in certs:
                story.append(Paragraph(f"• {cert}", body_style))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
