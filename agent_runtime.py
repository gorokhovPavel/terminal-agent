import json
from ai_client import call_model
from tools import TOOL_DEFINITIONS, call_tool, ToolError

MAX_STEPS = 10


def run_agent(task: str, system_prompt: str, conversation_history: list) -> str:
    # Шаг 1: добавляем задачу пользователя в историю
    conversation_history.append({"role": "user", "content": task})
    print(f"\n[agent] task: {task}")

    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    for step in range(MAX_STEPS):
        # Шаг 2: вызываем модель со списком tools
        message = call_model(messages, tools=TOOL_DEFINITIONS)

        # Шаг 3: проверяем наличие tool_calls
        if not message.tool_calls:
            # Шаг 6: финальный ответ — модель не выбрала tool
            final = message.content or ""
            conversation_history.append({"role": "assistant", "content": final})
            print(f"[agent] final answer (steps used: {step + 1})")
            return final

        # Сохраняем assistant-сообщение с tool_calls в историю
        assistant_msg = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        }
        messages.append(assistant_msg)
        conversation_history.append(assistant_msg)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            print(f"[agent] tool selected: {name}")

            try:
                args = json.loads(tool_call.function.arguments)
                # Шаг 4: выполняем разрешённый Python tool
                result = call_tool(name, args)
                result_content = json.dumps(result, ensure_ascii=False)
            except ToolError as e:
                result_content = f"Отказ: {e}"
                print(f"[agent] tool refused: {e}")
            except Exception as e:
                result_content = f"Ошибка выполнения: {e}"
                print(f"[agent] tool error: {e}")

            # Шаг 5: возвращаем результат модели через role: tool
            tool_result_msg = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_content,
            }
            messages.append(tool_result_msg)
            conversation_history.append(tool_result_msg)

    return f"Достигнут лимит шагов ({MAX_STEPS}). Агент остановлен."
