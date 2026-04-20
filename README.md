# 🏒 Hockey Feed

Новостной сайт для хоккейных фанатов. Коллеги пишут в Telegram → ИИ генерирует посты → они появляются на сайте автоматически.

## Структура проекта

```
hockey-news/
├── index.html          ← сайт (открывается в браузере)
├── posts.json          ← база постов (обновляется автоматически)
├── generate_posts.py   ← скрипт генерации через Claude API
└── .github/
    └── workflows/
        └── deploy.yml  ← автозапуск каждые 2 часа
```

## Настройка (один раз)

### 1. Telegram-бот

1. Напишите [@BotFather](https://t.me/BotFather) → `/newbot`
2. Придумайте имя и username боту
3. Скопируйте токен вида `7123456789:AAF...`
4. Добавьте бота в ваш Telegram-канал как **администратора**
5. Узнайте ID канала: перешлите любое сообщение из канала боту [@userinfobot](https://t.me/userinfobot)

### 2. Ключ Claude API

1. Зайдите на [console.anthropic.com](https://console.anthropic.com)
2. API Keys → Create Key
3. Скопируйте ключ `sk-ant-...`

### 3. Secrets в GitHub

В репозитории: **Settings → Secrets and variables → Actions → New repository secret**

| Название | Значение |
|---|---|
| `TELEGRAM_TOKEN` | токен бота от BotFather |
| `TELEGRAM_CHAT_ID` | ID канала, например `-1001234567890` |
| `ANTHROPIC_API_KEY` | ключ `sk-ant-...` |

### 4. Включить GitHub Pages

**Settings → Pages → Source: GitHub Actions** → Save

### 5. Первый запуск

**Actions → Generate & Deploy → Run workflow**

Через ~1 минуту сайт будет доступен по адресу:
`https://ВАШ_ЛОГИН.github.io/hockey-news/`

## Как пользоваться

- Коллеги пишут новости в Telegram-канал обычными сообщениями
- Каждые 2 часа скрипт забирает новые сообщения и генерирует посты
- Или нажмите **Actions → Run workflow** для немедленного обновления

## Формат поста в Telegram

Пишите свободным текстом, ИИ сам разберётся:

```
Сегодня ЦСКА победил СКА 4:2. Шайбы забивали Панарин (2), Капризов и Гусев. 
Матч прошёл в Москве, трибуны были заполнены до отказа.
```
