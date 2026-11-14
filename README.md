# GuitarSpace — чат-бот с ИИ-консультантом

Учебный проект: чат-бот для онлайн-школы игры на гитаре. Простой web-интерфейс, сценарный bot-flow, ИИ-консультант на основе AI Studio API, SQLite, локальный запуск и деплой на VPS.

---

## Легенда проекта

**Сервис:** GuitarSpace — онлайн-уроки игры на гитаре  
**Пользователь:** начинающий или любитель, который хочет научиться играть или улучшить технику  
**Задача бота:** помочь выбрать подходящий формат обучения, ответить на вопросы по услугам и правилам, принять заявку на пробный урок или консультацию

---

## Услуги (каталог)

| # | Услуга | Описание |
|---|--------|----------|
| 1 | Пробный урок | Первое знакомство с преподавателем, 30 мин, от 0 ₽ |
| 2 | Индивидуальный урок | Персональное занятие, 60 мин, от 1500 ₽ |
| 3 | Мини-курс для начинающих | 8 уроков с нуля: аккорды, ритм, первые песни |
| 4 | Разбор песни по запросу | Изучаем одну выбранную песню от начала до конца |
| 5 | Экспресс-консультация | Ответы на конкретные вопросы по технике, 30 мин |

---

## FAQ

### Услуги и программы
- Для кого подходят уроки?
- Нужна ли своя гитара?
- Какой уровень нужен для мини-курса?
- Можно ли сменить услугу после записи?

### Стоимость
- Сколько стоит пробный урок?
- Как оплатить занятие?
- Есть ли пакеты со скидкой?
- Что входит в стоимость урока?

### Формат и расписание
- Как проходят онлайн-уроки?
- Какая платформа используется?
- Как выбрать удобное время?
- Можно ли перенести урок?

### Правила и контакты
- Как отменить или перенести урок?
- За сколько часов нужно предупреждать?
- Как связаться с преподавателем?
- Что делать, если урок не состоялся по техническим причинам?

---

## Данные заявки

**Собираем:**
- Имя пользователя
- Удобный способ связи (мессенджер, @username или email)
- Уровень игры (нет опыта / есть базовые навыки / играю давно)
- Интересующая услуга
- Удобное время для связи

**Не запрашиваем:**
- Номер телефона (только если пользователь сам укажет)
- Паспортные и платёжные данные
- Адрес и любые геолокационные данные
- Данные несовершеннолетних без явного согласия родителей

---

## Bot-flow vs ИИ-консультант

| | Bot-flow | ИИ-консультант |
|---|---|---|
| Запуск | Кнопки главного меню | Кнопка «ИИ-консультант» или свободный текст |
| Модель | Не используется | AI Studio API |
| Сценарий | Фиксированный: шаги, ветки, форма | Свободный диалог по базе знаний |
| Заявка | Пошаговая форма | Черновик после диалога, подтверждение пользователем |
| source в БД | `bot_flow` | `ai_consultant` |
| Работает без API | Да | Нет |

---

## Ограничения ИИ-консультанта

- Отвечает только по материалам из `knowledge/`
- Не придумывает цены, сроки, скидки и гарантии, которых нет в базе знаний
- Не выполняет shell-команды и не работает с файловой системой за пределами `knowledge/`
- Не читает `.env` и системные файлы
- Если информации нет — честно говорит об этом и предлагает оставить заявку
- Задаёт не более 1–2 уточняющих вопросов перед черновиком заявки
- Сохраняет заявку только после явного подтверждения пользователем

---

## Структура проекта

```
guitarspace/
├─ app.py                  — FastAPI-сервер, роуты
├─ bot_flow.py             — сценарный бот без модели
├─ ai_client.py            — клиент AI Studio API
├─ agent_runtime.py        — agent loop
├─ db.py                   — инициализация SQLite и операции
├─ requirements.txt
├─ .env.example
├─ README.md
├─ agent/
│  ├─ soul.md              — системная инструкция консультанта
│  └─ tools.py             — 4 безопасных tools
├─ knowledge/
│  ├─ services.md          — каталог услуг
│  ├─ faq.md               — FAQ
│  └─ rules.md             — правила и контакты
├─ static/
│  ├─ index.html
│  ├─ style.css
│  └─ chat.js
├─ data/
│  └─ bot.sqlite3
└─ evidence/
   └─ screenshots/
      ├─ 01-local-main-chat.png
      ├─ 02-local-bot-flow.png
      ├─ 03-local-ai-consultant.png
      ├─ 04-local-database-proof.png
      └─ 05-vps-runtime-start.png
```

---

## Архитектура

### Interface
- `static/index.html` — страница чата с меню и полем ввода
- `static/style.css` — стили
- `static/chat.js` — отправка сообщений, рендер ответов, переключение режимов

