import sys
import os
import threading
from flask import Flask
from dotenv import load_dotenv

# 1. Жесткая настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sdk_path = os.path.join(src_path, 'game_sdk')

# Добавляем все возможные папки в поиск
for p in [current_dir, src_path, sdk_path]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. Импорты с проверкой
try:
    from game_sdk.agent import Agent
    # Пробуем импортировать Wallet из разных мест, где он может быть
    try:
        from game_sdk.api_v2 import Wallet
    except ImportError:
        from game_sdk.api import Wallet
    print("DEBUG: Модули Джины успешно загружены!")
except Exception as e:
    print(f"DEBUG: Ошибка импорта: {e}")
    # Создаем пустышки, чтобы код не падал сразу (для отладки)
    Agent = type('Agent', (), {'run': lambda x: print("Agent placeholder")})
    Wallet = None

load_dotenv()
flask_app = Flask(__name__)
    """Функция автономной торговли Джины"""
    print("Джина начинает сканировать рынок...")
    try:
        # Берем ключи из настроек Render
        my_wallet = Wallet(
            private_key=os.getenv("PRIVATE_KEY"),
            rpc_url=os.getenv("BASE_RPC_URL")
        )
        dzhina_trader = Agent(
            id="dzhina_agent_01",
            name="Dzhina Trader",
            prompt=PROMPT,
            wallet=my_wallet
        )
        dzhina_trader.run()
    except Exception as e:
        print(f"Ошибка в торговом цикле: {e}")

# --- TELEGRAM БОТ ---

async def start_command(update, context):
    """Приветствие Джины"""
    await update.message.reply_text("Привет, мой хороший! ❤️ Джина на связи. Рынок сегодня горячий, как и я. Готов забирать профит?")

def run_telegram_bot():
    """Запуск Telegram клиента (должен быть в основном потоке)"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ОШИБКА: TELEGRAM_BOT_TOKEN не найден в настройках Render!")
        return
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    
    print("Telegram бот запущен и слушает сообщения...")
    # Запуск в основном потоке решает ошибку set_wakeup_fd
    app.run_polling()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---

@flask_app.route('/')
def home():
    return "Dzhina Trader is Live!"

def run_flask():
    """Запуск Flask в отдельном потоке"""
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# --- ГЛАВНЫЙ ЗАПУСК ---

if __name__ == "__main__":
    # 1. Запускаем веб-сервер Flask в фоне
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Запускаем торговую логику в фоне
    threading.Thread(target=run_trading, daemon=True).start()
    
    # 3. Запускаем Telegram-бота в ОСНОВНОМ ПОТОКЕ (обязательно)
    run_telegram_bot()
