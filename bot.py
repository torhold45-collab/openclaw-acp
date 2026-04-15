import sys
import os
import threading
from flask import Flask
from dotenv import load_dotenv

# Настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from game_sdk.agent import Agent
from game_sdk.api_v2 import Wallet

load_dotenv()
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Dzhina Trading Bot is Active (No Telegram Mode)"

def start_trading():
    # Создаем кошелек и агента
    wallet = Wallet(os.getenv("PRIVATE_KEY"), os.getenv("BASE_RPC_URL"))
    dzhina = Agent("dzhina_01", "Dzhina Trader", "Character Prompt", wallet)
    dzhina.run()

if __name__ == "__main__":
    # 1. Запускаем торговый цикл в отдельном потоке
    trading_thread = threading.Thread(target=start_trading, daemon=True)
    trading_thread.start()

    # 2. Запускаем Flask для Render
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)
