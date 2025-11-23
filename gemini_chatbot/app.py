import streamlit as st
from google.genai import Client, types   # ✔ FIXED IMPORT

# ---------------------------
# 1. Configure API Key
# ---------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("❌ GEMINI_API_KEY missing! Create .streamlit/secrets.toml")
    st.stop()

client = Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"

# ---------------------------
# 2. UI Config
# ---------------------------
st.set_page_config(page_title="Kelvin's Gemini Chatbot", page_icon="🤖")
st.title("🤖 Kelvin's Gemini Chatbot")
st.write("Ask your PUIT AI Assistant anything.")

# ---------------------------
# 3. Chat Memory
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# 4. User Input
# ---------------------------
user_input = st.chat_input("Ask me something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    gemini_history = [
        types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["content"])])
        for msg in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=gemini_history,
                )
                reply = response.text
            except Exception as e:
                reply = f"⚠️ ERROR: {e}"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Button to clear
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
