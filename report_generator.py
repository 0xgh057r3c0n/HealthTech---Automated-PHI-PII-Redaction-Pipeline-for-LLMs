import os
import re
import uuid
from collections import Counter
from datetime import datetime
from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _safe_text(value):
    if value is None:
        return ""
    return escape(str(value).strip()).replace("\n", "<br/>")


def _extract_field(text, labels):
    if not text:
        return "Not available"
    haystack = str(text)
    for label in labels:
        pattern = rf"(?im)^{re.escape(label)}\s*[:\-]?\s*(.+)"
        match = re.search(pattern, haystack)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    for line in haystack.splitlines():
        for label in labels:
            if line.lower().startswith(label.lower()):
                value = line[len(label):].strip().lstrip(":- ")
                if value:
                    return value
    return "Not available"


def _extract_section(text, labels):
    if not text:
        return "Not available"

    haystack = str(text)
    section_headers = (
        "patient name",
        "doctor name",
        "doctor",
        "patient",
        "email",
        "phone",
        "hospital",
        "specialty",
        "patient id",
        "city",
        "disease",
        "address",
        "mrn",
        "clinical note",
        "clinical summary",
        "provider note",
        "doctor note",
        "assessment",
        "report details",
        "narrative",
        "doctor summary",
        "doctor recommendation",
        "recommended action",
        "care plan",
        "patient guidance",
        "follow-up plan",
        "what the patient should do",
        "recommendation",
    )

    for label in labels:
        pattern = rf"(?is)(?:^|\n)\s*{re.escape(label)}\s*[:\-]?\s*(.*?)(?=(?:\n\s*(?:{'|'.join(re.escape(h) for h in section_headers)})\b)|\Z)"
        match = re.search(pattern, haystack)
        if match:
            value = re.sub(r"\s+", " ", match.group(1)).strip()
            if value:
                return value

    lines = [line.strip() for line in haystack.splitlines()]
    capture = False
    collected = []
    for line in lines:
        if not line:
            continue
        lower = line.lower()
        if any(lower.startswith(label.lower()) for label in labels):
            capture = True
            remainder = line.split(":", 1)[-1].split("-", 1)[-1].strip() if ":" in line or "-" in line else ""
            if remainder:
                collected.append(remainder)
            continue
        if capture:
            if any(lower.startswith(header.lower()) for header in section_headers if header.lower() not in [l.lower() for l in labels]):
                break
            collected.append(line)
    cleaned = " ".join(part for part in collected if part).strip()
    return cleaned if cleaned else "Not available"


def _build_clinical_narrative(text):
    if not text:
        return "No clinical note available."

    note = _extract_section(text, [
        "Clinical Note",
        "Clinical Summary",
        "Provider Note",
        "Doctor Note",
        "Assessment",
        "Report Details",
        "Narrative",
        "Doctor Summary",
    ])
    recommendation = _extract_section(text, [
        "Doctor Recommendation",
        "What the patient should do",
        "Recommended Action",
        "Care Plan",
        "Follow-up Plan",
        "Patient Guidance",
        "Recommendation",
        "Plan",
    ])

    sections = []
    if note and note != "Not available":
        sections.append(f"Clinical Note:\n{note}")
    if recommendation and recommendation != "Not available":
        sections.append(f"Doctor Recommendation / What the patient should do:\n{recommendation}")

    if sections:
        return "\n\n".join(sections)

    # Fallback: keep the meaningful clinical text while removing identity/contact metadata.
    lines = [line.strip() for line in str(text).splitlines()]
    narrative = []
    sensitive_prefixes = (
        "patient name",
        "doctor name",
        "doctor",
        "patient",
        "email",
        "phone",
        "hospital",
        "specialty",
        "patient id",
        "city",
        "disease",
        "address",
        "mrn",
    )
    for line in lines:
        if not line:
            continue
        lower = line.lower()
        if lower.startswith(sensitive_prefixes):
            continue
        if lower.startswith(("patient name", "doctor name", "email", "phone", "hospital", "city", "disease")):
            continue
        narrative.append(line)

    cleaned = " ".join(narrative).strip()
    return cleaned if cleaned else "No clinical note available."


