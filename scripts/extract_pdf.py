from pypdf import PdfReader
import os

PDF_PATH = "Notes (1).pdf"

def extract_text(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return ""
        
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

if __name__ == "__main__":
    extracted = extract_text(PDF_PATH)
    # Save to a temp file for inspection or just print a preview
    with open("temp_pdf_content.txt", "w", encoding="utf-8") as f:
        f.write(extracted)
    print(f"Extracted {len(extracted)} characters. Saved to temp_pdf_content.txt")
