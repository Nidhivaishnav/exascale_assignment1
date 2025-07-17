#!/usr/bin/env python3
"""
Script to extract text from Word document (.docx) files.
"""

import sys
import os
from pathlib import Path

try:
    from docx import Document
    docx_available = True
except ImportError:
    docx_available = False

def extract_text_from_docx(file_path):
    """Extract text from a .docx file."""
    if not docx_available:
        print("python-docx not installed. Installing...")
        os.system("pip install python-docx")
        try:
            from docx import Document
        except ImportError:
            print("Failed to install python-docx. Please install manually: pip install python-docx")
            return None
    
    try:
        doc = Document(file_path)
        text = []
        
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        
        return '\n'.join(text)
    except Exception as e:
        print(f"Error reading document: {e}")
        return None

def main():
    docx_file = "Assignment - IIIT NR.docx"
    
    if not Path(docx_file).exists():
        print(f"File {docx_file} not found!")
        return
    
    print(f"Extracting text from {docx_file}...")
    text = extract_text_from_docx(docx_file)
    
    if text:
        # Save to text file
        output_file = "docs/assignment_text.txt"
        Path("docs").mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Text extracted and saved to {output_file}")
        print("\nFirst 1000 characters:")
        print(text[:1000])
        print("\n... (truncated)")
    else:
        print("Failed to extract text from the document.")

if __name__ == "__main__":
    main() 