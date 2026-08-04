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

# Nombre del archivo de imagen en el repositorio
IMAGE_FILENAME = "Logo anotIA.png"

# =========================================================
# ESTILOS CSS PERSONALIZADOS (DISEÑO Y COLORES)
# =========================================================
st.markdown("""
<style>
    /* Fondo general suave */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Subtítulo principal */
    .sub-title {
        color: #475569;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
    }
    
    /* Estilo del botón principal */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: #FFFFFF;
        font-weight: 700;
        font-size: 1.05rem;
        border-radius: 10px;
        padding: 0.65rem 1.25rem;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.25);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        box-shadow: 0 6px 12px -2px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
        color: #FFFFFF;
    }
    
    /* Pestañas personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        padding-left: 16px;
        padding-right: 16px;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        font-weight: 600;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EFF6FF !important;
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
    }

    /* Personalización del Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Descripción de la herramienta y ajustes
with st.sidebar:
    st.subheader("💡 ¿Qué es AnotIA?")
    st.info(
        "AnotIA es un asistente inteligente diseñado para optimizar el trabajo administrativo docente. "
        "Transforma observaciones y notas rápidas de aula en redacciones formales, pedagógicas e institucionales, "
        "alineadas al Reglamento Interno de Convivencia Escolar (RICE) de tu establecimiento."
    )
    
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
    st.caption("AnotIA Beta v0.2 • Tono Pedagógico Permanente")

# Obtener la API Key exclusivamente de los Secrets del Servidor
api_key_input = st.secrets.get("GEMINI_API_KEY", "")

# Encabezado Principal
if os.path.exists(IMAGE_FILENAME):
    st.image(IMAGE_FILENAME, width=320)
else:
    st.markdown("## ✏️ **AnotIA**")

st.markdown('<p class="sub-title"><i>"Menos tiempo redactando, más tiempo enseñando."</i></p>', unsafe_allow_html=True)

# Sistema de pestañas principales
tab_generador, tab_historial, tab_favoritos = st.tabs(["📝 Generador", "📜 Historial Reciente", "⭐ Favoritos Guardados"])

# ----------------------------------------------------
# PESTAÑA 1: GENERADOR
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
            height=160,
            placeholder="Ej: Durante la actividad de lenguaje, el alumno interrumpe constantemente a sus compañeros, se niega a realizar la guía y responde de forma desafiante al solicitárselo."
        )

        generar_btn = st.button("✨ Generar Redacción Profesional", use_container_width=True)

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
# PESTAÑA 2: HISTORIAL RECIENTE
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
                
                # Botón para guardar en Favoritos
                if st.button(f"⭐ Guardar en Favoritos", key=f"fav_{idx}"):
                    if item not in st.session_state.favoritos:
                        st.session_state.favoritos.append(item)
                        st.success("¡Añadido a tus Favoritos!")
                    else:
                        st.warning("Este registro ya estaba en tus Favoritos.")

# ----------------------------------------------------
# PESTAÑA 3: FAVORITOS GUARDADOS
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