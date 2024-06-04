from typing import List

from aiogram.types import Message

from core.utils.operations import try_delete
from core.utils.keyboards import Keyboards


class BaseManageDataMethods():


    def __init__(self, data: dict) -> None:
        self.data = data


    def get_del_list(self) -> List[Message]:
        '''возвращает список сообщений для удаления'''
        if 'dellist' not in self.data:
            self.data['dellist'] = []
        return self.data['dellist']


    def get_media(self) -> dict:
        '''Возвращает медиа обращения в поддержку'''
        if 'media' not in self.data:
            self.update_data(media={})
        return self.get_data()['media']


    def add_media(self, media: Message) -> None:
        data = self.get_media()
        if media.content_type == 'photo':
            data[media.photo[0].file_id] = 'photo'
        else:
            data[media.video.file_id] = 'video'
        self.update_data(media=data)


    def add_msg_to_del_list(self, msg: Message | List[Message]) -> None:
        '''Добавляет сообщение в список сообщений для удаления'''
        dellist = self.get_del_list()
        if isinstance(msg, list):
            for i in msg:
                self.add_msg_to_del_list(i)
        else:
            if msg not in dellist:
                dellist.append(msg)
        self.data['dellist'] = dellist


    async def clear_del_list(self) -> None:
        '''Очищает список для удаления, удаляет все сообщения для удаления'''
        dellist = self.get_del_list()
        await try_delete(dellist)
        self.data['dellist'] = []


    def set_data(self, data: dict) -> None:
        '''Ставит новые данные'''
        self.data = data


    def get_data(self, with_clear: bool = False) -> dict:
        '''Возвращает данные'''
        data = self.data
        if with_clear:
            self.data = {}
        return data


    def update_data(self, **kwargs) -> None:
        '''Обновляет данные'''
        data = self.get_data()
        for key, value in kwargs.items():
            data[key] = value
        self.set_data(data)


class ManageAdminData(BaseManageDataMethods):
    '''Управление данными админа'''


    def get_admin_data(self, with_clear: bool = False) -> dict:
        '''Возвращает данные адмниа'''
        if 'admin_data' not in self.data:
            self.data['admin_data'] = {}
        data = self.data['admin_data']
        if with_clear:
            self.clear_admin_data()
        return data


    def set_admin_data(self, data: dict) -> None:
        '''Ставит новые данные админа'''
        self.data['admin_data'] = data


    def update_admin_data(self, **kwargs) -> None:
        '''Обновляет данные админа'''
        data = self.get_admin_data()
        for key, value in kwargs.items():
            data[key] = value
        self.set_admin_data(data)


    def clear_admin_data(self) -> dict:
        '''Очищает данные админа'''
        if 'admin_data' not in self.data:
            return
        del self.data['admin_data']


    def get_product_media(self) -> dict:
        '''Возвращает медиа продукта'''
        data = self.get_admin_data()
        if 'media' not in data:
            self.update_admin_data(media={})
        return self.get_admin_data()['media']


    def add_product_media(self, media: Message) -> None:
        data = self.get_product_media()
        if media.content_type == 'photo':
            data[media.photo[0].file_id] = 'photo'
        else:
            data[media.video.file_id] = 'video'
        self.update_admin_data(media=data)


class ManageShopData(BaseManageDataMethods):


    def get_product_dict(self) -> dict:
        if 'product_dict' not in self.data:
            self.data['product_dict'] = {}
        return self.data['product_dict']


    def add_product_to_dict(self, product: int, count: int) -> None:
        '''Добавляет продукт в словарь'''
        product_dict = self.get_product_dict()
        product_dict[product] = count
        self.update_data(product_dict=product_dict)


    def del_product_from_product_dict(self, product: int) -> None:
        '''Удаляет продукт из словаря продуктов'''
        product_dict = self.get_product_dict()
        if product in product_dict:
            del product_dict[product]
            self.update_data(product_dict=product_dict)


    def get_category_page(self, call_data: str) -> int:
        '''возвращает текущую страницу категорий'''
        data = self.get_data()
        if 'category_page' in data and call_data != Keyboards.categories.callback_data:
            page = data['category_page']
        else:
            page = 1
            self.update_data(
                category_page=page,
                product_page=page,
            )
        return page


    def get_product_page(self) -> int:
        '''возвращает текущую страницу продуктов'''
        data = self.get_data()
        if 'product_page' in data:
            page = data['product_page']
        else:
            page = 1
            self.update_data(product_page=page)
        return page


    def get_category(self, call_data: str) -> str:
        '''Возвращает категорию продуктов'''
        data = self.get_data()
        if call_data not in [
            Keyboards.next_page_product.callback_data,
            Keyboards.previous_page_product.callback_data,
            Keyboards.to_products.callback_data
        ]: category = call_data
        else:
            if 'category' in data: category = data['category']
            else: category = None

        self.update_data(
            category=category,
            category_page=1
        )
        return category


class ManageData(
    ManageShopData,
    ManageAdminData
):
    '''Класс управления данными пользователя'''
