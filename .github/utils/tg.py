"""
Telegram module.

Used to send message in telegram
"""
import os

import telegram
import asyncio

token = os.environ['API_TOKEN']
chat_id = os.environ['CHAT_ID']
text = 'CI tests passed successfully!'


async def send_msg(token: str, chat_id: str, text: str) -> None:
    """
    Send message to a specific telegram chat.

    Args:
         token (str): Token for telegram API
         chat_id (str): Chat id where to send message
         text (str) : Text to be sent into telegram chat
    """
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=text)


asyncio.run(send_msg(token, chat_id, text))
