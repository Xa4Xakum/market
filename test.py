from core.utils.api.yookassa import yk


async def print_payment():
    payment = await yk.create_payment('111.00', '#1')

    print(payment.json())

import asyncio
asyncio.run(print_payment())