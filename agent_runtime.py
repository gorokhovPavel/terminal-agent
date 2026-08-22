from __future__ import annotations

import json
import logging
from pathlib import Path

from ai_client import call_model
from agent.tools import TOOL_DEFINITIONS, call_tool, ToolError

log = logging.getLogger(__name__)

MAX_STEPS = 10
SOUL_PATH = Path(__file__).parent / "agent" / "soul.md"


def load_soul() -> str:
    return SOUL_PATH.read_text(encoding="utf-8")


def run_agent(task: str, session_id: str, conversation_history: list) -> dict:
    system_prompt = load_soul()
    conversation_history.append({"role": "user", "content": task})
    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    log.info("agent | session=%s task=%r", session_id, task[:80])

    for step in range(MAX_STEPS):
        message = call_model(messages, tools=TOOL_DEFINITIONS)

        if not message.tool_calls:
            final = message.content or ""
            conversation_history.append({"role": "assistant", "content": final})
            log.info("agent | final answer steps=%d", step + 1)
            return {"text": final, "buttons": ["В главное меню"], "mode": "ai_consultant"}

        assistant_msg = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ],
        }
        messages.append(assistant_msg)
        conversation_history.append(assistant_msg)

        for tc in message.tool_calls:
            name = tc.function.name
            log.info("agent | tool=%s session=%s", name, session_id)
            try:
                args = json.loads(tc.function.arguments)
                result = call_tool(name, args, session_id=session_id)

                # Если черновик — возвращаем пользователю на подтверждение
                if name == "prepare_lead_draft":
                    draft_text = result["draft"]
                    result_content = json.dumps(result, ensure_ascii=False)
                    tool_msg = {"role": "tool", "tool_call_id": tc.id, "content": result_content}
                    messages.append(tool_msg)
                    conversation_history.append(tool_msg)

                    confirm_text = (
                        f"Вот черновик вашей заявки:\n\n{draft_text}\n"
                        "Отправить заявку?"
                    )
                    conversation_history.append({"role": "assistant", "content": confirm_text})
                    return {
                        "text": confirm_text,
                        "buttons": ["Да, отправить", "Изменить", "Отмена"],
                        "mode": "ai_consultant",
                        "pending_draft": result,
                    }

            except ToolError as e:
                result_content = f"Отказ: {e}"
                log.warning("agent | tool refused: %s", e)
            except Exception as e:
                result_content = f"Ошибка: {e}"
                log.error("agent | tool error: %s", e)
            else:
                result_content = json.dumps(result, ensure_ascii=False)

            tool_msg = {"role": "tool", "tool_call_id": tc.id, "content": result_content}
            messages.append(tool_msg)
            conversation_history.append(tool_msg)

    return {
        "text": f"Достигнут лимит шагов ({MAX_STEPS}). Попробуйте переформулировать вопрос.",
        "buttons": ["В главное меню"],
        "mode": "ai_consultant",
    }
