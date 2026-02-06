from pypdf import PdfReader
import sys

def get_text_map(pdf_path, output_file):
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
    items.sort(key=lambda k: (-k['y'], k['x']))

    with open(output_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"Y={item['y']:.1f} | X={item['x']:.1f} | '{item['text']}'\n")

if __name__ == "__main__":
    pdf_path = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    get_text_map(pdf_path, "pdf_layout.txt")
