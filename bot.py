import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Токен из переменных окружения (на Render или в .env)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN!")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐱 *Привет, мой повелитель!*\n\n"
        "Я — Джина, твой ласковый торговый агент. "
        "Уже анализирую рынок с 10 индикаторами и паттернами. "
        "Скоро начну торговать на Hyperliquid.\n\n"
        "Доступные команды:\n"
        "/status — посмотреть портфель\n"
        "/help — помощь\n"
        "/profit — отчёт о прибыли",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Заглушка — позже подключим реальные данные из Hyperliquid
    await update.message.reply_text(
        "💰 *Текущий портфель*\n"
        "Баланс USDC: 1000$\n"
        "Открытые позиции: 0\n"
        "PNL сегодня: 0$",
        parse_mode="Markdown"
    )

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 *Прибыль за сегодня:* 0.00$\n"
        "Твоя доля (5%): 0.00$\n"
        "Скоро появится реальная статистика!",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("profit", profit))
    print("🚀 Бот Джина запущен и слушает команды...")
    app.run_polling()

if __name__ == "__main__":
    main()
