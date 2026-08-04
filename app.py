"""
AnotIA - Asistente de Redacción de Anotaciones Pedagógicas con RICE e IA
Prototipo MVP construido con Streamlit y la API de Google Gemini (google-genai).
"""

import streamlit as st
import google.genai as genai
from google.genai import types
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Menos tiempo redactando, más tiempo enseñando",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización de historial y favoritos en st.session_state
if "historial" not in st.session_state:
    st.session_state.historial = []
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []

# Nombres de archivos de imágenes en el repositorio
IMAGE_LOGO = "Logo anotIA.png"
IMAGE_GRAFICOS = "grafico.png"

# =========================================================
# ESTILOS CSS TEMA CLARO: "EDUCATIVO & DINÁMICO" (#F8FAFC)
# =========================================================
st.markdown("""
<style>
    /* 1. Fondo general de la App (#F8FAFC) */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    /* 2. Títulos y Encabezados */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 800 !important;
    }

    /* 3. Subtítulo Banner superior (Tarjeta limpia blanca) */
    .sub-title {
        color: #1E293B !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
        background-color: #FFFFFF;
        padding: 10px 20px;
        border-radius: 10px;
        display: inline-block;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* 4. Insignia / Badge Superior */
    .badge-tag {
        background-color: #4F46E5;
        color: #FFFFFF;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 12px;
    }

    /* 5. Tarjetas contenedoras de columnas (#FFFFFF con sombra suave) */
    div[data-testid="stColumn"] {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
    }

    /* 6. Sidebar en Azul Slate Oscuro (#0F172A) */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {
        color: #F8FAFC !important;
    }

    /* Tarjeta informativa dentro del Sidebar */
    .sidebar-info-box {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 14px;
        border-left: 4px solid #4F46E5;
        color: #334155;
        font-size: 0.9rem;
        line-height: 1.4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    /* 7. Zona de Carga PDF (Drag & Drop) */
    .stFileUploader section {
        background-color: #1E293B !important;
        border: 2px dashed #475569 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    .stFileUploader section div, .stFileUploader section span {
        color: #CBD5E1 !important;
    }

    /* 8. Pestañas de navegación superiores (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 4px;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px 8px 0px 0px;
        padding-left: 16px;
        padding-right: 16px;
        background-color: transparent;
        border: none;
        font-weight: 700;
        font-size: 0.95rem;
        color: #64748B !important;
        white-space: nowrap;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EEF2FF !important;
        border-bottom: 3px solid #4F46E5 !important;
        color: #4F46E5 !important;
    }

    /* 9. Botón Principal de Acción (Índigo / Púrpura Vivo #4F46E5) */
    .stButton>button {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.25rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background-color: #4338CA !important;
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35) !important;
        color: #FFFFFF !important;
    }

    /* 10. Entradas de texto y selects */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }
    .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15) !important;
    }
    label {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* 11. Ajustes para Teléfonos Móviles (Responsive) */
    @media (max-width: 768px) {
        .sub-title {
            font-size: 0.95rem !important;
            padding: 8px 14px;
        }
        div[data-testid="stColumn"] {
            padding: 14px;
        }
        .stTabs [data-baseweb="tab"] {
            padding-left: 10px;
            padding-right: 10px;
            font-size: 0.85rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Descripción de la herramienta y ajustes
with st.sidebar:
    st.markdown('<span class="badge-tag">ASISTENTE DOCENTE IA</span>', unsafe_allow_html=True)
    st.subheader("💡 ¿Qué es AnotIA?")
    
    st.markdown("""
    <div class="sidebar-info-box">
        <strong>AnotIA</strong> optimiza el trabajo administrativo docente convirtiendo notas rápidas 
        en redacciones formales, pedagógicas y alineadas al <strong>Reglamento Interno (RICE)</strong> de tu colegio.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📄 Reglamento Interno (RICE)")
    uploaded_rice = st.file_uploader(
        "Subir PDF del RICE / Reglamento (Opcional)",
        type=["pdf"],
        help="Sube el documento PDF del colegio para que la IA cite exactamente la falta y el punto del reglamento."
    )
    if uploaded_rice:
        st.success("✅ RICE cargado correctamente")
    
    st.markdown("---")
    st.subheader("📌 Ajustes del Colegio")
    
    nivel_educativo = st.selectbox(
        "Nivel Educativo",
        ["Educación Parvularia", "Primer Ciclo", "Segundo Ciclo"]
    )
    
    st.markdown("---")
    st.caption("AnotIA v4.0 • Tema Claro Educativo")

# Obtener la API Key exclusivamente de los Secrets del Servidor
api_key_input = st.secrets.get("GEMINI_API_KEY", "")

# Encabezado Principal con Logo
if os.path.exists(IMAGE_LOGO):
    st.image(IMAGE_LOGO, width=280)
else:
    st.markdown("## ✏️ **AnotIA**")

st.markdown('<p class="sub-title"><i>"Menos tiempo redactando, más tiempo enseñando."</i></p>', unsafe_allow_html=True)

# Pestañas Principales (Gráficos Primero)
tab_graficos, tab_generador, tab_historial, tab_favoritos = st.tabs([
    "📊 Gráficos y Modelo Pedagógico", 
    "📝 Generador", 
    "📜 Historial Reciente", 
    "⭐ Favoritos"
])

# ----------------------------------------------------
# PESTAÑA 1: FOTO DE GRÁFICOS / MODELO PEDAGÓGICO
# ----------------------------------------------------
with tab_graficos:
    st.subheader("📈 Esquema Pedagógico y Gráficos de Referencia")
    st.write("Visualización del marco conceptual y flujo metodológico aplicado por AnotIA para el análisis de convivencia y RICE.")
    
    if os.path.exists(IMAGE_GRAFICOS):
        # Despliegue centrado y en tamaño moderado para buena visualización móvil
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image(IMAGE_GRAFICOS, use_container_width=True, caption="Esquema y Referencia Visual del Sistema AnotIA")
    else:
        st.warning(f"⚠️ Guarda la imagen de tus gráficos como `{IMAGE_GRAFICOS}` en GitHub para visualizarla aquí.")

# ----------------------------------------------------
# PESTAÑA 2: GENERADOR PRINCIPAL
# ----------------------------------------------------
with tab_generador:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📋 Datos de la Observación")
        
        tipo_anotacion = st.radio(
            "Tipo de Anotación / Registro",
            ["🌟 Anotación Positiva", "⚠️ Anotación Negativa / Convivencia", "📊 Observación Pedagógica / Informe"],
            horizontal=True
        )
        
        asunto_categoria = st.selectbox(
            "Categoría o Ámbito",
            [
                "Conducta / Clima de Aula",
                "Responsabilidad y Cumplimiento",
                "Rendimiento Académico",
                "Relaciones Interpersonales y Empatía",
                "Asistencia y Puntualidad",
                "Proceso de Aprendizaje",
                "Otro"
            ]
        )
        
        detalles = st.text_area(
            "Hechos u observaciones clave (palabras clave o borrador rápido)",
            height=150,
            placeholder="Ej: Durante la actividad de lenguaje, el alumno interrumpe constantemente a sus compañeros, se niega a realizar la guía y responde de forma desafiante al solicitárselo."
        )

        generar_btn = st.button("🚀 Generar Redacción Profesional", use_container_width=True)

    with col2:
        st.subheader("📄 Propuesta de Redacción y Cita RICE")
        
        if generar_btn:
            if not api_key_input:
                st.error("⚠️ Error del servidor: No se ha configurado la clave GEMINI_API_KEY en los Secrets de la aplicación.")
            elif not detalles.strip():
                st.warning("⚠️ Ingresa al menos unas cuantas palabras clave sobre el hecho observado.")
            else:
                with st.spinner("🤖 AnotIA está analizando la información y redactando con enfoque pedagógico..."):
                    try:
                        client = genai.Client(api_key=api_key_input)
                        contents_payload = []
                        
                        if uploaded_rice:
                            pdf_bytes = uploaded_rice.getvalue()
                            contents_payload.append(
                                types.Part.from_bytes(
                                    data=pdf_bytes,
                                    mime_type="application/pdf"
                                )
                            )
                            instruccion_rice = (
                                "Cuentas con el documento oficial del Reglamento Interno (RICE) adjunto. "
                                "Si la consulta es una 'Anotación Negativa', debes BUSCAR CUIDADOSAMENTE en el texto del PDF e IDENTIFICAR "
                                "el punto exacto (Artículo, Número, Letra, Título, Capítulo o Inciso) donde se tipifica la falta cometida, "
                                "citándolo de forma explícita."
                            )
                        else:
                            instruccion_rice = (
                                "No hay un documento RICE adjunto. Indica 'RICE no adjunto (Verificar artículo en reglamento interno)'."
                            )

                        system_instruction = f"""
                        Eres AnotIA, un experto asistente pedagógico especializado en convivencia escolar, pedagogía y legislación educativa.
                        Tu función es transformar notas sencillas de profesores en registros oficiales e institucionales para el Libro de Clases.

                        REGLA MANDATORIA DE TONO Y ESTILO:
                        - El tono de la escritura DEBE SER SIEMPRE CONSTRUCTIVO, FORMATIVO Y PEDAGÓGICO.
                        - Evita el uso de lenguaje punitivo, acusatorio o peyorativo.
                        - En registros de faltas o conductas negativas, centra la redacción en la descripción objetiva de los hechos, las oportunidades de mejora, la responsabilidad formativa y los compromisos a asumir.

                        Pautas del Establecimiento:
                        - Nivel Educativo: {nivel_educativo}
                        - {instruccion_rice}

                        REGLAS DE ESTRUCTURA OBLIGATORIA DE LA RESPUESTA:

                        1. PRIMERA PARTE (FUNDAMENTO Y TIPIFICACIÓN SEGÚN RICE):
                           - Debe ser MUY BREVE y DIRECTA a los 3 puntos requeridos.
                           - Título exacto: "### 📌 1. Fundamento y Tipificación según RICE"
                           - Solo incluye estas 3 líneas simples:
                             * **Falta / Situación Identificada:** [Descripción técnica y objetiva súper breve]
                             * **Ubicación en RICE (Punto / Artículo / Letra):** [Cita exacta del RICE según PDF, ej. Artículo 12, N°3, Letra b]
                             * **Protocolo Sugerido:** [Pasos resumidos del procedimiento]

                        2. SEGUNDA PARTE (OPCIONES PARA LIBRO DE CLASES):
                           - Presenta 2 opciones de redacción listas para copiar y pegar en el Libro de Clases:
                             * **Opción A (Breve / Directa):** Ideal para libro de clases físico (espacio reducido) o plataformas con límite estricto de caracteres.
                             * **Opción B (Formativa / Descriptiva):** Ideal para libro de clases digital o registros que requieran mayor detalle y contexto formativo.
                           - Ambas opciones deben ser constructivas, neutras y fundamentadas pedagógicamente.
                        """

                        prompt = f"""
                        Analiza la información y genera el resultado en Markdown respetando ESTRICTAMENTE el tono constructivo y el formato breve:

                        ---
                        ### 📌 1. Fundamento y Tipificación según RICE
                        - **Falta / Situación Identificada:** [Texto breve]
                        - **Ubicación en RICE (Punto / Artículo / Letra):** [Texto breve]
                        - **Protocolo Sugerido:** [Texto breve]

                        ---
                        ### 📝 2. Opciones de Redacción para el Libro de Clases (Físico / Digital)

                        #### 🔹 Opción A: Redacción Breve y Directa (Ideal para Libro Físico / Espacio acotado)
                        > [Escribe aquí el texto sintético, constructivo y profesional listo para copiar]

                        #### 🔹 Opción B: Redacción Formativa y Descriptiva (Ideal para Libro Digital)
                        > [Escribe aquí el texto detallado, pedagógico, formativo y formal listo para copiar]
                        ---

                        Datos ingresados por el docente:
                        - Tipo de Registro: {tipo_anotacion}
                        - Categoría: {asunto_categoria}
                        - Hechos descritos: {detalles}
                        """

                        contents_payload.append(prompt)

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents_payload,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.2,
                            )
                        )

                        resultado_texto = response.text
                        st.success("¡Análisis y redacción generados con éxito!")
                        st.markdown(resultado_texto)

                        # Guardar el registro en el historial local
                        registro_nuevo = {
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "tipo": tipo_anotacion,
                            "categoria": asunto_categoria,
                            "entrada": detalles,
                            "resultado": resultado_texto
                        }
                        st.session_state.historial.insert(0, registro_nuevo)

                    except Exception as e:
                        st.error(f"Error al procesar con Gemini: {str(e)}")

        else:
            st.info("👈 Selecciona el tipo de registro, ingresa los detalles y presiona el botón para generar.")

