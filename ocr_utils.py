import re

def extract_equipment_data(text):
    """
    Parses OCR text to find potential equipment data.
    Returns a dict with found keys.
    """
    data = {}
    text_upper = text.upper()
    
    # 1. Serial Number (SN, S/N, No Serie)
    # Looking for patterns like "SN 12345", "S/N: 12345"
    sn_pattern = r"(?:SN|S\/N|NO\.*\s*SERIE|SERIAL\s*NO)[\s\.:]*([A-Z0-9\-]+)"
    sn_match = re.search(sn_pattern, text_upper)
    if sn_match:
        data["serial_number"] = sn_match.group(1)
        
    # 2. Model (REF, Model, Modelo)
    model_pattern = r"(?:MODEL|MODELO|REF|TYPE)[\s\.:]*([A-Z0-9\-]+)"
    model_match = re.search(model_pattern, text_upper)
    if model_match:
        data["model"] = model_match.group(1)
        
    # 3. Brand (Common medical brands - simplistic check)
    brands = ["PHILIPS", "GE", "SIEMENS", "DRAEGER", "MINDRAY", "TOSHIBA", "CANON", "OLYMPUS", "STRYKER"]
    for brand in brands:
        if brand in text_upper:
            data["brand"] = brand.title() # Return as Title Case
            break
            
    return data
