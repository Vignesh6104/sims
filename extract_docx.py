from docx import Document
import sys

def extract_docx_structure(docx_path):
    try:
        doc = Document(docx_path)
        print(f"Reading structure from: {docx_path}
")
        
        for para in doc.paragraphs:
            # If paragraph has a style that looks like a heading or list item, print it
            if para.style.name.startswith('Heading'):
                print(f"HEADING [{para.style.name}]: {para.text}")
            elif para.text.strip(): # Only print non-empty paragraphs
                 print(f"PARA: {para.text[:100]}...") # Print first 100 chars
                 
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    docx_path = r"C:\Usersemov\Downloads\PROJECT_PHASE_2.docx"
    extract_docx_structure(docx_path)
