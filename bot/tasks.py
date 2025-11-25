import os
import asyncio
import logging
from aiogram import Bot
from celery import shared_task
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
PRE_MESSAGE = os.getenv("PRE_MESSAGE")
DAILY_MESSAGE = os.getenv("DAILY_MESSAGE")

logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, loop=loop)

bot_messages = []  # bot yuborgan message_id larini saqlash

@shared_task
def send_pre_message():
    async def _send():
        msg = await bot.send_message(TARGET_CHAT_ID, PRE_MESSAGE, parse_mode="HTML")
        bot_messages.append(msg.message_id)
        logger.info(f"Pre-message sent: {msg.message_id}")
    loop.run_until_complete(_send())

@shared_task
def send_daily_message():
    async def _send():
        msg = await bot.send_message(TARGET_CHAT_ID, DAILY_MESSAGE, parse_mode="HTML")
        bot_messages.append(msg.message_id)
        logger.info(f"Daily message sent: {msg.message_id}")
    loop.run_until_complete(_send())

@shared_task
def delete_bot_messages():
    async def _delete():
        global bot_messages
        for msg_id in bot_messages:
            try:
                await bot.delete_message(TARGET_CHAT_ID, msg_id)
                logger.info(f"Deleted bot message: {msg_id}")
            except Exception as e:
                logger.exception(f"Failed to delete message {msg_id}: {e}")
        bot_messages = []
    loop.run_until_complete(_delete())
