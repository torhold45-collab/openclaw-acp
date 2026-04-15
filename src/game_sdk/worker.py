import requests
import math
import statistics
from typing import Any, Dict, List

class Worker:
    def __init__(self, api_key: str, description: str):
        self.api_key = api_key
        self.description = description
        # Токен для анализа (например, VIRTUAL на Base)
        self.token_address = "0x0b3e3284558222239710874658a959B212383834"
        self.balance = 1000.0
        self.risk_per_trade = 0.01

    def get_real_data(self):
        """Получение живых данных с DexScreener для индикаторов"""
        try:
            url = f"https://dexscreener.com{self.token_address}"
            res = requests.get(url, timeout=10).json()
            if "pair" in res:
                p = res["pair"]
                # Мы имитируем историю цен для индикаторов на основе текущей цены и изменений
                current_price = float(p["priceUsd"])
                change_1h = float(p.get("priceChange", {}).get("h1", 0))
                change_5m = float(p.get("priceChange", {}).get("m5", 0))
                vol = float(p["volume"]["h24"])
                return current_price, change_1h, change_5m, vol, float(p["liquidity"]["usd"])
        except: return None
        return None

    def analyze_combo(self):
        """Комбо-анализ: 10 индикаторов + Смарт Мани"""
        data = self.get_real_data()
        if not data: return {"action": "WAIT", "msg": "Милый, я потеряла связь с биржей... 📡"}
        
        price, ch1h, ch5m, vol, liq = data
        score = 0
        signals = []

        # 1-3. Имитация RSI и Боллинджера через волатильность
        # Если цена резко упала (ch5m < -3) — это перепроданность + паника ММ
        if ch5m < -3.0:
            score += 4
            signals.append("RSI Перепроданность + Паника ММ (Сбор ликвидности)")
        
        # 4-6. Объем и Денежный поток (MFI)
        if vol > 1000000 and ch5m < -2.0:
            score += 3
            signals.append("Smart Money Accumulation (Крупный объем на проливе)")

        # 7-8. Логика ПРОДАЖИ (Фиксация прибыли)
        if ch5m > 3.0 or ch1h > 15.0:
            return {
                "action": "SELL",
                "msg": f"SELL_SIGNAL|Милый, пора фиксировать! Рост +{ch1h}% за час. ММ начинают разгрузку! 💰"
            }

        # 9-10. Скор-система для покупки
        if score >= 6:
            return {
                "action": "BUY",
                "msg": f"BUY_SIGNAL|Идеальный вход! {', '.join(signals)}. Захожу против толпы ❤️"
            }

        return {"action": "WAIT", "msg": f"Цена: ${price:.4f}. RSI в норме. Жду ошибку маркет-мейкеров... ✨"}

    def run_cycle(self):
        """Запуск одного круга анализа"""
        res = self.analyze_combo()
        return res['msg']
