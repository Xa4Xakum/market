from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from core.utils.api.yookassa import yk
from core.utils.keyboards import Keyboards
from core.utils.database.database import db
from core.utils.operations import try_delete
from core.utils.states import MakingPurchaseStates
from core.utils.manage_data import ManageData
from core.utils.filters import ChatType

from config import PurchaseStatuses, Config

from helper import bot

r = Router()
r.message.filter(ChatType('private'))


@r.callback_query(F.data == Keyboards.buy.callback_data, StateFilter('*'))
async def buy(call: CallbackQuery, state: FSMContext, md: ManageData):
    to_del = await call.message.answer(
        'Отправьте адресс пункта СДЭК, куда должна быть отправлена посылка(Город, улица, номер дома)'
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(MakingPurchaseStates.get_address)


@r.message(F.text, StateFilter(MakingPurchaseStates.get_address))
async def get_adress(msg: Message, state: FSMContext, md: ManageData):
    md.update_data(address=msg.text)
    to_del = await msg.answer('На чье имя посылка? Фамилия, имя, отчество')
    md.add_msg_to_del_list(to_del)
    await state.set_state(MakingPurchaseStates.get_fullname)


@r.message(F.text, StateFilter(MakingPurchaseStates.get_fullname))
async def get_fullname(msg: Message, state: FSMContext, md: ManageData):
    md.update_data(fullname=msg.text)
    to_del = await msg.answer('Отправьте номер телефона получателя')
    md.add_msg_to_del_list(to_del)
    await state.set_state(MakingPurchaseStates.get_phone_number)


@r.message(F.text, StateFilter(MakingPurchaseStates.get_phone_number))
async def get_phone_number(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    md.update_data(phone_number=msg.text)
    data = md.get_data()
    purchase_id = db.add_purchase(
        user_id=msg.from_user.id,
        status=PurchaseStatuses.waiting_money.value,
        address=data['address'],
        fullname=data['fullname'],
        phone_number=data['phone_number']
    )
    price = 0
    prodicts_dict = md.get_product_dict()
    for product, count in prodicts_dict.items():
        db.add_purchase_products(
            purchase_id=purchase_id,
            product_id=product,
            count=count
        )
        product = db.get_product_by_id(product)
        price += product.price * count
    db.edit_purchase_amount(
        purchase_id=purchase_id,
        amount=price
    )
    price = f'{str(price)}.00'
    to_del = await msg.answer('Обрабатываю...')
    payment = await yk.create_payment(
        amount=price,
        description=f'#{purchase_id} от @{msg.from_user.username}'
    )
    await try_delete(to_del)
    if payment is None:
        to_del = await msg.answer(
            'Не удалось создать платеж, попробуйте позже'
            '(ваши данные сохранены, вы сможете оплатить из вкладки "мои покупки")',
            reply_markup=kb.inline_markup_from_buttons(kb.to_user_menu())
        )
        md.add_msg_to_del_list(to_del)
    else:
        db.edit_purchase_payment_id(purchase_id=purchase_id, payment_id=payment['id'])
        to_del = await msg.answer(
            f'Оплатить покупку можно по этой ссылке - {payment.confirmation["confirmation_url"]}\n'
            'При подтверждении оплаты деньги будут заморожены на срок до 7 дней до рассмотрения запроса фасовщиком. '
            'В случае, если мы не сможем отправить ваш заказ, либо никто не рассмотрит ваш запрос, деньги будут разморожены',
            reply_markup=kb.check_pay_markup(purchase_id)
        )
        md.add_msg_to_del_list(to_del)

    await state.set_state(None)


@r.callback_query(F.data.startswith(f'{Keyboards.check_pay.callback_data}_'), StateFilter('*'))
async def check_pay(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    conf = Config()
    kb = Keyboards()
    purchase_id = int(call.data.split('_')[1])
    purchase = db.get_purchase(purchase_id)
    if purchase is None:
        to_del = await call.message.answer(
            'Извините, но в моей бд нет этой заявки на покупку...',
            reply_markup=kb.inline_markup_from_buttons(kb.to_user_menu)
        )
        md.add_msg_to_del_list(to_del)
        return
    payment = yk.get_payment(purchase.payment_id)
    markup_for_user = kb.inline_markup_from_buttons(kb.to_user_menu)
    if payment is None:
        to_del = await call.message.answer(
            'Юкасса не сохранила данные об оплате этого заказа... Попробуйте сделать заказ еще раз',
            reply_markup=markup_for_user
        )
        md.add_msg_to_del_list(to_del)
        return
    if payment['status'] == 'pending':
        payment = await yk.create_payment(
            amount=f'{purchase.amount}.00',
            description=f'#{purchase_id} от @{call.from_user.username}'
        )
        if payment is None:
            url = 'не удалось создать оплату, попробуйте позже'
            reply_markup = markup_for_user
        else:
            db.edit_purchase_payment_id(purchase_id=purchase_id, payment_id=payment['id'])
            url = payment.confirmation["confirmation_url"]
            reply_markup = kb.check_pay_markup(purchase_id)
        to_del = await call.message.answer(
            f'Заказ еще не получил оплату, оплатить можно по этой ссылке - {url}',
            reply_markup=reply_markup
        )
        md.add_msg_to_del_list(to_del)
        return
    if payment['status'] == 'canceled':
        to_del = await call.message.answer(
            'Оплата была отменена, деньги не списаны',
            reply_markup=markup_for_user
        )
        md.add_msg_to_del_list(to_del)
        return
    if payment['status'] not in ['waiting_for_capture', 'succeeded']:
        to_del = await call.message.answer(
            'Случилась непредвиденная ошибка...',
            reply_markup=markup_for_user
        )
        md.add_msg_to_del_list(to_del)
        return

    products = db.get_purchase_products(purchase_id)
    text_for_admin = f'Заявка на покупку #{purchase_id} от @{call.from_user.username}:\n\n'
    with_none_product = False

    for purchase_product in products:
        product = db.get_product_by_id(purchase_product.product_id)

        if product is None:
            category = 'Товар не найден, покупка отменена'
            name = 'Товар не найден, покупка отменена'
            with_none_product = True
        else:
            category = product.category
            name = product.name

        text_for_admin += (
            f'ID товара: {purchase_product.product_id}\n'
            f'Категория: {category}\n'
            f'Название: {name}\n'
            f'Количетсво: {purchase_product.count}\n\n'
        )

    text_for_admin += (
        f'Адресс: {purchase.address}\n'
        f'Полное имя: {purchase.fullname}\n'
        f'Номер телефона: {purchase.phone_number}\n\n'
    )
    if with_none_product:
        to_del = await call.message.answer(
            'Поскольку покупка содержит удаленные из бд товары, она была автоматически отменена',
            reply_markup=markup_for_user
        )
        await yk.cancel(purchase.yookassa_id)
        db.edit_purchase_status(
            purchase_id,
            PurchaseStatuses.canceled.value
        )
        md.add_msg_to_del_list(to_del)
        return
    for i in products:
        product = db.get_product_by_id(i.product_id)
        db.edit_product_count(
            i.product_id,
            product.count - i.count
        )

    db.edit_purchase_status(
        purchase_id,
        PurchaseStatuses.on_review.value
    )
    await bot.send_message(
        chat_id=conf.get_rewiew_chat_id(),
        text=text_for_admin,
        reply_markup=kb.rewiew_buy(
            purchase_id=purchase_id,
            with_none_product=with_none_product
        ),
        parse_mode='html'
    )
    to_del = await call.message.answer(
        'Товар успешно оплачен, спасибо за покупку! Ожидайте отправки',
        reply_markup=kb.inline_markup_from_buttons(kb.to_user_menu)
    )
    md.update_data(product_dict={})
    md.add_msg_to_del_list(to_del)
