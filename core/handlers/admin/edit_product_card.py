from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from core.utils.database.database import db
from core.utils.filters import Admin, WithPrivilegie, ContentTypes
from core.utils.states import EditProductCard
from core.utils.manage_data import ManageData
from core.utils.keyboards import Keyboards
from core.utils.flags_presets import Flags
from core.utils.operations import try_delete

from config import RolePrivilegies

r = Router()
r.callback_query.filter(
    Admin(),
    WithPrivilegie(RolePrivilegies.privilegie_edit_product_card)
)
r.message.filter(
    Admin(),
    WithPrivilegie(RolePrivilegies.privilegie_edit_product_card)
)


@r.callback_query(F.data == Keyboards.edit_product_card.callback_data)
async def edit_product_card(call: CallbackQuery, state: FSMContext, md: ManageData):
    await state.set_state(None)
    md.clear_admin_data()
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте id товара для изменения',
        reply_markup=kb.back_to_admin_menu_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditProductCard.get_product_id)


@r.message(
    F.text,
    StateFilter(EditProductCard.get_product_id),
    flags=Flags.get_id
)
async def get_product_id(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    product = db.get_product_by_id(int(msg.text))
    await state.set_state(None)

    if product is None:
        to_del = await msg.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_admin_menu_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    to_del = await msg.answer(
        text='Выберите, что хотите изменить:',
        reply_markup=kb.edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    md.update_admin_data(product_id=int(msg.text))


@r.callback_query(F.data == Keyboards.back_to_edit_product_card.callback_data, StateFilter('*'))
async def back_to_edit_product_card(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    if 'wait_to_del' in data:
        await try_delete(data['wait_to_del'])
    await state.set_state(None)
    to_del = await call.message.answer(
        text='Выберите, что хотите изменить:',
        reply_markup=kb.edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)


@r.callback_query(F.data == Keyboards.edit_name.callback_data)
async def edit_name(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте новое название',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditProductCard.get_name)


@r.message(F.text, StateFilter(EditProductCard.get_name))
async def get_name_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    product = db.get_product_by_id(data['product_id'])

    if product is None:
        to_del = await msg.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    prod = db.get_product_by_name_and_category(
        name=msg.text,
        category=product.category
    )

    if prod is not None:
        to_del = await msg.answer(
            text='Извините, но в этой категории уже есть товар с таким именем, попробуйте другое',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.edit_product_parametr(
        product_id=data['product_id'],
        parametr=db.Products.name,
        value=msg.text
    )
    to_del = await msg.answer(
        text='Изменено!',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.edit_category.callback_data)
async def edit_category(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте новую категорю',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditProductCard.get_category)


@r.message(F.text, StateFilter(EditProductCard.get_category))
async def get_category_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    product = db.get_product_by_id(data['product_id'])

    if product is None:
        to_del = await msg.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    category = db.get_category(msg.text)

    if category is not None:
        to_del = await msg.answer(
            text='Извините, но этой категории еще нет, попробуйте другую',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    prod = db.get_product_by_name_and_category(
        name=product.name,
        category=msg.text
    )

    if prod is not None:
        to_del = await msg.answer(
            text='Извините, но в этой категории уже есть товар с таким именем, попробуйте другую категорию',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.edit_product_parametr(
        product_id=data['product_id'],
        parametr=db.Products.category,
        value=msg.text
    )
    to_del = await msg.answer(
        text='Изменено!',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.edit_description.callback_data)
async def edit_description(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте новое описание',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditProductCard.get_description)


@r.message(F.text, StateFilter(EditProductCard.get_description))
async def get_description_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    product = db.get_product_by_id(data['product_id'])

    if product is None:
        to_del = await msg.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.edit_product_parametr(
        product_id=data['product_id'],
        parametr=db.Products.description,
        value=msg.text
    )
    to_del = await msg.answer(
        text='Изменено!',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.edit_price.callback_data)
async def edit_price(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте новую цену',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditProductCard.get_price)


@r.message(
    F.text,
    StateFilter(EditProductCard.get_price),
    flags=Flags.get_id
)
async def get_price_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    product = db.get_product_by_id(data['product_id'])

    if product is None:
        to_del = await msg.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) < 1:
        to_del = await msg.answer(
            text='Извините, но цена не может быть ниже одного рубля',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.edit_product_parametr(
        product_id=data['product_id'],
        parametr=db.Products.price,
        value=int(msg.text)
    )
    to_del = await msg.answer(
        text='Изменено!',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.edit_minimum_to_sell.callback_data)
async def edit_minimum_to_sell(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    to_del = await call.message.answer(
        text='Отправьте новое минимальное количество для покупки',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(EditProductCard.get_minimum_to_sell)


@r.message(
    F.text,
    StateFilter(EditProductCard.get_minimum_to_sell),
    flags=Flags.get_id
)
async def get_minimum_to_sell_to_edit(msg: Message, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    product = db.get_product_by_id(data['product_id'])

    if product is None:
        to_del = await msg.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) < 1:
        to_del = await msg.answer(
            text='Извините, но минимальное количество не может быть меньше 1',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if int(msg.text) > product.count:
        to_del = await msg.answer(
            text='Извините, но минимальное количество не может быть больше имеющегося на складе',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    db.edit_product_parametr(
        product_id=data['product_id'],
        parametr=db.Products.minimum_to_sell,
        value=int(msg.text)
    )
    to_del = await msg.answer(
        text='Изменено!',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)
    await state.set_state(None)


@r.callback_query(F.data == Keyboards.edit_media.callback_data)
async def edit_media(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    wait_to_del = await call.message.answer(
        text='Отправьте новые медиа товара',
        reply_markup=kb.stop_send_product_media_to_edit_markup()
    )
    md.update_admin_data(wait_to_del=wait_to_del)
    await state.set_state(EditProductCard.get_media)


@r.callback_query(
    F.data == Keyboards.stop_send_photo.callback_data,
    StateFilter(EditProductCard.get_media)
)
async def stop_send_media(call: CallbackQuery, state: FSMContext, md: ManageData):
    kb = Keyboards()
    data = md.get_admin_data()
    media = md.get_product_media()
    product = db.get_product_by_id(data['product_id'])

    if product is None:
        to_del = await call.message.answer(
            text='Извините, но я не могу найти товар с таким айди, попробуйте еще раз',
            reply_markup=kb.back_to_edit_product_card_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    if len(media) == 0:
        to_del = await call.message.answer(
            text='Вы не добавили ни одного фото или видео',
            reply_markup=kb.stop_send_product_media_to_edit_markup()
        )
        md.add_msg_to_del_list(to_del)
        return

    await try_delete(data['wait_to_del'])

    db.del_all_product_media(product.product_id)
    for k, v in media.items():
        db.add_product_media(
            file_id=k,
            product_id=product.product_id,
            media_type=v
        )

    await state.set_state(None)
    to_del = await call.message.answer(
        text='Медиа успешно изменены!',
        reply_markup=kb.back_to_edit_product_card_markup()
    )
    md.add_msg_to_del_list(to_del)


@r.message(
    StateFilter(EditProductCard.get_media),
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
