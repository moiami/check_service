from pydantic import BaseModel


class LLMPromptRequest(BaseModel):
    text: str
    model: str | None = None


class LLMPromptResponse(BaseModel):
    text: str
