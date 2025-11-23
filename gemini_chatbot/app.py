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
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.sidebar.subheader("🔑 Gemini API Configuration")
    api_key = st.sidebar.text_input(
        "Enter your GEMINI_API_KEY",
        type="password",
        help="Your key is only used in this session and never stored."
    )

if not api_key:
    st.error("❌ No API key found. Please enter it in the sidebar or secrets.toml.")
    st.stop()

client = Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"

# ---------------------------
# 2. UI Config
# ---------------------------
st.set_page_config(page_title="Gloria – AI Chatbot", page_icon="🤖")
st.title("🤖 Gloria – Your Personal AI Assistant")
st.write("Ask anything – coding, ML, PUIT work, advice, research… Gloria is here to help you!")

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
user_input = st.chat_input("Ask Gloria something...")

if user_input:
    # Save and show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build conversation history
    gemini_history = [
        types.Content(
            role=msg["role"],
            parts=[types.Part.from_text(text=msg["content"])]
        )
        for msg in st.session_state.messages
    ]

    # Add a personality instruction for Gloria
    system_instruction = types.Content(
        role="user",
        parts=[types.Part.from_text(
            text=(
                "Your name is Gloria. You are friendly, smart, and helpful. "
                "You assist with coding, machine learning, academic projects, and explanations. "
                "You explain things step-by-step like a tutor. "
                "You speak politely and professionally."
            )
        )]
    )

    # Add this instruction only once at beginning
    if len(gemini_history) == 1:
        gemini_history.insert(0, system_instruction)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Gloria is thinking..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=gemini_history,
                )
                reply = response.text
            except Exception as e:
                reply = f"⚠️ Error: {e}"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------------------------
# 5. Clear Chat
# ---------------------------
if st.button("🧹 Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
