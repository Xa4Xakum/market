from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from core.utils.keyboards import Keyboards
from core.utils.database.database import db
from core.utils.filters import ChatType
from core.utils.manage_data import ManageData
from core.utils.check_privilegies import CheckPrivilegies

r = Router()
r.message.filter(ChatType('private'))


@r.message(F.text, Command('start'), StateFilter('*'))
async def start(msg: Message, state: FSMContext, md: ManageData):
    await state.set_state(None)
    cp = CheckPrivilegies(msg.from_user.id)
    kb = Keyboards()

    to_del = await msg.answer(
        f'Привет, {msg.from_user.first_name}! Хочешь что-нибудь прикупить?',
        reply_markup=kb.user_start_menu(
            cp.have_any_privilegies()
        )
    )

    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.to_user_menu.callback_data, StateFilter('*'))
async def start_callback(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    cp = CheckPrivilegies(call.from_user.id)
    kb = Keyboards()
    to_del = await call.message.answer(
        f'Привет, {call.from_user.first_name}! Хочешь что-нибудь прикупить?',
        reply_markup=kb.user_start_menu(
            cp.have_any_privilegies()
        )
    )
    md.add_msg_to_del_list(to_del)
    md.add_msg_to_del_list(call.message)


@r.callback_query(F.data == Keyboards.questions.callback_data)
async def questions(call: CallbackQuery, md: ManageData):
    kb = Keyboards()

    questions = db.get_questions()
    text = 'К сожалению ответов на вопросы пока нет :(\n\n' if len(questions) == 0 else ''
    for question in questions:
        text += f'<b>{question.question}</b> - {question.answer}\n\n'
    text += 'Не узнали, что хотелось узнать? Напишите в обратную связь!'

    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.one_button_inline_markup(
            'Назад',
            callback_data=Keyboards.to_user_menu.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.rewiews.callback_data)
async def rewiews(call: CallbackQuery, md: ManageData):
    kb = Keyboards()
    text = (
        'Бот сделан с помощью разработчика <code>@Xa4_Xakum</code>, у него можно купить '
        'как уже готовых(к примеру этого), так и заказать разработку под ключ'
    )
    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.one_button_inline_markup(
            'Назад',
            callback_data=Keyboards.to_user_menu.callback_data
        ),
        parse_mode='html'
    )
    md.add_msg_to_del_list(to_del)
