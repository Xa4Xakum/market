
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext

from loguru import logger

from core.utils.database.database import db
from core.utils.filters import Admin, WithPrivilegie
from core.utils.operations import send_media_group
from core.utils.states import (
    ProductInfo,
    FAQ,
    DelFAQ,
    PurchaseInfo
)
from core.utils.manage_data import ManageData
from core.utils.keyboards import Keyboards
from core.utils.flags_presets import Flags

from config import RolePrivilegies, conf
from helper import bot


r = Router()
r.callback_query.filter(Admin())
r.message.filter(Admin())


@r.message(F.text, Command('amenu'), StateFilter('*'))
async def amenu(msg: Message, state: FSMContext, md: ManageData):
    await state.set_state(None)
    kb = Keyboards()
    to_del = await msg.answer(
        'Выберите действие:',
        reply_markup=kb.admin_menu_markup(msg.from_user.id)
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.to_admin_menu.callback_data, StateFilter('*'))
async def amenu_callback(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    kb = Keyboards()
    to_del = await call.message.answer(
        'Выберите действие:',
        reply_markup=kb.admin_menu_markup(call.from_user.id)
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(
    F.data == Keyboards.del_question_answer.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_edit_questions)
)
async def del_question(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте вопрос',
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(DelFAQ.get_question)


@r.message(F.text, StateFilter(DelFAQ.get_question), WithPrivilegie(RolePrivilegies.privilegie_edit_questions))
async def get_question(msg: Message, state: FSMContext, md: ManageData):
    question = db.get_question(msg.text)
    kb = Keyboards()
    markup = kb.inline_markup_from_buttons(kb.to_admin_menu)
    if question is None:
        to_del = await msg.answer(
            'Такого вопроса еще нет, попробуйте еще раз',
            reply_markup=markup
        )
        md.add_msg_to_del_list(to_del)
        return

    db.del_question(msg.text)
    to_del = await msg.answer(
        'Вопрос удален!',
        reply_markup=markup
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(
    F.data == Keyboards.add_question_answer.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_edit_questions)
)
async def add_question(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте вопрос',
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(FAQ.get_question)


@r.message(F.text, StateFilter(FAQ.get_question), WithPrivilegie(RolePrivilegies.privilegie_edit_questions))
async def get_question_to_add(msg: Message, state: FSMContext, md: ManageData):
    question = db.get_question(msg.text)
    kb = Keyboards()
    if question is not None:
        to_del = await msg.answer(
            f'Такой вопрос уже есть:\n'
            f'<b>{question.question}</b> - {question.answer}\n\n'
            'Попробуйте другой вопрос',
            parse_mode='html',
            reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
        )
        md.add_msg_to_del_list(to_del)
        return
    md.update_data(question=msg.text)
    to_del = await msg.answer(
        'Отправьте ответ на этот вопрос',
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(FAQ.get_answer)


@r.message(F.text, StateFilter(FAQ.get_answer), WithPrivilegie(RolePrivilegies.privilegie_edit_questions))
async def get_answer(msg: Message, state: FSMContext, md: ManageData):
    data = md.get_data()
    db.add_question(
        question=data['question'],
        answer=msg.text
    )
    kb = Keyboards()
    to_del = await msg.answer(
        f'Добавлен вопрос-ответ:\n'
        f'<b>{data["question"]}</b> - {msg.text}',
        parse_mode='html',
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.product_info.callback_data)
async def product_info(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте id товара, информацию о котором вы хотите получить',
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(ProductInfo.get_info)


@r.message(
    F.text,
    StateFilter(ProductInfo.get_info),
    flags=Flags.get_id,
)
async def get_info(msg: Message, state: FSMContext, md: ManageData):
    product = db.get_product_by_id(int(msg.text))
    kb = Keyboards()
    if product is None:
        to_del = await msg.answer(
            'В бд нет товара с таким id, попробуйте еще раз',
            reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
        )
        md.add_msg_to_del_list(to_del)
        return

    media = db.get_all_media_by_product_id(product.product_id)
    media_to_send = {}
    for i in media:
        media_to_send[i.file_id] = i.media_type

    md.add_msg_to_del_list(
        await send_media_group(
            chat_id=msg.chat.id,
            media=media_to_send
        )
    )
    text = (
        f'#{product.product_id}\n'
        f'Категория: {product.category}\n'
        f'Название: {product.name}\n'
        f'Количество: {product.count}\n'
        f'Цена: {product.price}\n'
        f'Минимум для покупки: {product.minimum_to_sell}\n'
        f'Описание:\n{product.description}'
    )
    try:
        to_del = await msg.answer(
            text=text,
            reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu),
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


@r.callback_query(
    F.data == Keyboards.purchase_info.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_get_purchase_info)
)
async def purchase_info(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте id покупки, информацию о которой вы хотите получить',
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(PurchaseInfo.get_info)


@r.message(
    F.text,
    StateFilter(PurchaseInfo.get_info),
    WithPrivilegie(RolePrivilegies.privilegie_get_purchase_info),
    flags=Flags.get_id
)
async def get_purchase_info(msg: Message, state: FSMContext, md: ManageData):
    purchase = db.get_purchase(int(msg.text))
    kb = Keyboards()
    if purchase is None:
        to_del = await msg.answer(
            'В моей бд нет покупки с таким id, проверьте правильность и попробуйте еще раз',
            reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
        )
        md.add_msg_to_del_list(to_del)
        return
    purchase_products = db.get_purchase_products(int(msg.text))
    text = (
        f'Покупка #{purchase.purchase_id}\n'
        f'Адресс: {purchase.address}\n'
        f'ФИО: {purchase.fullname}\n'
        f'Номер телефона: {purchase.phone_number}\n'
        f'Статус покупки: {purchase.status}\n'
        f'Заказанные товары:\n\n'
    )
    for purchase_product in purchase_products:
        text += f'Товар #{purchase_product.product_id}\n'
        text += f'В количестве: {purchase_product.count}\n'
        product = db.get_product_by_id(purchase_product.product_id)
        if product is None:
            text += 'Не найден\n\n'
            continue
        text += (
            f'По цене за штуку: {product.price}\n'
            f'Категория: {product.category}\n'
            f'Наименование: {product.name}\n\n'
        )
    to_del = await msg.answer(
        text,
        reply_markup=kb.inline_markup_from_buttons(kb.to_admin_menu)
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)
