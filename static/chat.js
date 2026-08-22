const messagesEl = document.getElementById('messages');
const inputEl    = document.getElementById('user-input');
const sendBtn    = document.getElementById('send-btn');

// Генерируем session_id один раз на вкладку
const sessionId = 'sess_' + Math.random().toString(36).slice(2, 10);

// Текущий режим: 'bot_flow' | 'ai_consultant'
let mode = 'bot_flow';

// ── Рендеринг ────────────────────────────────────────────────

function appendMessage(role, text, buttons = [], isAI = false) {
  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;

  if (isAI) {
    const badge = document.createElement('span');
    badge.className = 'ai-badge';
    badge.textContent = '✦ ИИ-консультант';
    wrap.appendChild(badge);
  }

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  wrap.appendChild(bubble);

  if (buttons.length) {
    const btnsWrap = document.createElement('div');
    btnsWrap.className = 'buttons';
    buttons.forEach(label => {
      const b = document.createElement('button');
      b.className = 'btn';
      b.textContent = label;
      b.addEventListener('click', () => sendMessage(label));
      btnsWrap.appendChild(b);
    });
    wrap.appendChild(btnsWrap);
  }

  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'message bot typing';
  wrap.innerHTML = '<div class="bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

// ── Отправка ─────────────────────────────────────────────────

async function sendMessage(text) {
  text = text.trim();
  if (!text) return;

  // Кнопка «ИИ-консультант» переключает режим
  if (text === 'ИИ-консультант') {
    mode = 'ai_consultant';
    appendMessage('user', text);
    appendMessage('bot', 'Режим ИИ-консультанта активирован. Задайте вопрос об услугах, стоимости или правилах GuitarSpace.', [], true);
    inputEl.value = '';
    return;
  }

  // Кнопка «В главное меню» сбрасывает режим
  if (text === 'В главное меню' || text === '/start') {
    mode = 'bot_flow';
  }

  appendMessage('user', text);
  inputEl.value = '';
  setLoading(true);

  const typing = showTyping();

  try {
    const endpoint = mode === 'ai_consultant' ? '/api/ai' : '/api/chat';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, text }),
    });

    const data = await res.json();
    typing.remove();

    // Только если были в bot_flow и сервер сигнализирует переключиться в AI
    if (mode !== 'ai_consultant' && data.mode === 'ai_consultant') {
      mode = 'ai_consultant';
      appendMessage('bot', 'Режим ИИ-консультанта активирован. Задайте вопрос об услугах, стоимости или правилах GuitarSpace.', [], true);
      return;
    }

    // Если AI вернул команду вернуться в меню
    if (data.mode === 'bot_flow') {
      mode = 'bot_flow';
    }

    const isAI = mode === 'ai_consultant';
    appendMessage('bot', data.text, data.buttons || [], isAI);

  } catch (err) {
    typing.remove();
    appendMessage('bot', 'Произошла ошибка соединения. Попробуйте ещё раз.');
  } finally {
    setLoading(false);
  }
}

function setLoading(on) {
  sendBtn.disabled = on;
  inputEl.disabled = on;
}

// ── События ───────────────────────────────────────────────────

sendBtn.addEventListener('click', () => sendMessage(inputEl.value));

inputEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage(inputEl.value);
  }
});

// ── Старт ─────────────────────────────────────────────────────

(async () => {
  setLoading(true);
  const typing = showTyping();
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, text: '/start' }),
    });
    const data = await res.json();
    typing.remove();
    appendMessage('bot', data.text, data.buttons || []);
  } catch {
    typing.remove();
    appendMessage('bot', 'Не удалось подключиться к серверу.');
  } finally {
    setLoading(false);
    inputEl.focus();
  }
})();
