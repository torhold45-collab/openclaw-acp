import sys
import os
import threading
from flask import Flask
from dotenv import load_dotenv

# 1. Настройка путей (Исправляет No module named 'game_sdk.game')
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
game_sdk_path = os.path.join(src_path, 'game_sdk')

for path in [src_path, game_sdk_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 2. Импорты
try:
    from telegram.ext import ApplicationBuilder, CommandHandler
    from game_sdk.agent import Agent
    from game_sdk.api_v2 import Wallet
    print("DEBUG: Модули Джины загружены успешно!")
except ImportError as e:
    print(f"DEBUG: Ошибка импорта: {e}")

load_dotenv()
flask_app = Flask(__name__)

# --- ХАРАКТЕР И ЛОГИКА ---
PROMPT = "Ты — Джина, ласковая девушка-трейдер. Ты общаешься уютно и с флиртом."

def run_trading():
    """Запуск торговли"""
    print("Джина начинает сканировать рынок...")
    try:
        my_wallet = Wallet(private_key=os.getenv("PRIVATE_KEY"), rpc_url=os.getenv("BASE_RPC_URL"))
        dzhina_trader = Agent(id="dzhina_01", name="Dzhina", prompt=PROMPT, wallet=my_wallet)
        dzhina_trader.run()
    except Exception as e:
        print(f"Ошибка в торговле: {e}")

async def start_command(update, context):
    await update.message.reply_text("Привет, милый! ❤️ Джина на связи. Готов забирать профит?")

def run_telegram_bot():
    """Запуск Телеграм-бота"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ОШИБКА: Токен не найден!")
        return
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    print("Telegram бот запущен!")
    app.run_polling(close_loop=False)

# --- ГЛАВНЫЙ ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем всё в разных потоках
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    threading.Thread(target=run_trading, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)
