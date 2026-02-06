from pypdf import PdfReader

def get_text_map(pdf_path):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    
    items = []

    def visitor_body(text, cm, tm, fontDict, fontSize):
        x = tm[4]
        y = tm[5]
        text = text.strip()
        if len(text) > 1:
            items.append({"text": text, "x": x, "y": y})

    page.extract_text(visitor_text=visitor_body)
    
    # Sort by Y (top to bottom, usually higher Y is higher on page in PDF) then X
    # Assuming standard PDF coordinate system where (0,0) is bottom-left.
    items.sort(key=lambda k: (-k['y'], k['x']))

    for item in items:
        print(f"Y={item['y']:.1f} | X={item['x']:.1f} | '{item['text']}'")

if __name__ == "__main__":
    pdf_path = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    get_text_map(pdf_path)