# ----------------------------------------------------
# PESTAÑA 3: HISTORIAL RECIENTE
# ----------------------------------------------------
with tab_historial:
    st.subheader("📜 Historial de Anotaciones de la Sesión")
    st.caption("Conserva las redacciones generadas durante el uso actual de la aplicación.")
    
    if not st.session_state.historial:
        st.info("Aún no has generado anotaciones en esta sesión.")
    else:
        for idx, item in enumerate(st.session_state.historial):
            with st.expander(f"🕒 {item['fecha']} | {item['tipo']} - {item['categoria']}"):
                st.markdown(f"**Borrador ingresado:** {item['entrada']}")
                st.markdown("---")
                st.markdown(item["resultado"])
                
                if st.button(f"⭐ Guardar en Favoritos", key=f"fav_{idx}"):
                    if item not in st.session_state.favoritos:
                        st.session_state.favoritos.append(item)
                        st.success("¡Añadido a tus Favoritos!")
                    else:
                        st.warning("Este registro ya estaba en tus Favoritos.")

# ----------------------------------------------------
# PESTAÑA 4: FAVORITOS GUARDADOS
# ----------------------------------------------------
with tab_favoritos:
    st.subheader("⭐ Mis Plantillas / Registros Favoritos")
    st.caption("Guarda aquí redacciones recurrentes o modelos de respuesta para volver a copiarlos cuando lo necesites.")
    
    if not st.session_state.favoritos:
        st.info("No tienes plantillas o anotaciones en Favoritos. Puedes agregar las que generes desde la pestaña de Historial.")
    else:
        for idx_fav, fav in enumerate(st.session_state.favoritos):
            with st.expander(f"⭐ {fav['tipo']} - {fav['categoria']} ({fav['fecha']})"):
                st.markdown(f"**Borrador original:** {fav['entrada']}")
                st.markdown("---")
                st.markdown(fav["resultado"])
                
                if st.button(f"❌ Quitar de Favoritos", key=f"del_fav_{idx_fav}"):
                    st.session_state.favoritos.pop(idx_fav)
                    st.rerun()