from __future__ import annotations

from db import save_lead, save_feedback

SERVICES = [
    ("Пробный урок", "Первое знакомство с преподавателем, 30 мин — от 0 ₽"),
    ("Индивидуальный урок", "Персональное занятие, 60 мин — от 1500 ₽"),
    ("Мини-курс для начинающих", "8 уроков с нуля: аккорды, ритм, первые песни"),
    ("Разбор песни по запросу", "Изучаем одну выбранную песню от начала до конца"),
    ("Экспресс-консультация", "Ответы на конкретные вопросы по технике, 30 мин"),
]

FAQ = {
    "Услуги и программы": [
        ("Для кого подходят уроки?", "Для любого уровня — от полного нуля до любителя, который хочет улучшить технику."),
        ("Нужна ли своя гитара?", "Да, для занятий нужна акустическая или классическая гитара."),
        ("Какой уровень нужен для мини-курса?", "Никакого — курс рассчитан на тех, кто берёт гитару в руки впервые."),
        ("Можно ли сменить услугу после записи?", "Да, напишите преподавателю до начала урока — согласуем замену."),
    ],
    "Стоимость": [
        ("Сколько стоит пробный урок?", "Пробный урок — от 0 ₽, уточняйте актуальную цену при записи."),
        ("Как оплатить занятие?", "Оплата картой или переводом — реквизиты пришлёт преподаватель."),
        ("Есть ли пакеты со скидкой?", "Да, при покупке от 4 уроков — скидка 10%. Уточните при записи."),
        ("Что входит в стоимость урока?", "Занятие с преподавателем, разбор домашнего задания и материалы к уроку."),
    ],
    "Формат и расписание": [
        ("Как проходят онлайн-уроки?", "Через Zoom или Google Meet — ссылку пришлёт преподаватель."),
        ("Как выбрать удобное время?", "Укажите предпочтительное время в заявке — согласуем расписание."),
        ("Можно ли перенести урок?", "Да, если предупредить не менее чем за 12 часов."),
        ("Какая платформа используется?", "Zoom или Google Meet по договорённости с преподавателем."),
    ],
    "Правила и контакты": [
        ("Как отменить или перенести урок?", "Напишите преподавателю в мессенджер не менее чем за 12 часов."),
        ("Что делать, если урок не состоялся по техническим причинам?", "Урок переносится на удобное время без штрафов."),
        ("Как связаться с преподавателем?", "Контакт придёт после подтверждения записи."),
        ("За сколько часов нужно предупреждать?", "Минимум за 12 часов до урока."),
    ],
}

LEVELS = ["Нет опыта", "Есть базовые навыки", "Играю давно"]

MAIN_MENU_BUTTONS = ["Услуги", "FAQ", "Оставить заявку", "ИИ-консультант", "Обратная связь"]


def _main_menu() -> dict:
    return {
        "text": "Привет! Я бот GuitarSpace 🎸\nВыберите, что вас интересует:",
        "buttons": MAIN_MENU_BUTTONS,
        "next_state": "main_menu",
    }


def _services_message() -> dict:
    lines = ["Наши услуги:\n"]
    for i, (name, desc) in enumerate(SERVICES, 1):
        lines.append(f"{i}. *{name}*\n   {desc}")
    return {
        "text": "\n".join(lines),
        "buttons": ["Оставить заявку", "В главное меню"],
        "next_state": "main_menu",
    }


def _faq_menu() -> dict:
    return {
        "text": "Выберите категорию FAQ:",
        "buttons": list(FAQ.keys()) + ["В главное меню"],
        "next_state": "faq_menu",
    }


def _faq_category(category: str) -> dict:
    items = FAQ.get(category, [])
    lines = [f"*{category}*\n"]
    for q, a in items:
        lines.append(f"❓ {q}\n{a}\n")
    return {
        "text": "\n".join(lines),
        "buttons": ["Другая категория", "Оставить заявку", "В главное меню"],
        "next_state": "main_menu",
    }


