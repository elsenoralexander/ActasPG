from pypdf import PdfReader

def inspect_paths(pdf_path):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    
    # This is a basic attempt to find rectangles (re, or lines)
    # pypdf doesn't have a high-level "get_paths" easily, so we parse content stream.
    # This might be complex. Alternative: "Blind" Grid test.
    
    content = page.get_contents()
    if content:
        # Very raw parsing
        ops = content.get_data().split(b'\n')
        count = 0
        for op in ops:
            if b're' in op: # Rectangle operator
                try:
                    parts = op.strip().split(b' ')
                    # format: x y w h re
                    if parts[-1] == b're':
                        x = float(parts[-2-3])
                        y = float(parts[-2-2])
                        w = float(parts[-2-1])
                        h = float(parts[-2])
                        print(f"Rect: X={x:.1f}, Y={y:.1f}, W={w:.1f}, H={h:.1f}")
                        count += 1
                except:
                    pass
        print(f"Found {count} rectangles.")

if __name__ == "__main__":
    pdf_path = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    inspect_paths(pdf_path)
