import streamlit as st
from ui import render_sidebar, render_chat_ui
from utils import initialize_session_state

def main():
    initialize_session_state()
    render_sidebar()
    render_chat_ui()

if __name__ == "__main__":
    main()
