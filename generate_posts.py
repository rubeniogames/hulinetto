#!/usr/bin/env python3
"""
generate_posts.py
Читает новые сообщения из Telegram-канала,
генерирует посты через Claude API и сохраняет в posts.json
"""

import os
import json
import datetime
import urllib.request
import urllib.parse

# ── Настройки (берутся из переменных окружения GitHub Actions) ──────────────
TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]       # токен бота от @BotFather
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]     # ID канала, напр. -1001234567890
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]   # ключ с console.anthropic.com
POSTS_FILE = "posts.json"
MAX_NEW_MESSAGES = 20   # сколько последних сообщений обрабатывать за один прогон

# ── Вспомогательные функции ──────────────────────────────────────────────────

def http_get(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())

def http_post(url, data, headers=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# ── Шаг 1: Получить сообщения из Telegram ───────────────────────────────────

def get_telegram_messages():
    """Возвращает последние текстовые сообщения из канала."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?limit=100"
    data = http_get(url)
    messages = []
    for update in data.get("result", []):
        msg = update.get("channel_post") or update.get("message", {})
        text = msg.get("text", "").strip()
        chat_id = str(msg.get("chat", {}).get("id", ""))
        # фильтруем только нужный канал и непустые тексты
        if text and chat_id == str(TELEGRAM_CHAT_ID):
            messages.append({
                "id": str(update["update_id"]),
                "text": text,
                "date": datetime.datetime.utcfromtimestamp(
                    msg.get("date", 0)
                ).isoformat() + "Z",
            })
    return messages[-MAX_NEW_MESSAGES:]  # берём последние N

# ── Шаг 2: Сгенерировать пост через Claude ───────────────────────────────────

def generate_post(raw_text):
    """Отправляет сырой текст в Claude, получает готовый пост в JSON."""
    prompt = f"""Ты редактор хоккейного новостного сайта.
Тебе дают сырое сообщение от репортёра. Преврати его в короткий новостной пост.

Сырое сообщение:
\"\"\"{raw_text}\"\"\"

Ответь ТОЛЬКО валидным JSON без лишних символов:
{{
  "title": "Короткий броский заголовок (до 80 символов)",
  "body": "Текст поста — 2-3 предложения, живо и по делу",
  "tag": "news | match | transfer | rumor"
}}"""

    response = http_post(
        "https://api.anthropic.com/v1/messages",
        {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01"},
    )

    raw = response["content"][0]["text"].strip()
    # убираем возможные markdown-обёртки
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── Шаг 3: Обновить posts.json ───────────────────────────────────────────────

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def already_processed(posts, msg_id):
    return any(p.get("telegram_id") == msg_id for p in posts)

# ── Главная логика ────────────────────────────────────────────────────────────

def main():
    print("📡 Получаем сообщения из Telegram...")
    messages = get_telegram_messages()
    print(f"   Найдено: {len(messages)} сообщений")

    posts = load_posts()
    new_count = 0

    for msg in messages:
        if already_processed(posts, msg["id"]):
            print(f"   ⏭  Пропускаем (уже есть): {msg['id']}")
            continue

        print(f"   ✍️  Генерируем пост для: {msg['text'][:60]}...")
        try:
            generated = generate_post(msg["text"])
            post = {
                "id": f"tg_{msg['id']}",
                "telegram_id": msg["id"],
                "title": generated["title"],
                "body": generated["body"],
                "tag": generated.get("tag", "news"),
                "source": "Telegram-канал команды",
                "created_at": msg["date"],
            }
            posts.append(post)
            new_count += 1
            print(f"   ✅  '{post['title']}'")
        except Exception as e:
            print(f"   ❌  Ошибка генерации: {e}")

    save_posts(posts)
    print(f"\n🏒 Готово! Добавлено новых постов: {new_count}. Всего в ленте: {len(posts)}")

if __name__ == "__main__":
    main()
