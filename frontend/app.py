import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

API_URL = os.getenv("API_GATEWAY_URL", "http://gateway:8000")

st.set_page_config(page_title="Gestión de Inventario TI", layout="wide")

st.title("Sistema de Gestión de Inventario TI")

st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Inicio", "Proveedores", "Equipos", "Mantenimiento", "Reportes"])

if page == "Inicio":
    st.write("### Bienvenido al sistema de gestión de inventario de TI.")
    st.info("Utilice el menú lateral para navegar entre los módulos.")

elif page == "Proveedores":
    st.header("Gestión de Proveedores")
    
    tab1, tab2 = st.tabs(["Listado", "Registrar/Editar"])
    
    with tab1:
        st.subheader("Listado de Proveedores")
        try:
            response = requests.get(f"{API_URL}/providers")
            if response.status_code == 200:
                providers = response.json()
                if providers:
                    df = pd.DataFrame(providers)
                    st.dataframe(df)
                else:
                    st.info("No hay proveedores registrados.")
            else:
                st.error("Error al cargar proveedores")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    with tab2:
        st.subheader("Registrar o Editar Proveedor")
        mode = st.radio("Modo", ["Registrar", "Editar"])
        
        if mode == "Editar":
            provider_id_input = st.number_input("ID del Proveedor a editar", min_value=1, step=1)
            load_btn = st.button("Cargar Datos")
            
            if "edit_provider_data" not in st.session_state:
                st.session_state.edit_provider_data = {}
                
            if load_btn:
                try:
                    res = requests.get(f"{API_URL}/providers/{provider_id_input}")
                    if res.status_code == 200:
                        st.session_state.edit_provider_data = res.json()
                        st.success("Datos cargados")
                    else:
                        st.error("Proveedor no encontrado")
                        st.session_state.edit_provider_data = {}
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.session_state.edit_provider_data = {}

        with st.form("provider_form"):
            current_data = st.session_state.get("edit_provider_data", {})
            
            name = st.text_input("Nombre", value=current_data.get("name", ""))
            contact = st.text_input("Contacto", value=current_data.get("contact_name", ""))
            email = st.text_input("Email", value=current_data.get("email", ""))
            phone = st.text_input("Teléfono", value=current_data.get("phone", ""))
            address = st.text_area("Dirección", value=current_data.get("address", ""))
            
            submitted = st.form_submit_button("Guardar")
            
            if submitted:
                data = {"name": name, "contact_name": contact, "email": email, "phone": phone, "address": address}
                try:
                    if mode == "Registrar":
                        res = requests.post(f"{API_URL}/providers", json=data)
                    else:
                        res = requests.put(f"{API_URL}/providers/{provider_id_input}", json=data)
                        
                    if res.status_code == 200:
                        st.success(f"Proveedor {'registrado' if mode == 'Registrar' else 'actualizado'} exitosamente")
                        st.session_state.edit_provider_data = {} # Clear
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

