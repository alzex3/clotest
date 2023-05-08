import asyncio
import logging

from aiogram import Bot, Dispatcher
from environs import Env


async def main():
    env = Env()
    env.read_env()

    import handlers

    bot = Bot(token=env("TELEGRAM_TOKEN"))
    dp = Dispatcher()

    dp.include_router(handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
