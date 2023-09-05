from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from making_baking_bot import register_handlers
from config import *


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="/deliveries", description="Скинуть доставки"
        ),
        BotCommand(
            command="/delivery_calculation",
            description="Рассчитать стоимость доставки"
        )
    ]
    await bot.set_my_commands(commands)


# Объявление и инициализация объектов бота и диспетчера.

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(dp):
    # Регистрация хэндлеров
    register_handlers(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


async def on_shutdown(dp):
    await bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()


executor.start_polling(dp, on_startup=on_startup)
