from dotenv import load_dotenv
import os

load_dotenv()

LLM_URL = os.getenv("LLM_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_REQUEST_TEXT_FIELD = os.getenv("LLM_REQUEST_TEXT_FIELD", "prompt")
LLM_REQUEST_MODEL_FIELD = os.getenv("LLM_REQUEST_MODEL_FIELD", "model")
LLM_RESPONSE_FIELD = os.getenv("LLM_RESPONSE_FIELD", "response")

COMMENTS_SERVICE_URL = os.getenv("COMMENTS_SERVICE_URL")
RESOURCE_SERVICE_URL = os.getenv("RESOURCE_SERVICE_URL")
TOP_MOVIES_LIMIT = int(os.getenv("TOP_MOVIES_LIMIT", "5"))
TOP_MOVIES_PERIOD_SECONDS = int(os.getenv("TOP_MOVIES_PERIOD_SECONDS", "86400"))
TOP_MOVIES_RUN_HOUR = int(os.getenv("TOP_MOVIES_RUN_HOUR", "3"))
TOP_MOVIES_RUN_MINUTE = int(os.getenv("TOP_MOVIES_RUN_MINUTE", "0"))

CHECK_COMMENT_RULES = [
    "Ненависть/дискриминация по признакам (раса, нация, религия, гендер и т.д.)",
    "Призывы к насилию, угрозы, вред себе/другим",
    "Оскорбления, унижения, травля",
    "Сексуальный контент (особенно с участием несовершеннолетних) или чрезмерно непристойный",
    "Спам/реклама/фишинг",
]

CHECK_USER_RULES = [
    "Систематические нарушения правил (повторяемость токсичных комментариев или репортов)",
    "Спам-поведение (много однотипных сообщений или рекламы)",
    "Ненависть/дискриминация по признакам (раса, нация, религия, гендер и т.д.)",
    "Призывы к насилию, угрозы, вред себе/другим",
    "Целенаправленная травля других пользователей",
    "Распространение вредного или опасного контента (фишинг, вредоносные ссылки)",
    "Нарушения в разных контекстах (не разовый случай, а повторяемость)",
]
