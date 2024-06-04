from typing import List

from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from loguru import logger

from core.utils.database.database import db, DataBase
from core.utils.keyboards import Keyboards
from config import RolePrivilegies, conf
from helper import bot


async def try_delete(
    msg: List[Message] | Message
):
    '''Пытается удалить сообщение'''
    if isinstance(msg, list):
        for i in msg:
            await try_delete(i)
        return
    try:
        await msg.delete()
    except Exception as e:
        logger.warning(f'Сообщение от пользователя не было удалено по причине {e}')



def is_int(string: str | List[str]) -> bool:
    '''
    Проверяет, является ли строка числом

    :param string: Проверяемая строка или список проверяемых строк
    '''
    try:
        if isinstance(string, list):
            for i in string:
                num = int(i)
        else:
            num = int(string)
        return True
    except ValueError:
        return False


def is_float(string: str | List[str]) -> bool:
    '''
    Проверяет, является ли строка числом

    :param string: Проверяемая строка или список проверяемых строк
    '''
    try:
        if isinstance(string, list):
            for i in string:
                num = float(i)
        else:
            num = float(string)
        return True
    except ValueError:
        return False


def make_product_text(product: DataBase.Products, page: str):

    if product is None:
        return 'Товаров нет :('

    text = (
        f'#{product.product_id}\n'
        f'<b>{product.name}</b>\n\n'

        f'{product.description}\n\n'

        f'<i>~ {add_spase_to_digit(str(product.price))} ₽</i>\n'
    )

    if product.minimum_to_sell > 1:
        text += f'<i>~ От {product.minimum_to_sell} штук</i>\n'

    text += (
        f'<i>~ Осталось {product.count} единиц</i>\n\n'
        f'Категория: {product.category} {page}'
    )

    return text



def add_spase_to_digit(total: str):
    if not is_int(total):
        return total

    total_with_tabs = ''
    iterator = 3 - len(total) % 3
    for i in total:
        total_with_tabs += i
        iterator += 1
        if iterator % 3 == 0:
            total_with_tabs += ' '

    return total_with_tabs


def get_basket_products_info(products_dict: dict):
    text = ''
    total = 0
    for i, count in products_dict.items():
        product = db.get_product_by_id(int(i))
        text += (
            f'ID товара: <code>{i}</code>\n'
        )
        price = 'Товар не найден :('
        if product is None:
            text += 'Товар не найден :(\n'
        else:
            text += (
                f'Категория: {product.category}\n'
                f'Название: {product.name}\n'
            )
            price = product.price * count
        text += (
            f'Количество: {count}\n'
            f'Цена: {add_spase_to_digit(str(product.price))} р.\n'
            f'<i>~ Всего {add_spase_to_digit(str(price))} р. ~</i>\n\n'
        )
        total += price

    if len(text) == 0:
        text = 'Корзина пуста, поэтому ей грустно :('
    else:
        text += f'<i>~ К оплате - {add_spase_to_digit(str(total))} р. ~</i>'
    return text


def calculate_category_page(call_data: str, pages_count: int, page: int) -> int:
    '''Высчитывает новую страницу категорий'''
    if call_data == Keyboards.next_page_category.callback_data:
        page = 1 if page + 1 > pages_count else page + 1
    elif call_data == Keyboards.previous_page_category.callback_data:
        page = pages_count if page - 1 < 1 else page - 1
    else: page = 1
    return page


def calculate_product_page(call_data: str, pages_count: int, page: int) -> int:
    '''Высчитывает новую страницу продуктов'''
    if call_data == Keyboards.next_page_product.callback_data:
        page = 1 if page + 1 > pages_count else page + 1
    elif call_data == Keyboards.previous_page_product.callback_data:
        page = pages_count if page - 1 < 1 else page - 1
    else: page = 1
    return page


def set_loggers():
    logger.add(
        'logs/{time}.log',
        level='INFO',
        backtrace=True,
        diagnose=True,
        rotation='00:00',
        retention='1 week',
        catch=True
    )
    logger.add(
        'errors/{time}.log',
        level='ERROR',
        backtrace=True,
        diagnose=True,
        rotation='00:00',
        retention='1 week',
        catch=True
    )


def add_owner_to_db():
    '''Добавляет владельца в бд'''
    role = db.get_role('Владелец')
    if role is None:
        db.add_role('Владелец')

    rp = RolePrivilegies()
    privilegies = db.get_all_role_privilegies('Владелец')
    privilegies = [i.privilegies for i in privilegies]
    all_privilegies = rp.get_all_privilegies()

    for i in all_privilegies:
        if i not in privilegies:
            db.add_privilegie(
                role='Владелец',
                privilegie=i
            )

    admin = db.get_admin(conf.get_admin_id())
    if admin is None:
        db.add_admin(
            admin_id=conf.get_admin_id(),
            role='Владелец',
            name=''
        )


async def send_media_group(
        chat_id: int,
        media: dict,
        caption: str = None,
        reply_to_msg: int = None
) -> Message | None:
    '''
    Отправляет медиагруппу в указанный чат, возвращает сообщение медиагруппы

    :param chat_id: Куда кидать медиагруппу
    :param media: медиа(айди: тип медиа), которую надо кидать
    '''

    media_group = MediaGroupBuilder(caption=caption)
    logger.debug(f'Длинна медиа {len(media)}')

    if len(media) == 0: return
    added = 0

    for key, value in media.items():
        if value == 'photo':
            added += 1
            media_group.add_photo(media=key)
        elif value == 'video':
            added += 1
            media_group.add_video(media=key)
        else:
            continue

    if added == 0: return
    msg = await bot.send_media_group(
        chat_id=chat_id,
        media=media_group.build(),
        reply_to_message_id=reply_to_msg
    )
    return msg
