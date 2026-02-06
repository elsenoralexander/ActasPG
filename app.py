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

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando memoria: {e}")

# --- CALLBACKS ---
def on_service_change():
    memory = load_memory()
    # Check all possible keys for service selection
    service = st.session_state.get("service") or st.session_state.get("service_baja")
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
    # Check all possible keys for model selection (though it might be same key, better safe)
    model = st.session_state.get("model") or st.session_state.get("model_baja")
    if model and model in memory.get("defaults", {}).get("models", {}):
        m_data = memory["defaults"]["models"][model]
        if m_data.get("description"): st.session_state["description"] = m_data["description"]
        if m_data.get("brand"): st.session_state["brand"] = m_data["brand"]
        if m_data.get("provider"): st.session_state["provider"] = m_data["provider"]
        if m_data.get("contact"): st.session_state["contact"] = m_data["contact"]

def on_reception_change():
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

def on_components_change():
    # Sync edits from data_editor widget state to session_state["components_df"]
    state = st.session_state.get("components_editor_final")
    if state:
        df = st.session_state["components_df"]
        
        # Handle edits
        for row_idx, changes in state.get("edited_rows", {}).items():
            for col, val in changes.items():
                df.iloc[int(row_idx)][col] = val
        
        # Handle additions
        added = state.get("added_rows", [])
        if added:
            new_rows = pd.DataFrame(added)
            # Ensure columns match
            for col in df.columns:
                if col not in new_rows.columns:
                    new_rows[col] = ""
            st.session_state["components_df"] = pd.concat([df, new_rows], ignore_index=True)
            
        # Handle deletions
        deleted = state.get("deleted_rows", [])
        if deleted:
            st.session_state["components_df"] = df.drop(deleted).reset_index(drop=True)

# --- VIEWS ---

def show_database(memory):
    st.title("💾 Gestión de Base de Datos")
    st.info("Desde aquí puedes editar o borrar la información que el Agente 'aprende' automáticamente.")

    tab_serv, tab_mod = st.tabs(["🏢 Servicios y Plantas", "📦 Modelos y Equipos"])

    with tab_serv:
        services = memory.get("defaults", {}).get("services", {})
        if not services:
            st.write("No hay servicios guardados todavía.")
        else:
            s_list = sorted(list(services.keys()))
            selected_s = st.selectbox("Selecciona un Servicio para editar", [""] + s_list)

            if selected_s:
                s_data = services[selected_s]
                with st.form("edit_service_form"):
                    st.subheader(f"Editando: {selected_s}")
                    new_manager = st.text_input("Responsable", value=s_data.get("manager", ""))
                    new_unit = st.text_input("Unidad", value=s_data.get("unit", ""))
                    new_floor = st.text_input("Planta", value=s_data.get("floor", ""))
                    new_hole = st.text_input("Hueco", value=s_data.get("hole", ""))
                    new_c_name = st.text_input("Centro", value=s_data.get("center_name", "POLICLINICA GIPUZKOA"))
                    new_c_code = st.text_input("Cód. Centro", value=s_data.get("center_code", "001"))

                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                        services[selected_s] = {
                            "manager": new_manager,
                            "unit": new_unit,
                            "floor": new_floor,
                            "hole": new_hole,
                            "center_name": new_c_name,
                            "center_code": new_c_code
                        }
                        save_memory(memory)
                        st.success("¡Servicio actualizado!")
                        st.rerun()
                    
                    if c2.form_submit_button("🗑️ Borrar Servicio", use_container_width=True):
                        del services[selected_s]
                        save_memory(memory)
                        st.warning("Servicio eliminado.")
                        st.rerun()

    with tab_mod:
        models = memory.get("defaults", {}).get("models", {})
        if not models:
            st.write("No hay modelos guardados todavía.")
        else:
            m_list = sorted(list(models.keys()))
            selected_m = st.selectbox("Selecciona un Modelo para editar", [""] + m_list)

            if selected_m:
                m_data = models[selected_m]
                with st.form("edit_model_form"):
                    st.subheader(f"Modelo: {selected_m}")
                    new_desc = st.text_input("Descripción", value=m_data.get("description", ""))
                    new_brand = st.text_input("Marca", value=m_data.get("brand", ""))
                    new_prov = st.text_input("Proveedor", value=m_data.get("provider", ""))
                    new_cont = st.text_input("Contacto", value=m_data.get("contact", ""))

                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                        models[selected_m] = {
                            "description": new_desc,
                            "brand": new_brand,
                            "provider": new_prov,
                            "contact": new_cont
                        }
                        save_memory(memory)
                        st.success("¡Modelo actualizado!")
                        st.rerun()

                    if c2.form_submit_button("🗑️ Borrar Modelo", use_container_width=True):
                        del models[selected_m]
                        save_memory(memory)
                        st.warning("Modelo eliminado.")
                        st.rerun()

