from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from core.utils.keyboards import Keyboards
from core.utils.database.database import db
from core.utils.operations import try_delete, send_media_group
from core.utils.states import FeedBack
from core.utils.manage_data import ManageData
from core.utils.filters import ChatType, ContentTypes

from config import conf

from helper import bot

r = Router()
r.message.filter(ChatType('private'))


@r.callback_query(F.data == Keyboards.feedback.callback_data)
async def feedback(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Опишите подробно возникшую проблему или задайте свой вопрос',
        reply_markup=kb.back_to_user_menu()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(FeedBack.get_description)


@r.message(F.text, StateFilter(FeedBack.get_description))
async def get_description(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    md.update_data(text=msg.text)
    wait_to_del = await msg.answer(
        text=(
            'Добавьте фото или видео, но не более 10 штук, можно вместе и то, и другое. '
            'Вы можете пропустить этот шаг, нажав на кнопку'
        ),
        reply_markup=kb.stop_send_feedback_photo()
    )
    md.update_data(wait_to_del=wait_to_del)
    await state.set_state(FeedBack.get_media)


@r.callback_query(
    F.data == Keyboards.stop_send_photo.callback_data,
    StateFilter(FeedBack.get_media)
)
async def stop_send_media(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    kb = Keyboards()
    media = md.get_media()
    data = md.get_data(True)
    await try_delete(data['wait_to_del'])
    ticket_id = db.add_feedback(
        sender_id=call.from_user.id,
        date=datetime.now(),
        ticket_text=data['text']
    )
    feedback_text = (
        f'<b>Обращение #{ticket_id} от @{call.from_user.username}</b>\n\n'
        f'{data["text"]}'
    )
    to_db = await bot.send_message(
        chat_id=conf.get_feedback_chat_id(),
        text=feedback_text,
        parse_mode='html'
    )
    await send_media_group(
        chat_id=conf.get_feedback_chat_id(),
        media=media,
        caption=f'К обращение #{ticket_id}'
    )
    db.edit_feedback_message_id(
        ticket_id=ticket_id,
        message_id=to_db.message_id
    )
    to_del = await call.message.answer(
        text='Ваше обращение отправлено!',
        reply_markup=kb.back_to_user_menu()
    )
    md.add_msg_to_del_list(to_del)


@r.message(
    StateFilter(FeedBack.get_media),
    ContentTypes('photo', 'video')
)
async def get_product_media(msg: Message, md: ManageData):
    await try_delete(msg)
    media_dict = md.get_media()
    if len(media_dict) == 10:
        to_del = await msg.answer('Нельзя добавить больше 10 вложений!')
        md.add_msg_to_del_list(to_del)
        return
    md.add_media(msg)
