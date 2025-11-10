#!/usr/bin/env python3
"""Extract text from PDF file."""

import sys

try:
    import PyPDF2
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "View_Job_Posting_Details-2.pdf"
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''.join([page.extract_text() for page in reader.pages])
        print(text)
except ImportError:
    try:
        import pypdf
        pdf_path = sys.argv[1] if len(sys.argv) > 1 else "View_Job_Posting_Details-2.pdf"
        with open(pdf_path, 'rb') as pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            text = ''.join([page.extract_text() for page in reader.pages])
            print(text)
    except ImportError:
        print("Please install PyPDF2 or pypdf: pip install PyPDF2")
        sys.exit(1)