elif page == "Equipos":
    st.header("Gestión de Equipos")
    
    # Fetch providers
    providers_list = []
    try:
        p_res = requests.get(f"{API_URL}/providers")
        if p_res.status_code == 200:
            providers_list = p_res.json()
    except:
        pass
    provider_options = {p['name']: p['id'] for p in providers_list}
    
    tab1, tab2, tab3 = st.tabs(["Inventario", "Registrar/Editar", "Historial"])
    
    with tab1:
        try:
            response = requests.get(f"{API_URL}/equipment")
            if response.status_code == 200:
                equipment = response.json()
                if equipment:
                    df = pd.DataFrame(equipment)
                    st.dataframe(df)
                else:
                    st.info("No hay equipos registrados.")
            else:
                st.error("Error al cargar equipos")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    with tab2:
        st.subheader("Registrar o Editar Equipo")
        mode = st.radio("Modo Equipo", ["Registrar", "Editar"])
        
        if mode == "Editar":
            eq_id_input = st.number_input("ID del Equipo a editar", min_value=1, step=1)
            load_btn = st.button("Cargar Equipo")
            
            if "edit_eq_data" not in st.session_state:
                st.session_state.edit_eq_data = {}
                
            if load_btn:
                try:
                    res = requests.get(f"{API_URL}/equipment/{eq_id_input}")
                    if res.status_code == 200:
                        st.session_state.edit_eq_data = res.json()
                        st.success("Datos cargados")
                    else:
                        st.error("Equipo no encontrado")
                        st.session_state.edit_eq_data = {}
                except:
                    pass
        else:
            st.session_state.edit_eq_data = {}

        with st.form("equipment_form"):
            current_data = st.session_state.get("edit_eq_data", {})
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre", value=current_data.get("name", ""))
                serial = st.text_input("Número de Serie", value=current_data.get("serial_number", ""))
                type_ = st.text_input("Tipo", value=current_data.get("type", ""))
                brand = st.text_input("Marca", value=current_data.get("brand", ""))
            with col2:
                model = st.text_input("Modelo", value=current_data.get("model", ""))
                
                status_opts = ["available", "assigned", "maintenance", "retired"]
                curr_status = current_data.get("status", "available")
                status = st.selectbox("Estado", status_opts, index=status_opts.index(curr_status) if curr_status in status_opts else 0)
                
                location = st.text_input("Ubicación", value=current_data.get("location", ""))
                
                # Find current provider name
                curr_prov_id = current_data.get("provider_id")
                curr_prov_name = next((name for name, pid in provider_options.items() if pid == curr_prov_id), None)
                
                prov_keys = list(provider_options.keys())
                prov_idx = prov_keys.index(curr_prov_name) if curr_prov_name in prov_keys else 0
                
                provider_name = st.selectbox("Proveedor", prov_keys if prov_keys else ["Sin proveedores"], index=prov_idx)
            
            submitted = st.form_submit_button("Guardar")
            if submitted:
                provider_id = provider_options.get(provider_name) if provider_options else None
                data = {
                    "name": name, "serial_number": serial, "type": type_, "brand": brand,
                    "model": model, "status": status, "location": location, "provider_id": provider_id
                }
                try:
                    if mode == "Registrar":
                        res = requests.post(f"{API_URL}/equipment", json=data)
                    else:
                        res = requests.put(f"{API_URL}/equipment/{eq_id_input}", json=data)
                        
                    if res.status_code == 200:
                        st.success(f"Equipo {'registrado' if mode == 'Registrar' else 'actualizado'} exitosamente")
                        st.session_state.edit_eq_data = {}
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    with tab3:
        st.subheader("Historial de Equipos")
        hist_eq_id = st.number_input("ID del Equipo para ver historial", min_value=1, step=1)
        if st.button("Ver Historial"):
            try:
                res = requests.get(f"{API_URL}/equipment/{hist_eq_id}/history")
                if res.status_code == 200:
                    history = res.json()
                    if history:
                        st.dataframe(pd.DataFrame(history))
                    else:
                        st.info("No hay historial para este equipo.")
                else:
                    st.error("Error al obtener historial")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "Mantenimiento":
    st.header("Gestión de Mantenimiento")
    
    # Fetch equipment
    equipment_list = []
    try:
        e_res = requests.get(f"{API_URL}/equipment")
        if e_res.status_code == 200:
            equipment_list = e_res.json()
    except:
        pass
    equipment_options = {f"{e['name']} ({e['serial_number']})": e['id'] for e in equipment_list}
    
    tab1, tab2 = st.tabs(["Calendario/Listado", "Programar Mantenimiento"])
    
    with tab1:
        st.subheader("Mantenimientos Programados y Realizados")
        try:
            response = requests.get(f"{API_URL}/maintenance")
            if response.status_code == 200:
                maintenance = response.json()
                if maintenance:
                    df = pd.DataFrame(maintenance)
                    
                    # Simple Calendar View (Table sorted by date)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values(by='date', ascending=False)
                    
                    st.dataframe(df)
                    
                    st.write("### Próximos Mantenimientos")
                    today = pd.Timestamp.now()
                    upcoming = df[(df['date'] >= today) & (df['status'] == 'scheduled')]
                    if not upcoming.empty:
                        st.dataframe(upcoming)
                    else:
                        st.info("No hay mantenimientos próximos programados.")
                else:
                    st.info("No hay registros de mantenimiento.")
            else:
                st.error("Error al cargar mantenimientos")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    with tab2:
        st.subheader("Registrar Mantenimiento")
        with st.form("maintenance_form"):
            eq_name = st.selectbox("Equipo", list(equipment_options.keys()) if equipment_options else ["Sin equipos"])
            type_ = st.selectbox("Tipo", ["preventive", "corrective"])
            description = st.text_area("Descripción")
            cost = st.number_input("Costo Estimado/Real", min_value=0.0, step=0.01)
            date = st.date_input("Fecha Programada")
            technician = st.text_input("Técnico Asignado")
            status = st.selectbox("Estado", ["scheduled", "completed", "cancelled"])
            
            submitted = st.form_submit_button("Registrar")
            if submitted:
                equipment_id = equipment_options.get(eq_name) if equipment_options else None
                if equipment_id:
                    data = {
                        "equipment_id": equipment_id, "type": type_, "description": description,
                        "cost": cost, "date": str(date), "technician": technician, "status": status
                    }
                    try:
                        res = requests.post(f"{API_URL}/maintenance", json=data)
                        if res.status_code == 200:
                            st.success("Mantenimiento registrado")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")

elif page == "Reportes":
    st.header("Dashboard y Reportes")
    
    try:
        response = requests.get(f"{API_URL}/reports/stats")
        if response.status_code == 200:
            stats = response.json()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Equipos", stats.get("total_equipment", 0))
            col2.metric("Costo Total Mantenimiento", f"${stats.get('total_maintenance_cost', 0):,.2f}")
            
            st.subheader("Equipos por Estado")
            status_data = stats.get("equipment_by_status", {})
            if status_data:
                df_status = pd.DataFrame(list(status_data.items()), columns=["Estado", "Cantidad"])
                fig = px.pie(df_status, values="Cantidad", names="Estado", title="Distribución de Estados")
                st.plotly_chart(fig)
                
            st.subheader("Exportar Datos")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Generar Reporte Excel"):
                    try:
                        r = requests.get(f"{API_URL}/reports/export/excel")
                        if r.status_code == 200:
                            st.download_button(
                                label="Descargar Excel",
                                data=r.content,
                                file_name="inventario.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.error("Error generando Excel")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with c2:
                if st.button("Generar Reporte PDF"):
                    try:
                        r = requests.get(f"{API_URL}/reports/export/pdf")
                        if r.status_code == 200:
                            st.download_button(
                                label="Descargar PDF",
                                data=r.content,
                                file_name="inventario.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error("Error generando PDF")
                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            st.error("Error al cargar estadísticas")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
