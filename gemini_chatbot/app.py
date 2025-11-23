import streamlit as st
from google import genai
from google.genai import types

# ---------------------------
# 1. Configure Gemini client
# ---------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    st.error("❌ No GEMINI_API_KEY found in .streamlit/secrets.toml")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"  # you can change to "gemini-2.0-flash-001" if needed

# ---------------------------
# 2. Streamlit page config
# ---------------------------
st.set_page_config(page_title="Kelvin's Gemini Chatbot", page_icon="🤖")

st.title("🤖 Kelvin's Gemini Chatbot")
st.write("Chat with your personal AI assistant powered by Google Gemini.")

# ---------------------------
# 3. Session state for chat
# ---------------------------
if "messages" not in st.session_state:
    # We'll store messages as a list of {"role": "user"/"assistant", "content": "..."}
    st.session_state.messages = []

# Show previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# 4. Chat input
# ---------------------------
user_input = st.chat_input("Ask me anything...")

if user_input:
    # 4.1 Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 4.2 Build Gemini conversation history
    gemini_history = []
    for m in st.session_state.messages:
        if m["role"] == "user":
            role = "user"
        else:
            role = "model"  # assistant -> model for Gemini

        gemini_history.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=m["content"])]
            )
        )

    # 4.3 Call Gemini API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=gemini_history,
                )
                bot_reply = response.text
            except Exception as e:
                bot_reply = f"⚠️ Error talking to Gemini: `{e}`"

        st.markdown(bot_reply)

    # 4.4 Save bot reply to history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# ---------------------------
# 5. Optional: Clear chat
# ---------------------------
if st.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()
