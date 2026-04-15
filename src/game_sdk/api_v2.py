import os

class Wallet:
    def __init__(self, private_key, rpc_url):
        self.private_key = private_key
        self.rpc_url = rpc_url

    def execute_trade(self, side, amount):
        # В будущем здесь будет Web3.py для реального свапа на Uniswap
        print(f">>> ИСПОЛНЕНО: {side} на {amount}$ в сети Base")
        return True
