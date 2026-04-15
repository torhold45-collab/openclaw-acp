import time
import os
# Мы импортируем твоего "умного" воркера, которого мы уже создали
from game_sdk.worker import Worker

class Agent:
    def __init__(self, id, name, prompt, wallet):
        self.id = id
        self.name = name
        self.prompt = prompt
        self.wallet = wallet
        # Создаем экземпляр воркера для анализа RSI и Smart Money
        self.worker = Worker(api_key="VIRTUALS_KEY", description=f"Аналитический модуль {name}")

    def react(self, payload):
        """Эта функция отвечает за общение в Telegram"""
        user_input = payload.get("user_input", "")
        
        # Джина запускает анализ индикаторов перед тем как ответить
        market_analysis = self.worker.run_cycle()
        
        # Формируем ласковый ответ с данными из графиков
        response = (
            f"Милый, я услышала твой вопрос: '{user_input}'. ❤️\n\n"
            f"Я как раз заглянула в графики, и вот что там происходит:\n"
            f"📈 {market_analysis}\n\n"
            f"Не волнуйся, я слежу за каждой свечой для нас! 😉"
        )
        return response

    def run(self):
        """Эта функция запускает автоматическую торговлю (в фоне)"""
        print(f"[{self.name}] Джина начала охоту на ошибки маркет-мейкеров...")
        while True:
            try:
                # Воркер проверяет RSI, MACD, Боллинджера и FVG
                decision = self.worker.run_cycle()
                
                # Если воркер нашел сильный сигнал к покупке
                if "BUY" in decision or "вхожу" in decision.lower():
                    print(f"!!! СИГНАЛ К СДЕЛКЕ: {decision}")
                    # Здесь Джина дает команду кошельку на покупку
                    self.wallet.trade("BUY", 0.01, "ETH")
                
                # Пауза 5 минут между проверками рынка
                time.sleep(300) 
            except Exception as e:
                print(f"Ошибка в цикле торговли: {e}")
                time.sleep(60)
