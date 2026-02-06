from pypdf import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_grid_overlay():
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 6)
    
    # Draw vertical lines every 50 units
    for x in range(0, 600, 20):
        can.setStrokeColorRGB(0.8, 0.8, 0.8)
        can.line(x, 0, x, 842)
        can.setFillColorRGB(0.5, 0.5, 0.5)
        can.drawString(x+2, 830, str(x))
        if x % 100 == 0:
            can.setStrokeColorRGB(1, 0, 0) # Red for 100s
            can.line(x, 0, x, 842)

    # Draw horizontal lines every 20 units
    for y in range(0, 850, 20):
        can.setStrokeColorRGB(0.8, 0.8, 0.8)
        can.line(0, y, 595, y)
        can.setFillColorRGB(0.5, 0.5, 0.5)
        can.drawString(5, y+2, str(y))

    can.save()
    packet.seek(0)
    return packet

def create_debug_pdf(original_pdf_path, output_pdf_path):
    overlay_packet = create_grid_overlay()
    overlay_pdf = PdfReader(overlay_packet)
    original_pdf = PdfReader(original_pdf_path)
    writer = PdfWriter()
    
    page = original_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)
    
    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"Created {output_pdf_path}")

if __name__ == "__main__":
    original = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    output = "Acta_Con_Rejilla.pdf"
    create_debug_pdf(original, output)
