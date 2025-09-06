from aiogram import Bot


class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    async def send_message(self, message: str):
        await self.bot.send_message(chat_id=self.chat_id, text=message)
