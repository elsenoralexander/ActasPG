import json
from pypdf import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_overlay(data):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
# --- COORDINATE MAPS ---

COORDINATE_MAPS = {
    "recepcion": {
        "template": "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf",
        "text": {
            "center_name": (125, 717),
            "service": (125, 703),
            "manager": (125, 690),
            "center_code": (435, 717),
            "unit": (380, 703),
            "floor": (380, 690),
            "hole": (485, 690),
            "description": (130, 652),
            "brand": (130, 638),
            "serial_number": (130, 624),
            "provider": (130, 610),
            "model": (380, 638),
            "property": (380, 624),
            "contact": (380, 610),
            "reception_date": (130, 572),
            "acceptance_date": (290, 572),
            "warranty_end": (445, 572),
            "periodicity": (425, 543),
            "main_inventory_number": (130, 370),
            "parent_inventory_number": (365, 370),
            "order_number": (420, 235),
            "amount_tax_included": (420, 210),
        },
        "bools": {
            "compliance": {True: (290, 555), False: (320, 555)},
            "manuals_usage": {True: (290, 545), False: (320, 545)},
            "manuals_tech": {True: (290, 530), False: (320, 530)},
            "order_accordance": {True: (290, 515), False: (320, 515)},
            "patient_data": {True: (290, 500), False: (320, 500)},
            "backup_required": {True: (290, 490), False: (320, 490)},
            "preventive_maintenance": {True: (480, 555), False: (515, 555)},
            "maintenance_contract": {True: (480, 530), False: (515, 530)},
            "received_correctly": {True: (285, 248), False: (320, 248)}, 
            "users_trained": {True: (285, 234), False: (320, 234)},
            "safe_to_use": {True: (285, 221), False: (320, 221)},
            "requires_epis": {True: (285, 207), False: (320, 207)},
        },
        "states": {
            "good": (255, 465),
            "bad": (365, 465),
            "obsolete": (480, 465)
        },
        "obs": {"x": 60, "start_y": 430, "min_y": 400, "width": 460},
        "table": {"start_y": 340, "row_height": 18, "cols": [60, 210, 300, 380, 440]}
    },
    "baja": {
        "template": "acta baja equipos.pdf",
        "text": {
            "center_name": (120, 696),
            "service": (120, 683),
            "manager": (120, 670),
            "center_code": (425, 696),
            "unit": (370, 683),
            "floor": (370, 670),
            "hole": (470, 670),
            "description": (120, 622),
            "brand": (120, 609),
            "serial_number": (120, 596),
            "main_inventory_number": (120, 583),
            "model": (355, 609),
            "property": (355, 596),
            "parent_inventory_number": (355, 583),
            "baja_date": (120, 534),
            "work_order_number": (445, 234),
        },
        "bools": {
            "repair_budget": {True: (270, 234), False: (300, 234)},
            "replacement_budget": {True: (270, 221), False: (300, 221)},
            "sat_report": {True: (270, 208), False: (300, 208)},
            "other_docs": {True: (270, 195), False: (300, 195)},
            "data_cleaned": {True: (270, 182), False: (300, 182)},
        },
        "states": {}, 
        "obs": {"x": 60, "start_y": 370, "min_y": 280, "width": 440},
        "justification": {"x": 60, "start_y": 510, "min_y": 420, "width": 440},
        "table": None
    }
}

