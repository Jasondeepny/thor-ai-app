from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    role: str
    model: str
