from dotenv import load_dotenv
import os

load_dotenv()

LLM_URL = os.getenv("LLM_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_REQUEST_TEXT_FIELD = os.getenv("LLM_REQUEST_TEXT_FIELD", "prompt")
LLM_REQUEST_MODEL_FIELD = os.getenv("LLM_REQUEST_MODEL_FIELD", "model")
LLM_RESPONSE_FIELD = os.getenv("LLM_RESPONSE_FIELD", "response")
