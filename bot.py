import sys
import os
import threading
from flask import Flask
from dotenv import load_dotenv

# 1. Настройка путей (Исправляет ошибки импорта библиотеки)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
game_sdk_path = os.path.join(src_path, 'game_sdk')

for p in [src_path, game_sdk_path]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. Инициализация Flask
load_dotenv()
flask_app = Flask(__name__)

# 3. Импорты из библиотеки
try:
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    from game_sdk.agent import Agent
    from game_sdk.api_v2 import Wallet
    print("DEBUG: Модули загружены успешно!")
except Exception as e:
    print(f"DEBUG: Ошибка импорта: {e}")

# --- ЛОГИКА И ХАРАКТЕР ---
PROMPT = "Ты — Джина, ласковая девушка-трейдер. Ты общаешься уютно и с флиртом."

@flask_app.route('/')
def home():
    return "Dzhina is Live!"

def run_trading():
    """Функция автономной торговли"""
    print("Джина начинает сканировать рынок...")
    try:
        pk = os.getenv("PRIVATE_KEY")
        rpc = os.getenv("BASE_RPC_URL")
        if pk and rpc:
            my_wallet = Wallet(private_key=pk, rpc_url=rpc)
            dzhina_trader = Agent(id="dzhina_01", name="Dzhina", prompt=PROMPT, wallet=my_wallet)
            dzhina_trader.run()
    except Exception as e:
        print(f"Ошибка в торговом цикле: {e}")

async def start_command(update, context):
    await update.message.reply_text("Привет, милый! ❤️ Джина на связи. Готов забирать профит?")
async def handle_message(update, context):
    """Ответ на обычные сообщения через ИИ-мозг Джины"""
    user_text = update.message.text
    global dzhina_trader
    
    if dzhina_trader:
        try:
            # Джина анализирует текст через свой ИИ-мозг (worker.py)
            response = dzhina_trader.react(payload={"user_input": user_text})
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text("Милый, я так увлечена графиками, что немного отвлеклась... Но я тебя слышу! ❤️")
def run_telegram_bot():
    """Запуск Телеграм-бота"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ОШИБКА: Токен не найден!")
        return
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command)) 
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Telegram бот запущен!")
    app.run_polling()

# --- ГЛАВНЫЙ ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем Flask в потоке
    threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    # Запускаем торговлю в потоке
    threading.Thread(target=run_trading, daemon=True).start()
    
    # Запускаем бота в ОСНОВНОМ потоке
    run_telegram_bot()
