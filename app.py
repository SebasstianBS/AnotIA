"""
AnotIA - Asistente de Redacción de Anotaciones Pedagógicas con RICE e IA
Prototipo MVP construido con Streamlit y la API de Google Gemini (google-genai).
Estilo Minimalista SaaS (Notion AI / Linear / OpenAI)
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

# Inicialización de historial, favoritos y mensajes del chat en st.session_state
if "historial" not in st.session_state:
    st.session_state.historial = []
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "¡Hola! 👋 Soy tu **Asistente de Orientación Pedagógica y Convivencia Escolar**.\n\n"
                "📌 **Mi rol exclusivo:** Orientarte en **estrategias de aula, pautas para entrevistas con apoderados, mediación y aplicación del RICE**.\n\n"
                "💡 *Nota:* Si buscas redactar la anotación formal lista para copiar al Libro de Clases, te sugiero usar la pestaña **📝 Generador (Registro Oficial)**."
            )
        }
    ]

# Nombres de archivos de imágenes en el repositorio
IMAGE_LOGO = "Logo anotIA.png"
IMAGE_GRAFICOS = "grafico.png"

# =========================================================
# ESTILOS CSS - ESTILO SAAS MODERNO CON CHAT DE ALTO CONTRASTE
# =========================================================
st.markdown("""
<style>
    /* 1. Fondo General con Gradiente Radial Tecnológico */
    .stApp {
        background: radial-gradient(circle at top right, rgba(109, 93, 246, 0.12), transparent 30%), #FAFBFF !important;
        color: #1F2937 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* 2. Encabezados y Tipografía General */
    h1, h2, h3, h4, h5, h6 {
        color: #1F2937 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    p, span, label, div, li {
        color: #1F2937;
    }

    /* 3. Logo con estilo tipográfico SaaS */
    .logo-container {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .logo-anot {
        color: #1F2937;
    }
    .logo-ia {
        background: linear-gradient(135deg, #6D5DF6 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 4. Subtítulo Banner Superior */
    .sub-title {
        color: #6B7280 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        margin-top: 0rem;
        margin-bottom: 1.5rem;
    }

    /* 5. Insignia / Badge Superior */
    .badge-tag {
        background: rgba(109, 93, 246, 0.1);
        color: #6D5DF6 !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        display: inline-block;
        margin-bottom: 12px;
        border: 1px solid rgba(109, 93, 246, 0.2);
    }

    /* 6. Tarjetas Clean (#FFFFFF, Bordes #E5E7EB, Sombra Suave) */
    div[data-testid="stColumn"] {
        background-color: #FFFFFF !important;
        padding: 24px !important;
        border-radius: 18px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 16px;
    }

    /* 7. Sidebar Oscuro (#111827) */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4, 
    section[data-testid="stSidebar"] h5, 
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stCaption {
        color: #9CA3AF !important;
    }

    /* Tarjeta Informativa dentro del Sidebar */
    .sidebar-info-box {
        background-color: #1F2937;
        border-radius: 12px;
        padding: 14px;
        border: 1px solid #374151;
        color: #E5E7EB !important;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    .sidebar-info-box strong {
        color: #8B5CF6 !important;
    }

    /* 8. Carga de Archivos RICE (PDF Uploader) */
    .stFileUploader section {
        background-color: #1F2937 !important;
        border: 2px dashed #374151 !important;
        border-radius: 12px !important;
        padding: 14px !important;
    }
    .stFileUploader section div, 
    .stFileUploader section span, 
    .stFileUploader section small,
    .stFileUploader section p {
        color: #9CA3AF !important;
        font-weight: 500 !important;
    }

    /* 9. Pestañas de Navegación (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 4px;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 10px;
        padding-left: 18px;
        padding-right: 18px;
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        font-weight: 600;
        font-size: 0.9rem;
        color: #6B7280 !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6D5DF6 !important;
        border-color: #6D5DF6 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(109, 93, 246, 0.3) !important;
    }

    /* 10. Botón Principal */
    .stButton>button {
        background: linear-gradient(90deg, #6D5DF6 0%, #3B82F6 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(109, 93, 246, 0.25) !important;
        transition: all 0.25s ease-in-out !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #7C6CFF 0%, #408AF8 100%) !important;
        box-shadow: 0 10px 30px rgba(109, 93, 246, 0.35) !important;
        transform: translateY(-1px);
        color: #FFFFFF !important;
    }

    /* 11. Entradas de Texto y Selects General */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border-radius: 12px !important;
        border: 1px solid #D1D5DB !important;
    }
    .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #6D5DF6 !important;
        box-shadow: 0 0 0 4px rgba(109, 93, 246, 0.18) !important;
    }
    label {
        color: #1F2937 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    /* 12. AJUSTES EXCLUSIVOS DE CHAT */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
    }

    /* Mensajes del usuario (Profesor) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #111827 !important;
        border-color: #1F2937 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) div,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) span {
        color: #FFFFFF !important;
    }

    /* Campo de entrada de texto del Chat */
    [data-testid="stChatInput"] {
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6B7280 !important;
    }

    /* Tarjetas sugeridas de orientación */
    .guide-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .guide-card h5 {
        margin: 0 0 4px 0 !important;
        font-size: 0.95rem !important;
        color: #6D5DF6 !important;
    }
    .guide-card p {
        margin: 0 !important;
        font-size: 0.85rem !important;
        color: #6B7280 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Estilo Dark SaaS
with st.sidebar:
    st.markdown("""
    <div class="logo-container" style="margin-bottom: 12px;">
        <span class="logo-anot" style="color: #FFFFFF;">anot</span><span class="logo-ia">IA</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<span class="badge-tag">ASISTENTE DOCENTE IA</span>', unsafe_allow_html=True)
    st.subheader("💡 ¿Qué es AnotIA?")
    
    st.markdown("""
    <div class="sidebar-info-box">
        <strong>AnotIA</strong> es la plataforma integral para optimizar la labor docente:<br><br>
        • <strong>📝 Generador:</strong> Para redacción de registros oficiales del Libro de Clases.<br>
        • <strong>💬 Orientación:</strong> Asistente conversacional de estrategia y convivencia escolar.
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
    st.caption("AnotIA v6.4 • Integración Cita RICE")

# Obtener la API Key exclusivamente de los Secrets del Servidor
api_key_input = st.secrets.get("GEMINI_API_KEY", "")

# Encabezado Principal
if os.path.exists(IMAGE_LOGO):
    st.image(IMAGE_LOGO, width=240)
else:
    st.markdown("""
    <div class="logo-container">
        <span class="logo-anot">anot</span><span class="logo-ia">IA</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p class="sub-title"><i>Menos escritura. Más tiempo para enseñar.</i></p>', unsafe_allow_html=True)

# Pestañas Principales (Gráficos van primero)
tab_graficos, tab_generador, tab_chat, tab_historial, tab_favoritos = st.tabs([
    "📊 Estadísticas y Modelo", 
    "📝 Generador (Registro Oficial)", 
    "💬 Asistente de Orientación",
    "📜 Historial", 
    "⭐ Favoritos"
])

# ----------------------------------------------------
# PESTAÑA 1: FOTO DE GRÁFICOS / MODELO PEDAGÓGICO
# ----------------------------------------------------
with tab_graficos:
    st.subheader("📈 Esquema Pedagógico y Gráficos de Referencia")
    st.write("Visualización del marco conceptual y flujo metodológico aplicado por AnotIA para el análisis de convivencia y RICE.")
    
    if os.path.exists(IMAGE_GRAFICOS):
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image(IMAGE_GRAFICOS, use_container_width=True, caption="Esquema y Referencia Visual del Sistema AnotIA")
    else:
        st.warning(f"⚠️ Guarda la imagen de tus gráficos como `{IMAGE_GRAFICOS}` en GitHub para visualizarla aquí.")

# ----------------------------------------------------
# PESTAÑA 2: GENERADOR PRINCIPAL (REGISTRO OFICIAL)
# ----------------------------------------------------
with tab_generador:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📋 Datos de la Observación")
        st.caption("Transforma apuntes rápidos en redacciones estructuradas para el Libro de Clases.")
        
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

        generar_btn = st.button("✨ Generar Redacción Oficial", use_container_width=True)

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
                                "citándolo de forma explícita e INTEGRÁNDOLO directamente en la redacción de cada opción para el Libro de Clases."
                            )
                        else:
                            instruccion_rice = (
                                "No hay un documento RICE adjunto. En la cita del RICE e integrada en cada opción de redacción, indica '(Referencia RICE: Verificar artículo/punto en reglamento interno del establecimiento)'."
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
                             * **Ubicación en RICE (Punto / Artículo / Letra):** [Cita exacta del RICE según PDF o nota genérica si no hay PDF]
                             * **Protocolo Sugerido:** [Pasos resumidos del procedimiento]

                        2. SEGUNDA PARTE (OPCIONES PARA LIBRO DE CLASES CON CITA RICE INTEGRADA):
                           - Presenta 2 opciones de redacción listas para copiar y pegar en el Libro de Clases.
                           - OBLIGATORIO: Ambas opciones DEBEN INCLUIR DENTRO DEL TEXTO REDACTADO la referencia/cita del punto exacto del RICE (ej. "[Según RICE Art. 14, N° 2, Letra b]").
                             * **Opción A (Breve / Directa):** Ideal para libro de clases físico (espacio reducido) o plataformas con límite estricto de caracteres. Incluye la cita RICE de forma sintética al final o al inicio del texto.
                             * **Opción B (Formativa / Descriptiva):** Ideal para libro de clases digital. Incluye la cita RICE contextualizada dentro del cuerpo del texto formativo.
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
                        > [Escribe aquí el texto sintético, constructivo y profesional listo para copiar, INCLUYENDO la cita o referencia explícita del punto del RICE]

                        #### 🔹 Opción B: Redacción Formativa y Descriptiva (Ideal para Libro Digital)
                        > [Escribe aquí el texto detallado, pedagógico, formativo y formal listo para copiar, INCLUYENDO la cita o referencia explícita del punto del RICE]
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
# PESTAÑA 3: CHAT ASISTENTE (ORIENTACIÓN Y ESTRATEGIA)
# ----------------------------------------------------
with tab_chat:
    st.subheader("💬 Asistente de Orientación y Convivencia Escolar")
    st.caption("Obtén asesoría estratégica, guiones para apoderados y resolución de dudas pedagógicas.")

    # Tarjetas de rol
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.markdown("""
        <div class="guide-card">
            <h5>🎯 Estrategias de Aula</h5>
            <p>Pregunta por acciones preventivas o manejo de conductas disruptivas específicas.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_g2:
        st.markdown("""
        <div class="guide-card">
            <h5>🗣️ Guiones de Entrevista</h5>
            <p>Pide pautas formativas para abordar temas delicados con apoderados o estudiantes.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_g3:
        st.markdown("""
        <div class="guide-card">
            <h5>📖 Asesoría RICE</h5>
            <p>Resuelve dudas sobre protocolos de convivencia y conductos regulares.</p>
        </div>
        """, unsafe_allow_html=True)

    # Botones de sugerencias de un solo clic (Prompt Starters)
    st.write("💡 **Consultas frecuentes de orientación:**")
    col_s1, col_s2, col_s3 = st.columns(3)

    if col_s1.button("👉 Estrategia para alumno disruptivo"):
        st.session_state.chat_messages.append({
            "role": "user", 
            "content": "¿Qué estrategia formativa de aula puedo aplicar con un estudiante que interrumpe constantemente la clase?"
        })
        st.rerun()

    if col_s2.button("👉 Guión para entrevista con apoderado"):
        st.session_state.chat_messages.append({
            "role": "user", 
            "content": "¿Cómo puedo estructurar una reunión con un apoderado para informarle sobre faltas de respeto recurrentes sin generar conflicto?"
        })
        st.rerun()

    if col_s3.button("👉 Paso a paso ante falta grave (RICE)"):
        st.session_state.chat_messages.append({
            "role": "user", 
            "content": "¿Cuál es el procedimiento o conducto regular habitual según el RICE ante una agresión verbal entre estudiantes?"
        })
        st.rerun()

    st.markdown("---")

    # Renderizar historial de mensajes del chat
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de texto del chat
    if prompt_chat := st.chat_input("Escribe tu consulta sobre estrategias de aula, apoderados o RICE..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt_chat})
        with st.chat_message("user"):
            st.markdown(prompt_chat)

        # Generar respuesta de la IA con restricciones de dominio estricta
        with st.chat_message("assistant"):
            if not api_key_input:
                st.error("⚠️ Configura la clave GEMINI_API_KEY en los Secrets de la aplicación.")
            else:
                with st.spinner("Consultando marco de orientación pedagógica..."):
                    try:
                        client = genai.Client(api_key=api_key_input)
                        
                        system_chat = f"""
                        Eres el Asistente de Orientación Pedagógica y Convivencia Escolar de AnotIA (Chile).

                        REGLA DE DOMINIO Y RESTRICCIÓN DE ÁMBITO (MANDATORIA):
                        - Tu ÚNICO campo de actuación es la pedagogía, convivencia escolar, RICE, estrategias de aula y gestión con apoderados/estudiantes.
                        - SI EL USUARIO HACE PREGUNTAS AJENAS A ESTOS TEMAS (ej. recetas de cocina, cultura general, programación general, opiniones personales, noticias, deportes, entretenimiento, etc.):
                          1. NO intentes responder la consulta ajena.
                          2. Declina amablemente la solicitud recordando tu propósito.
                          3. Redirige al docente hacia cómo puedes ayudarle en el ámbito educativo.

                        Ejemplo de respuesta cuando la consulta está fuera de ámbito:
                        "Como asistente de AnotIA, estoy especializado exclusivamente en orientación pedagógica, convivencia escolar y RICE. ¿Hay alguna duda sobre estrategias de aula, entrevistas con apoderados o gestión de convivencia en la que te pueda orientar hoy?"

                        Pautas de contexto:
                        - Nivel Educativo configurado: {nivel_educativo}.
                        - Si el docente solicita redactar una anotación formal final para el libro de clases, recuérdale que la pestaña '📝 Generador (Registro Oficial)' está diseñada específicamente para esa función.
                        """
                        
                        response_chat = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_chat,
                            config=types.GenerateContentConfig(
                                system_instruction=system_chat,
                                temperature=0.1
                            )
                        )
                        
                        st.markdown(response_chat.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response_chat.text})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# ----------------------------------------------------
# PESTAÑA 4: HISTORIAL RECIENTE
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
# PESTAÑA 5: FAVORITOS GUARDADOS
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