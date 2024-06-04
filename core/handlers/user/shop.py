from math import ceil

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from loguru import logger

from core.utils.keyboards import Keyboards
from core.utils.database.database import db
from core.utils.filters import ChatType
from core.utils.api.yookassa import yk
from core.utils.operations import (
    make_product_text,
    is_int,
    get_basket_products_info,
    calculate_category_page,
    calculate_product_page,
    send_media_group
)
from core.utils.states import Shop
from core.utils.manage_data import ManageData

from config import PurchaseStatuses, conf
from helper import bot

r = Router()
r.message.filter(ChatType('private'))


@r.callback_query(F.data == Keyboards.to_shop.callback_data)
async def to_shop(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    kb = Keyboards()
    to_del = await call.message.answer('Выберите действие:', reply_markup=kb.market_markup())
    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.find_by_id.callback_data)
async def fing_by_id(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте id требуемого товара',
        reply_markup=kb.one_button_inline_markup(text='Назад', callback_data=kb.to_shop.callback_data)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.get_id_to_find)


@r.message(
    F.text,
    StateFilter(Shop.get_id_to_find)
)
async def get_id_to_find(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    if not is_int(msg.text):
        to_del = await msg.answer(
            text='Сообщение не является числом, возможно вы написали id с символом #, попробуйте еще раз',
            reply_markup=kb.one_button_inline_markup(text='Назад', callback_data=kb.to_shop.callback_data)
        )
        md.add_msg_to_del_list(to_del)
        return

    product = db.get_product_by_id(int(msg.text))
    if product is None:
        to_del = await msg.answer(
            text='В моей бд нет товара с таким id, убедитесь в правильности и попробуйте еще раз',
            reply_markup=kb.one_button_inline_markup(text='Назад', callback_data=kb.to_shop.callback_data)
        )
        md.add_msg_to_del_list(to_del)
        return

    text = make_product_text(
        product=product,
        page=''
    )

    media = db.get_all_media_by_product_id(int(msg.text))
    media_to_send = {}
    for i in media:
        media_to_send[i.file_id] = i.media_type
    to_del = await send_media_group(
        chat_id=msg.chat.id,
        media=media_to_send
    )
    md.add_msg_to_del_list(to_del)

    try:
        to_del = await msg.answer(
            text=text,
            reply_markup=kb.make_finded_product_makrup(int(msg.text)),
            parse_mode='html'
        )
    except Exception as e:
        logger.error(f'Не удалось отправить карточку товара #{product.product_id} по причине {e}')
        to_del = await msg.answer(
            text='Не удалось отправить карточку товара. Простите за неудобства, мы уже работаем над этой проблемой',
            reply_markup=kb.one_button_inline_markup(
                text='Назад',
                callback_data=kb.to_shop.callback_data
            )
        )
        await bot.send_message(
            chat_id=conf.get_feedback_chat_id(),
            text=(
                f'Не удалось отправить карточку товара #{product.product_id} пользователю @{msg.from_user.username} '
                f'по причине {e}. Убедитесь, что текст карточки не содержит неподдерживаемых тегов.'
            )
        )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_product)


