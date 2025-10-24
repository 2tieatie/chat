from fastapi import APIRouter, Depends, HTTPException, Body

from app.api.models import QueryPayload, Chat
from chat.ask import ask
from common.models import LLMResponse
from config import Config, logger

router = APIRouter(prefix="/chat", tags=["chat"])

chat = Chat(user_id=None, messages=[])


async def get_payload(payload: QueryPayload = Body(...)) -> QueryPayload:
    return payload


async def get_user_id_from_body(payload: QueryPayload = Depends(get_payload)) -> str:
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    if chat.user_id and chat.user_id != payload.user_id:
        logger.info(
            f"Switching user: {chat.user_id} -> {payload.user_id}. Clearing chat history."
        )
        chat.messages.clear()

    chat.user_id = payload.user_id
    return payload.user_id


async def get_body_message(payload: QueryPayload = Depends(get_payload)) -> str:
    if not payload.message:
        raise HTTPException(status_code=400, detail="message is required")

    if len(payload.message) > Config.max_message_length:
        raise HTTPException(
            status_code=400,
            detail=f"message is too long, make it less than {Config.max_message_length} characters",
        )
    return payload.message


@router.post("/", response_model=LLMResponse)
async def handle_new_query(
    user_id: str = Depends(get_user_id_from_body),
    message: str = Depends(get_body_message),
):
    logger.info(f"[{user_id}] User message: {message}")
    chat.messages.append({"role": "user", "content": message})

    response = await ask(query=message, messages=chat.messages)

    ai_text = (
        response.text
        if hasattr(response, "text")
        else response.model_dump().get("text")
    )

    logger.info(f"[{user_id}] AI answer: {ai_text}")
    chat.messages.append({"role": "assistant", "content": ai_text})

    return response.model_dump()
