class GAMEClient:
    def __init__(self, api_key):
        self.api_key = api_key
        print("DEBUG: GAME Client инициализирован и готов к работе.")

    def get_status(self):
        return "Online"
