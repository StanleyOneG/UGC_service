import os
import telegram
import asyncio

token = os.environ["API_TOKEN"]
chat_id = os.environ["CHAT_ID"]
text = "CI tests passed successfully!"


async def send_msg(token: str, chat_id: str, text: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=text)


asyncio.run(send_msg(token, chat_id, text))
