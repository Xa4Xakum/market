from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from core.utils.database.database import db
from core.utils.filters import Admin, WithPrivilegie, ContentTypes
from core.utils.states import (
    AddCategory,
    AddProduct,
    DelCategory,
    DelProduct,
    AddProdCount,
)
from core.utils.manage_data import ManageData
from core.utils.keyboards import Keyboards
from core.utils.flags_presets import Flags
from core.utils.operations import try_delete

from config import RolePrivilegies

r = Router()
r.callback_query.filter(Admin())
r.message.filter(Admin())


@r.callback_query(F.data == Keyboards.manage_products.callback_data, StateFilter('*'))
async def manage_products(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    data = md.get_admin_data(True)
    if 'wait_to_del' in data:
        await try_delete(data['wait_to_del'])
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Выберите действие',
        reply_markup=kb.manage_products_markup(call.from_user.id)
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.del_cat.callback_data, WithPrivilegie(RolePrivilegies.privilegie_add_del_cat))
async def delcat(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте категорию, которую хотите удалить',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(DelCategory.get_category)


@r.message(F.text, StateFilter(DelCategory.get_category), WithPrivilegie(RolePrivilegies.privilegie_add_del_cat))
async def get_del_category(msg: Message, state: FSMContext, md: ManageData):
    category = db.get_category(msg.text)
    kb = Keyboards()
    if category is None:
        to_del = await msg.answer(
            'Такой категории еще нет, убедитесь в правильности ввода и попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    products = db.get_all_products_with_category(msg.text)
    if len(products) != 0:
        to_del = await msg.answer(
            'Нельзя удалить категорию, если в ней есть товары',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.del_category(msg.text)
    to_del = await msg.answer(
        'Категория успешно удалена',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(
    F.data == Keyboards.del_product_from_shop.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_add_del_product)
)
async def del_prod(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте id продукта, который хотите удалить(без #)',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(DelProduct.get_id)


@r.message(
    F.text,
    StateFilter(DelProduct.get_id),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_product),
    flags=Flags.get_id
)
async def get_prod_to_del(msg: Message, state: FSMContext, md: ManageData):
    product = db.get_product_by_id(int(msg.text))
    kb = Keyboards()
    if product is None:
        to_del = await msg.answer(
            'В бд нет товара с таким id, проверьте правильность и попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.del_product(int(msg.text))
    to_del = await msg.answer(
        'Товар успешно удален!',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(
    F.data == Keyboards.add_product_count.callback_data,
    WithPrivilegie(RolePrivilegies.privilegie_add_product_count)
)
async def add_product_count(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте id товара, кол-во которого хотите изменить',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProdCount.get_id)


@r.message(
    F.text,
    StateFilter(AddProdCount.get_id),
    WithPrivilegie(RolePrivilegies.privilegie_add_product_count),
    flags=Flags.get_id
)
async def get_id_to_add(msg: Message, state: FSMContext, md: ManageData):
    product = db.get_product_by_id(int(msg.text))
    kb = Keyboards()
    if product is None:
        to_del = await msg.answer(
            'В бд нет товара с таким id, убедитесь в правильности и попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_data(id=int(msg.text))
    to_del = await msg.answer(
        'Отправьте число, сколько надо прибавить(если перед числом поставите -, то отбавить)',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProdCount.get_new_count)


@r.message(
    F.text,
    StateFilter(AddProdCount.get_new_count),
    WithPrivilegie(RolePrivilegies.privilegie_add_product_count),
    flags=Flags.get_id
)
async def get_count_to_add(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_data()
    prod = db.get_product_by_id(data['id'])
    new_count = prod.count + int(msg.text)

    if new_count < prod.minimum_to_sell:
        to_del = await msg.answer(
            'Количество товара не может быть меньше, чем минимум для продажи, попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.edit_product_count(data['id'], new_count)
    to_del = await msg.answer(
        'Готово',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProdCount.get_new_count)


@r.callback_query(F.data == Keyboards.add_cat.callback_data, WithPrivilegie(RolePrivilegies.privilegie_add_del_cat))
async def add_category(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте категорию, которую хотите добавить',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddCategory.get_category)


@r.message(F.text, StateFilter(AddCategory.get_category), WithPrivilegie(RolePrivilegies.privilegie_add_del_cat))
async def get_add_category(msg: Message, state: FSMContext, md: ManageData):
    category = db.get_category(msg.text)
    kb = Keyboards()
    if category is not None:
        to_del = await msg.answer(
            'Такая категория уже есть, попробуйте другую',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.add_category(msg.text)
    to_del = await msg.answer(
        'Категория успешно добавлена',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.add_product.callback_data, WithPrivilegie(RolePrivilegies.privilegie_add_del_product))
async def add_prod(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        'Отправьте категорию продукта',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProduct.get_category)


@r.message(F.text, StateFilter(AddProduct.get_category), WithPrivilegie(RolePrivilegies.privilegie_add_del_product))
async def get_prod_category(msg: Message, state: FSMContext, md: ManageData):
    category = db.get_category(msg.text)
    kb = Keyboards()
    if category is None:
        to_del = await msg.answer(
            'Такой категории нет, возможно вы написали с маленькой буквы, попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_admin_data(category=msg.text)
    to_del = await msg.answer(
        'Отправьте название товара',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProduct.get_name)


@r.message(F.text, StateFilter(AddProduct.get_name), WithPrivilegie(RolePrivilegies.privilegie_add_del_product))
async def get_product_name(msg: Message, state: FSMContext, md: ManageData):
    data = md.get_admin_data()
    kb = Keyboards()
    product = db.get_product_by_name_and_category(msg.text, data['category'])

    if product is not None:
        to_del = await msg.answer(
            'Товар с таким именем уже есть в такой категории',
            reply_markup=kb.back_to_manage_products()
        )
        return

    to_del = await msg.answer(
        'Отправьте описание товара',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    md.update_admin_data(name=msg.text)
    await state.set_state(AddProduct.get_description)


@r.message(F.text, StateFilter(AddProduct.get_description), WithPrivilegie(RolePrivilegies.privilegie_add_del_product))
async def get_product_description(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    md.update_admin_data(description=msg.text)
    to_del = await msg.answer(
        'Отправьте количество единиц товара, которое есть на складе',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProduct.get_count)


@r.message(
    F.text,
    StateFilter(AddProduct.get_count),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_product),
    flags=Flags.get_id
)
async def get_product_count(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    if int(msg.text) < 0:
        to_del = await msg.answer(
            'Количетво товара не может быть меньше нуля, попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_admin_data(count=int(msg.text))
    to_del = await msg.answer(
        'Отправьте цену, по которой хотите продавать ваш товар',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProduct.get_price)


@r.message(
    F.text,
    StateFilter(AddProduct.get_price),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_product),
    flags=Flags.get_id
)
async def get_product_price(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    if int(msg.text) < 1:
        to_del = await msg.answer(
            'Цена товара не может быть меньше одного рубля, попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_admin_data(price=int(msg.text))
    to_del = await msg.answer(
        'Отправьте минимальное количество для продажи(продажа от 5 штук, например). Отправьте только цифру',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(AddProduct.get_minimum_to_sell)


@r.message(
    F.text,
    StateFilter(AddProduct.get_minimum_to_sell),
    WithPrivilegie(RolePrivilegies.privilegie_add_del_product),
    flags=Flags.get_id
)
async def get_minimum_to_sell(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    if int(msg.text) < 1:
        to_del = await msg.answer(
            'Минимальное количество для продажи должно быть больше 0, попробуйте еще раз',
            reply_markup=kb.back_to_manage_products()
        )
        md.add_msg_to_del_list(to_del)
        return

    md.update_admin_data(minimum_to_sell=int(msg.text))
    wait_to_del = await msg.answer(
        'Отправьте до 10 медиа(фото и/или видео) вашего товара, нажмите кнопку, когда закончите',
        reply_markup=kb.stop_send_product_photo_markup()
    )
    md.update_admin_data(wait_to_del=wait_to_del)
    await state.set_state(AddProduct.get_media)


@r.callback_query(
    F.data == Keyboards.stop_send_photo.callback_data,
    StateFilter(AddProduct.get_media)
)
async def stop_send_media(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    media = md.get_product_media()

    if len(media) == 0:
        to_del = await call.message.answer(
            text='Вы не добавили ни одного фото или видео',
            reply_markup=kb.stop_send_product_photo_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    data = md.get_admin_data(True)
    await try_delete(data['wait_to_del'])
    product_id = db.add_product(**data)
    for k, v in media.items():
        db.add_product_media(
            file_id=k,
            product_id=product_id,
            media_type=v
        )

    await state.set_state(None)
    to_del = await call.message.answer(
        text=f'Товар #{product_id} успешно добавлен',
        reply_markup=kb.back_to_manage_products()
    )
    md.add_msg_to_del_list(to_del)


@r.message(
    StateFilter(AddProduct.get_media),
    ContentTypes('photo', 'video')
)
async def get_product_media(msg: Message, md: ManageData):
    await try_delete(msg)
    media_dict = md.get_product_media()
    if len(media_dict) == 10:
        to_del = await msg.answer('Нельзя добавить больше 10 вложений!')
        md.add_msg_to_del_list(to_del)
        return
    md.add_product_media(msg)
