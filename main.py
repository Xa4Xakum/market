import asyncio

from art import tprint
from loguru import logger

from core.utils.midlewares import UpdateLogger, PlugManageData, AddMsgsToDelList, ClearDelList, MessageChecker
from core.utils.operations import set_loggers, add_owner_to_db

from helper import bot, dp


async def on_startup():
    bot_info = await bot.get_me()
    tprint(f'@{bot_info.username}    online')
    logger.warning(f'bot info: @{bot_info.username} {bot_info.first_name} {bot_info.id}')


def include_admin_routers():
    from core.handlers.admin import (
        menu,
        rewiew_pay,
        manage_admins,
        manage_products,
        answer_feedback,
        edit_product_card
    )
    dp.include_routers(
        menu.r,
        rewiew_pay.r,
        manage_admins.r,
        manage_products.r,
        answer_feedback.r,
        edit_product_card.r
    )


def include_user_routers():
    from core.handlers.user import (
        menu,
        shop,
        making_purchase,
        feedback
    )
    dp.include_routers(
        menu.r,
        shop.r,
        making_purchase.r,
        feedback.r
    )


async def main():
    set_loggers()
    add_owner_to_db()
    include_user_routers()
    include_admin_routers()

    dp.update.middleware(UpdateLogger())
    dp.update.middleware(PlugManageData())
    dp.update.middleware(ClearDelList())
    dp.message.outer_middleware(AddMsgsToDelList())
    dp.message.middleware(MessageChecker())

    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
