# Buscar la API Key: primero en la barra lateral, si no, en los Secrets de Streamlit
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/100/teacher.png", width=80)
    st.title("✏️ AnotIA")
    st.caption("Menos tiempo redactando, más tiempo enseñando.")
    
    st.markdown("---")
    
    # Campo opcional por si alguien quiere usar su propia Key
    user_api_key = st.text_input(
        "Clave API personalizada (Opcional)",
        type="password",
        help="Si tienes tu propia clave de Google Gemini, puedes ingresarla aquí."
    )
    
    # Si el usuario no ingresó una Key, usa la que configuraste en los Secrets del servidor
    if user_api_key.strip():
        api_key_input = user_api_key
    else:
        api_key_input = st.secrets.get("GEMINI_API_KEY", "")

    st.markdown("---")
    st.subheader("📄 Reglamento Interno (RICE)")
    # ... (El resto del código de la barra lateral continúa igual)