@r.callback_query(
    F.data.in_([
        Keyboards.next_page_category.callback_data,
        Keyboards.previous_page_category.callback_data
    ]), StateFilter(Shop.choose_category)
)
@r.callback_query(F.data == Keyboards.categories.callback_data, StateFilter('*'))
async def choose_category(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    page = md.get_category_page(call.data)

    categories = db.get_all_categories()
    categories = [i.name for i in categories]
    pages_count = ceil(len(categories) / 10)

    page = calculate_category_page(
        call_data=call.data,
        pages_count=pages_count,
        page=page
    )

    md.update_data(category_page=page)
    categories_min = max(0, page - 1) * 10
    categories_max = min(page * 10, len(categories))

    to_del = await call.message.answer(
        text=f'Стр. {page}/{pages_count}. Выберите категорию:',
        reply_markup=kb.make_category_markup(
            categories=categories[categories_min:categories_max]
        )
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_category)


@r.callback_query(
    F.data.not_in([
        Keyboards.next_page_category.callback_data,
        Keyboards.previous_page_category.callback_data,
        Keyboards.to_shop.callback_data
    ]), StateFilter(Shop.choose_category)
)
@r.callback_query(
    F.data.in_([
        Keyboards.next_page_product.callback_data,
        Keyboards.previous_page_product.callback_data,
        Keyboards.to_products.callback_data
    ]), StateFilter(Shop.choose_product)
)
@r.callback_query(F.data == Keyboards.to_products.callback_data, StateFilter(Shop.get_count))
async def choose_product(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    page = md.get_product_page()
    category = md.get_category(call.data)
    products = db.get_all_products_with_category(category)
    pages_count = len(products)
    page = calculate_product_page(
        call_data=call.data,
        pages_count=pages_count,
        page=page
    )
    md.update_data(product_page=page)
    if len(products) < 1:
        to_del = await call.message.answer(
            'В этой категории пока еще нет товаров :(',
            reply_markup=kb.one_button_inline_markup(
                text='К категориям',
                callback_data=kb.categories.callback_data
            )
        )
        md.add_msg_to_del_list(to_del)
        return

    product = products[page - 1]
    product_id = product.product_id

    text = make_product_text(
        product=product,
        page=f'{page}/{pages_count}'
    )

    media = db.get_all_media_by_product_id(product_id)
    media_to_send = {}
    for i in media:
        media_to_send[i.file_id] = i.media_type
    to_del = await send_media_group(
        chat_id=call.message.chat.id,
        media=media_to_send
    )
    md.add_msg_to_del_list(to_del)
    try:
        to_del = await call.message.answer(
            text=text,
            reply_markup=kb.make_product_makrup(product_id),
            parse_mode='html'
        )
    except Exception as e:
        logger.error(f'Не удалось отправить карточку товара #{product.product_id} по причине {e}')
        to_del = await call.message.answer(
            text='Не удалось отправить карточку товара. Простите за неудобства, мы уже работаем над этой проблемой',
            reply_markup=kb.one_button_inline_markup(
                text='Назад',
                callback_data=kb.categories.callback_data
            )
        )
        await bot.send_message(
            chat_id=conf.get_feedback_chat_id(),
            text=(
                f'Не удалось отправить карточку товара #{product.product_id} пользователю @{call.from_user.username} '
                f'по причине {e}. Убедитесь, что текст карточки не содержит неподдерживаемых тегов.'
            )
        )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_product)


@r.callback_query(
    F.data.not_in([
        Keyboards.next_page_product.callback_data,
        Keyboards.previous_page_product.callback_data,
        Keyboards.open_basket.callback_data,
        Keyboards.to_products.callback_data,
        Keyboards.del_product.callback_data,
        Keyboards.clear_basket.callback_data,
        Keyboards.edit_product_count.callback_data,
        Keyboards.buy.callback_data,
        Keyboards.to_shop.callback_data
    ]), StateFilter(Shop.choose_product)
)
async def get_product(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    product = db.get_product_by_id(int(call.data))
    if product is None:
        await call.answer('Извините, такого товара нет в моей бд...')
        return

    to_del = await call.message.answer(
        'Отправьте количество, которое хотите купить',
        reply_markup=kb.one_button_inline_markup(
            text='Назад',
            callback_data=kb.to_shop.callback_data
        )
    )

    await state.set_state(Shop.get_count)
    md.update_data(current_product=int(call.data))
    md.add_msg_to_del_list(to_del)


@r.message(F.text, StateFilter(Shop.get_count))
async def get_count(msg: Message, md: ManageData):
    kb = Keyboards()
    data = md.get_data()
    markup = kb.one_button_inline_markup(
        text='Назад',
        callback_data=kb.to_shop.callback_data
    )

    if len(msg.text.split()) != 1:
        to_del = await msg.answer('Отправьте только 1 число', reply_markup=markup)
        md.add_msg_to_del_list(to_del)
        return

    if not is_int(msg.text):
        to_del = await msg.answer('Отправьте именно число, без букв и пробелов', reply_markup=markup)
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) < 1:
        to_del = await msg.answer('Вы не можете купить меньше одного товара, пропробуйте еще раз', reply_markup=markup)
        md.add_msg_to_del_list(to_del)
        return

    product = db.get_product_by_id(data['current_product'])

    if product is None:
        to_del = await msg.answer('Извините, такого товара нет в моей бд...', reply_markup=markup)
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) > product.count:
        to_del = await msg.answer('Вы не можете купить больше, чем есть на складе', reply_markup=markup)
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) < product.minimum_to_sell:
        to_del = await msg.answer(f'Этот товар можно купить только от {product.minimum_to_sell} штук', reply_markup=markup)
        md.add_msg_to_del_list(to_del)
        return

    md.add_product_to_dict(data['current_product'], int(msg.text))

    to_del = await msg.answer(
        'Добавлено!',
        reply_markup=markup
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.open_basket.callback_data, StateFilter('*'))
async def open_basket(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    products_dict = md.get_product_dict()
    text = get_basket_products_info(products_dict=products_dict)
    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.basket_markup(products_dict),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_product)


