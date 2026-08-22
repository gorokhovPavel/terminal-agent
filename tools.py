from pathlib import Path

BASE_DIR = Path(__file__).parent
WORKSPACE_DIR = BASE_DIR / "workspace"
NOTES_DIR = BASE_DIR / "notes"


class ToolError(Exception):
    pass


def _safe_path(raw: str, allowed_dir: Path, must_exist: bool = False) -> Path:
    if not raw.endswith(".md"):
        raise ToolError(f"Разрешены только .md файлы, получено: {raw!r}")

    path = (allowed_dir / raw).resolve()

    if not path.is_relative_to(allowed_dir.resolve()):
        raise ToolError(f"Путь выходит за пределы разрешённой папки: {raw!r}")

    if must_exist and not path.exists():
        raise ToolError(f"Файл не найден: {raw!r}")

    return path


def read_markdown_file(path: str) -> dict:
    resolved = _safe_path(path, WORKSPACE_DIR, must_exist=True)
    content = resolved.read_text(encoding="utf-8")
    print(f"[tool] read_markdown_file: {resolved.relative_to(BASE_DIR)}")
    return {"path": path, "content": content}


def write_note(filename: str, content: str) -> dict:
    NOTES_DIR.mkdir(exist_ok=True)
    resolved = _safe_path(filename, NOTES_DIR)
    resolved.write_text(content, encoding="utf-8")
    print(f"[tool] write_note: {resolved.relative_to(BASE_DIR)} ({resolved.stat().st_size} bytes)")
    return {"path": filename, "bytes": resolved.stat().st_size}


def call_tool(name: str, args: dict) -> dict:
    if name == "read_markdown_file":
        return read_markdown_file(args["path"])
    if name == "write_note":
        return write_note(args["filename"], args["content"])
    raise ToolError(f"Неизвестный tool: {name!r}")


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_markdown_file",
            "description": (
                "Читает Markdown-файл из папки workspace/. "
                "Используй когда нужно узнать содержание файла перед ответом или summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Относительный путь к файлу внутри workspace/, например 'lesson.md'.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_note",
            "description": (
                "Создаёт или перезаписывает Markdown-заметку в папке notes/. "
                "Используй когда пользователь просит сохранить summary или заметку."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Имя файла внутри notes/, например 'lesson_summary.md'.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Полный Markdown-текст заметки.",
                    },
                },
                "required": ["filename", "content"],
            },
        },
    },
]
