import streamlit as st
import json
import os
from datetime import datetime
import fill_acta  # Our local script
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIG ---
# --- CONFIG ---
st.set_page_config(page_title="Agente de Actas", layout="wide", initial_sidebar_state="expanded")

# --- STYLE INJECTION ---
# --- STYLE INJECTION ---
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    :root {
        --q-primary: #00B1A8;
        --q-secondary: #023E54;
        --q-bg: #F8FAFC;
        --q-card: #FFFFFF;
        --q-text: #1E293B;
        --q-text-muted: #64748B;
        --q-border: #E2E8F0;
        --q-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
        --q-shadow-premium: 0 20px 25px -5px rgb(0 0 0 / 0.05), 0 8px 10px -6px rgb(0 0 0 / 0.05);
    }

    /* Reset & Base */
    .stApp {
        background-color: var(--q-bg);
        color: var(--q-text);
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* App Header / Navigation */
    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.8) !important;
        backdrop-filter: blur(10px);
    }

    /* Typography */
    h1, h2, h3, .stHeading {
        font-family: 'Outfit', sans-serif !important;
        color: var(--q-secondary) !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 2rem !important;
    }

    /* Premium Cards */
    .custom-card {
        background: var(--q-card);
        border: 1px solid var(--q-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--q-shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .custom-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--q-shadow-premium);
        border-color: var(--q-primary);
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--q-border);
        box-shadow: 10px 0 30px rgba(0,0,0,0.02);
    }
    
    section[data-testid="stSidebar"] .stMarkdown p {
        font-weight: 500;
        color: var(--q-text-muted);
    }

    /* Input & Selection Overrides */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div, 
    textarea {
        background-color: #FFFFFF !important;
        border: 1px solid var(--q-border) !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="select"]:focus-within > div, 
    div[data-baseweb="input"]:focus-within > div {
        border-color: var(--q-primary) !important;
        box-shadow: 0 0 0 4px rgba(0, 177, 168, 0.1) !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--q-secondary) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(2, 62, 84, 0.15);
    }

    .stButton > button:hover {
        background: var(--q-primary) !important;
        transform: scale(1.02);
        box-shadow: 0 8px 16px rgba(0, 177, 168, 0.2);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid var(--q-border) !important;
        color: var(--q-text-muted) !important;
        padding: 0 1.5rem !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--q-primary) !important;
        color: white !important;
        border-color: var(--q-primary) !important;
    }

    /* Data Editor / Table Styling */
    div[data-testid="stDataEditor"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--q-border);
    }

    /* Hidden Streamlit Branding & Overrides */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animation */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp main {
        animation: slideUp 0.7s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    </style>
    """, unsafe_allow_html=True)

def card_begin(title=None):
    html = f'<div class="custom-card">'
    if title:
        html += f'<h3 style="margin-top:0; margin-bottom:1.5rem; font-size:0.9rem; color:#64748B; text-transform:uppercase; letter-spacing:0.1em; font-weight:700;">{title}</h3>'
    st.markdown(html, unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

# --- FIREBASE SETUP ---
MEMORY_FILE = "memory.json"

def init_firestore():
    if not firebase_admin._apps:
        try:
            # Try to load from Streamlit Secrets
            if "firebase_service_account" in st.secrets:
                secret_data = st.secrets["firebase_service_account"]
                if isinstance(secret_data, str):
                    try:
                        key_dict = json.loads(secret_data)
                    except json.JSONDecodeError:
                        st.error("❌ El secreto 'firebase_service_account' no es un JSON válido.")
                        return None, "error_json"
                else:
                    key_dict = dict(secret_data)
                
                cred = credentials.Certificate(key_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client(), "cloud"
            else:
                # If no secrets, we still return None but we don't suppress the fact that sync is offline
                return None, "local"
        except Exception as e:
            st.error(f"❌ Error conectando con Firebase: {e}")
            return None, f"error_{e}"
    return firestore.client(), "cloud"

# Initialize Firebase silently
db, db_mode = init_firestore()
COLLECTION = "app_data"
DOCUMENT = "memory"

# --- HELPERS ---
def load_memory():
    if db:
        try:
            doc_ref = db.collection(COLLECTION).document(DOCUMENT)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            st.error(f"Error cargando de Firestore: {e}")
    
    # Fallback to local file or default
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"defaults": {"services": {}, "models": {}}}

def save_memory(memory):
    # Save to Firestore
    if db:
        try:
            doc_ref = db.collection(COLLECTION).document(DOCUMENT)
            doc_ref.set(memory)
        except Exception as e:
            st.error(f"Error guardando en Firestore: {e}")
            
    # Always save to local as backup if possible
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando memoria local: {e}")

# --- CALLBACKS ---
def on_service_change():
    memory = load_memory()
    # Check all possible keys for service selection
    service_sel = st.session_state.get("service_select_recepcion") or st.session_state.get("service_select_baja")
    
    if service_sel and service_sel != "➕ AÑADIR NUEVO...":
        s_data = memory.get("defaults", {}).get("services", {}).get(service_sel, {})
        st.session_state["service"] = service_sel
        st.session_state["manager"] = s_data.get("manager", "")
        st.session_state["floor"] = s_data.get("floor", "")
        st.session_state["unit"] = s_data.get("unit", "")
        st.session_state["hole"] = s_data.get("hole", "")
        st.session_state["center_name"] = s_data.get("center_name", "POLICLINICA GIPUZKOA")
        st.session_state["center_code"] = s_data.get("center_code", "001")
    elif service_sel == "➕ AÑADIR NUEVO...":
        st.session_state["service"] = ""
        # We don't clear other fields to let users edit them for the new service

def on_model_change():
    memory = load_memory()
    # Check both reception and baja keys
    model_sel = st.session_state.get("model_select_recepcion") or st.session_state.get("model_select_baja")
    
    if model_sel and model_sel != "➕ AÑADIR NUEVO...":
        m_data = memory.get("defaults", {}).get("models", {}).get(model_sel, {})
        st.session_state["model"] = model_sel
        if m_data.get("description"): st.session_state["description"] = m_data["description"]
        if m_data.get("brand"): st.session_state["brand"] = m_data["brand"]
        if m_data.get("provider"): st.session_state["provider"] = m_data["provider"]
        if m_data.get("contact"): st.session_state["contact"] = m_data["contact"]
    elif model_sel == "➕ AÑADIR NUEVO...":
        st.session_state["model"] = ""
        # We don't clear other fields automatically to let users edit them for the new model

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
    
    if db_mode != "cloud":
        st.warning("⚠️ **Modo Local Activo**: Los cambios se guardarán solo en este dispositivo. Configura Firebase para sincronización en la nube.")

    tab_serv, tab_mod = st.tabs(["🏢 Servicios y Plantas", "📦 Modelos y Equipos"])

    with tab_serv:
        # --- ADD NEW SERVICE ---
        with st.expander("➕ AÑADIR NUEVO SERVICIO", expanded=False):
            with st.form("new_service_form"):
                n_name = st.text_input("Nombre del Servicio (Ej: RADIOLOGÍA)")
                col1, col2 = st.columns(2)
                n_manager = col1.text_input("Responsable")
                n_unit = col2.text_input("Unidad")
                n_floor = col1.text_input("Planta")
                n_hole = col2.text_input("Hueco")
                n_c_name = col1.text_input("Centro", value="POLICLINICA GIPUZKOA")
                n_c_code = col2.text_input("Cód. Centro", value="001")
                
                if st.form_submit_button("✨ Crear Servicio", use_container_width=True):
                    if n_name:
                        services = memory.get("defaults", {}).get("services", {})
                        services[n_name] = {
                            "manager": n_manager, "unit": n_unit, "floor": n_floor,
                            "hole": n_hole, "center_name": n_c_name, "center_code": n_c_code
                        }
                        save_memory(memory)
                        st.success(f"¡Servicio '{n_name}' creado!")
                        st.rerun()
                    else:
                        st.error("El nombre del servicio es obligatorio.")

        card_begin("🏢 Editar Servicios Existentes")
        services = memory.get("defaults", {}).get("services", {})
        if not services:
            st.write("No hay servicios guardados todavía.")
        else:
            s_list = sorted(list(services.keys()))
            selected_s = st.selectbox("Selecciona para editar", [""] + s_list)

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
                            "manager": new_manager, "unit": new_unit, "floor": new_floor,
                            "hole": new_hole, "center_name": new_c_name, "center_code": new_c_code
                        }
                        save_memory(memory)
                        st.success("¡Servicio actualizado!")
                        st.rerun()
                    
                    if c2.form_submit_button("🗑️ Borrar Servicio", use_container_width=True):
                        del services[selected_s]
                        save_memory(memory)
                        st.warning("Servicio eliminado.")
                        st.rerun()
        card_end()

    with tab_mod:
        # --- ADD NEW MODEL ---
        with st.expander("➕ AÑADIR NUEVA REFERENCIA / MODELO", expanded=False):
            with st.form("new_model_form"):
                n_m_name = st.text_input("Nombre del Modelo / Referencia")
                n_m_desc = st.text_input("Descripción")
                col1, col2 = st.columns(2)
                n_m_brand = col1.text_input("Marca")
                n_m_prov = col2.text_input("Proveedor")
                n_m_cont = st.text_input("Contacto")
                
                if st.form_submit_button("✨ Crear Modelo", use_container_width=True):
                    if n_m_name:
                        models = memory.get("defaults", {}).get("models", {})
                        models[n_m_name] = {
                            "description": n_m_desc, "brand": n_m_brand,
                            "provider": n_m_prov, "contact": n_m_cont
                        }
                        save_memory(memory)
                        st.success(f"¡Modelo '{n_m_name}' creado!")
                        st.rerun()
                    else:
                        st.error("El nombre del modelo es obligatorio.")

        card_begin("📦 Editar Modelos Existentes")
        models = memory.get("defaults", {}).get("models", {})
        if not models:
            st.write("No hay modelos guardados todavía.")
        else:
            m_list = sorted(list(models.keys()))
            selected_m = st.selectbox("Selecciona para editar", [""] + m_list)

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
                            "description": new_desc, "brand": new_brand,
                            "provider": new_prov, "contact": new_cont
                        }
                        save_memory(memory)
                        st.success("¡Modelo actualizado!")
                        st.rerun()

                    if c2.form_submit_button("🗑️ Borrar Modelo", use_container_width=True):
                        del models[selected_m]
                        save_memory(memory)
                        st.warning("Modelo eliminado.")
                        st.rerun()
        card_end()

# --- GLOBAL DEFAULTS ---
GLOBAL_DEFAULTS = {
    "center_name": "POLICLINICA GIPUZKOA",
    "center_code": "001",
    "description": "",
    "main_inventory_number": "INV-"
}

def show_baja_form(memory):
    st.title("🗑️ Nueva Acta de Baja")
    init_session_state()
    
    # Common fields that share memory
    col1, col2 = st.columns(2)
    with col1:
        card_begin("📍 Ubicación")
        # BUSCADOR DE SERVICIO (ComboBox)
        service_list = sorted(list(memory.get("defaults", {}).get("services", {}).keys()))
        service_options = [""] + service_list + ["➕ AÑADIR NUEVO..."]
        
        s_sel_idx = 0
        curr_s = st.session_state.get("service", "")
        if curr_s in service_list: s_sel_idx = service_list.index(curr_s) + 1
        
        selected_s = st.selectbox("Servicio (Buscador)", service_options, index=s_sel_idx, key="service_select_baja", on_change=on_service_change)
        
        if selected_s == "➕ AÑADIR NUEVO...":
            st.text_input("Nombre del Nuevo Servicio", key="service")
        else:
            st.text_input("Servicio", key="service", disabled=True)
            
        st.text_input("Centro", key="center_name")
        st.text_input("Código Centro", key="center_code")
        st.text_input("Responsable", key="manager")
        st.text_input("Unidad", key="unit")
        st.text_input("Planta", key="floor")
        st.text_input("Hueco", key="hole")
        card_end()
    
    with col2:
        card_begin("📦 Equipo")
        st.text_input("Descripción", key="description")
        st.text_input("Marca", key="brand")
        
        # BUSCADOR DE MODELO (ComboBox)
        model_list = sorted(list(memory.get("defaults", {}).get("models", {}).keys()))
        model_options = [""] + model_list + ["➕ AÑADIR NUEVO..."]
        
        sel_idx = 0
        curr_m = st.session_state.get("model", "")
        if curr_m in model_list: sel_idx = model_list.index(curr_m) + 1
        
        selected_m = st.selectbox("Modelo (Buscador)", model_options, index=sel_idx, key="model_select_baja", on_change=on_model_change)
        
        if selected_m == "➕ AÑADIR NUEVO...":
            st.text_input("Nombre del Nuevo Modelo", key="model")
        else:
            st.text_input("Modelo", key="model", disabled=True)
            
        st.text_input("Nº Serie", key="serial")
        st.text_input("Propiedad", key="property")
        st.text_input("Nº Inventario", key="main_inventory_number")
        st.text_input("Nº Inventario Padre", key="parent_inventory_number")
        card_end()

    st.markdown("---")
    
    col_inf, col_acc = st.columns(2)
    with col_inf:
        card_begin("📑 Informe Justificativo")
        st.date_input("Fecha Baja", key="baja_date_val")
        st.text_area("Justificación de la Baja", key="justification_report", height=150)
        card_end()

    with col_acc:
        card_begin("✅ Aceptación de la Baja")
        st.text_input("Número Orden de Trabajo", key="work_order_number")
        c_chk1, c_chk2 = st.columns(2)
        with c_chk1:
            st.checkbox("Presupuesto reparación", key="repair_budget", value=True)
            st.checkbox("Presupuesto reposición", key="replacement_budget", value=True)
        with c_chk2:
            st.checkbox("SAT oficial", key="sat_report", value=True)
            st.checkbox("Otros documentos", key="other_docs", value=True)
        st.checkbox("Limpieza de datos realizada", key="data_cleaned", value=True)
        st.text_area("Observaciones", key="obs_baja", height=68)
        card_end()
    
    if st.button("🚀 GENERAR ACTA DE BAJA (PDF)", type="primary", use_container_width=True):
        baja_date = st.session_state["baja_date_val"].strftime("%d/%m/%Y") if st.session_state["baja_date_val"] else ""
        service = st.session_state.get("service", "")
        
        data = {
            "center_name": st.session_state["center_name"], "center_code": st.session_state["center_code"],
            "service": service, "manager": st.session_state["manager"],
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

def init_session_state():
    fields = ["service", "center_name", "center_code", "manager", "unit", "floor", 
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

def show_reception_form(memory):
    st.title("📋 Nueva Acta de Recepción")
    init_session_state()
    
    # Sidebar: Reset button
    with st.sidebar:
        if st.button("🧹 Limpiar Formulario", use_container_width=True):
            for k in ["center_name", "center_code", "manager", "unit", "floor", "hole", "description", "brand", "model", "serial", "provider", "property", "contact", "main_inventory_number", "parent_inventory_number", "order_number", "amount_tax_included", "work_order_number", "justification_report"]:
                st.session_state[k] = GLOBAL_DEFAULTS.get(k, "")
            st.session_state["components_df"] = pd.DataFrame(columns=["name", "inventory", "brand", "model", "serial"])
            st.session_state["reception_date_val"] = datetime.now().date()
            st.session_state["acceptance_date_val"] = datetime.now().date()
            st.session_state["baja_date_val"] = datetime.now().date()
            st.session_state["warranty_end_val"] = None
            st.rerun()

    # --- FORM UI ---
    col1, col2 = st.columns(2)
    
    with col1:
        card_begin("📍 Ubicación")
        # BUSCADOR DE SERVICIO (ComboBox)
        service_list = sorted(list(memory.get("defaults", {}).get("services", {}).keys()))
        service_options = [""] + service_list + ["➕ AÑADIR NUEVO..."]
        
        s_sel_idx = 0
        curr_s = st.session_state.get("service", "")
        if curr_s in service_list: s_sel_idx = service_list.index(curr_s) + 1
        
        selected_s = st.selectbox("Servicio (Buscador)", service_options, index=s_sel_idx, key="service_select_recepcion", on_change=on_service_change)
        
        if selected_s == "➕ AÑADIR NUEVO...":
            st.text_input("Nombre del Nuevo Servicio", key="service")
        else:
            st.text_input("Servicio", key="service", disabled=True)

        st.text_input("Centro", key="center_name")
        st.text_input("Código Centro", key="center_code")
        st.text_input("Responsable", key="manager")
        st.text_input("Unidad", key="unit")
        st.text_input("Planta", key="floor")
        st.text_input("Hueco", key="hole")
        card_end()

    with col2:
        card_begin("📦 Equipo")
        st.text_input("Descripción", key="description")
        st.text_input("Marca", key="brand")
        
        # BUSCADOR DE MODELO (ComboBox)
        model_list = sorted(list(memory.get("defaults", {}).get("models", {}).keys()))
        model_options = [""] + model_list + ["➕ AÑADIR NUEVO..."]
        
        sel_idx = 0
        curr_m = st.session_state.get("model", "")
        if curr_m in model_list: sel_idx = model_list.index(curr_m) + 1
        
        selected_m = st.selectbox("Modelo (Buscador)", model_options, index=sel_idx, key="model_select_recepcion", on_change=on_model_change)
        
        if selected_m == "➕ AÑADIR NUEVO...":
            st.text_input("Nombre del Nuevo Modelo", key="model")
        else:
            st.text_input("Modelo", key="model", disabled=True)
            
        st.text_input("Nº Serie", key="serial")
        st.text_input("Proveedor", key="provider")
        st.text_input("Propiedad", key="property")
        st.text_input("Contacto", key="contact")
        card_end()
        
        card_begin("📅 Fechas y Garantía")
        c_d1, c_d2 = st.columns(2)
        c_d1.date_input("Recepción", key="reception_date_val", on_change=on_reception_change)
        c_d2.date_input("Aceptación", key="acceptance_date_val", on_change=calculate_warranty_end)
        st.radio("Años de Garantía", options=[0, 1, 2, 3, 4], key="warranty_years", horizontal=True, on_change=calculate_warranty_end)
        st.date_input("Fin Garantía", key="warranty_end_val")
        card_end()
        
        reception_date = st.session_state["reception_date_val"].strftime("%d/%m/%Y") if st.session_state["reception_date_val"] else ""
        acceptance_date = st.session_state["acceptance_date_val"].strftime("%d/%m/%Y") if st.session_state["acceptance_date_val"] else ""
        warranty_end = st.session_state["warranty_end_val"].strftime("%d/%m/%Y") if st.session_state["warranty_end_val"] else ""

    st.markdown("---")
    
    col_reg, col_ver = st.columns(2)
    with col_reg:
        card_begin("📝 Registro y Aceptación")
        st.text_input("Nº Inventario", key="main_inventory_number")
        st.text_input("Nº Inventario Padre", key="parent_inventory_number")
        st.text_input("Número Pedido", key="order_number")
        st.text_input("Importe (IVA inc.)", key="amount_tax_included")
        card_end()

    with col_ver:
        card_begin("✅ Verificaciones")
        tab_v1, tab_v2, tab_v3 = st.tabs(["📋 General", "🔒 Seguridad", "🔧 Mantenimiento"])
        with tab_v1:
            compliance = st.checkbox("Cumple normativa", value=True)
            manuals_usage = st.checkbox("Manual Uso", value=True)
            manuals_tech = st.checkbox("Manual Técnico", value=True)
            order_accordance = st.checkbox("Acorde a pedido", value=True)
        with tab_v2:
            patient_data = st.checkbox("Maneja datos pac.", value=True)
            backup_required = st.checkbox("Requiere copia seg.", value=True)
            requires_epis = st.checkbox("Requiere EPIS", value=True)
            safe_to_use = st.checkbox("Seguro para uso", value=True)
            received_correctly = st.checkbox("Recibido/Instalado correctamente", value=True)
            users_trained = st.checkbox("Usuarios formados", value=True)
        with tab_v3:
            preventive = st.checkbox("Mant. Preventivo", value=True)
            contract = st.checkbox("Contrato Mant.", value=True)
            periodicity = st.selectbox("Periodicidad", ["Anual", "Semestral", "Trimestral", "Bienal"])
            status = st.radio("Estado del Equipo", ["good", "bad", "obsolete"], format_func=lambda x: {"good":"Buen Estado", "bad":"Mal Estado", "obsolete":"Obsoleto"}[x])
        card_end()

    st.markdown("---")
    card_begin("🔧 Componentes del Equipo")
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
    observations = st.text_area("Observaciones", height=100)
    card_end()
    
    if st.button("🚀 GENERAR ACTA PDF", type="primary", use_container_width=True):
        service_val = st.session_state.get("service", "")
        data = {
            "center_name": st.session_state["center_name"], "center_code": st.session_state["center_code"],
            "service": service_val, "manager": st.session_state["manager"],
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
    inject_custom_css()
    # --- NAVIGATION ---
    with st.sidebar:
        st.markdown(f"""
            <div style='padding: 1rem 0 2rem 0;'>
                <h2 style='margin:0; font-size: 1.6rem; color: #023E54; font-family: "Outfit", sans-serif; font-weight: 800;'>
                    ACTAS PG
                </h2>
                <div style='display: flex; align-items: center; gap: 6px; margin-top: 4px;'>
                    <span style='width: 8px; height: 8px; background: {"#10B981" if db_mode == "cloud" else "#F59E0B"}; border-radius: 50%;'></span>
                    <span style='color: #64748B; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>
                        {"Cloud Sync" if db_mode == "cloud" else "Modo Local"}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        view = st.radio("Sección", ["📝 Nueva Acta", "💾 Base de Datos"], label_visibility="collapsed")
        
        report_type = "recepcion"
        if view == "📝 Nueva Acta":
            st.markdown("<p style='font-size:0.7rem; font-weight:700; color:#64748B; margin: 2rem 0 0.5rem 0; text-transform:uppercase; letter-spacing:0.1em;'>Tipo de Documento</p>", unsafe_allow_html=True)
            report_sel = st.pills("Doc", ["📋 Recepción", "🗑️ Baja"], selection_mode="single", label_visibility="collapsed", key="pill_nav")
            report_type = "recepcion" if report_sel == "📋 Recepción" else "baja"
            
        st.markdown("<div style='position: fixed; bottom: 20px; left: 20px; color: #94A3B8; font-size: 0.7rem; font-weight:500;'>v2.5 • Premium Clinical UI</div>", unsafe_allow_html=True)

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
