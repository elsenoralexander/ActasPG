from pypdf import PdfReader

def dump_content(pdf_path, output):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    content = page.get_contents()
    if content:
        data = content.get_data().decode('latin-1', errors='ignore')
        with open(output, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"Dumped content to {output}")
    else:
        print("No content found.")

if __name__ == "__main__":
    pdf_path = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    dump_content(pdf_path, "pdf_content.txt")
