import os
from datetime import datetime

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph


def generate_report(username, original_text, redacted_text, entities):

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"report_{timestamp}.pdf"

    filepath = os.path.join("reports", filename)

    doc = SimpleDocTemplate(filepath)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>HealthTech AI Redaction Report</b>", styles["Title"]))

    story.append(Paragraph(f"<b>User:</b> {username}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now()}", styles["Normal"]))

    story.append(Paragraph("<br/><b>Original Text</b>", styles["Heading2"]))
    story.append(Paragraph(original_text.replace("\n", "<br/>"), styles["Normal"]))

    story.append(Paragraph("<br/><b>Redacted Text</b>", styles["Heading2"]))
    story.append(Paragraph(redacted_text.replace("\n", "<br/>"), styles["Normal"]))

    story.append(Paragraph("<br/><b>Entities Found</b>", styles["Heading2"]))

    for entity in entities:
        story.append(Paragraph(f"• {entity}", styles["Normal"]))

    doc.build(story)

    return filepath