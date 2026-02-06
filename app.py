import streamlit as st
import json
import os
from datetime import datetime
import fill_acta  # Our local script
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Agente de Actas", layout="wide")

MEMORY_FILE = "memory.json"

# --- HELPERS ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"defaults": {"services": {}, "models": {}}}

# --- CALLBACKS ---
def on_service_change():
    memory = load_memory()
    service = st.session_state.get("service")
    if service and service in memory.get("defaults", {}).get("services", {}):
        s_data = memory["defaults"]["services"][service]
        st.session_state["manager"] = s_data.get("manager", "")
        st.session_state["floor"] = s_data.get("floor", "")
        st.session_state["unit"] = s_data.get("unit", "")
        st.session_state["hole"] = s_data.get("hole", "")
        st.session_state["center_name"] = s_data.get("center_name", "POLICLINICA GIPUZKOA")
        st.session_state["center_code"] = s_data.get("center_code", "001")

def on_model_change():
    memory = load_memory()
    model = st.session_state.get("model")
    if model and model in memory.get("defaults", {}).get("models", {}):
        m_data = memory["defaults"]["models"][model]
        # Auto-fill all known fields for this model
        if m_data.get("description"): st.session_state["description"] = m_data["description"]
        if m_data.get("brand"): st.session_state["brand"] = m_data["brand"]
        if m_data.get("provider"): st.session_state["provider"] = m_data["provider"]
        if m_data.get("contact"): st.session_state["contact"] = m_data["contact"]

def on_reception_change():
    # Sync Acceptance date with Reception date
    st.session_state["acceptance_date_val"] = st.session_state["reception_date_val"]

def calculate_warranty_end():
    years = st.session_state.get("warranty_years", 0)
    start_date = st.session_state.get("acceptance_date_val", datetime.now().date())
    if years > 0:
        try:
            st.session_state["warranty_end_val"] = start_date.replace(year=start_date.year + years)
        except ValueError: # Feb 29
            st.session_state["warranty_end_val"] = start_date + (datetime(start_date.year + years, 1, 1).date() - datetime(start_date.year, 1, 1).date())
    else:
        st.session_state["warranty_end_val"] = None

