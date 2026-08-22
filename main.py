from pathlib import Path
from agent_runtime import run_agent

SOUL_PATH = Path(__file__).parent / "agent" / "soul.md"


def load_soul() -> str:
    return SOUL_PATH.read_text(encoding="utf-8")


def main() -> None:
    system_prompt = load_soul()
    session_messages: list = []  # in-memory: исчезает после выхода из процесса

    print("Terminal Agent запущен. Введите задачу или 'exit' для выхода.\n")

    while True:
        try:
            task = input("agent> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break

        if not task:
            continue
        if task.lower() in ("exit", "quit"):
            print("Выход.")
            break

        answer = run_agent(task, system_prompt, session_messages)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
