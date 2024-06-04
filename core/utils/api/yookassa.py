import asyncio

import uuid
from loguru import logger
from yookassa import Configuration, Payment

from config import Config
from helper import bot



class Yookassa():


    def __init__(self) -> None:
        conf = Config()
        Configuration.account_id = conf.get_yookassa_shop_id()
        Configuration.secret_key = conf.get_yookassa_token()


    async def create_payment(
            self,
            amount: str,
            description: str
    ):
        bot_info = await bot.get_me()
        for i in range(10):
            try:
                return Payment.create({
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": f"https://t.me/{bot_info.username}"
                    },
                    "capture": False,
                    "description": description
                }, idempotency_key=str(uuid.uuid4())
                )
            except Exception as e:
                logger.error(f'Ошибка создания платежа ({e}), попытка #{i + 1}, новая попытка через 10 секунд...')
                await asyncio.sleep(10)


    def get_payment(
            self,
            payment_id: str
    ):
        return Payment.find_one(str(payment_id))


    async def capture(
            self,
            payment_id: str
    ):
        for i in range(10):
            try:
                Payment.capture(payment_id)
                return True
            except Exception as e:
                logger.error(f'Ошибка списания платежа ({e}), попытка #{i + 1}, новая попытка через 10 секунд...')
                await asyncio.sleep(10)

        return False


    async def cancel(
            self,
            payment_id: str
    ):
        for i in range(10):
            try:
                Payment.cancel(payment_id)
                return True
            except Exception as e:
                logger.error(f'Ошибка отмены платежа ({e}), попытка #{i + 1}, новая попытка через 10 секунд...')
                await asyncio.sleep(10)

        return False


yk = Yookassa()
