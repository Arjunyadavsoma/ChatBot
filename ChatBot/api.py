# api.py
import json
import requests
import httpx
from config import API_KEY
from utils import logger, handle_error

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


def validate_api_key():
    """
    Check that the NVIDIA_API_KEY is present and correctly formatted.
    Raises ValueError on failure.
    """
    if not API_KEY:
        raise ValueError("NVIDIA_API_KEY missing; please set it in your .env file.")
    if not API_KEY.startswith("nvapi-"):
        raise ValueError("Invalid NVIDIA_API_KEY; it should start with 'nvapi-'.")
    return True


import streamlit as st

def query_nvidia_llm_stream(messages, model_name, api_settings):
    """
    Stream chat completions from NVIDIA LLM synchronously.
    Yields chunks of content, or logs and stops on error.
    """
    pdf_text = st.session_state.get('pdf_text', None)
    if pdf_text:
        messages.insert(0, {"role": "system", "content": f"Here is the content of the PDF: {pdf_text}"})
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        payload = {
            "model": model_name,
            "max_tokens": api_settings.get("max_tokens"),
            "temperature": api_settings.get("temperature"),
            "top_p": api_settings.get("top_p"),
            "stream": True,
            "messages": messages
        }
        resp = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=60)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                decoded = decoded[len("data: "):]
            if decoded.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(decoded)
                delta = chunk.get("choices", [])[0].get("delta", {})
                content_piece = delta.get("content", "")
                if content_piece:
                    yield content_piece
            except json.JSONDecodeError:
                yield "Error decoding JSON chunk."
                continue
    except requests.exceptions.RequestException as e:
        yield f"Synchronous API request error: {e}"
    except Exception as e:
        yield f"Unexpected synchronous API error: {e}"


async def async_query_nvidia_llm_stream(messages, model_name, api_settings):
    """
    Stream chat completions from NVIDIA LLM asynchronously.
    Yields chunks of content, or logs and stops on error.
    """
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        payload = {
            "model": model_name,
            "max_tokens": api_settings.get("max_tokens"),
            "temperature": api_settings.get("temperature"),
            "top_p": api_settings.get("top_p"),
            "stream": True,
            "messages": messages
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", API_URL, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        line = line[len("data: "):]
                    if line.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line)
                        delta = chunk.get("choices", [])[0].get("delta", {})
                        content_piece = delta.get("content", "")
                        if content_piece:
                            yield content_piece
                    except json.JSONDecodeError:
                        yield "Error decoding JSON chunk."
                        continue
    except Exception as e:
        yield f"Async error querying NVIDIA LLM API: {e}"
