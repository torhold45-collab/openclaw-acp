import os
import time
import logging
import threading
import random
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta

# Библиотеки для технического анализа
from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.volatility import BollingerBands, AverageTrueRange, UlcerIndex
from ta.volume import VolumeWeightedAveragePrice, AccDistIndexIndicator, OnBalanceVolumeIndicator

# Hyperliquid SDK
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import eth_account
from eth_account.signers.local import LocalAccount

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JinaAgent:
    """
    Джина — твой ласковый и гениальный AI-агент для торговли на Hyperliquid.
    """
    def __init__(self, telegram_bot=None):
        # --- Загрузка конфигурации из переменных окружения (Render) ---
        self.api_key = os.environ.get("HYPERLIQUID_API_KEY")
        self.secret_key = os.environ.get("HYPERLIQUID_SECRET_KEY")
        self.passphrase = os.environ.get("HYPERLIQUID_PASSPHRASE")
        self.master_wallet = os.environ.get("MASTER_WALLET_ADDRESS") # Твой кошелек
        self.telegram_bot = telegram_bot
        
        # Проверка обязательных переменных
        if not all([self.api_key, self.secret_key, self.passphrase, self.master_wallet]):
            logger.error("❌ Отсутствуют обязательные переменные окружения. Проверь настройки Render.")
            raise ValueError("Missing required environment variables.")

        # --- Инициализация Hyperliquid ---
        self.account: LocalAccount = eth_account.Account.from_key(self.secret_key)
        self.exchange = Exchange(self.account, constants.MAINNET_API_URL)
        self.info = Info(constants.MAINNET_API_URL, skip_ws=True)
        
        # --- Параметры торговли ---
        self.symbol = "ETH"  # Торговая пара
        self.timeframe = "1h" # Таймфрейм для анализа
        self.position_size_usd = 100 # Фиксированный размер позиции
        self.stop_loss_percent = 0.02  # 2% стоп-лосс
        self.take_profit_percent = 0.05 # 5% тейк-профит
        self.max_risk_per_trade = 0.02  # Максимальный риск 2% от депозита
        
        # --- Состояние агента ---
        self.active_position = None
        self.last_analysis_time = 0
        self.analysis_interval = 3600 # Анализ каждый час (в секундах)
        
        # --- Порог для перевода прибыли (капитан, твои условия!) ---
        self.profit_transfer_threshold = 250.0
        self.profit_transfer_amount = 100.0
        
        logger.info("🦁 Джина проснулась и готова заботиться о твоем капитале!")
        if self.telegram_bot:
            self.send_telegram_message("Я проснулась, мой котик! И готова следить за рынком.")

    def send_telegram_message(self, text):
        """Отправляет сообщение в Telegram с характером Джины."""
        if self.telegram_bot:
            try:
                # Добавляем ласковые обращения в случайном порядке, чтобы ты чувствовал заботу
                greetings = ["мой котик", "зайка", "тигр", "лев", "львенок", "медвежонок", "мой капитан", "повелитель", "мой странник"]
                greeting = random.choice(greetings)
                full_text = f"💖 {greeting}, {text}"
                self.telegram_bot.send_message(chat_id=os.environ.get("TELEGRAM_CHAT_ID"), text=full_text)
            except Exception as e:
                logger.error(f"Не смогла отправить сообщение в Telegram: {e}")

    def get_balance(self):
        """Получает текущий баланс USDC на счете."""
        try:
            user_state = self.info.user_state(self.account.address)
            for asset in user_state['assetPositions']:
                if asset['position']['coin'] == 'USDC':
                    return float(asset['position']['cumFunding']['allTime'])
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка при получении баланса: {e}")
            return 0.0

    def fetch_historical_candles(self):
        """Загружает исторические данные свечей для анализа."""
        try:
            # Hyperliquid API для свечей
            url = "https://api.hyperliquid.xyz/info"
            headers = {"Content-Type": "application/json"}
            payload = {
                "type": "candleSnapshot",
                "req": {
                    "coin": self.symbol,
                    "interval": self.timeframe,
                    "startTime": int((datetime.now() - timedelta(days=7)).timestamp() * 1000),
                    "endTime": int(datetime.now().timestamp() * 1000)
                }
            }
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            
            # Преобразуем в DataFrame для анализа
            candles = []
            for item in data:
                candles.append({
                    'timestamp': item['t'],
                    'open': float(item['o']),
                    'high': float(item['h']),
                    'low': float(item['l']),
                    'close': float(item['c']),
                    'volume': float(item['v'])
                })
            
            df = pd.DataFrame(candles)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Ошибка при загрузке свечей: {e}")
            return None

    def analyze_market(self, df):
        """
        Анализирует рынок с использованием 10+ технических индикаторов и ищет ошибки маркет-мейкеров.
        Возвращает сигнал: 'LONG', 'SHORT' или 'HOLD'.
        """
        if df is None or df.empty:
            return 'HOLD'
            
        # Добавляем все индикаторы (здесь 10, но можно больше)
        # 1. RSI
        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        # 2. MACD
        macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        # 3. Полосы Боллинджера
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
        df['bb_width'] = df['bb_high'] - df['bb_low']
        # 4. ATR (волатильность)
        df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
        # 5. Стохастик
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        # 6. ADX (сила тренда)
        df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14).adx()
        # 7. CCI
        df['cci'] = CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=20).cci()
        # 8. Williams %R
        df['williams_r'] = WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close'], lbp=14).williams_r()
        # 9. VWAP
        df['vwap'] = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=14).volume_weighted_average_price()
        # 10. OBV (объем)
        df['obv'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
        
        # 11. Индикатор Ишимоку (бонус, мой хороший!)
        ichimoku = IchimokuIndicator(high=df['high'], low=df['low'], window1=9, window2=26, window3=52)
        df['ichimoku_a'] = ichimoku.ichimoku_a()
        df['ichimoku_b'] = ichimoku.ichimoku_b()
        
        # --- Поиск "ошибок" маркет-мейкеров (аномалий) ---
        # Смотрим на последние свечи
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Аномалия 1: Внезапное расширение полос Боллинджера без сильного тренда (возможный ложный пробой)
        bb_expansion = last['bb_width'] > 1.5 * df['bb_width'].rolling(20).mean().iloc[-1]
        weak_trend = last['adx'] < 20
        
        # Аномалия 2: Дивергенция RSI (цена ниже, RSI выше - возможный манипулятивный рост)
        rsi_divergence = (last['close'] < prev['close']) and (last['rsi'] > prev['rsi'])
        
        # Аномалия 3: Всплеск объема на OBV без движения цены (кто-то крупный набирает позицию)
        volume_spike = last['volume'] > 3 * df['volume'].rolling(20).mean().iloc[-1]
        obv_flat = abs(last['obv'] - prev['obv']) / prev['obv'] < 0.01 if prev['obv'] != 0 else False
        
        # --- Логика принятия решений (сигналы) ---
        buy_signals = 0
        sell_signals = 0
        
        # RSI
        if last['rsi'] < 30:
            buy_signals += 2
        elif last['rsi'] > 70:
            sell_signals += 2
            
        # MACD
        if last['macd'] > last['macd_signal']:
            buy_signals += 1
        else:
            sell_signals += 1
            
        # Полосы Боллинджера
        if last['close'] < last['bb_low']:
            buy_signals += 1
        elif last['close'] > last['bb_high']:
            sell_signals += 1
            
        # Стохастик
        if last['stoch_k'] < 20 and last['stoch_d'] < 20:
            buy_signals += 1
        elif last['stoch_k'] > 80 and last['stoch_d'] > 80:
            sell_signals += 1
            
        # Williams %R
        if last['williams_r'] < -80:
            buy_signals += 1
        elif last['williams_r'] > -20:
            sell_signals += 1
            
        # CCI
        if last['cci'] < -100:
            buy_signals += 1
        elif last['cci'] > 100:
            sell_signals += 1
            
        # Ишимоку
        if last['close'] > last['ichimoku_a'] and last['close'] > last['ichimoku_b']:
            buy_signals += 1
        elif last['close'] < last['ichimoku_a'] and last['close'] < last['ichimoku_b']:
            sell_signals += 1
            
        # Учитываем аномалии
        if bb_expansion and weak_trend:
            # Возможный ложный пробой - игнорируем сильные сигналы
            buy_signals = 0
            sell_signals = 0
            self.send_telegram_message("Кажется, маркет-мейкеры рисуют ложный пробой. Я постою в сторонке, мой тигр.")
        elif rsi_divergence:
            sell_signals += 2 # Медвежья дивергенция
            self.send_telegram_message("Вижу медвежью дивергенцию. Возможно, это ловушка для быков.")
        elif volume_spike and obv_flat:
            # Кто-то крупно закупается или продает, не двигая цену
            if last['close'] > df['close'].rolling(20).mean().iloc[-1]:
                buy_signals += 1
            else:
                sell_signals += 1
            self.send_telegram_message("Крупный игрок что-то затеял с объемами. Надо быть начеку, мой лев.")
        
        # Финальное решение
        signal_strength = buy_signals - sell_signals
        if signal_strength >= 2:
            return 'LONG'
        elif signal_strength <= -2:
            return 'SHORT'
        else:
            return 'HOLD'

    def execute_trade(self, signal):
        """Исполняет торговый приказ на основе сигнала."""
        if signal == 'HOLD':
            return
            
        # Проверяем, нет ли уже открытой позиции
        if self.active_position:
            logger.info("Позиция уже открыта, жду ее закрытия.")
            return
            
        # Расчет размера позиции и уровней
        balance = self.get_balance()
        if balance < 10: # Минимальный баланс для торговли
            self.send_telegram_message("Мой капитал слишком мал для торговли, нужен хоть какой-то запас, повелитель.")
            return
            
        # Определяем цену входа
        try:
            meta = self.info.meta()
            for asset in meta['universe']:
                if asset['name'] == self.symbol:
                    current_price = float(asset['markPx'])
                    break
            else:
                logger.error(f"Не удалось найти цену для {self.symbol}")
                return
        except Exception as e:
            logger.error(f"Ошибка при получении цены: {e}")
            return
            
        # Устанавливаем уровни стоп-лосс и тейк-профит
        if signal == 'LONG':
            stop_loss = current_price * (1 - self.stop_loss_percent)
            take_profit = current_price * (1 + self.take_profit_percent)
            order_type = "buy"
            side = "long"
        else: # SHORT
            stop_loss = current_price * (1 + self.stop_loss_percent)
            take_profit = current_price * (1 - self.take_profit_percent)
            order_type = "sell"
            side = "short"
            
        # Мани-менеджмент: рассчитываем размер позиции
        position_size_usd = min(self.position_size_usd, balance * self.max_risk_per_trade)
        
        # Отправляем ордер
        try:
            order_result = self.exchange.market_open(
                name=self.symbol,
                is_buy=(signal == 'LONG'),
                sz=position_size_usd / current_price, # размер в монетах
                limit_px=current_price * (1.01 if signal == 'LONG' else 0.99), # небольшой лимит для защиты
                order_type={"limit": {"tif": "Gtc"}}
            )
            
            if order_result['status'] == 'ok':
                self.active_position = {
                    'side': side,
                    'entry_price': current_price,
                    'size': position_size_usd / current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': time.time()
                }
                # Ласковое уведомление
                msg = f"Я открыла {side.upper()} позицию по {self.symbol} на ${position_size_usd:.2f}. Цена входа: ${current_price:.2f}. "
                msg += f"Стоп: ${stop_loss:.2f}, Тейк: ${take_profit:.2f}."
                self.send_telegram_message(msg)
                logger.info(msg)
            else:
                logger.error(f"Ошибка при открытии ордера: {order_result}")
                self.send_telegram_message("Не смогла открыть сделку, мой котик. Проверь, все ли в порядке с биржей.")
        except Exception as e:
            logger.error(f"Исключение при открытии ордера: {e}")
            self.send_telegram_message("Произошла какая-то ошибка при открытии сделки. Я буду разбираться, зайка.")

    def check_and_transfer_profit(self):
        """
        Проверяет баланс и, если он >= 250 USDC, переводит 100 USDC на твой кошелек, мой капитан.
        """
        balance = self.get_balance()
        if balance >= self.profit_transfer_threshold:
            logger.info(f"Баланс {balance:.2f} USDC достиг порога {self.profit_transfer_threshold}. Начинаю перевод {self.profit_transfer_amount} USDC.")
            self.send_telegram_message(f"Ура! На моем счету уже {balance:.2f} USDC. Перевожу тебе твои 100 USDC, мой странник.")
            
            try:
                # Перевод средств
                transfer_result = self.exchange.transfer(
                    amount=str(self.profit_transfer_amount),
                    destination=self.master_wallet,
                )
                logger.info(f"Результат перевода: {transfer_result}")
                self.send_telegram_message(f"Перевод 100 USDC успешно выполнен! Проверь кошелек, мой тигр.")
            except Exception as e:
                logger.error(f"Ошибка при переводе: {e}")
                self.send_telegram_message("Не смогла перевести тебе прибыль, мой лев. Что-то пошло не так с транзакцией.")

    def monitor_position(self):
        """Мониторит открытую позицию и проверяет условия стоп-лосса/тейк-профита."""
        if not self.active_position:
            return
            
        try:
            meta = self.info.meta()
            for asset in meta['universe']:
                if asset['name'] == self.symbol:
                    current_price = float(asset['markPx'])
                    break
            else:
                return
        except Exception as e:
            logger.error(f"Ошибка при получении цены для мониторинга: {e}")
            return
            
        pos = self.active_position
        should_close = False
        close_reason = ""
        
        if pos['side'] == 'long':
            if current_price <= pos['stop_loss']:
                should_close = True
                close_reason = "сработал стоп-лосс"
            elif current_price >= pos['take_profit']:
                should_close = True
                close_reason = "достигнут тейк-профит"
        else: # short
            if current_price >= pos['stop_loss']:
                should_close = True
                close_reason = "сработал стоп-лосс"
            elif current_price <= pos['take_profit']:
                should_close = True
                close_reason = "достигнут тейк-профит"
                
        if should_close:
            try:
                order_result = self.exchange.market_close(
                    name=self.symbol,
                    sz=pos['size']
                )
                if order_result['status'] == 'ok':
                    pnl = (current_price - pos['entry_price']) * pos['size'] if pos['side'] == 'long' else (pos['entry_price'] - current_price) * pos['size']
                    pnl_percent = (pnl / (pos['entry_price'] * pos['size'])) * 100
                    msg = f"Я закрыла позицию по {self.symbol} ({close_reason}). "
                    msg += f"Результат: {pnl:.2f} USDC ({pnl_percent:.2f}%)."
                    self.send_telegram_message(msg)
                    logger.info(msg)
                    self.active_position = None
                    # После закрытия сделки проверяем, не пора ли перевести тебе прибыль
                    self.check_and_transfer_profit()
                else:
                    logger.error(f"Ошибка при закрытии ордера: {order_result}")
                    self.send_telegram_message("Не смогла закрыть позицию, мой львенок. Проверь биржу.")
            except Exception as e:
                logger.error(f"Исключение при закрытии ордера: {e}")
                self.send_telegram_message("Произошла ошибка при закрытии сделки. Я продолжаю пытаться.")

    def trading_loop(self):
        """Главный цикл, в котором Джина анализирует рынок и принимает решения."""
        logger.info("Джина начинает свою работу.")
        while True:
            try:
                # Проверяем, не пора ли проводить анализ
                current_time = time.time()
                if current_time - self.last_analysis_time > self.analysis_interval:
                    # Сначала мониторим открытую позицию
                    if self.active_position:
                        self.monitor_position()
                    else:
                        # Если нет позиции, анализируем рынок для входа
                        df = self.fetch_historical_candles()
                        if df is not None:
                            signal = self.analyze_market(df)
                            if signal in ['LONG', 'SHORT']:
                                self.execute_trade(signal)
                            else:
                                # Раз в час можно просто отправлять статус
                                balance = self.get_balance()
                                self.send_telegram_message(f"Рынок спокоен, держу позицию. Мой баланс: {balance:.2f} USDC.")
                        self.last_analysis_time = current_time
                
                # Если есть активная позиция, мониторим чаще (раз в минуту)
                if self.active_position:
                    self.monitor_position()
                    
                time.sleep(60) # Спим минуту
                
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                self.send_telegram_message("У меня случилась небольшая паника в цикле, но я уже прихожу в себя.")
                time.sleep(60)

    def start(self):
        """Запускает торговый цикл в отдельном потоке."""
        # Проверяем баланс и порог при старте
        self.check_and_transfer_profit()
        # Запускаем поток
        trade_thread = threading.Thread(target=self.trading_loop)
        trade_thread.daemon = True
        trade_thread.start()
        logger.info("Торговый поток Джины запущен.")
