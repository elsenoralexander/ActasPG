from pypdf import PdfReader

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        print(f"--- Page {i+1} ---")
        print(page.extract_text())

if __name__ == "__main__":
    pdf_path = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    extract_text(pdf_path)
