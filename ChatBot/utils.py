import uuid
import logging
import json
from datetime import datetime
import streamlit as st
from config import DEFAULT_SYSTEM_PROMPT


# Logger setup
logger = logging.getLogger("nvidia_assistant")
logger.setLevel(logging.INFO)

def handle_error(error_message, exception=None):
    """Handle error logging."""
    logger.error(f"{error_message}: {str(exception)}" if exception else error_message)

def initialize_session_state():
    """Initialize session state variables"""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

def log_event(event_type, metadata=None):
    """Log events for analytics"""
    event = {
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    logger.info(f"EVENT: {json.dumps(event)}")

def get_themed_color(light_color, dark_color):
    """Return color based on the current theme"""
    return dark_color if st.session_state.get('theme') == "dark" else light_color