def create_overlay(data, report_type="recepcion"):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 10)
    
    config = COORDINATE_MAPS.get(report_type, COORDINATE_MAPS["recepcion"])
    
    def draw_scaled_string(canvas, text, x, y, max_width, initial_font_size=10):
        text = str(text)
        font_size = initial_font_size
        while font_size > 4:
            if canvas.stringWidth(text, "Helvetica", font_size) <= max_width:
                break
            font_size -= 0.5
        canvas.setFont("Helvetica", font_size)
        canvas.drawString(x, y, text)
        canvas.setFont("Helvetica", initial_font_size)

    # --- FILL TEXT FIELDS ---
    text_mapping = config["text"]
    for key, value in data.items():
        if key in text_mapping:
            x, y = text_mapping[key]
            can.drawString(x, y, str(value))

    # --- FILL OBSERVATIONS ---
    obs_config = config["obs"]
    if "observations" in data and obs_config:
        obs_text = data["observations"]
        obs_x = obs_config["x"]
        start_y = obs_config["start_y"]
        min_y = obs_config["min_y"]
        max_width = obs_config["width"]
        
        font_size = 10
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
            return lines * (size + 2)
            
        while font_size > 4:
            needed = calculate_needed_height(obs_text, font_size, max_width)
            if (start_y - needed) >= min_y: break
            font_size -= 0.5
            
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
        if current_line: can.drawString(obs_x, curr_y, current_line)
        can.setFont("Helvetica", 10)

    # --- FILL JUSTIFICATION (Baja only) ---
    just_config = config.get("justification")
    if "justification_report" in data and just_config:
        j_text = data["justification_report"]
        j_x, j_y, j_min, j_w = just_config["x"], just_config["start_y"], just_config["min_y"], just_config["width"]
        f_size = 10
        def calc_h(t, s, w):
            ls = 0
            curr = ""
            for wd in t.split(" "):
                tst = curr + " " + wd if curr else wd
                if can.stringWidth(tst, "Helvetica", s) > w:
                    ls += 1
                    curr = wd
                else: curr = tst
            if curr: ls += 1
            return ls * (s + 2)
        while f_size > 4:
            if (j_y - calc_h(j_text, f_size, j_w)) >= j_min: break
            f_size -= 0.5
        can.setFont("Helvetica", f_size)
        lh = f_size + 2
        cy = j_y
        curr = ""
        for wd in j_text.split(" "):
            tst = curr + " " + wd if curr else wd
            if can.stringWidth(tst, "Helvetica", f_size) > j_w:
                can.drawString(j_x, cy, curr)
                cy -= lh
                curr = wd
            else: curr = tst
        if curr: can.drawString(j_x, cy, curr)
        can.setFont("Helvetica", 10)

    # --- FILL BOOLEANS ---
    bool_mapping = config["bools"]
    for key, coords in bool_mapping.items():
        if key in data:
            val = data[key]
            if val is True: can.drawString(coords[True][0], coords[True][1], "X")
            elif val is False: can.drawString(coords[False][0], coords[False][1], "X")
                
    # --- FILL EQUIPMENT STATUS ---
    state_mapping = config["states"]
    if "equipment_status" in data:
        status = data["equipment_status"].lower()
        if status in state_mapping:
            can.drawString(state_mapping[status][0], state_mapping[status][1], "X")

    # --- FILL COMPONENTS TABLE ---
    tbl_config = config.get("table")
    if tbl_config and "components" in data and isinstance(data["components"], list):
        start_y = tbl_config["start_y"]
        row_height = tbl_config["row_height"]
        cols = tbl_config["cols"]
        for i, comp in enumerate(data["components"]):
            current_y = start_y - (i * row_height)
            if current_y < 50: break
            draw_scaled_string(can, comp.get("name", ""), cols[0], current_y, 130)
            draw_scaled_string(can, comp.get("inventory", ""), cols[1], current_y, 70)
            draw_scaled_string(can, comp.get("brand", ""), cols[2], current_y, 60)
            draw_scaled_string(can, comp.get("model", ""), cols[3], current_y, 55)
            draw_scaled_string(can, comp.get("serial", ""), cols[4], current_y, 80)
    
    can.save()
    packet.seek(0)
    return packet

def fill_pdf(original_pdf_path, output_pdf_path, data, report_type="recepcion"):
    # Create overlay
    overlay_packet = create_overlay(data, report_type=report_type)
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