# --- MAIN ---
def main():
    st.title("📋 Agente de Actas de Recepción")
    
    # Initialize Session State for fields if not present
    defaults = {
        "center_name": "POLICLINICA GIPUZKOA",
        "center_code": "001",
        "description": "",
        "main_inventory_number": "INV-"
    }
    
    # Core Fields
    fields = ["center_name", "center_code", "manager", "unit", "floor", 
              "hole", "description", "brand", "model", "serial", "provider",
              "property", "contact", "main_inventory_number", "parent_inventory_number",
              "order_number", "amount_tax_included"]
    for f in fields:
        if f not in st.session_state:
            st.session_state[f] = defaults.get(f, "")
            
    # Date/Time Fields (Stored as objects)
    if "reception_date_val" not in st.session_state:
        st.session_state["reception_date_val"] = datetime.now().date()
    if "acceptance_date_val" not in st.session_state:
        st.session_state["acceptance_date_val"] = datetime.now().date()
    if "warranty_end_val" not in st.session_state:
        st.session_state["warranty_end_val"] = None
    if "warranty_years" not in st.session_state:
        st.session_state["warranty_years"] = 2

    # Persistent Components DataFrame
    if "components_df" not in st.session_state:
        st.session_state["components_df"] = pd.DataFrame(columns=["name", "inventory", "brand", "model", "serial"])

    memory = load_memory()
    
    # --- SIDEBAR & MEMORY ---
    with st.sidebar:
        st.title("🤖 Ajustes de Agente")
        if st.button("🧹 Limpiar Formulario", use_container_width=True):
            # Clear all except constant defaults
            for k in fields:
                st.session_state[k] = defaults.get(k, "")
            st.session_state["components_df"] = pd.DataFrame(columns=["name", "inventory", "brand", "model", "serial"])
            st.session_state["reception_date_val"] = datetime.now().date()
            st.session_state["acceptance_date_val"] = datetime.now().date()
            st.session_state["warranty_end_val"] = None
            st.rerun()

        st.markdown("---")
        if st.checkbox("Ver/Editar Memoria"):
            st.json(memory)
            
    # --- FORM ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Ubicación")
        
        # Smart Service Selection
        service_options = [""] + list(memory.get("defaults", {}).get("services", {}).keys())
        
        s_col1, s_col2 = st.columns([3, 1])
        is_new_service = s_col2.checkbox("Nuevo ➕")
        
        if is_new_service:
            service = st.text_input("Nuevo Servicio", key="service", help="Escribe el nombre del nuevo servicio")
        else:
            service = st.selectbox("Servicio", service_options, key="service", on_change=on_service_change)

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
        st.text_input("Modelo", key="model", on_change=on_model_change)
        st.text_input("Nº Serie", key="serial")
        st.text_input("Proveedor", key="provider")
        st.text_input("Propiedad", key="property")
        st.text_input("Contacto", key="contact")
        
        st.caption("Fechas y Garantía")
        c_d1, c_d2 = st.columns(2)
        
        c_d1.date_input("Recepción", key="reception_date_val", on_change=on_reception_change)
        c_d2.date_input("Aceptación", key="acceptance_date_val", on_change=calculate_warranty_end)
        
        st.radio("Años de Garantía", options=[0, 1, 2, 3, 4], key="warranty_years", horizontal=True, on_change=calculate_warranty_end)
        st.date_input("Fin Garantía", key="warranty_end_val")
        
        # Format strings for PDF
        reception_date = st.session_state["reception_date_val"].strftime("%d/%m/%Y") if st.session_state["reception_date_val"] else ""
        acceptance_date = st.session_state["acceptance_date_val"].strftime("%d/%m/%Y") if st.session_state["acceptance_date_val"] else ""
        warranty_end = st.session_state["warranty_end_val"].strftime("%d/%m/%Y") if st.session_state["warranty_end_val"] else ""

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
        contract = st.checkbox("Contrato Mant.", value=True)
        periodicity = st.selectbox("Periodicidad", ["Anual", "Semestral", "Trimestral", "Bienal"])
        status = st.radio("Estado del Equipo", ["good", "bad", "obsolete"], format_func=lambda x: {"good":"Buen Estado", "bad":"Mal Estado", "obsolete":"Obsoleto"}[x])

    st.markdown("---")
    
    st.subheader("🔧 Componentes del Equipo")
    
    # Extract suggestions from memory
    past_models = []
    past_brands = []
    for m in memory.get("defaults", {}).get("models", {}).values():
        if m.get("model"): past_models.append(m["model"])
        if m.get("brand"): past_brands.append(m["brand"])
    
    # Also look into past services or components if we had a deep history (skipping for brevity)
    
    edited_df = st.data_editor(
        st.session_state["components_df"],
        num_rows="dynamic",
        use_container_width=True,
        key="components_editor_v2", # New key for stability
        column_config={
            "name": "Nombre Componente",
            "inventory": "Nº Inventario",
            "brand": st.column_config.SelectboxColumn("Marca", options=list(set(past_brands))),
            "model": st.column_config.SelectboxColumn("Modelo", options=list(set(past_models))),
            "serial": "Nº Serie"
        }
    )
    # Update master state
    if edited_df is not None:
        st.session_state["components_df"] = edited_df

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
            "components": st.session_state["components_df"].to_dict("records") 
        }
        
        # --- UPDATE MEMORY (Learning) ---
        if service:
            if "services" not in memory["defaults"]: 
                memory["defaults"]["services"] = {}
            
            # Save or Update service data
            memory["defaults"]["services"][service] = {
                "manager": st.session_state["manager"],
                "floor": st.session_state["floor"],
                "unit": st.session_state["unit"],
                "hole": st.session_state["hole"],
                "center_name": st.session_state["center_name"],
                "center_code": st.session_state["center_code"]
            }
            # Optional: Also link model to service for even deeper memory?
            # memory["defaults"]["services"][service]["last_model"] = model
            
        if model:
            if "models" not in memory["defaults"]:
                memory["defaults"]["models"] = {}
                
            # Save or Update model data
            memory["defaults"]["models"][model] = {
                "description": st.session_state["description"],
                "brand": st.session_state["brand"],
                "provider": st.session_state["provider"],
                "contact": st.session_state["contact"]
            }
            
        if service or model:
            try:
                with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(memory, f, indent=4, ensure_ascii=False)
            except Exception as e:
                st.warning(f"No se pudo guardar la memoria: {e}")
            
        # Also auto-learn components' brands/models if missing
        for comp in data["components"]:
            c_mod = comp.get("model")
            if c_mod and c_mod not in memory["defaults"]["models"]:
                 memory["defaults"]["models"][c_mod] = {
                     "brand": comp.get("brand", ""),
                     "description": comp.get("name", ""), # Component Name -> Description
                     "provider": "",
                     "contact": ""
                 }
        # Save again if components added
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4, ensure_ascii=False)
            
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
