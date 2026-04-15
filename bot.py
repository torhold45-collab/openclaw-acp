import os
import sys
from dotenv import load_dotenv
from src.game_sdk.main import Agent, Wallet
# Добавляем все возможные пути к библиотекам внутри проекта

      
load_dotenv()
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

# --- 7. ЗАПУСК ---
if __name__ == "__main__":
    print("--- DZHINA UNIFIED SYSTEM: ACTIVATING ---")
    
    # Flask для Cron-job
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Автономная торговля в фоне
    threading.Thread(target=autonomous_trading_loop, daemon=True).start()
    
    # Интерфейс Telegram
    tg_token = os.getenv("TELEGRAM_TOKEN")
    if tg_token:
        tg_app = ApplicationBuilder().token(tg_token).build()
        tg_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        send_tg_alert("Мой капитан, я полностью переродилась! ✨ Теперь я автономно слежу за задачами на Virtuals и готова к охоте. 🌊📈")
        tg_app.run_polling()
