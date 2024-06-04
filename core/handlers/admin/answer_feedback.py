from datetime import datetime

from aiogram import Router
from aiogram.types import Message

from loguru import logger

from core.utils.database.database import db
from core.utils.filters import Admin, WithPrivilegie, ReplyToBotMsg, ChatsIds
from core.utils.keyboards import Keyboards

from config import RolePrivilegies, conf
from helper import bot

r = Router()
r.message.filter(
    Admin(),
    WithPrivilegie(RolePrivilegies.privilegie_answer_tickets),
    ReplyToBotMsg(),
    ChatsIds(conf.get_feedback_chat_id())
)


@r.message()
async def answer_ticket(msg: Message):
    kb = Keyboards()
    ticket = db.get_ticket_by_message_id(
        msg.reply_to_message.message_id
    )

    if ticket is None:
        await msg.reply('В моей бд нет этого обращения')
        logger.warning(f'Не найдено обращение, на которое ответил @{msg.from_user.username}')
        return

    admin = db.get_admin(msg.from_user.id)
    text = (
        f'<b>{admin.role} {admin.name} в ответ на ваше обращение #{ticket.ticket_id}</b>\n\n'
        f'{msg.text}'
    )
    try:
        await bot.send_message(
            chat_id=ticket.sender_id,
            text=text,
            reply_markup=kb.inline_markup_from_buttons(kb.to_user_menu),
            parse_mode='html'
        )
    except Exception as e:
        await msg.reply(
            f'Не удалсь ответить на это обращение(#{ticket.ticket_id}) по причине {e}. '
            'Возможно вы добавили в ответ запрещенные символы(такие как <>), убедитесь в их отсутствии, либо '
            'исправьте ошибки(ответ отправляется в формате html файла, то есть поддерживаются теги html)'
        )
        logger.error(f'Не удалось ответить на обращение по причине {e}')
        return
    db.answer_feedback(
        ticket_id=ticket.ticket_id,
        moderator_id=msg.from_user.id,
        answer_text=msg.text,
        answer_date=datetime.now()
    )
    await msg.reply(f'Ответ на обращение #{ticket.ticket_id} доставлен')