### Backend
- `app.py` — FastAPI-сервер, маршруты `/api/chat` (bot-flow) и `/api/ai` (агент)
- `bot_flow.py` — конечный автомат: меню → ветки → форма заявки (без модели)
- Сессии через `session_id`, генерируется на клиенте

### Database
- `db.py` — инициализация БД при старте, `save_lead`, `save_feedback`
- `leads`: `session_id, source, service, contact, problem_text, agent_summary, missing_info, status, created_at`
- `feedback`: `session_id, message_text, created_at`
- Файл: `data/bot.sqlite3`

### Agent
- `ai_client.py` — OpenAI-совместимый клиент для Yandex AI Studio
- `agent_runtime.py` — agent loop: задача → model call → tool-call → result → answer
- `agent/tools.py` — 4 tools с защитой путей
- `agent/soul.md` — роль, тон, ограничения
- `knowledge/` — база знаний: `services.md`, `faq.md`, `rules.md`

---

## MVP: что входит и что нет

**Входит:**
- Web-чат с bot-flow и ИИ-консультантом
- SQLite с двумя таблицами
- Локальный запуск и запуск на VPS

**Не входит:**
- Домен и публичная ссылка
- Кабинет управления / админка
- Авторизация и роли
- Внешние production-контуры
- Уведомления и рассылки

---

## Запуск

```bash
# 1. Клонировать репозиторий и перейти в папку
git clone https://github.com/gorokhovPavel/terminal-agent.git guitarspace
cd guitarspace

# 2. Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env по шаблону
cp .env.example .env
# Заполнить YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_MODEL_URI

# 5. Запустить
python app.py
# Открыть http://localhost:8000
```

## Логи и повторный запуск

```bash
# Логи в реальном времени
tail -f app.log

# Остановить
Ctrl+C  # локально
pkill -f app.py  # на VPS

# Повторный запуск на VPS
pkill -f app.py 2>/dev/null; sleep 1
nohup .venv/bin/python app.py >> app.log 2>&1 &
```

---

## .env.example

```
YANDEX_API_KEY=
YANDEX_FOLDER_ID=
YANDEX_MODEL_URI=gpt://<folder_id>/gpt-oss-120b/latest
YANDEX_BASE_URL=https://ai.api.cloud.yandex.net/v1
YANDEX_TEMPERATURE=0.4
YANDEX_MAX_TOKENS=12000
```

---

## Tools ИИ-консультанта

| Tool | Что делает | Ограничение |
|------|-----------|-------------|
| `search_knowledge` | Ищет по файлам `knowledge/` | Только внутри `knowledge/` |
| `read_knowledge_file` | Читает конкретный .md-файл | Только `.md` внутри `knowledge/` |
| `prepare_lead_draft` | Готовит черновик заявки | Не сохраняет в БД |
| `save_confirmed_lead` | Сохраняет заявку в SQLite | Только после подтверждения пользователем |

## Биллинг и лимиты AI Studio

Перед первым запросом к модели убедитесь, что в Yandex Cloud активен биллинг или trial, папка имеет доступ к выбранной модели, а лимит токенов не исчерпан. При ошибке `429` или `quota exceeded` проверьте статус в консоли Yandex Cloud.


...

import { expect, Page } from '@playwright/test';

export const DEFAULT_PRODUCT_URL =
  '/?page=retailLoanProduct&clientId=1086338415&retailLoanProductId=30e415bb-a63d-4d67-b410-57d80654e0e0';

export async function openOperationModal(
  page: Page,
  operationName: string,
  productUrl: string = DEFAULT_PRODUCT_URL
) {
  await page.goto(productUrl);

  // 1. Нажимаем кнопку "Операции"
  await page.getByRole('button', { name: 'Операции' }).click();

  // 2. Фильтруем список через поле поиска
  const searchInput = page.getByPlaceholder('Выберите операцию');
  await expect(searchInput).toBeVisible();
  await searchInput.fill(operationName);

  // 3. Кликаем по найденному пункту операции
  await page.getByText(operationName).last().click({ force: true });

  // 4. Ждем появления модалки (проверяем наличие диалога или кнопки)
  await expect(page.getByRole('dialog')).toBeVisible();
}


import { expect, test } from '@playwright/test';
import { openOperationModal } from '@/shared/lib/e2e/openOperationModal'; // поправьте путь под ваш алиас

const OPERATION_NAME = 'Ручная установка/снятие признака блокировки на КД';

test.describe('КД: Ручная установка/снятие признака блокировки', () => {
  test.beforeEach(async ({ page }) => {
    await openOperationModal(page, OPERATION_NAME);
  });

  test('устанавливает блокировку и закрывает модалку', async ({ page }) => {
    // Здесь сразу начинаем проверять саму модалку
    const applyButton = page.getByRole('button', { name: 'Выполнить' });
    // ...
  });
});

