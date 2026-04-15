import os
from web3 import Web3

class Wallet:
    def __init__(self, private_key, rpc_url):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address

    def get_balance(self):
        balance_wei = self.w3.eth.get_balance(self.address)
        return self.w3.from_wei(balance_wei, 'ether')

    def execute_trade(self, side, amount_in_eth):
        """Реальный свап ETH на токен (или обратно)"""
        print(f"ПОДПИСЫВАЮ ТРАНЗАКЦИЮ: {side} {amount_in_eth} ETH...")
        
        try:
            nonce = self.w3.eth.get_transaction_count(self.address)
            
            # Базовые параметры транзакции
            tx = {
                'nonce': nonce,
                'to': '0x...' , # Адрес контракта роутера биржи (например Uniswap)
                'value': self.w3.to_wei(amount_in_eth, 'ether'),
                'gas': 250000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': 8453 # ID сети Base
            }
            
            # Подпись и отправка
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"ТРАНЗАКЦИЯ ОТПРАВЛЕНА: {self.w3.to_hex(tx_hash)}")
            return True
        except Exception as e:
            print(f"ОШИБКА БЛОКЧЕЙНА: {e}")
            return False
