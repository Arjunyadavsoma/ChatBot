import streamlit as st
from config import AVAILABLE_MODELS
from api import query_nvidia_llm_stream
import json

import PyPDF2

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None
    return text

def render_sidebar():
    """Render sidebar with settings, tools, and chat history"""
    st.sidebar.title("Settings & Tools")
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")

    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        if text:
            st.session_state['pdf_text'] = text
            st.success("PDF uploaded and text extracted!")
        else:
            st.session_state['pdf_text'] = None
    else:
        st.session_state['pdf_text'] = None

    selected_model = st.sidebar.selectbox("Select Model", options=list(AVAILABLE_MODELS.keys()), key="model")
    st.session_state['selected_model'] = AVAILABLE_MODELS[selected_model]
    st.session_state['max_tokens'] = st.sidebar.slider("Max Tokens", min_value=100, max_value=2000, value=1000, step=100)
    st.session_state['temperature'] = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
    st.session_state['top_p'] = st.sidebar.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.01)

def render_chat_ui():
    """Render chat UI"""
    st.title("NVIDIA AI Interview Assistant")
    st.write("By Arjun Yadav")

    if 'pdf_text' in st.session_state and st.session_state['pdf_text']:
        st.write("You can now ask questions about the uploaded PDF.")
    else:
        st.write("Upload a PDF to start asking questions.")

    conversation_history = st.session_state.get('history', [])

    # Add system prompt at the beginning of the conversation
    if not conversation_history or conversation_history[0]['role'] != 'system':
        st.session_state.history.insert(0, {"role": "system", "content": st.session_state.system_prompt})

    # Display conversation history to the user, skipping the system prompt
    for message in st.session_state.history[1:]:
        with st.chat_message(message['role']):
            st.write(message['content'])

    user_input = st.chat_input("Ask a question")
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Get response from LLM using the full history including system prompt
        response = query_nvidia_llm_stream(
            st.session_state.history,
            st.session_state['selected_model'],
            {"max_tokens": st.session_state['max_tokens'], "temperature": st.session_state['temperature'], "top_p": st.session_state['top_p']}
        )
        full_response = ""
        with st.chat_message("assistant"):
            response_container = st.empty()
            for chunk in response:
                full_response += chunk
                response_container.write(full_response)
        st.session_state.history.append({"role": "assistant", "content": full_response})

    if st.button("Clear Conversation"):
        st.session_state.history = [{"role": "system", "content": st.session_state.system_prompt}]
        st.rerun()
