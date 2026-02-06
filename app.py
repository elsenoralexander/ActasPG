import streamlit as st
import json
import os
from datetime import datetime
import fill_acta  # Our local script

# --- CONFIG ---
st.set_page_config(page_title="Agente de Actas", layout="wide")

MEMORY_FILE = "memory.json"

# --- HELPERS ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"defaults": {"services": {}, "providers": {}}}

# --- MAIN ---
def main():
    st.title("📋 Agente de Actas de Recepción")
    
    # Initialize Session State for fields if not present
    defaults = {
        "center_code": "001",
        "description": "Monitor",
        "main_inventory_number": "INV-"
    }
    fields = ["center_name", "center_code", "manager", "unit", "floor", 
              "hole", "description", "brand", "model", "serial", "provider",
              "property", "contact", "main_inventory_number", "parent_inventory_number",
              "order_number", "amount_tax_included"]
    for f in fields:
        if f not in st.session_state:
            st.session_state[f] = defaults.get(f, "")
    
    if "components" not in st.session_state:
        st.session_state["components"] = []

    memory = load_memory()
    
    # --- SIDEBAR: KNOWLEDGE BASE ---
    with st.sidebar:
        st.header("🧠 Memoria del Agente")
        if st.checkbox("Ver/Editar Memoria"):
            st.json(memory)
            
    # --- FORM ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Ubicación")
        
        # Smart Service Selection
        service_options = [""] + list(memory["defaults"]["services"].keys())
        service = st.selectbox("Servicio", service_options, index=0)
        
        # Smart Learning Logic (Triggered on change)
        if service and service in memory["defaults"]["services"]:
            # Only overwrite if empty or user just selected service? 
            # Simple approach: If service selected, fill defaults.
            s_data = memory["defaults"]["services"][service]
            
            # Update session state if they match the "defaults logic"
            # We use text_input "value" argument directly backed by session state? No, key handles it.
            # We need to manually update session state but avoiding loops.
            # Let's just update if the user hasn't typed something specific? 
            # Or just overwrite: User selects Service -> We fill logic.
            # Ideally we'd compare with previous service selection.
            
            # Simple override for now (User can edit after):
            if st.session_state["manager"] == "": st.session_state["manager"] = s_data.get("manager", "")
            if st.session_state["floor"] == "": st.session_state["floor"] = s_data.get("floor", "")
            if st.session_state["unit"] == "": st.session_state["unit"] = s_data.get("unit", "")
            if st.session_state["hole"] == "": st.session_state["hole"] = s_data.get("hole", "")
            # Only set center if empty to allow global default
            if st.session_state["center_name"] == "": st.session_state["center_name"] = s_data.get("center_name", "Hospital General")

        # Inputs linked to st.session_state
        st.text_input("Centro", key="center_name")
        st.text_input("Código Centro", key="center_code")
        st.text_input("Responsable", key="manager")
        st.text_input("Unidad", key="unit")
        st.text_input("Planta", key="floor")
        st.text_input("Hueco", key="hole")

    with col2:
        st.subheader("📦 Equipo")
        st.text_input("Descripción", key="description")
        st.text_input("Marca", key="brand")
        st.text_input("Modelo", key="model")
        st.text_input("Nº Serie", key="serial")
        st.text_input("Proveedor", key="provider")
        st.text_input("Propiedad", key="property")
        st.text_input("Contacto", key="contact")
        
        st.caption("Fechas")
        c_d1, c_d2 = st.columns(2)
        today = datetime.now().strftime("%d/%m/%Y")
        reception_date = c_d1.text_input("Recepción", value=today)
        acceptance_date = c_d2.text_input("Aceptación", value=today)
        warranty_end = st.text_input("Fin Garantía (dd/mm/aaaa)")

    st.markdown("---")
    
    # --- REGISTRATION AND ACCEPTANCE ---
    st.subheader("📝 Registro y Aceptación")
    reg_col1, reg_col2 = st.columns(2)
    with reg_col1:
        st.text_input("Nº Inventario", key="main_inventory_number")
        st.text_input("Nº Inventario Padre", key="parent_inventory_number")
    with reg_col2:
        st.text_input("Número Pedido", key="order_number")
        st.text_input("Importe (IVA inc.)", key="amount_tax_included")

    st.markdown("---")
    
    # --- CHECKBOXES ---
    st.subheader("✅ Verificaciones")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("**Recepción**")
        compliance = st.checkbox("Cumple normativa", value=True)
        manuals_usage = st.checkbox("Manual Uso", value=True)
        manuals_tech = st.checkbox("Manual Técnico", value=False)
        order_accordance = st.checkbox("Acorde a pedido", value=True)
        
    with c2:
        st.markdown("**Seguridad / Datos**")
        patient_data = st.checkbox("Maneja datos pac.", value=True)
        backup_required = st.checkbox("Requiere copia seg.", value=False)
        requires_epis = st.checkbox("Requiere EPIS", value=False)
        safe_to_use = st.checkbox("Seguro para uso", value=True)
        received_correctly = st.checkbox("Recibido/Instalado correctamente", value=True)
        users_trained = st.checkbox("Usuarios formados", value=True)
        
    with c3:
        st.markdown("**Mantenimiento y Estado**")
        preventive = st.checkbox("Mant. Preventivo", value=True)
        contract = st.checkbox("Contrato Mant.", value=False)
        periodicity = st.selectbox("Periodicidad", ["Semestral", "Anual", "Trimestral"])
        status = st.radio("Estado del Equipo", ["good", "bad", "obsolete"], format_func=lambda x: {"good":"Buen Estado", "bad":"Mal Estado", "obsolete":"Obsoleto"}[x])

    st.markdown("---")
    
    st.subheader("🔧 Componentes del Equipo")
    # Using data_editor for easy components management
    import pandas as pd
    df_components = pd.DataFrame(st.session_state["components"])
    if df_components.empty:
        df_components = pd.DataFrame(columns=["name", "inventory", "brand", "model", "serial"])
    
    edited_df = st.data_editor(
        df_components,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "name": "Nombre Componente",
            "inventory": "Nº Inventario",
            "brand": "Marca",
            "model": "Modelo",
            "serial": "Nº Serie"
        }
    )
    st.session_state["components"] = edited_df.to_dict("records")

    st.markdown("---")
    
    # --- EXTRAS ---
    st.subheader("Extras")
    observations = st.text_area("Observaciones", height=100)
    
    # --- SUBMIT ---
    if st.button("🚀 GENERAR ACTA PDF", type="primary", use_container_width=True):
        # Build Data JSON
        data = {
            "center_name": st.session_state["center_name"],
            "center_code": st.session_state["center_code"],
            "service": service if service else "",
            "manager": st.session_state["manager"],
            "unit": st.session_state["unit"],
            "floor": st.session_state["floor"],
            "hole": st.session_state["hole"],
            "description": st.session_state["description"],
            "brand": st.session_state["brand"],
            "model": st.session_state["model"],
            "serial_number": st.session_state["serial"],
            "provider": st.session_state["provider"],
            "reception_date": reception_date,
            "acceptance_date": acceptance_date,
            "warranty_end": warranty_end,
            "compliance": compliance,
            "manuals_usage": manuals_usage,
            "manuals_tech": manuals_tech,
            "order_accordance": order_accordance,
            "patient_data": patient_data,
            "backup_required": backup_required,
            "requires_epis": requires_epis,
            "safe_to_use": safe_to_use,
            "preventive_maintenance": preventive,
            "maintenance_contract": contract,
            "periodicity": periodicity,
            "equipment_status": status,
            "main_inventory_number": st.session_state["main_inventory_number"],
            "parent_inventory_number": st.session_state["parent_inventory_number"],
            "order_number": st.session_state["order_number"],
            "amount_tax_included": st.session_state["amount_tax_included"],
            "property": st.session_state["property"],
            "contact": st.session_state["contact"],
            "received_correctly": received_correctly,
            "users_trained": users_trained,
            "observations": observations,
            "components": st.session_state["components"] 
        }
        
        # Save JSON (for record)
        with open("last_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        # Generate PDF
        try:
            # Find the template file robustly (handling NFD/NFC normalization for Spanish characters)
            import unicodedata
            template_filename = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
            
            def find_file(target):
                target_norm = unicodedata.normalize('NFC', target)
                for f in os.listdir("."):
                    if unicodedata.normalize('NFC', f) == target_norm:
                        return f
                return target

            actual_template = find_file(template_filename)
            
            fill_acta.fill_pdf(
                actual_template,
                "Acta_Generada_Web.pdf",
                data
            )
            st.success("¡PDF Generado!")
            
            with open("Acta_Generada_Web.pdf", "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_file,
                    file_name="Acta_Recepcion.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generando PDF: {e}")

if __name__ == "__main__":
    main()
