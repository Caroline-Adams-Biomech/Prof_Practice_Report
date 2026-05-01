# -*- coding: utf-8 -*-
"""
Created on Fri May  1 09:35:17 2026

@author: Caroline Adams
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

def create_full_report(summary_blocks, output_path="report.pdf"):

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph("Performance Monitoring Summary", styles["Title"]))
    elements.append(Spacer(1, 14))

    for block in summary_blocks:

        if block["type"] == "text":
            elements.append(Paragraph(block["content"], styles["Normal"]))
            elements.append(Spacer(1, 10))

        elif block["type"] == "heading":
            elements.append(Paragraph(block["content"], styles["Heading2"]))
            elements.append(Spacer(1, 10))

        elif block["type"] == "success":
            table = Table([[block["content"]]])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.lightgreen),
                ("TEXTCOLOR", (0,0), (-1,-1), colors.black),
                ("BOX", (0,0), (-1,-1), 1, colors.green),
                ("PADDING", (0,0), (-1,-1), 8),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        elif block["type"] == "info":
            table = Table([[block["content"]]])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.lightblue),
                ("TEXTCOLOR", (0,0), (-1,-1), colors.black),
                ("BOX", (0,0), (-1,-1), 1, colors.blue),
                ("PADDING", (0,0), (-1,-1), 8),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        elif block["type"] == "divider":
            elements.append(Spacer(1, 14))

    doc.build(elements)

    return output_path