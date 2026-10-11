
import os
import streamlit as st
from groq import Groq

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

MODEL_NAME = "openai/gpt-oss-120b"

# --------------------------------------------------
# Custom CSS: Highlight the chat input box
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Highlight the chat text box */
    div[data-testid="stChatInput"] {
        border: 2px solid #4F8BF9 !important;
        border-radius: 14px !important;
        box-shadow: 0 0 10px rgba(79, 139, 249, 0.30);
        background-color: #F5F9FF !important;
        padding: 3px;
    }

    div[data-testid="stChatInput"]:focus-within {
        border: 2px solid #1769FF !important;
        box-shadow: 0 0 14px rgba(23, 105, 255, 0.45);
    }

    div[data-testid="stChatInput"] textarea {
        color: #172033 !important;
        font-size: 16px !important;
    }

    /* Header styling */
    .main-title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 6px;
    }

    .subtitle {
        text-align: center;
        color: #777777;
        margin-bottom: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Read Groq API key securely
# Priority: Streamlit Secrets, then environment variable
# --------------------------------------------------
api_key = None

try:
    api_key = st.secrets.get("GROQ_API_KEY")
except Exception:
    pass

api_key = api_key or os.environ.get("GROQ_API_KEY")

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🤖 My AI Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ask anything and get an AI-powered answer.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    st.write("**AI Provider:** Groq")
    st.write(f"**Model:** `{MODEL_NAME}`")

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower values give more focused answers."
    )

    max_tokens = st.select_slider(
        "Response length",
        options=[250, 500, 1000, 2000],
        value=1000
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Groq")

# --------------------------------------------------
# Check API key without displaying it
# --------------------------------------------------
if not api_key:
    st.warning("The chatbot is not configured yet.")

    st.markdown(
        """
        To enable the chatbot, add your Groq API key
        to Streamlit Secrets or set the `GROQ_API_KEY`
        environment variable.

        The API key is kept out of the webpage.
        """
    )

    st.stop()

# Initialize Groq client
try:
    client = Groq(api_key=api_key)
except Exception:
    st.error("Unable to initialize the AI client. Check your configuration.")
    st.stop()

# --------------------------------------------------
# Initialize chat history
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# Display previous messages
# --------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------------------------
# Chat input
# --------------------------------------------------
prompt = st.chat_input("✨ Type your question here...")

if prompt:
    # Save and display the user's message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare conversation history
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Give clear, accurate, friendly answers "
                "in simple language when appropriate."
            )
        }
    ]

    messages.extend(st.session_state.messages)

    # Generate response using Groq
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "The AI returned an empty response."

            st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as error:
            error_text = str(error).lower()

            if "429" in error_text or "rate_limit" in error_text:
                st.error(
                    "Groq rate limit reached. Please wait and try again."
                )
            elif (
                "401" in error_text
                or "authentication" in error_text
                or "invalid_api_key" in error_text
            ):
                st.error(
                    "Groq authentication failed. "
                    "Check the API key in your server settings."
                )
            elif (
                "insufficient_quota" in error_text
                or "billing" in error_text
            ):
                st.error(
                    "The API account may have insufficient quota. "
                    "Check your Groq account limits."
                )
            else:
                st.error(
                    "Unable to get a response. "
                    "Please try again later."
                )
