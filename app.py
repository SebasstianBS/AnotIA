"""
AnotIA - Asistente de Redacción de Anotaciones Pedagógicas con RICE e IA
Prototipo MVP construido con Streamlit y la API de Google Gemini (google-genai).
"""

import streamlit as st
import google.genai as genai
from google.genai import types
import os

# Configuración de la página
st.set_page_config(
    page_title="Menos tiempo redactando, más tiempo enseñando",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nombre del archivo de imagen en tu repositorio
IMAGE_FILENAME = "Logo anotIA.png"

# Estilos CSS personalizados
st.markdown("""
<style>
    .sub-title {
        color: #4B5563;
        font-size: 1.25rem;
        font-weight: 500;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Solo opciones pedagógicas para el profesor
with st.sidebar:
    if os.path.exists(IMAGE_FILENAME):
        st.image(IMAGE_FILENAME, width=160)
    else:
        st.image("https://img.icons8.com/illustrations/100/teacher.png", width=80)
        
    st.caption("Menos tiempo redactando, más tiempo enseñando.")
    
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
    st.caption("AnotIA v2.5 • Tono Pedagógico Permanente")

# Obtener la API Key exclusivamente de los Secrets del Servidor
api_key_input = st.secrets.get("GEMINI_API_KEY", "")

# Encabezado Principal: Solo Logo Agrandado y Eslogan
if os.path.exists(IMAGE_FILENAME):
    st.image(IMAGE_FILENAME, width=320)
else:
    st.markdown("## ✏️ **AnotIA**")

st.markdown('<p class="sub-title"><i>"Menos tiempo redactando, más tiempo enseñando."</i></p>', unsafe_allow_html=True)

# Formulario Principal
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

# Procesamiento con Gemini
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

                    st.success("¡Análisis y redacción generados con éxito!")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Error al procesar con Gemini: {str(e)}")

    else:
        st.info("👈 Selecciona el tipo de registro, ingresa los detalles y presiona el botón para generar.")