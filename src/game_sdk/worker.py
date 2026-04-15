import math
import statistics
from typing import Any, Dict, List

class Worker:
    def __init__(self, api_key: str, description: str):
        self.api_key = api_key
        self.description = description
        self.balance = 1000.0
        self.risk_per_trade = 0.01

    # --- МАТЕМАТИЧЕСКОЕ ЯДРО ---
    
    def get_indicators(self, candles: List[Dict]) -> Dict:
        close = [c['close'] for c in candles]
        high = [c['high'] for c in candles]
        low = [c['low'] for c in candles]
        vol = [c['volume'] for c in candles]

        # 1. RSI
        rsi = self._calc_rsi(close)
        # 2. EMA 200 (Глобальный фильтр)
        ema200 = self._calc_ema(close, 200)
        # 3. Bollinger Bands
        bb_mid, bb_up, bb_low = self._calc_bollinger(close)
        # 4. MACD
        macd_line, signal_line = self._calc_macd(close)
        # 5. Stochastic
        stoch_k = self._calc_stochastic(close, high, low)
        # 6. MFI (Money Flow Index)
        mfi = self._calc_mfi(candles)
        # 7. ATR (Волатильность для стопа)
        atr = self._calc_atr(candles)
        
        return {
            "rsi": rsi, "ema200": ema200, "bb_low": bb_low, "bb_up": bb_up,
            "macd": macd_line, "signal": signal_line, "stoch": stoch_k,
            "mfi": mfi, "atr": atr, "last_price": close[-1]
        }

    # --- СТРАТЕГИЯ SMART MONEY ---

    def analyze_combo(self, candles: List[Dict]):
        ind = self.get_indicators(candles)
        score = 0
        signals = []

        # ЛОГИКА ВХОДА (LONG)
        # А) Против тренда (Скальпинг ошибок ММ):
        if ind['last_price'] < ind['bb_low'] and ind['rsi'] < 30:
            score += 3
            signals.append("Panic Selloff (BB+RSI)")
        
        # Б) Подтверждение объемами:
        if ind['mfi'] < 20:
            score += 2
            signals.append("Smart Money Accumulation (MFI)")
            
        # В) Технический разворот:
        if ind['macd'] > ind['signal'] and ind['stoch'] < 25:
            score += 3
            signals.append("Momentum Shift (MACD+Stoch)")

        # Г) Фильтр ММ (Ищем FVG):
        if candles[-3]['high'] < candles[-1]['low']:
            score += 2
            signals.append("FVG Gap (MM Trap)")

        # ИТОГОВОЕ РЕШЕНИЕ
        if score >= 7:
            # Расчет стоп-лосса по ATR (в 2 раза больше текущей волатильности)
            sl = ind['last_price'] - (ind['atr'] * 2)
            tp = ind['last_price'] + (ind['atr'] * 4) # R/R 1:2
            
            return {
                "action": "BUY",
                "msg": f"Милый, я вхожу! Сигналы: {', '.join(signals)}. Тейк на {tp:.2f}, стоп на {sl:.2f} ❤️"
            }
        
        return {"action": "WAIT", "msg": f"Жду комбо-сигнал... (Score: {score}/7, RSI: {ind['rsi']:.1f})"}

    # --- ВСПОМОГАТЕЛЬНЫЕ РАСЧЕТЫ ---
    def _calc_rsi(self, data, n=14):
        if len(data) < n+1: return 50
        diffs = [data[i] - data[i-1] for i in range(1, len(data))]
        plus = [d if d > 0 else 0 for d in diffs[-n:]]
        minus = [abs(d) if d < 0 else 0 for d in diffs[-n:]]
        rs = (sum(plus)/n) / (sum(minus)/n + 1e-9)
        return 100 - (100 / (1 + rs))

    def _calc_ema(self, data, n):
        if len(data) < n: return data[-1]
        alpha = 2 / (n + 1)
        ema = data[0]
        for p in data: ema = (p - ema) * alpha + ema
        return ema

    def _calc_bollinger(self, data, n=20):
        if len(data) < n: return data[-1], data[-1], data[-1]
        sma = sum(data[-n:]) / n
        std = statistics.stdev(data[-n:])
        return sma, sma + (2*std), sma - (2*std)

    def _calc_macd(self, data):
        ema12 = self._calc_ema(data, 12)
        ema26 = self._calc_ema(data, 26)
        macd = ema12 - ema26
        return macd, self._calc_ema([macd], 9) # Упрощенно

    def _calc_stochastic(self, close, high, low, n=14):
        hh, ll = max(high[-n:]), min(low[-n:])
        return ((close[-1] - ll) / (hh - ll + 1e-9)) * 100

    def _calc_mfi(self, candles, n=14):
        # Упрощенный индекс денежного потока
        vols = [c['volume'] for c in candles[-n:]]
        return 20 if sum(vols) > 500 else 50 # Заглушка логики

    def _calc_atr(self, candles, n=14):
        tr = [abs(c['high'] - c['low']) for c in candles[-n:]]
        return sum(tr) / n

    def run_cycle(self):
        # Генерируем 200 свечей для анализа
        mock_candles = [{"close": 100+i, "high": 105+i, "low": 95+i, "volume": 100+i} for i in range(210)]
        return self.analyze_combo(mock_candles)['msg']
