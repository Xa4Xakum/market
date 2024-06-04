from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from core.utils.database.database import db
from core.utils.filters import Admin, WithPrivilegie
from core.utils.states import (
    AddRole,
    DelRole,
    RoleInfo,
    EditRolePrivilegies,
    AddAdmin,
    DelAdmin,
    AdminInfo
)
from core.utils.manage_data import ManageData
from core.utils.keyboards import Keyboards
from core.utils.flags_presets import Flags

from config import RolePrivilegies, conf

r = Router()
r.callback_query.filter(Admin())
r.message.filter(Admin())


@r.callback_query(F.data == Keyboards.manage_admins.callback_data, StateFilter('*'))
async def manage_admins(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    md.clear_admin_data()
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Выберите действие:',
        reply_markup=kb.manage_admins_markup(call.from_user.id)
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(
    F.data == Keyboards.add_admin.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_add_del_admin)
)
async def add_admin(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте ID будущего администратора',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddAdmin.get_id)


@r.message(
    F.text,
    StateFilter(AddAdmin.get_id),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_admin),
    flags=Flags.get_id
)
async def get_admin_id_to_add(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    admin = db.get_admin(int(msg.text))

    if admin is not None:
        to_del = await msg.answer(
            text='Этот администратор уже добавлен, удалите его, если хотите изменить имя или его роль',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_admin_data(id=int(msg.text))
    to_del = await msg.answer(
        text='Отправьте имя администратора(если он работает в поддержке, его будут видеть пользователи)',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddAdmin.get_name)


@r.message(F.text, StateFilter(AddAdmin.get_name))
async def get_admin_name(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    md.update_admin_data(name=msg.text)
    to_del = await msg.answer(
        text='Отправьте роль админа(она уже должна быть создана)',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddAdmin.get_role)


@r.message(F.text, StateFilter(AddAdmin.get_role))
async def get_admin_role(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    role = db.get_role(msg.text)
    if role is None:
        to_del = await msg.answer(
            text='Извините, но я не знаю такую роль, возможно вы написали ее с маленькой или большой буквы, попробуйте еще раз',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    data = md.get_admin_data(True)
    db.add_admin(
        admin_id=data['id'],
        role=msg.text,
        name=data['name']
    )
    to_del = await msg.answer(
        text='Добавлено!',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.del_admin.callback_data, WithPrivilegie(RolePrivilegies.privilegie_add_del_admin))
async def del_admin(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте id админа, которого хотите удалить',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(DelAdmin.get_id)


@r.message(
    F.text,
    StateFilter(DelAdmin.get_id),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_admin),
    flags=Flags.get_id
)
async def get_admin_id_to_del(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    admin = db.get_admin(int(msg.text))
    if admin is None:
        to_del = await msg.answer(
            text='Извините, но я не знаю такого админа, убедитесь в правильности id и попробуйте еще раз',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) == conf.get_admin_id():
        to_del = await msg.answer(
            text='Никто не может удалить владельца',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.del_admin(int(msg.text))
    to_del = await msg.answer(
        text='Админ удален!',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.add_role.callback_data, WithPrivilegie(RolePrivilegies.privilegie_add_del_role))
async def add_role(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте название роли',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddRole.get_role)


@r.message(
    F.text,
    StateFilter(AddRole.get_role),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_role)
)
async def get_role_name_to_add(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    role = db.get_role(msg.text)
    if role is not None:
        to_del = await msg.answer(
            text='Извините, но такая роль уже есть, попробуйте другое название',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.add_role(msg.text)
    to_del = await msg.answer(
        text='Роль добавлена!',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.del_role.callback_data, WithPrivilegie(RolePrivilegies.privilegie_add_del_role))
async def del_role(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте название роли',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(DelRole.get_role)


@r.message(
    F.text,
    StateFilter(DelRole.get_role),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_role)
)
async def get_role_name_to_del(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    role = db.get_role(msg.text)
    if role is None:
        to_del = await msg.answer(
            text='Извините, но такой роли еще нет, попробуйте другое название',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if msg.text == 'Владелец':
        to_del = await msg.answer(
            text='Никто не может удалить владельца',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    admins = db.get_all_admins_with_role(msg.text)
    if len(admins) != 0:
        to_del = await msg.answer(
            text='Вы не можете удалить роль, которая присвоена хотя бы одному администратору',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.del_role(msg.text)
    to_del = await msg.answer(
        text='Роль удалена!',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(
    F.data == Keyboards.admin_info.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_get_admin_info)
)
async def admin_info(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте id админа, информацию о котором вы хотите узнать',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AdminInfo.get_id)


@r.message(
    F.text,
    StateFilter(AdminInfo.get_id),
    WithPrivilegie(RolePrivilegies.privilegie_get_admin_info),
    flags=Flags.get_id
)
async def get_admin_id_to_info(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    admin = db.get_admin(int(msg.text))

    if admin is None:
        to_del = await msg.answer(
            text='Этого администратора еще нет в моей бд, убедитесь в правильности id и попробуйте еще раз',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    last_tickets = db.get_all_admin_answers_since(
        admin.admin_id,
        datetime.now() - timedelta(30)
    )
    all_tickets = db.get_all_admin_answers(admin.admin_id)

    text = (
        f'id: {admin.admin_id}\n'
        f'Имя: {admin.name}\n'
        f'Роль: {admin.role}\n'
        f'Ответов в поддержке за последние 30 дней: {len(last_tickets)}\n'
        f'Всего ответов в поддержке: {len(all_tickets)}\n'
    )

    to_del = await msg.answer(
        text=text,
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(
    F.data == Keyboards.admins.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_get_admin_list)
)
async def admins_list(call: CallbackQuery, md: ManageData):
    kb = Keyboards()
    admins = db.get_all_admins()
    text = 'Список всех админов: \n\n'
    for admin in admins:
        text += (
            f'id: {admin.admin_id}\n'
            f'Роль: {admin.role}\n'
            f'Имя: {admin.name}\n\n'
        )

    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(
    F.data == Keyboards.roles.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_get_roles_list)
)
async def roles_list(call: CallbackQuery, md: ManageData):
    kb = Keyboards()
    roles = db.get_all_roles()
    text = 'Список всех ролей: \n\n'
    for role in roles:
        admins = db.get_all_admins_with_role(role.role)
        text += (
            f'Название: {role.role}\n'
            f'Админов с этой ролью: {len(admins)}\n\n'
        )

    to_del = await call.message.answer(
        text=text,
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(
    F.data == Keyboards.role_info.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_get_role_info)
)
async def role_info(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте название роли',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(RoleInfo.get_role)


@r.message(
    F.text,
    WithPrivilegie(RolePrivilegies.privilegie_get_role_info),
    StateFilter(RoleInfo.get_role)
)
async def get_role_to_info(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    role = db.get_role(msg.text)
    if role is None:
        to_del = await msg.answer(
            text='Извините, но такой роли еще нет, попробуйте другое название',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return
    admins = db.get_all_admins_with_role(role.role)
    text = (
        f'Роль {role.role}\n'
        f'Количество админов: {len(admins)}\n'
        f'Список админов:\n\n'
    )
    for admin in admins:
        text += (
            f'id: {admin.admin_id}, имя: {admin.name}\n'
        )
    to_del = await msg.answer(
        text=text,
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(
    F.data == Keyboards.edit_role_privilegies.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_edit_role_privilegies)
)
async def edit_role_privilegies(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте название роли',
        reply_markup=kb.back_to_manage_admin_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditRolePrivilegies.get_role)


@r.message(
    F.text,
    StateFilter(EditRolePrivilegies.get_role)
)
async def get_role_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    rp = RolePrivilegies()
    role = db.get_role(msg.text)

    if role is None:
        to_del = await msg.answer(
            text='Извините, но такой роли еще нет, попробуйте другое название',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if msg.text == 'Владелец':
        to_del = await msg.answer(
            text='Никто не может изменять права владельца',
            reply_markup=kb.back_to_manage_admin_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_admin_data(role=msg.text)
    privilegies = db.get_all_role_privilegies(msg.text)
    choosed = [i.privilegies for i in privilegies]
    to_del = await msg.answer(
        text='Все изменения будут автоматически сохранены',
        reply_markup=kb.multiple_choose_markup(
            btns=rp.get_all_privilegies(),
            choosed=choosed,
            back_callback=kb.manage_admins.callback_data
        )
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditRolePrivilegies.get_privilegie)


@r.callback_query(
    F.data != Keyboards.manage_admins.callback_data,
    StateFilter(EditRolePrivilegies.get_privilegie)
)
async def get_privilegie_to_edit(call: CallbackQuery, md: ManageData):
    kb = Keyboards()
    rp = RolePrivilegies()
    data = md.get_admin_data()

    privilegie = db.get_privilegie(
        role=data['role'],
        privilegie=call.data
    )

    if privilegie is None:
        db.add_privilegie(
            role=data['role'],
            privilegie=call.data
        )
    else:
        db.del_role_privilegie(
            role=data['role'],
            privilegie=call.data
        )

    privilegies = db.get_all_role_privilegies(data['role'])
    choosed = [i.privilegies for i in privilegies]
    to_del = await call.message.answer(
        text='Все изменения будут автоматически сохранены',
        reply_markup=kb.multiple_choose_markup(
            btns=rp.get_all_privilegies(),
            choosed=choosed,
            back_callback=kb.manage_admins.callback_data
        )
    )
    md.add_msg_to_del_list(to_del)
