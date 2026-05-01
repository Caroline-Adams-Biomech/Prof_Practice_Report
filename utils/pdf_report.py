# -*- coding: utf-8 -*-
"""
Created on Fri May  1 09:35:17 2026

@author: Caroline Adams
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

def create_full_report(figures, insights, output_path="report.pdf"):

    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # =========================================================
    # TITLE
    # =========================================================
    elements.append(Paragraph("Wheelchair Racing Performance Monitoring Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # =========================================================
    # SUMMARY INSIGHT
    # =========================================================
    elements.append(Paragraph("Key Performance Insight", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(insights["summary"], styles["Normal"]))
    elements.append(Spacer(1, 16))

    # =========================================================
    # ADD FIGURES
    # =========================================================
    for i, fig in enumerate(figures):

        img_path = f"temp_fig_{i}.png"

        # Save Plotly figure to image
        fig.write_image(img_path)

        # Add to PDF
        elements.append(Image(img_path, width=450, height=250))
        elements.append(Spacer(1, 16))

    # =========================================================
    # BUILD PDF
    # =========================================================
    doc.build(elements)

    # Clean up images
    for i in range(len(figures)):
        try:
            os.remove(f"temp_fig_{i}.png")
        except:
            pass

    return output_path
