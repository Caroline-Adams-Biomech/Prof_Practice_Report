# -*- coding: utf-8 -*-
"""
Created on Fri May  1 09:35:17 2026

@author: Caroline Adams
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from plotly.io import to_image
import os

def create_full_report(figures, insights, output_path="report.pdf"):

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph("Wheelchair Racing Performance Monitoring Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Insight
    elements.append(Paragraph("Key Performance Insight", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(insights["summary"], styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Figures
    for i, fig in enumerate(figures):

        img_path = f"temp_fig_{i}.png"

        try:
            img_bytes = to_image(fig, format="png")

            with open(img_path, "wb") as f:
                f.write(img_bytes)

            elements.append(Image(img_path, width=450, height=250))
            elements.append(Spacer(1, 16))

        except Exception as e:
            elements.append(Paragraph("⚠️ Plot could not be rendered", styles["Normal"]))
            elements.append(Spacer(1, 16))
            print(f"Error exporting figure {i}:", e)

    # Build PDF
    doc.build(elements)

    # Cleanup
    for i in range(len(figures)):
        try:
            os.remove(f"temp_fig_{i}.png")
        except:
            pass

    return output_path