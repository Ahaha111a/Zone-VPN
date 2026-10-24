import asyncio, logging
from aiogram import Bot, Dispatcher
from config import settings
from app.db import Database
from app.handlers import router
from app.jobs import expiry_worker

async def main():
    if not settings.token:
        raise RuntimeError("BOT_TOKEN не задан. Заполните .env.")
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
    db = Database(settings.db_path)
    await db.init()
    bot = Bot(settings.token)
    dp = Dispatcher()
    dp["db"] = db
    dp.include_router(router)
    job = asyncio.create_task(expiry_worker(bot, db))
    try:
        await dp.start_polling(bot)
    finally:
        job.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