def process(session: dict, user_input: str) -> dict:
    state = session.get("state", "main_menu")
    text = user_input.strip()

    # Глобальные переходы
    if text in ("В главное меню", "/start"):
        session.clear()
        return _main_menu()

    # --- Главное меню ---
    if state == "main_menu":
        if text == "Услуги":
            session["state"] = "main_menu"
            return _services_message()

        if text == "FAQ":
            session["state"] = "faq_menu"
            return _faq_menu()

        if text in ("Оставить заявку", "Оставить заявку 📝"):
            session["state"] = "lead_name"
            return {
                "text": "Как вас зовут?",
                "buttons": [],
                "next_state": "lead_name",
            }

        if text == "ИИ-консультант":
            session["state"] = "ai_consultant"
            return {
                "text": "__ai_consultant__",
                "buttons": [],
                "next_state": "ai_consultant",
                "mode": "ai_consultant",
            }

        if text == "Обратная связь":
            session["state"] = "feedback"
            return {
                "text": "Напишите ваш отзыв или пожелание — мы читаем каждое сообщение:",
                "buttons": ["В главное меню"],
                "next_state": "feedback",
            }

        return {
            "text": "Выберите один из вариантов:",
            "buttons": MAIN_MENU_BUTTONS,
            "next_state": "main_menu",
        }

    # --- FAQ ---
    if state == "faq_menu":
        if text in FAQ:
            session["state"] = "main_menu"
            return _faq_category(text)
        return _faq_menu()

    # --- Обратная связь ---
    if state == "feedback":
        if text:
            save_feedback(session.get("session_id", "unknown"), text)
            session["state"] = "main_menu"
            return {
                "text": "Спасибо за отзыв! Мы обязательно его учтём.",
                "buttons": MAIN_MENU_BUTTONS,
                "next_state": "main_menu",
            }
        return {
            "text": "Напишите ваш отзыв:",
            "buttons": ["В главное меню"],
            "next_state": "feedback",
        }

    # --- Сбор заявки ---
    if state == "lead_name":
        session["lead_name"] = text
        session["state"] = "lead_contact"
        return {
            "text": "Как с вами связаться? Укажите @username в Telegram или email:",
            "buttons": [],
            "next_state": "lead_contact",
        }

    if state == "lead_contact":
        session["lead_contact"] = text
        session["state"] = "lead_level"
        return {
            "text": "Какой у вас уровень игры на гитаре?",
            "buttons": LEVELS,
            "next_state": "lead_level",
        }

    if state == "lead_level":
        session["lead_level"] = text
        session["state"] = "lead_service"
        service_names = [s[0] for s in SERVICES]
        return {
            "text": "Какая услуга вас интересует?",
            "buttons": service_names,
            "next_state": "lead_service",
        }

    if state == "lead_service":
        session["lead_service"] = text
        session["state"] = "lead_time"
        return {
            "text": "В какое время вам удобно заниматься? (например: будни вечером, суббота утром)",
            "buttons": [],
            "next_state": "lead_time",
        }

    if state == "lead_time":
        session["lead_time"] = text
        session["state"] = "lead_confirm"

        name = session.get("lead_name", "—")
        contact = session.get("lead_contact", "—")
        level = session.get("lead_level", "—")
        service = session.get("lead_service", "—")
        time_pref = session.get("lead_time", "—")

        summary = (
            f"Имя: {name}\n"
            f"Контакт: {contact}\n"
            f"Уровень: {level}\n"
            f"Услуга: {service}\n"
            f"Удобное время: {time_pref}"
        )
        session["lead_summary"] = summary

        return {
            "text": f"Проверьте данные заявки:\n\n{summary}\n\nВсё верно?",
            "buttons": ["Отправить заявку", "Изменить", "Отмена"],
            "next_state": "lead_confirm",
        }

    if state == "lead_confirm":
        if text == "Отправить заявку":
            problem = f"Уровень: {session.get('lead_level', '—')}. Время: {session.get('lead_time', '—')}"
            save_lead(
                session_id=session.get("session_id", "unknown"),
                source="bot_flow",
                service=session.get("lead_service"),
                contact=session.get("lead_contact"),
                problem_text=problem,
            )
            session.clear()
            return {
                "text": "Заявка принята! Мы свяжемся с вами в ближайшее время. 🎸",
                "buttons": MAIN_MENU_BUTTONS,
                "next_state": "main_menu",
            }

        if text == "Изменить":
            session["state"] = "lead_name"
            return {
                "text": "Давайте начнём заново. Как вас зовут?",
                "buttons": [],
                "next_state": "lead_name",
            }

        if text == "Отмена":
            session.clear()
            return {
                "text": "Заявка отменена. Вы всегда можете вернуться.",
                "buttons": MAIN_MENU_BUTTONS,
                "next_state": "main_menu",
            }

        return {
            "text": f"Проверьте данные:\n\n{session.get('lead_summary', '')}\n\nВсё верно?",
            "buttons": ["Отправить заявку", "Изменить", "Отмена"],
            "next_state": "lead_confirm",
        }

    # Fallback
    session.clear()
    return _main_menu()
