# -*- coding: utf-8 -*-
"""
Created on Fri May  1 12:26:27 2026

@author: Caroline Adams
"""

from playwright.sync_api import sync_playwright

def create_full_report(url, output_path="report.pdf"):

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Open your Streamlit page
        page.goto(url)

        # Wait for content to load
        page.wait_for_timeout(2000)

        # Save as PDF
        page.pdf(path=output_path, format="A4")

        browser.close()

    return output_path