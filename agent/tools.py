from __future__ import annotations

from pathlib import Path

from db import save_lead

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


class ToolError(Exception):
    pass


def _safe_knowledge_path(filename: str) -> Path:
    if not filename.endswith(".md"):
        raise ToolError(f"Разрешены только .md файлы: {filename!r}")
    path = (KNOWLEDGE_DIR / filename).resolve()
    if not path.is_relative_to(KNOWLEDGE_DIR.resolve()):
        raise ToolError(f"Путь выходит за пределы knowledge/: {filename!r}")
    if not path.exists():
        raise ToolError(f"Файл не найден: {filename!r}")
    return path


def search_knowledge(query: str) -> dict:
    query_lower = query.lower()
    results = []
    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        matched = [ln for ln in lines if query_lower in ln.lower()]
        if matched:
            results.append({
                "file": md_file.name,
                "matches": matched[:5],
            })
    if not results:
        return {"found": False, "query": query, "results": []}
    return {"found": True, "query": query, "results": results}


def read_knowledge_file(filename: str) -> dict:
    path = _safe_knowledge_path(filename)
    content = path.read_text(encoding="utf-8")
    return {"filename": filename, "content": content}


def prepare_lead_draft(
    service: str,
    contact: str,
    problem_text: str,
    missing_info: str = "",
) -> dict:
    draft = (
        f"Услуга: {service}\n"
        f"Контакт: {contact}\n"
        f"Запрос: {problem_text}\n"
    )
    if missing_info:
        draft += f"Не хватает: {missing_info}\n"
    return {
        "draft": draft,
        "service": service,
        "contact": contact,
        "problem_text": problem_text,
        "missing_info": missing_info,
    }


def save_confirmed_lead(
    session_id: str,
    service: str,
    contact: str,
    problem_text: str,
    agent_summary: str = "",
    missing_info: str = "",
) -> dict:
    lead_id = save_lead(
        session_id=session_id,
        source="ai_consultant",
        service=service,
        contact=contact,
        problem_text=problem_text,
        agent_summary=agent_summary,
        missing_info=missing_info,
    )
    return {"saved": True, "lead_id": lead_id}


def call_tool(name: str, args: dict, session_id: str = "") -> dict:
    if name == "search_knowledge":
        return search_knowledge(args["query"])
    if name == "read_knowledge_file":
        return read_knowledge_file(args["filename"])
    if name == "prepare_lead_draft":
        return prepare_lead_draft(
            args["service"], args["contact"],
            args["problem_text"], args.get("missing_info", ""),
        )
    if name == "save_confirmed_lead":
        return save_confirmed_lead(
            session_id,
            args["service"], args["contact"],
            args["problem_text"],
            args.get("agent_summary", ""), args.get("missing_info", ""),
        )
    raise ToolError(f"Неизвестный tool: {name!r}")


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Ищет по базе знаний GuitarSpace. Используй для поиска информации об услугах, ценах, правилах и FAQ.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Поисковый запрос на русском языке"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_knowledge_file",
            "description": "Читает конкретный файл из базы знаний. Доступны: services.md, faq.md, rules.md.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Имя файла, например 'services.md'"},
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_lead_draft",
            "description": "Готовит черновик заявки для показа пользователю. Не сохраняет в базу данных.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service":      {"type": "string", "description": "Выбранная услуга"},
                    "contact":      {"type": "string", "description": "Контакт пользователя"},
                    "problem_text": {"type": "string", "description": "Запрос или описание задачи"},
                    "missing_info": {"type": "string", "description": "Что ещё нужно уточнить (если есть)"},
                },
                "required": ["service", "contact", "problem_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_confirmed_lead",
            "description": "Сохраняет заявку в базу данных. Вызывай ТОЛЬКО после явного подтверждения пользователя.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service":       {"type": "string"},
                    "contact":       {"type": "string"},
                    "problem_text":  {"type": "string"},
                    "agent_summary": {"type": "string", "description": "Краткое резюме консультации"},
                    "missing_info":  {"type": "string", "description": "Что осталось невыясненным"},
                },
                "required": ["service", "contact", "problem_text"],
            },
        },
    },
]
