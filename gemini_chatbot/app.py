import streamlit as st

# Try to import the new Gemini SDK
try:
    from google.genai import Client, types
except ImportError:
    st.error(
        "The `google-genai` package is not installed.\n\n"
        "Install it with:\n\n"
        "```bash\npip install google-genai\n```"
    )
    st.stop()

# ---------------------------
# 1. Configure API Key
# ---------------------------

# Try to read from Streamlit secrets (best for Streamlit Cloud / local projects)
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# If not found, fall back to a sidebar input (useful in Colab)
if not api_key:
    st.sidebar.subheader("🔑 Gemini API Configuration")
    api_key = st.sidebar.text_input(
        "Enter your GEMINI_API_KEY",
        type="password",
        help="Your key is not stored; it's only used in this session.",
    )

if not api_key:
    st.error("❌ No API key found. Set GEMINI_API_KEY in secrets or paste it in the sidebar.")
    st.stop()

client = Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"

# ---------------------------
# 2. UI Config
# ---------------------------
st.set_page_config(page_title="Kelvin's Gemini Chatbot", page_icon="🤖")
st.title("🤖 Kelvin's Gemini Chatbot")
st.write("Ask your PUIT AI Assistant anything (coding, ML, Android, datasets, etc.).")

# ---------------------------
# 3. Chat Memory
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# 4. User Input
# ---------------------------
user_input = st.chat_input("Ask me something...")

if user_input:
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build Gemini conversation history
    gemini_history = [
        types.Content(
            role=msg["role"],
            parts=[types.Part.from_text(text=msg["content"])]
        )
        for msg in st.session_state.messages
    ]

    # Optional: add a "persona" instruction as first message
    system_instruction = types.Content(
        role="user",
        parts=[types.Part.from_text(
            text=(
                "You are Kelvin's personal assistant for school (PUIT). "
                "Explain things clearly step by step, and be friendly. "
                "If he asks about code or ML, explain like a tutor."
            )
        )]
    )
    if len(gemini_history) == 1:
        gemini_history.insert(0, system_instruction)

    # Call Gemini
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=gemini_history,
                )
                reply = response.text
            except Exception as e:
                reply = f"⚠️ ERROR talking to Gemini: `{e}`"

        st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------------------------
# 5. Button to Clear Chat
# ---------------------------
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
