import json
import fill_acta

data = {
    "center_name": "CENTRO DE PRUEBA",
    "center_code": "999",
    "service": "Mantenimiento",
    "manager": "Alex Test",
    "description": "EQUIPO TEST",
    "brand": "MARCA TEST",
    "model": "MODELO TEST",
    "serial_number": "SN-12345",
    "baja_date": "07/02/2026",
    "justification_report": "Esta es una justificación de prueba para ver si el texto aparece correctamente en el PDF coordinado.",
    "repair_budget": True,
    "work_order_number": "OT-001",
    "observations": "Observaciones de prueba."
}

try:
    fill_acta.fill_pdf("acta baja equipos.pdf", "debug_baja.pdf", data, report_type="baja")
    print("PDF generated successfully: debug_baja.pdf")
except Exception as e:
    print(f"Error: {e}")
