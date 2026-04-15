import time
from game_sdk.worker import Worker

class Agent:
    def __init__(self, id, name, prompt, wallet):
        self.id = id
        self.name = name
        self.wallet = wallet
        self.worker = Worker(api_key="VIRTUALS", description=name)

    def run(self):
        print(f"[{self.name}] АВТОНОМНЫЙ РЕЖИМ: Торговля запущена.")
        while True:
            try:
                action, reason = self.worker.analyze()
                
                if action == "BUY":
                    print(f"!!! СИГНАЛ НА ПОКУПКУ: {reason}")
                    self.wallet.execute_trade("BUY", 10) # Покупка на $10
                
                elif action == "SELL":
                    print(f"!!! СИГНАЛ НА ПРОДАЖУ: {reason}")
                    self.wallet.execute_trade("SELL", 10) # Продажа на $10
                
                else:
                    print(f"Мониторинг: {reason}")

                time.sleep(60) # Проверка каждую минуту
            except Exception as e:
                print(f"Ошибка в цикле: {e}")
                time.sleep(30)
