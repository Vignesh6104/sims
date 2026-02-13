import sys
from docx import Document

def read_docx(file_path):
    try:
        doc = Document(file_path)
        print(f"--- START DOCUMENT CONTENT ---")
        for para in doc.paragraphs:
            if para.text.strip():
                style = para.style.name
                print(f"[{style}] {para.text}")
        print(f"--- END DOCUMENT CONTENT ---")
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        read_docx(sys.argv[1])
    else:
        print("Usage: python read_reference_docx.py <path_to_docx>")