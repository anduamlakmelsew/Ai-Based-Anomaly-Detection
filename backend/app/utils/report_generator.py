from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(scan_result, output_path):
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Security Scan Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Target: {scan_result['target']}", styles["Normal"]))
    elements.append(Paragraph(f"Risk Score: {scan_result['risk']['score']}", styles["Normal"]))
    elements.append(Paragraph(f"Risk Level: {scan_result['risk']['level']}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    for f in scan_result["findings"]:
        elements.append(Paragraph(f"<b>{f['type']}</b>", styles["Heading3"]))
        elements.append(Paragraph(f"Severity: {f['severity']}", styles["Normal"]))
        elements.append(Paragraph(f"URL: {f.get('url','')}", styles["Normal"]))
        elements.append(Paragraph(f"Fix: {f.get('remediation','')}", styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)