# --- GLOBAL DEFAULTS ---
GLOBAL_DEFAULTS = {
    "center_name": "POLICLINICA GIPUZKOA",
    "center_code": "001",
    "description": "",
    "main_inventory_number": "INV-"
}

def show_baja_form(memory):
    st.title("🗑️ Nueva Acta de Baja")
    
    # Common fields that share memory
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Ubicación")
        service_options = [""] + list(memory.get("defaults", {}).get("services", {}).keys())
        service = st.selectbox("Servicio", service_options, key="service_baja", on_change=on_service_change)
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
        st.text_input("Propiedad", key="property")
        st.text_input("Nº Inventario", key="main_inventory_number")
        st.text_input("Nº Inventario Padre", key="parent_inventory_number")

    st.markdown("---")
    st.subheader("📑 Informe Justificativo")
    c_just1, c_just2 = st.columns([1, 2])
    with c_just1:
        st.date_input("Fecha Baja", key="baja_date_val")
    with c_just2:
        justification = st.text_area("Justificación de la Baja", key="justification_report", height=100)

    st.markdown("---")
    st.subheader("✅ Aceptación de la Baja")
    c_acc1, c_acc2 = st.columns(2)
    with c_acc1:
        rep_budget = st.checkbox("Se adjunta presupuesto reparación", key="repair_budget", value=True)
        rep_repos = st.checkbox("Se adjunta presupuesto reposición", key="replacement_budget", value=True)
        sat_off = st.checkbox("Se adjunta SAT oficial justificativo", key="sat_report", value=True)
    with c_acc2:
        st.text_input("Número Orden de Trabajo", key="work_order_number")
        other_docs = st.checkbox("Se adjuntan otros documentos", key="other_docs", value=True)
        data_clean = st.checkbox("Limpieza de datos de paciente realizada", key="data_cleaned", value=True)

    st.markdown("---")
    st.subheader("Extras")
    observations = st.text_area("Observaciones", key="obs_baja", height=100)
    
    if st.button("🚀 GENERAR ACTA DE BAJA (PDF)", type="primary", use_container_width=True):
        baja_date = st.session_state["baja_date_val"].strftime("%d/%m/%Y") if st.session_state["baja_date_val"] else ""
        
        data = {
            "center_name": st.session_state["center_name"], "center_code": st.session_state["center_code"],
            "service": service if service else "", "manager": st.session_state["manager"],
            "unit": st.session_state["unit"], "floor": st.session_state["floor"], "hole": st.session_state["hole"],
            "description": st.session_state["description"], "brand": st.session_state["brand"],
            "model": st.session_state["model"], "serial_number": st.session_state["serial"],
            "property": st.session_state["property"], "main_inventory_number": st.session_state["main_inventory_number"],
            "parent_inventory_number": st.session_state["parent_inventory_number"],
            "baja_date": baja_date, "justification_report": justification,
            "repair_budget": rep_budget, "replacement_budget": rep_repos,
            "sat_report": sat_off, "work_order_number": st.session_state["work_order_number"],
            "other_docs": other_docs, "data_cleaned": data_clean, "observations": observations
        }
        
        # Guardar en memoria
        if service:
            if "services" not in memory["defaults"]: memory["defaults"]["services"] = {}
            memory["defaults"]["services"][service] = {
                "manager": st.session_state["manager"], "floor": st.session_state["floor"],
                "unit": st.session_state["unit"], "hole": st.session_state["hole"],
                "center_name": st.session_state["center_name"], "center_code": st.session_state["center_code"]
            }
        
        model_key = st.session_state.get("model")
        if model_key:
            if "models" not in memory["defaults"]: memory["defaults"]["models"] = {}
            memory["defaults"]["models"][model_key] = {
                "description": st.session_state["description"], "brand": st.session_state["brand"]
            }
        save_memory(memory)
            
        try:
            import unicodedata
            template_filename = "acta baja equipos.pdf"
            actual_template = next((f for f in os.listdir(".") if unicodedata.normalize('NFC', f) == unicodedata.normalize('NFC', template_filename)), template_filename)
            
            output_path = "Acta_Baja_Generada.pdf"
            fill_acta.fill_pdf(actual_template, output_path, data, report_type="baja")
            
            with open(output_path, "rb") as f:
                st.session_state["baja_pdf_content"] = f.read()
            st.success("✅ Acta de Baja Generada con éxito.")
        except Exception as e:
            st.error(f"Error generando PDF de Baja: {e}")

    # Mostrar botón de descarga si el PDF está listo
    if "baja_pdf_content" in st.session_state:
        st.download_button(
            label="📥 DESCARGAR ACTA DE BAJA",
            data=st.session_state["baja_pdf_content"],
            file_name=f"Acta_Baja_{st.session_state.get('serial', 'EQUIPO')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

def show_reception_form(memory):
    st.title("📋 Nueva Acta de Recepción")
    
    fields = ["center_name", "center_code", "manager", "unit", "floor", 
              "hole", "description", "brand", "model", "serial", "provider",
              "property", "contact", "main_inventory_number", "parent_inventory_number",
              "order_number", "amount_tax_included", "work_order_number", "justification_report"]
    for f in fields:
        if f not in st.session_state:
            st.session_state[f] = GLOBAL_DEFAULTS.get(f, "")
            
    if "reception_date_val" not in st.session_state: st.session_state["reception_date_val"] = datetime.now().date()
    if "acceptance_date_val" not in st.session_state: st.session_state["acceptance_date_val"] = datetime.now().date()
    if "baja_date_val" not in st.session_state: st.session_state["baja_date_val"] = datetime.now().date()
    if "warranty_end_val" not in st.session_state: st.session_state["warranty_end_val"] = None
    if "warranty_years" not in st.session_state: st.session_state["warranty_years"] = 2
    if "components_df" not in st.session_state:
        st.session_state["components_df"] = pd.DataFrame(columns=["name", "inventory", "brand", "model", "serial"])

    # Sidebar: Reset button
    with st.sidebar:
        if st.button("🧹 Limpiar Formulario", use_container_width=True):
            for k in fields: st.session_state[k] = GLOBAL_DEFAULTS.get(k, "")
            st.session_state["components_df"] = pd.DataFrame(columns=["name", "inventory", "brand", "model", "serial"])
            st.session_state["reception_date_val"] = datetime.now().date()
            st.session_state["acceptance_date_val"] = datetime.now().date()
            st.session_state["baja_date_val"] = datetime.now().date()
            st.session_state["warranty_end_val"] = None
            st.rerun()

    # --- FORM UI ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Ubicación")
        service_options = [""] + list(memory.get("defaults", {}).get("services", {}).keys())
        s_col1, s_col2 = st.columns([3, 1])
        is_new_service = s_col2.checkbox("Nuevo ➕")
        
        if is_new_service:
            service = st.text_input("Nuevo Servicio", key="service", help="Escribe el nombre del nuevo servicio")
        else:
            service = st.selectbox("Servicio", service_options, key="service", on_change=on_service_change)

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
        
        reception_date = st.session_state["reception_date_val"].strftime("%d/%m/%Y") if st.session_state["reception_date_val"] else ""
        acceptance_date = st.session_state["acceptance_date_val"].strftime("%d/%m/%Y") if st.session_state["acceptance_date_val"] else ""
        warranty_end = st.session_state["warranty_end_val"].strftime("%d/%m/%Y") if st.session_state["warranty_end_val"] else ""

    st.markdown("---")
    st.subheader("📝 Registro y Aceptación")
    reg_col1, reg_col2 = st.columns(2)
    with reg_col1:
        st.text_input("Nº Inventario", key="main_inventory_number")
        st.text_input("Nº Inventario Padre", key="parent_inventory_number")
    with reg_col2:
        st.text_input("Número Pedido", key="order_number")
        st.text_input("Importe (IVA inc.)", key="amount_tax_included")

    st.markdown("---")
    st.subheader("✅ Verificaciones")
    c_v1, c_v2, c_v3 = st.columns(3)
    with c_v1:
        st.markdown("**Recepción**")
        compliance = st.checkbox("Cumple normativa", value=True)
        manuals_usage = st.checkbox("Manual Uso", value=True)
        manuals_tech = st.checkbox("Manual Técnico", value=True)
        order_accordance = st.checkbox("Acorde a pedido", value=True)
    with c_v2:
        st.markdown("**Seguridad / Datos**")
        patient_data = st.checkbox("Maneja datos pac.", value=True)
        backup_required = st.checkbox("Requiere copia seg.", value=True)
        requires_epis = st.checkbox("Requiere EPIS", value=True)
        safe_to_use = st.checkbox("Seguro para uso", value=True)
        received_correctly = st.checkbox("Recibido/Instalado correctamente", value=True)
        users_trained = st.checkbox("Usuarios formados", value=True)
    with c_v3:
        st.markdown("**Mantenimiento y Estado**")
        preventive = st.checkbox("Mant. Preventivo", value=True)
        contract = st.checkbox("Contrato Mant.", value=True)
        periodicity = st.selectbox("Periodicidad", ["Anual", "Semestral", "Trimestral", "Bienal"])
        status = st.radio("Estado del Equipo", ["good", "bad", "obsolete"], format_func=lambda x: {"good":"Buen Estado", "bad":"Mal Estado", "obsolete":"Obsoleto"}[x])

    st.markdown("---")
    st.subheader("🔧 Componentes del Equipo")
    # Botones para añadir filas explícitamente (ayuda a evitar borrados y permite poner marca por defecto)
    c_btn1, c_btn2 = st.columns([1, 2])
    with c_btn1:
        if st.button("➕ Fila Vacía", use_container_width=True):
            new_row = pd.DataFrame([{"name":"", "inventory":"", "brand":"", "model":"", "serial":""}])
            st.session_state["components_df"] = pd.concat([st.session_state["components_df"], new_row], ignore_index=True)
            st.rerun()
    with c_btn2:
        main_brand = st.session_state.get("brand", "")
        if st.button(f"➕ Fila Marca: {main_brand if main_brand else '...'}", use_container_width=True):
            new_row = pd.DataFrame([{"name":"", "inventory":"", "brand":main_brand, "model":"", "serial":""}])
            st.session_state["components_df"] = pd.concat([st.session_state["components_df"], new_row], ignore_index=True)
            st.rerun()

    # Editor sin restricciones (Texto libre) con CALLBACK para máxima estabilidad
    st.data_editor(
        st.session_state["components_df"],
        num_rows="dynamic",
        use_container_width=True,
        key="components_editor_final",
        on_change=on_components_change,
        column_config={
            "name": "Nombre Componente",
            "inventory": "Nº Inventario",
            "brand": "Marca (Libre)",
            "model": "Modelo (Libre)",
            "serial": "Nº Serie"
        }
    )
    # Ya no asignamos edited_df directamente aquí para evitar el "flasheo" de reset

    st.markdown("---")
    st.subheader("Extras")
    observations = st.text_area("Observaciones", height=100)
    
    if st.button("🚀 GENERAR ACTA PDF", type="primary", use_container_width=True):
        data = {
            "center_name": st.session_state["center_name"], "center_code": st.session_state["center_code"],
            "service": service if service else "", "manager": st.session_state["manager"],
            "unit": st.session_state["unit"], "floor": st.session_state["floor"], "hole": st.session_state["hole"],
            "description": st.session_state["description"], "brand": st.session_state["brand"],
            "model": st.session_state["model"], "serial_number": st.session_state["serial"],
            "provider": st.session_state["provider"], "reception_date": reception_date,
            "acceptance_date": acceptance_date, "warranty_end": warranty_end,
            "compliance": compliance, "manuals_usage": manuals_usage, "manuals_tech": manuals_tech,
            "order_accordance": order_accordance, "patient_data": patient_data,
            "backup_required": backup_required, "requires_epis": requires_epis, "safe_to_use": safe_to_use,
            "preventive_maintenance": preventive, "maintenance_contract": contract,
            "periodicity": periodicity, "equipment_status": status,
            "main_inventory_number": st.session_state["main_inventory_number"],
            "parent_inventory_number": st.session_state["parent_inventory_number"],
            "order_number": st.session_state["order_number"], "amount_tax_included": st.session_state["amount_tax_included"],
            "property": st.session_state["property"], "contact": st.session_state["contact"],
            "received_correctly": received_correctly, "users_trained": users_trained,
            "observations": observations, "components": st.session_state["components_df"].to_dict("records") 
        }
        
        # --- UPDATE MEMORY ---
        if service:
            if "services" not in memory["defaults"]: memory["defaults"]["services"] = {}
            memory["defaults"]["services"][service] = {
                "manager": st.session_state["manager"], "floor": st.session_state["floor"],
                "unit": st.session_state["unit"], "hole": st.session_state["hole"],
                "center_name": st.session_state["center_name"], "center_code": st.session_state["center_code"]
            }
        
        model_key = st.session_state.get("model")
        if model_key:
            if "models" not in memory["defaults"]: memory["defaults"]["models"] = {}
            memory["defaults"]["models"][model_key] = {
                "description": st.session_state["description"], "brand": st.session_state["brand"],
                "provider": st.session_state["provider"], "contact": st.session_state["contact"]
            }
        
        save_memory(memory)
            
        try:
            import unicodedata
            template_filename = "CORP27.3_GM1_F3_Acta recepción equipos electromédicos.pdf"
            actual_template = next((f for f in os.listdir(".") if unicodedata.normalize('NFC', f) == unicodedata.normalize('NFC', template_filename)), template_filename)
            
            output_path = "Acta_Generada_Web.pdf"
            fill_acta.fill_pdf(actual_template, output_path, data)
            
            with open(output_path, "rb") as f:
                st.session_state["recepcion_pdf_content"] = f.read()
            st.success("✅ Acta de Recepción Generada con éxito.")
        except Exception as e:
            st.error(f"Error generando PDF: {e}")

    # Mostrar botón de descarga si el PDF está listo
    if "recepcion_pdf_content" in st.session_state:
        st.download_button(
            label="📥 DESCARGAR ACTA DE RECEPCIÓN",
            data=st.session_state["recepcion_pdf_content"],
            file_name=f"Acta_Recepcion_{st.session_state.get('serial', 'EQUIPO')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

def main():
    # --- NAVIGATION ---
    with st.sidebar:
        st.title("🤖 Agente de Actas")
        view = st.radio("Sección", ["📝 Nueva Acta", "💾 Base de Datos"], label_visibility="collapsed")
        
        report_type = "recepcion"
        if view == "📝 Nueva Acta":
            st.markdown("---")
            report_type = st.radio("Tipo de Acta", ["Recepción", "Baja"], horizontal=False)
            report_type = "recepcion" if report_type == "Recepción" else "baja"
            
        st.markdown("---")

    memory = load_memory()
    if view == "💾 Base de Datos":
        show_database(memory)
    else:
        if report_type == "recepcion":
            show_reception_form(memory)
        else:
            show_baja_form(memory)

if __name__ == "__main__":
    main()