@r.callback_query(F.data == Keyboards.del_product.callback_data, StateFilter('*'))
async def del_product(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    products_dict = md.get_product_dict()
    text = 'Отправьте ID товара, который хотите удалить из корзины. Товары в корзине:\n\n'
    text += get_basket_products_info(products_dict=products_dict)
    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.one_button_inline_markup(
            text='Назад',
            callback_data=Keyboards.open_basket.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.del_product)


@r.message(F.text, StateFilter(Shop.del_product))
async def get_product_for_del(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    products_dict = md.get_product_dict()
    if msg.text not in products_dict and int(msg.text) not in products_dict:
        to_del = await msg.answer(
            'В корзине нет продукта с таким ID',
            reply_markup=kb.basket_markup(products_dict),
            parse_mode='html'
        )
        md.add_msg_to_del_list(to_del)
        return

    md.del_product_from_product_dict(int(msg.text))
    to_del = await msg.answer(
        text='Товар удален!',
        reply_markup=kb.one_button_inline_markup(
            text='Назад',
            callback_data=Keyboards.open_basket.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_product)


@r.callback_query(F.data == Keyboards.clear_basket.callback_data, StateFilter('*'))
async def clear_basket(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    md.update_data(product_dict={})
    to_del = await call.message.answer(
        text='Корзина очищена!',
        reply_markup=kb.one_button_inline_markup(
            text='Назад',
            callback_data=Keyboards.open_basket.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_product)


@r.callback_query(F.data == Keyboards.edit_product_count.callback_data, StateFilter('*'))
async def edit_product_count(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    products_dict = md.get_product_dict()
    text = 'Отправьте ID товара, кол-во которого хотите изменить. Товары в корзине:\n\n'
    text += get_basket_products_info(products_dict=products_dict)
    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.one_button_inline_markup(
            text='Назад',
            callback_data=Keyboards.open_basket.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.get_product_to_edit)


@r.message(F.text, StateFilter(Shop.get_product_to_edit))
async def get_product_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    products_dict = md.get_product_dict()
    if msg.text not in products_dict and int(msg.text) not in products_dict:
        to_del = await msg.answer(
            'В корзине нет продукта с таким ID',
            reply_markup=kb.basket_markup(products_dict),
            parse_mode='html'
        )
        md.add_msg_to_del_list(to_del)
        return

    to_del = await msg.answer(
        text='Отправьте новое количество',
        reply_markup=kb.one_button_inline_markup(
            text='назад',
            callback_data=Keyboards.open_basket.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
    md.update_data(product_to_edit=msg.text)
    await state.set_state(Shop.get_count_to_edit)


@r.message(F.text, StateFilter(Shop.get_count_to_edit))
async def get_count_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_data()
    markup = kb.one_button_inline_markup(
        text='назад',
        callback_data=Keyboards.open_basket.callback_data
    )

    if not is_int(msg.text):
        to_del = await msg.answer(
            'Новое количество должно быть целым числом, попробуйте еще раз',
            reply_markup=markup
        )
        md.add_msg_to_del_list(to_del)
        return

    product = db.get_product_by_id(int(data['product_to_edit']))
    if int(msg.text) == 0:
        md.del_product_from_product_dict(data['product_to_edit'])
        to_del = await msg.answer(
            'Товар успешно удален!',
            reply_markup=markup
        )
        md.add_msg_to_del_list(to_del)
        return

    if product.minimum_to_sell > int(msg.text):
        to_del = await msg.answer(
            f'Минимальная покупка этого товара идет только от {product.minimum_to_sell} лотов. '
            'Попробуйте еще раз или вернитесь назад',
            reply_markup=markup
        )
        md.add_msg_to_del_list(to_del)
        return

    md.add_product_to_dict(int(data['product_to_edit']), int(msg.text))
    md.set_data(data)
    to_del = await msg.answer(
        'Количество успешно изменено!',
        reply_markup=markup
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(Shop.choose_product)


@r.callback_query(F.data == Keyboards.purchases_history.callback_data)
async def purchases_history(call: CallbackQuery, md: ManageData):
    kb = Keyboards()
    await call.answer('Ищу в базе данных...')
    purchase = db.get_all_user_purchases(call.from_user.id)
    for j in purchase:
        text = (
            f'ID покупки: #{j.purchase_id}\n'
            f'Общая стоимость: {j.amount} р.\n'
            f'Статус: {j.status}\n\n'
        )
        products = db.get_purchase_products(purchase_id=j.purchase_id)
        with_none_product = False
        for i in products:
            text += (
                f'ID товара: <code>{i.product_id}</code>\n'
            )
            product = db.get_product_by_id(i.product_id)
            if product is None:
                text += 'Товар не найден :(\n'
                with_none_product = True
            else:
                text += (
                    f'Название: {product.name}\n'
                    f'Описание: {product.description}\n'
                    f'{i.count} по {product.price} р, всего {i.count * product.price}\n\n'
                )

        reply_markup = None
        if with_none_product:
            text += 'Покупка содержит удаленные товары, поэтому была отменена'
        elif j.status == PurchaseStatuses.waiting_money.value:
            payment = await yk.create_payment(
                amount=f'{j.amount}.00',
                description=f'#{j.purchase_id} от @{call.from_user.username}'
            )
            if payment is None:
                text += 'Не удалось создать оплату, попробуйте позже\n\n'
            else:
                db.edit_purchase_payment_id(j.purchase_id, payment['id'])
                text += f'Оплатить можно по этой ссылке - {payment.confirmation["confirmation_url"]}'
                reply_markup = kb.check_pay_markup(j.purchase_id)
        to_del = await call.message.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode='html'
        )
        md.add_msg_to_del_list(to_del)

    markup = kb.one_button_inline_markup(
        'Назад',
        callback_data=Keyboards.to_shop.callback_data
    )
    to_del = await call.message.answer(
        text='Вот, что вы купили за все время:\n\n' if len(purchase) > 0 else 'Вы еще ничего не купили :(',
        reply_markup=markup
    )
    md.add_msg_to_del_list(to_del)
