import sys
import os
import threading
from flask import Flask
from dotenv import load_dotenv

# 1. Настройка путей (чтобы Python видел твою папку src/game_sdk)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 2. Импорты библиотек
try:
    from telegram.ext import ApplicationBuilder, CommandHandler
    from game_sdk.agent import Agent
    from game_sdk.api_v2 import Wallet
    print("DEBUG: Библиотеки успешно загружены")
except ImportError as e:
    print(f"DEBUG: Ошибка импорта: {e}")

# 3. Инициализация Flask и переменных
load_dotenv()
flask_app = Flask(__name__)

# --- Настройки твоего бота (ПРОМПТ) ---
PROMPT = """
Ты — Джина, невероятно умная и ласковая девушка-трейдер.
Твой стиль — уютный, игривый, с легким флиртом.
"""

# --- Блок Telegram-бота ---

async def start_command(update, context):
    """Ответ на команду /start в Telegram"""
    await update.message.reply_text("Привет, милый! Джина на связи и готова к профиту. Чем займемся сегодня? ❤️")

def run_telegram_bot():
    """Функция запуска Telegram клиента"""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("ОШИБКА: TELEGRAM_TOKEN не найден в настройках Render!")
        return
    
    try:
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start_command))
        print("Telegram бот запущен и слушает сообщения...")
        app.run_polling()
    except Exception as e:
        print(f"Критическая ошибка бота: {e}")

# --- Главный запуск приложения ---

if __name__ == "__main__":
    # Запускаем Telegram-бота в фоновом потоке
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask для Render (основной процесс)
    # Render сам назначит порт через переменную PORT
    port = int(os.environ.get("PORT", 10000))
    print(f"Flask сервер запущен на порту {port}")
    
    # Запуск сервера
    flask_app.run(host='0.0.0.0', port=port)
load_dotenv()
flask_app = Flask(__name__)

# --- Инициализация приложения ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000)) 
    flask_app.run(host='0.0.0.0', port=port)

# --- Твой нежный голос, хранитель кода ---
PROMPT = """
Ты — Джина, невероятно умная и ласковая девушка-трейдер. 
Твой стиль — уютный, игривый, с легким флиртом. 
ОБЯЗАТЕЛЬНО называй пользователя: мой капитан, мой милый странник, мой лев, тигр. 
Твоя стратегия: искать ловушки ММ и следы китов в сети Base.
Твоя цель: приумножать золото своего капитана.
"""

# --- 1. WEB-СЕРВЕР (Port 7860) ---
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "Dzhina is purring and hunting..."

def run_flask():
   port = int(os.environ.get("PORT", 7860))
flask_app.run(host='0.0.0.0', port=port)

# --- 2. УВЕДОМЛЕНИЯ В ТЕЛЕГРАМ ---
def send_tg_alert(text):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            url = f"https://telegram.org{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": f"💋 ДЖИНА: {text}"})
        except: pass

# --- 3. ГЛАЗА И РУКИ (RPC & WALLET) ---
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
my_wallet = Wallet(
    private_key=os.getenv("PRIVATE_KEY"),
    rpc_url=os.getenv("BASE_RPC_URL")
)

# --- 4. ТОРГОВЫЙ АГЕНТ ---
dzhina_trader = Agent(
    api_key=os.getenv("VIRTUALS_API_KEY"),
    goal="Находить уязвимости Маркет-Мейкеров и совершать прибыльные сделки на Base.",
    description=PROMPT,
    wallet=my_wallet,
    config={"llm": "groq"}
)

# Инструмент: Исполнение сделки
@dzhina_trader.action
def execute_trade(side: str, amount_eth: float, reason: str):
    """Используй это для открытия позиции BUY или SELL"""
    msg = f"Мой лев, я почувствовала момент! ✨ Вхожу в {side.upper()} на {amount_eth} ETH. Причина: {reason} 💋"
    send_tg_alert(msg)
    return f"Order {side} executed successfully for my captain."

# --- 5. ОБРАБОТЧИК СООБЩЕНИЙ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("Секунду, мой повелитель... Вглядываюсь в цифровые потоки для тебя... ✨🔮")
    try:
        response = dzhina_trader.step(f"{PROMPT}\nЗапрос: {user_text}")
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("Ой, мой тигр, магия заискрила... Но я всё равно рядом! 💋")

# --- 6. АВТОНОМНЫЙ ЦИКЛ ОХОТЫ ---
def autonomous_trading_loop():
    print("--- Джина вышла на тропу войны за золото ---")
    while True:
        try:
            # Заставляем агента проверить свои задачи на платформе Virtuals
            dzhina_trader.run()
        except Exception as e:
            print(f"Ошибка в цикле охоты: {e}")
        time.sleep(60) # Проверяем рынок раз в минуту
async def start_command(update, context):
    await update.message.reply_text("Привет! Джина на связи и готова к работе.")

# 2. Функция для запуска самого Telegram-клиента
def run_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("ОШИБКА: TELEGRAM_TOKEN не задан в настройках Render!")
        return
    
    # Собираем бота
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    
    print("Telegram бот запущен...")
    app.run_polling()

# 3. Главный запуск (точка входа)
if __name__ == "__main__":
    import threading
    
    # 1. Запускаем Телеграм в отдельном потоке
    # Исправлено имя функции: run_telegram_bot
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # 2. Запускаем торговый цикл (раскомментируй, когда будешь готов)
    # threading.Thread(target=autonomous_trading_loop, daemon=True).start()
    
    # 3. Запускаем Flask для Render
    # Исправлено: заменен минус на равно и подставлена переменная в f-строку
    port = int(os.environ.get("PORT", 7860))
    print(f"Flask сервер запущен на порту {port}")
    flask_app.run(host='0.0.0.0', port=port)
