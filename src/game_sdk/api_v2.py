import os

class Wallet:
    def __init__(self, private_key, rpc_url):
        self.private_key = private_key
        self.rpc_url = rpc_url
        # В будущем здесь будет адрес, полученный из ключа
        self.address = "0x..." 

    def get_balance(self):
        """Проверка баланса в сети Base"""
        return "1.0 ETH" # Заглушка, пока не подключили Web3

    def trade(self, side, amount, symbol="ETH"):
        """Команда на совершение сделки"""
        print(f"💰 БЛОКЧЕЙН: Выполняю {side} {amount} {symbol} на Base...")
        print(f"Использую RPC: {self.rpc_url}")
        # Здесь будет реальный код отправки транзакции
        return True
