import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="Ask AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f7f9fc 0%, #eef3fb 100%); }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 22px;
        background: linear-gradient(120deg, #172554 0%, #4338ca 58%, #7c3aed 100%);
        color: white;
        margin-bottom: 1.25rem;
        box-shadow: 0 12px 30px rgba(49, 46, 129, .16);
    }
    .hero h1 { margin: 0; font-size: 2rem; letter-spacing: -.03em; }
    .hero p { margin: .45rem 0 0 0; color: #e0e7ff; font-size: 1rem; }
    .mini-card {
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1rem;
        background: rgba(255,255,255,.88);
        min-height: 105px;
    }
    .mini-card strong { color: #312e81; }
    div[data-testid="stChatMessage"] {
        background: rgba(255,255,255,.84);
        border: 1px solid #e8edf5;
        border-radius: 16px;
        padding: .85rem 1rem;
        box-shadow: 0 3px 12px rgba(15,23,42,.035);
    }
    .footer { text-align: center; color: #64748b; font-size: .8rem; padding: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ✨ Ask AI")
    st.caption("A simple, friendly AI assistant for your team.")
    st.divider()

    api_key = st.text_input(
        "OpenAI API key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="For local use, set OPENAI_API_KEY in your .env file. For deployment, use Streamlit Secrets.",
    )
    model = st.selectbox(
        "Model",
        options=["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
        index=0,
        help="Choose a model available to your OpenAI API account.",
    )
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    answer_style = st.selectbox(
        "Answer style",
        ["Balanced", "Concise", "Detailed", "Explain for beginners"],
        index=0,
    )
    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Your API key is used by this app to call OpenAI. Never share it publicly.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Main page ----------
st.markdown("""
<div class="hero">
  <h1>What can I help you with?</h1>
  <p>Ask a question, explore an idea, or get help with your work — in plain language.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="mini-card">💡 <strong>Learn something</strong><br><span>Get clear explanations of complex topics.</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="mini-card">✍️ <strong>Write & improve</strong><br><span>Draft emails, summaries, and useful content.</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="mini-card">🧩 <strong>Solve a problem</strong><br><span>Brainstorm options and work through questions.</span></div>', unsafe_allow_html=True)

st.markdown("### Conversation")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "✨"):
        st.markdown(message["content"])

prompt = st.chat_input("Type your question here…")

if prompt:
    if not api_key.strip():
        st.error("Add your OpenAI API key in the sidebar, or configure OPENAI_API_KEY in your .env / Streamlit Secrets.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    style_instructions = {
        "Balanced": "Give a clear, helpful answer with enough detail to be useful.",
        "Concise": "Be concise and lead with the answer. Use bullets when helpful.",
        "Detailed": "Give a thorough, well-structured answer with examples where useful.",
        "Explain for beginners": "Explain in beginner-friendly language, define jargon, and use a simple example.",
    }[answer_style]

    instructions = (
        "You are a helpful, professional AI assistant. "
        + style_instructions
        + " If the request is ambiguous, ask a focused clarifying question. "
        "Use headings and bullet points when they improve readability."
    )

    try:
        client = OpenAI(api_key=api_key.strip())
        # Responses API accepts conversation turns as role/content input items.
        conversation_input = [
            {"role": item["role"], "content": item["content"]}
            for item in st.session_state.messages
        ]
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Thinking…"):
                response = client.responses.create(
                    model=model,
                    instructions=instructions,
                    input=conversation_input,
                    temperature=temperature,
                )
                answer = response.output_text or "I couldn't generate a text response. Please try again."
            st.markdown(answer)
            st.caption(f"Powered by OpenAI · {model}")
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as exc:
        # Avoid printing credentials or environment variables in the UI.
        st.error("The request could not be completed. Check your API key, model access, and network connection, then try again.")
        with st.expander("Technical details"):
            st.code(f"{type(exc).__name__}: {exc}")

st.markdown('<div class="footer">Please verify important information before relying on it. Do not enter passwords or sensitive personal data.</div>', unsafe_allow_html=True)
