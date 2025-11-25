import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# load env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
FORBIDDEN_WORDS = [w.strip().lower() for w in os.getenv("FORBIDDEN_WORDS","").split(",") if w.strip()]
DAILY_MESSAGE = os.getenv("DAILY_MESSAGE", "Assalomu alaykum! Bu asosiy xabar.")
PRE_MESSAGE = os.getenv("PRE_MESSAGE", "Xabar 5 daqiqa qoldi.")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN murojat etilmagan. .env faylini tekshiring.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, loop=loop)
dp = Dispatcher(bot)


@dp.message_handler()
async def get_chat_id(message: types.Message):
    await message.reply(f"Guruh chat ID: {message.chat.id}")

# global flag for forbidden words
paused = False  # True bo'lsa 12:00 xabari yuborilmaydi


async def send_daily_message(text: str):
    """Yuborishdan oldin paused holatini tekshiradi."""
    global paused
    logger.info(f"send_daily_message called; paused={paused}")
    if paused and text == DAILY_MESSAGE:
        logger.info("Daily message paused. Not sending.")
        return
    try:
        await bot.send_message(TARGET_CHAT_ID, text, parse_mode="HTML")
        logger.info("Message sent: %s", text)
    except Exception as e:
        logger.exception("Failed to send message: %s", e)


def schedule_jobs(scheduler):
    tz = pytz.timezone(TIMEZONE)

    # 11:55 - pre-message
    scheduler.add_job(send_daily_message, CronTrigger(hour=11, minute=55, timezone=tz),
                      args=[PRE_MESSAGE], id="pre_msg", replace_existing=True)

    # 12:00 - daily message
    scheduler.add_job(send_daily_message, CronTrigger(hour=9, minute=58, timezone=tz),
                      args=[DAILY_MESSAGE], id="daily_msg", replace_existing=True)


    logger.info("Scheduled jobs for 11:55 and 12:00 (%s)", TIMEZONE)


@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.reply(
        "Salom! Men guruhga xabar yuboruvchi botman. "
        "12:00 xabarlar FORBIDDEN_WORDS ga bog'liq bloklanadi."
    )


@dp.message_handler(lambda message: message.chat.type in ['group', 'supergroup'], content_types=types.ContentTypes.TEXT)
async def handle_group_text(message: types.Message):
    """Guruhdagi matnni tekshiradi; forbidden word topilsa 12:00 xabari to'xtatiladi."""
    global paused
    text = (message.text or "").lower()
    if not text or not FORBIDDEN_WORDS:
        return

    for bad in FORBIDDEN_WORDS:
        if bad and bad in text:
            paused = True
            await message.reply(f"12:00 xabari to'xtatildi — taqiqlangan so'z topildi: '{bad}'")
            logger.info("Paused because forbidden word found: %s", bad)
            return


@dp.message_handler(commands=["resume"])
async def cmd_resume(message: types.Message):
    """12:00 xabarlarini qayta yoqish."""
    global paused
    paused = False
    await message.reply("12:00 dagi xabarlar qayta yoqildi.")


@dp.message_handler(commands=["status"])
async def cmd_status(message: types.Message):
    """Current pause status."""
    global paused
    await message.reply(f"Paused: {paused}")


async def on_startup(dp):
    # start scheduler
    scheduler = AsyncIOScheduler()
    schedule_jobs(scheduler)
    scheduler.start()
    logger.info("Scheduler started")


async def on_shutdown(dp):
    logger.info("Shutting down..")
    await bot.close()


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
