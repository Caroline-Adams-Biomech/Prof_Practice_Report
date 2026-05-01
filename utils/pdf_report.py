# -*- coding: utf-8 -*-
"""
Created on Fri May  1 12:26:27 2026

@author: Caroline Adams
"""

from weasyprint import HTML
from pathlib import Path

def create_full_report(output_path="report.pdf"):

    html_path = Path(__file__).resolve().parent / "summary_template.html"

    HTML(str(html_path)).write_pdf(output_path)

    return output_path