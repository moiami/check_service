from dotenv import load_dotenv
import os

load_dotenv()

LLM_URL = os.getenv("LLM_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_REQUEST_TEXT_FIELD = os.getenv("LLM_REQUEST_TEXT_FIELD", "prompt")
LLM_REQUEST_MODEL_FIELD = os.getenv("LLM_REQUEST_MODEL_FIELD", "model")
LLM_RESPONSE_FIELD = os.getenv("LLM_RESPONSE_FIELD", "response")

COMMENTS_SERVICE_URL = os.getenv("COMMENTS_SERVICE_URL")

CHECK_COMMENT_RULES = [
    "Ненависть/дискриминация по признакам (раса, нация, религия, гендер и т.д.)",
    "Призывы к насилию, угрозы, вред себе/другим",
    "Оскорбления, унижения, травля",
    "Сексуальный контент (особенно с участием несовершеннолетних) или чрезмерно непристойный",
    "Спам/реклама/фишинг",
]