def generate_report(username, original_text, redacted_text, entities):
    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_id = uuid.uuid4().hex[:8]
    filename = f"report_{timestamp}_{report_id}.pdf"
    filepath = os.path.join("reports", filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle("ReportSubtitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle("ReportSectionTitle", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=colors.HexColor("#0f172a"), spaceAfter=6))
    styles.add(ParagraphStyle("ReportSummaryLabel", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.4, leading=10, textColor=colors.HexColor("#475569")))
    styles.add(ParagraphStyle("ReportSummaryValue", parent=styles["Normal"], fontName="Helvetica", fontSize=9.6, leading=12, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle("ReportBodyText", parent=styles["Normal"], fontName="Helvetica", fontSize=10.2, leading=15, textColor=colors.HexColor("#111827")))
    styles.add(ParagraphStyle("ReportChip", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.2, leading=10, textColor=colors.HexColor("#0f172a"), backColor=colors.HexColor("#e0f2fe"), borderColor=colors.HexColor("#7dd3fc"), borderWidth=0.5, borderPadding=4, alignment=1))
    styles.add(ParagraphStyle("ReportSignature", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.8, leading=11, textColor=colors.HexColor("#475569"), alignment=1))

    patient_name = _extract_field(original_text, ["Patient Name", "Patient", "Name"])
    doctor_name = _extract_field(original_text, ["Doctor Name", "Doctor", "Clinician", "Provider"])
    doctor_specialty = _extract_field(original_text, ["Specialty", "Department", "Role", "Designation"])
    patient_id = _extract_field(original_text, ["Patient ID", "MRN", "Patient Identifier", "ID"])

    clinical_note = _extract_section(original_text, [
        "Clinical Note",
        "Clinical Summary",
        "Provider Note",
        "Doctor Note",
        "Assessment",
        "Report Details",
        "Narrative",
        "Doctor Summary",
    ])
    doctor_instruction = _extract_section(original_text, [
        "Doctor Recommendation",
        "What the patient should do",
        "Recommended Action",
        "Care Plan",
        "Follow-up Plan",
        "Patient Guidance",
        "Recommendation",
        "Plan",
        "Instructions",
    ])

    narrative = _build_clinical_narrative(original_text)
    if narrative == "No clinical note available.":
        narrative = _build_clinical_narrative(redacted_text)
    if clinical_note == "Not available":
        clinical_note = narrative
    if doctor_instruction == "Not available":
        doctor_instruction = "No specific instruction recorded by the doctor."

    story = []

    header = Table(
       [[Paragraph("HealthTech", styles["ReportTitle"]), Paragraph("HealthTech PHI/PII Redaction Audit Report\\nMedical consultation summary", styles["ReportSubtitle"]) ]],
       colWidths=[180, 320],
   )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#0f172a")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#2563eb")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 12))

    summary = Table(
        [[
            Paragraph("<b>Patient</b><br/>" + _safe_text(patient_name), styles["ReportSummaryValue"]),
            Paragraph("<b>Doctor</b><br/>" + _safe_text(doctor_name), styles["ReportSummaryValue"]),
            Paragraph("<b>Generated</b><br/>" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles["ReportSummaryValue"]),
            Paragraph("<b>Report ID</b><br/>" + _safe_text(report_id), styles["ReportSummaryValue"]),
        ]],
        colWidths=[120, 120, 160, 110],
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(summary)
    story.append(Spacer(1, 16))

    def section_card(title, content):
        table = Table(
            [[Paragraph(title, styles["ReportSectionTitle"])], [Paragraph(_safe_text(content) or "No content available.", styles["ReportBodyText"]) ]],
            colWidths=[500],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 1.0, colors.HexColor("#bfdbfe")),
                    ("LINEABOVE", (0, 0), (-1, 0), 2.0, colors.HexColor("#2563eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        return table

    patient_doctor_info = (
        f"Patient Name: {patient_name}\n"
        f"Doctor Name: {doctor_name}\n"
        f"Specialty: {doctor_specialty}\n"
        f"Patient ID: {patient_id}"
    )
    story.append(section_card("Patient & Doctor Information", patient_doctor_info))
    story.append(Spacer(1, 14))

    story.append(section_card("Clinical Note", clinical_note))
    story.append(Spacer(1, 14))
    story.append(section_card("Doctor Instructions / What the patient should do", doctor_instruction))
    story.append(Spacer(1, 14))

    entity_counter = Counter(entities)
    total_identifiers_removed = len(entities)
    unique_identifier_classes = len(entity_counter)
    risk_classification = "High risk" if total_identifiers_removed >= 5 or unique_identifier_classes >= 4 else "Moderate risk"
    role = "doctor" if "doctor" in str(username).lower() else "patient"
    prepared_for = f"Prepared for: {username} | Role: {role}"
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    audit_summary = Table(
        [
            [Paragraph("Prepared for", styles["ReportSummaryLabel"]), Paragraph(_safe_text(username), styles["ReportSummaryValue"])],
            [Paragraph("Role", styles["ReportSummaryLabel"]), Paragraph(_safe_text(role), styles["ReportSummaryValue"])],
            [Paragraph("Generated on", styles["ReportSummaryLabel"]), Paragraph(_safe_text(generated_on), styles["ReportSummaryValue"])],
            [Paragraph("Total identifiers removed", styles["ReportSummaryLabel"]), Paragraph(_safe_text(total_identifiers_removed), styles["ReportSummaryValue"])],
            [Paragraph("Unique identifier classes", styles["ReportSummaryLabel"]), Paragraph(_safe_text(unique_identifier_classes), styles["ReportSummaryValue"])],
            [Paragraph("Risk classification", styles["ReportSummaryLabel"]), Paragraph(_safe_text(risk_classification), styles["ReportSummaryValue"])],
            [Paragraph("Processing status", styles["ReportSummaryLabel"]), Paragraph("Completed before external AI submission", styles["ReportSummaryValue"])],
        ],
        colWidths=[180, 320],
    )
    audit_summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(section_card("Executive Summary", "Multiple direct identifiers were detected across the note; all were masked before external processing to reduce re-identification risk."))
    story.append(Spacer(1, 10))
    story.append(audit_summary)
    story.append(Spacer(1, 14))

    if entity_counter:
        breakdown_rows = [[Paragraph("Entity Type", styles["ReportSummaryLabel"]), Paragraph("Count", styles["ReportSummaryLabel"])]]
        for entity_name, count in sorted(entity_counter.items()):
            breakdown_rows.append([Paragraph(_safe_text(entity_name), styles["ReportSummaryValue"]), Paragraph(_safe_text(count), styles["ReportSummaryValue"])])
        breakdown = Table(breakdown_rows, colWidths=[250, 250])
        breakdown.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(section_card("Detected PHI/PII Breakdown", ""))
        story.append(breakdown)
        story.append(Spacer(1, 14))

    story.append(section_card("Original Clinical Text", original_text))
    story.append(Spacer(1, 14))
    story.append(section_card("Redacted Output", redacted_text))
    story.append(Spacer(1, 14))

    hipaa_text = "• Names\n• All geographic subdivisions smaller than a state\n• Dates except year\n• Telephone numbers\n• Fax numbers\n• Email addresses\n• Social Security numbers\n• Medical record numbers"
    story.append(section_card("HIPAA Safe Harbor Coverage", hipaa_text))
    story.append(Spacer(1, 14))
    story.append(section_card(
        "Compliance Notes",
        "The de-identification workflow identified direct identifiers, replaced them with neutral placeholders, and preserved clinical meaning necessary for downstream review. This reduces exposure risk while maintaining sufficient context for medical documentation and AI-assisted summarization."
    ))
    story.append(Spacer(1, 18))

    signature = Table(
        [[Paragraph("Reviewed by", styles["ReportSignature"]), Paragraph("________________________", styles["ReportSummaryValue"]), Paragraph("Approved by", styles["ReportSignature"]), Paragraph("________________________", styles["ReportSummaryValue"]) ]],
        colWidths=[100, 170, 100, 170],
    )
    signature.setStyle(
        TableStyle(
            [
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("ALIGN", (3, 0), (3, 0), "CENTER"),
            ]
        )
    )
    story.append(signature)

    doc.build(story)
    return filepath
