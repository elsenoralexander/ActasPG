from pypdf import PdfReader

def list_fields(pdf_path):
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    if fields:
        for field_name, value in fields.items():
            print(f"Field: {field_name}, Value: {value}")
    else:
        print("No form fields found.")

if __name__ == "__main__":
    pdf_path = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
    list_fields(pdf_path)
