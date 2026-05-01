# -*- coding: utf-8 -*-
"""
Created on Fri May  1 09:35:17 2026

@author: Caroline Adams
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def create_full_report(summary_content, output_path="report.pdf"):

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph("Wheelchair Racing Performance Monitoring Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Loop through content blocks
    for block in summary_content:
        elements.append(Paragraph(block, styles["Normal"]))
        elements.append(Spacer(1, 12))

    doc.build(elements)

    return output_path
