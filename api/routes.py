from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from agent.rag_agent import answer

router = APIRouter(prefix="/api", tags=["rag"])


class ChatRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query must not be empty")
        if len(v) > 2000:
            raise ValueError("query too long (max 2000 chars)")
        return v


class ChatResponse(BaseModel):
    query: str
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = answer(req.query)
        return ChatResponse(query=req.query, response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
