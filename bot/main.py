import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
from tasks import send_daily_message

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["send"])
async def cmd_send(message: types.Message):
    from tasks import send_daily_message
    send_daily_message.delay()
    await message.reply("Daily message qayta yuborildi!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
