#!/usr/bin/env python3
"""
Create a Word document containing all source code from the research paper project.
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Create document
doc = Document()

# Set default font
style = doc.styles['Normal']
font = style.font
font.name = 'Consolas'
font.size = Pt(9)

# Adjust margins
for section in doc.sections:
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Create code style
code_style = doc.styles.add_style('CodeStyle', WD_STYLE_TYPE.PARAGRAPH)
code_style.font.name = 'Consolas'
code_style.font.size = Pt(8.5)
code_style.font.color.rgb = RGBColor(0x2D, 0x2D, 0x2D)
code_style.paragraph_format.space_before = Pt(0)
code_style.paragraph_format.space_after = Pt(0)
code_style.paragraph_format.line_spacing = 1.0

# Heading style
heading_style = doc.styles['Heading 1']
heading_style.font.size = Pt(14)
heading_style.font.bold = True

heading2_style = doc.styles['Heading 2']
heading2_style.font.size = Pt(12)
heading2_style.font.bold = True

# Base directory
base_dir = r"C:\Users\Sachin\OneDrive\Documents\ML_proj\research_paper"

# Add title
title = doc.add_heading('IEEE Research Paper - Complete Source Code', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('Project: Personalised Indian Meal Recommendation from Ingredient-Level Recipe Features')
doc.add_paragraph('Generated: 2026-11-22')
doc.add_paragraph('')

# Function to add a file to the document
def add_file_section(doc, filepath, relpath):
    """Add a file's contents as a section in the document."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"[Error reading file: {e}]"
    
    # Add file path as heading
    doc.add_heading(relpath, level=2)
    
    # Add content with code style
    for line in content.split('\n'):
        p = doc.add_paragraph(line, style='CodeStyle')
        # Keep lines together
        p.paragraph_format.keep_together = True
    
    doc.add_paragraph('')  # Space between files

# List of files to include in order
files_to_include = [
    ('IEEE_Research_Paper.tex', 'LaTeX Source (Main Document)'),
    ('references.bib', 'BibTeX References'),
    ('figures/generate_figures.py', 'Figure Generation Script'),
    ('PAPER_VALIDATION_REPORT.md', 'Validation Report'),
]

# Add each file
for filename, description in files_to_include:
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        add_file_section(doc, filepath, f"{description} ({filename})")
    else:
        doc.add_heading(f"MISSING: {filename}", level=2)
        doc.add_paragraph(f"File not found: {filepath}")
        doc.add_paragraph('')

# Save document
output_path = os.path.join(base_dir, 'IEEE_Research_Paper_Source_Code.docx')
doc.save(output_path)
print(f"Word document saved to: {output_path}")