from aiogram import Router, F
from aiogram.types import CallbackQuery

from loguru import logger

from core.utils.api.yookassa import yk
from core.utils.keyboards import Keyboards
from core.utils.database.database import db
from core.utils.operations import try_delete
from core.utils.filters import Admin, WithPrivilegie

from config import PurchaseStatuses, RolePrivilegies

from helper import bot

r = Router()
r.callback_query.filter(Admin())
r.message.filter(Admin())


@r.callback_query(F.data.startswith(f'{Keyboards.accept.callback_data}_'), WithPrivilegie(RolePrivilegies.privilegie_rewiew_pay))
async def accept_pay(call: CallbackQuery):
    purchase_id = int(call.data.split('_')[1])
    purchase = db.get_purchase(purchase_id)
    products = db.get_purchase_products(purchase_id)
    with_none_product = False
    kb = Keyboards()

    for purchase_product in products:
        product = db.get_product_by_id(purchase_product.product_id)
        if product is None:
            with_none_product = True
    user_markup = kb.inline_markup_from_buttons(kb.to_user_menu)
    if with_none_product:
        await yk.cancel(purchase.yookassa_id)
        await call.answer('Поскольку покупка содержит удаленные товары, он была отменена', show_alert=True)
        await bot.send_message(
            chat_id=purchase.user_id,
            text='Ваша покупка была отменена по причине: товар удален. Деньги не были списаны',
            reply_markup=user_markup
        )
        db.edit_purchase_status(
            purchase_id,
            PurchaseStatuses.canceled.value
        )
        await try_delete(call.message)
        return

    await call.answer('Списываю...')
    captured = await yk.capture(purchase.payment_id)
    if not captured:
        await call.answer(
            'Не удалось списать деньги, попробуйте позже...',
            True
        )
        return
    await call.answer('Списано')
    admin = db.get_admin(call.from_user.id)
    try:
        await call.message.edit_text(text=f'{call.message.text}\n\nПринял(а) {admin.role} {admin.name}')
    except Exception as e:
        logger.error(f'Не удалось изменить сообщение на этапе принятия оплаты по причине {e}')

    db.edit_purchase_status(
        purchase_id,
        PurchaseStatuses.geted_money.value
    )
    await bot.send_message(
        chat_id=purchase.user_id,
        text='Ваша покупка обработана, ожидайте отправки',
        reply_markup=user_markup
    )


@r.callback_query(F.data.startswith(f'{Keyboards.reject.callback_data}_'), WithPrivilegie(RolePrivilegies.privilegie_rewiew_pay))
async def reject_pay(call: CallbackQuery):
    purchase_id = int(call.data.split('_')[1])
    purchase = db.get_purchase(purchase_id)
    canceled = await yk.cancel(purchase.payment_id)
    kb = Keyboards()

    if not canceled:
        await call.answer('Не удалось отменить покупку, попробуйте позже...', True)
        return

    products = db.get_purchase_products(purchase_id)

    for purchase_product in products:
        product = db.get_product_by_id(purchase_product.product_id)
        if product is not None:
            db.edit_product_count(
                product.product_id,
                product.count + purchase_product.count
            )

    db.edit_purchase_status(
        purchase_id=purchase_id,
        status=PurchaseStatuses.canceled.value
    )

    await bot.send_message(
        chat_id=purchase.user_id,
        text='Вашу покупку отменил фасовщик. Деньги не были списаны',
        reply_markup=kb.inline_markup_from_buttons(kb.to_user_menu)
    )
    admin = db.get_admin(call.from_user.id)
    try:
        await call.message.edit_text(text=f'{call.message.text}\n\nОтменил(а) {admin.role} {admin.name}')
    except Exception as e:
        logger.error(f'Не удалось изменить сообщение на этапе принятия оплаты по причине {e}')
