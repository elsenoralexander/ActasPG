import json
from pypdf import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_overlay(data):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
    # Font settings
    can.setFont("Helvetica", 10)
    
    def draw_scaled_string(canvas, text, x, y, max_width, initial_font_size=10):
        text = str(text)
        font_size = initial_font_size
        while font_size > 4:
            if canvas.stringWidth(text, "Helvetica", font_size) <= max_width:
                break
            font_size -= 0.5
        canvas.setFont("Helvetica", font_size)
        canvas.drawString(x, y, text)
        canvas.setFont("Helvetica", initial_font_size) # Reset
    
    # Coordinate Mapping - Visual Corrections
    
    # Left Column: User wanted "closer to edge" -> Shift X from 140 to 110
    # Right Column: "Align left inside column" -> Unify X to 390
    
    # Coordinate Mapping - Final User Tweaks
    
    # Text Fields
    text_mapping = {
        # DATOS DE UBICACIÓN
        "center_name": (125, 717),
        "service": (125, 703),
        "manager": (125, 690),
        "center_code": (435, 717),
        "unit": (380, 703),
        "floor": (380, 690),
        "hole": (485, 690),
        
        # DATOS DE EQUIPO
        "description": (130, 652),
        "brand": (130, 638),
        "serial_number": (130, 624),
        "provider": (130, 610),
        "model": (380, 638),
        "property": (380, 624),
        "contact": (380, 610),
        
        # RECEPCIÓN (Dates)
        "reception_date": (130, 572),
        "acceptance_date": (290, 572),
        "warranty_end": (445, 572),
        "periodicity": (425, 543),
        
        # REGISTRO
        # Reverting to original Y=370, X=130 per user correction ("El primero estaba bien")
        "main_inventory_number": (130, 370),
        "parent_inventory_number": (365, 370),
        
        # ACEPTACIÓN
        "order_number": (420, 235),
        "amount_tax_included": (420, 210),
    }

    # Boolean Fields (Custom X/Y per field)
    # User Request: "El primer bloque de SI Y NO en RECEPCIÓN ... SI y=290" -> Interpreting as x=290 due to context (y=555 range).
    # User Request: "ACEPTACIÓN ... SI x=285"
    
    bool_precise_mapping = {
        # Recepcion (SI moved to X=290)
        "compliance": {True: (290, 555), False: (320, 555)},
        "manuals_usage": {True: (290, 545), False: (320, 545)},
        "manuals_tech": {True: (290, 530), False: (320, 530)},
        "order_accordance": {True: (290, 515), False: (320, 515)},
        "patient_data": {True: (290, 500), False: (320, 500)},
        "backup_required": {True: (290, 490), False: (320, 490)},
        
        # Maintenance (Unchanged)
        "preventive_maintenance": {True: (480, 555), False: (515, 555)},
        "maintenance_contract": {True: (480, 530), False: (515, 530)},
        
        # Acceptance (SI moved to X=285)
        # Keeping Ys consistent with previous block unless specified otherwise.
        "received_correctly": {True: (285, 248), False: (320, 248)}, 
        "users_trained": {True: (285, 234), False: (320, 234)},
        "safe_to_use": {True: (285, 221), False: (320, 221)},
        "requires_epis": {True: (285, 207), False: (320, 207)},
    }
    
    # State of Equipment
    # "y=465"
    state_mapping = {
        "good": (255, 465),
        "bad": (365, 465),
        "obsolete": (480, 465)
    }

    # --- FILL TEXT FIELDS ---
    for key, value in data.items():
        if key in text_mapping:
            x, y = text_mapping[key]
            can.drawString(x, y, str(value))

    # --- FILL OBSERVATIONS (Auto-scaling) ---
    if "observations" in data:
        obs_text = data["observations"]
        obs_x = 60
        start_y = 430
        min_y = 400
        max_width = 520 - obs_x
        
        font_size = 10
        
        # Helper to calculate needed height
        def calculate_needed_height(text, size, width):
            lines = 0
            curr_line = ""
            words = text.split(" ")
            for word in words:
                test = curr_line + " " + word if curr_line else word
                if can.stringWidth(test, "Helvetica", size) > width:
                    lines += 1
                    curr_line = word
                else:
                    curr_line = test
            if curr_line: lines += 1
            return lines * (size + 2) # line spacing
            
        # Iteratively reduce font size if needed
        while font_size > 4:
            needed = calculate_needed_height(obs_text, font_size, max_width)
            if (start_y - needed) >= min_y:
                break
            font_size -= 0.5
            
        # Draw
        can.setFont("Helvetica", font_size)
        line_height = font_size + 2
        curr_y = start_y
        
        words = obs_text.split(" ")
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if can.stringWidth(test_line, "Helvetica", font_size) > max_width:
                can.drawString(obs_x, curr_y, current_line)
                curr_y -= line_height
                current_line = word
            else:
                current_line = test_line
        if current_line:
            can.drawString(obs_x, curr_y, current_line)

        # Reset font
        can.setFont("Helvetica", 10)

    # --- FILL BOOLEANS (Precise) ---
    for key, coords in bool_precise_mapping.items():
        if key in data:
            val = data[key]
            # Val should be boolean.
            if val is True:
                can.drawString(coords[True][0], coords[True][1], "X")
            elif val is False:
                can.drawString(coords[False][0], coords[False][1], "X")
                
    # --- FILL EQUIPMENT STATUS ---
    if "equipment_status" in data:
        status = data["equipment_status"].lower()
        if status in state_mapping:
            can.drawString(state_mapping[status][0], state_mapping[status][1], "X")


    # --- FILL COMPONENTS (Table) ---
    # "y=340 para el primero" refers to the first row of components data.
    # Second Nº Inventory (Table Column) X changed to 210.
    
    if "components" in data and isinstance(data["components"], list):
        start_y = 340
        row_height = 18 
        for i, comp in enumerate(data["components"]):
            current_y = start_y - (i * row_height)
            if current_y < 50: break
            
            # Use draw_scaled_string with user-provided X boundaries
            # Component Name: x=60, max_x=190 -> width=130
            draw_scaled_string(can, comp.get("name", ""), 60, current_y, 130)
            
            # Nº Inventario: x=210, max_x=280 -> width=70
            draw_scaled_string(can, comp.get("inventory", ""), 210, current_y, 70)
            
            # Marca: x=300, max_x=360 -> width=60
            draw_scaled_string(can, comp.get("brand", ""), 300, current_y, 60)
            
            # Modelo: x=380, max_x=435 -> width=55
            draw_scaled_string(can, comp.get("model", ""), 380, current_y, 55)
            
            # Nº Serie: x=440, max_x=520 -> width=80
            draw_scaled_string(can, comp.get("serial", ""), 440, current_y, 80)
    
    can.save()
    packet.seek(0)
    return packet

def fill_pdf(original_pdf_path, output_pdf_path, data):
    # Create overlay
    overlay_packet = create_overlay(data)
    overlay_pdf = PdfReader(overlay_packet)
    
    # Read original
    original_pdf = PdfReader(original_pdf_path)
    writer = PdfWriter()
    
    # Merge
    page = original_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)
    
    # Add remaining pages if any (usually just 1 page for Acta)
    for i in range(1, len(original_pdf.pages)):
        writer.add_page(original_pdf.pages[i])
        
    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"Created {output_pdf_path}")

if __name__ == "__main__":
    # Test data
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    original = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    output = "Acta_Rellenada.pdf"
    
    fill_pdf(original, output, data)
