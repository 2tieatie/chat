from typing import List

from langchain_openai import ChatOpenAI

from common.models import LLMResponse, EmbeddingsContext
from config import Config, LLM_MODEL
from db.helpers import search_vectors
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

from utils.embeddings import embed_texts

llm = ChatOpenAI(model=LLM_MODEL, temperature=0.0)

async def ask(query: str, messages: List[AnyMessage]) -> LLMResponse:
    if not messages:
        messages.append(SystemMessage(content=Config.system_prompt))

    context = await _retrieve_context(query)
    human_message = _build_human_message(query, context)
    messages.append(human_message)
    response = await llm.ainvoke(input=messages)
    messages.append(AIMessage(content=response.text))
    return LLMResponse(text=response.content, context=context)

async def _retrieve_context(query: str) -> List[EmbeddingsContext]:
    q_vecs = await embed_texts([query])
    q_vec = q_vecs[0]
    res = await search_vectors(Config.qdrant_collection, vector=q_vec, limit=Config.top_k, with_payload=True)
    context_chunks = []

    for h in res.points:
        payload = h.payload or {}
        text = payload.get("text")
        context_chunks.append(EmbeddingsContext(text=text, chunk_index=payload.get("chunk_index"), filename=payload.get("filename"), score=h.score))

    return context_chunks

def _build_human_message(query: str, context: List[EmbeddingsContext]) -> HumanMessage:
    return HumanMessage(content=f"""
## Task
<clear, 1–3 sentence instruction of what to do>

## Answering Rules
- Use only the Context below.
- If uncertain, say so.
- Cite with [source#N].

## Context
{"\n".join([f'[source#{index}, filename={c.filename}, chunk={c.chunk_index}]{c.text}' for index, c in enumerate(context)])}

## Question
{query}

## Output Format
- Respond in Markdown.
- Start with a 2–3 sentence direct answer.
- Then add details with bullet points and source tags [source#N].
""")