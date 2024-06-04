from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.utils.check_privilegies import CheckPrivilegies


class UserButtons():
    '''Кнопки пользователей'''
    to_shop = InlineKeyboardButton(text='К покупкам', callback_data='К покупкам')
    purchases_history = InlineKeyboardButton(text='История покупок', callback_data='История покупок')
    categories = InlineKeyboardButton(text='Выбрать категорию', callback_data='Выбрать категорию')
    to_products = InlineKeyboardButton(text='К товарам', callback_data='К товарам')
    feedback = InlineKeyboardButton(text='Обратная связь', callback_data='Обратная связь')
    rewiews = InlineKeyboardButton(text='О нас', callback_data='Наши отзывы')
    questions = InlineKeyboardButton(text='FAQ', callback_data='FAQ')
    to_user_menu = InlineKeyboardButton(text='В меню', callback_data='В меню')
    previous_page_category = InlineKeyboardButton(text='<-', callback_data='<- категория')
    next_page_category = InlineKeyboardButton(text='->', callback_data='-> категория')
    previous_page_product = InlineKeyboardButton(text='<-', callback_data='<- товар')
    next_page_product = InlineKeyboardButton(text='->', callback_data='-> товар')
    open_basket = InlineKeyboardButton(text='Открыть корзину', callback_data='Открыть корзину')
    del_product = InlineKeyboardButton(text='Удалить товар', callback_data='Удалить товар')
    clear_basket = InlineKeyboardButton(text='Очистить корзину', callback_data='Очистить корзину')
    edit_product_count = InlineKeyboardButton(text='Изменить количество', callback_data='Изменить количество')
    buy = InlineKeyboardButton(text='К оформлению', callback_data='К оформлению')
    check_pay = InlineKeyboardButton(text='Оплатил', callback_data='pay')
    find_by_id = InlineKeyboardButton(text='Найти по id', callback_data='Найти по id')


class ManageProductButtons():
    '''Кнопки изменения категорий и товаров'''

    manage_products = InlineKeyboardButton(text='Управление товарами', callback_data='Управление товарами')
    add_cat = InlineKeyboardButton(text='Добавить категорию', callback_data='Добавить категорию')
    del_cat = InlineKeyboardButton(text='Удалить категорию', callback_data='Удалить категорию')
    add_product = InlineKeyboardButton(text='Добавить товар', callback_data='Добавить товар')
    del_product_from_shop = InlineKeyboardButton(text='Удалить товар', callback_data='Удалить товар с магазина')
    add_product_count = InlineKeyboardButton(text='Добавить кол-во товара', callback_data='Добавить кол-во товара')


class ManageAdminsButtons():
    '''Управление администраторами'''


    manage_admins = InlineKeyboardButton(text='Управление админами', callback_data='Управление админами')
    add_role = InlineKeyboardButton(text='Добавить роль', callback_data='Добавить роль')
    del_role = InlineKeyboardButton(text='Удалить роль', callback_data='Удалить роль')
    role_info = InlineKeyboardButton(text='Информация о роли', callback_data='Информация о роли')
    edit_role_privilegies = InlineKeyboardButton(text='Изменить права роли', callback_data='Изменить права роли')
    add_admin = InlineKeyboardButton(text='Добавить админа', callback_data='Добавить админа')
    del_admin = InlineKeyboardButton(text='Удалить админа', callback_data='Удалить админа')
    admin_info = InlineKeyboardButton(text='Информация об админе', callback_data='Информация об админе')
    roles = InlineKeyboardButton(text='Список ролей', callback_data='Список ролей')
    admins = InlineKeyboardButton(text='Список админов', callback_data='Список админов')


class EditProductCardButtons():
    '''Изменение карточки товара'''


    edit_product_card = InlineKeyboardButton(text='Изменить карточку товара', callback_data='Изменить карточку товара')
    back_to_edit_product_card = InlineKeyboardButton(text='Назад', callback_data='back_to_edit_product_card')
    edit_name = InlineKeyboardButton(text='Название', callback_data='Название')
    edit_description = InlineKeyboardButton(text='Описание', callback_data='Описание')
    edit_price = InlineKeyboardButton(text='Цену', callback_data='Цену')
    edit_minimum_to_sell = InlineKeyboardButton(text='Минимум для покупки', callback_data='Минимум для покупки')
    edit_media = InlineKeyboardButton(text='Медиа', callback_data='Медиа')
    edit_category = InlineKeyboardButton(text='Категорию', callback_data='Категорию')


class AdminButtons(
    ManageProductButtons,
    ManageAdminsButtons,
    EditProductCardButtons
):
    '''Кнопки админов'''
    to_admin_menu = InlineKeyboardButton(text='В админку', callback_data='В админку')
    accept = InlineKeyboardButton(text='Принять', callback_data='abuy')
    reject = InlineKeyboardButton(text='Отклонить', callback_data='rbuy')

    add_question_answer = InlineKeyboardButton(text='Добавить вопрос-ответ', callback_data='Добавить вопрос-ответ')
    del_question_answer = InlineKeyboardButton(text='Удалить вопрос-ответ', callback_data='Удалить вопрос-ответ')
    product_info = InlineKeyboardButton(text='Информация о товаре', callback_data='Информация о товаре')
    purchase_info = InlineKeyboardButton(text='Информация о покупке', callback_data='Информация о покупке')


class Buttons(UserButtons, AdminButtons):
    '''Все кнопки бота'''
    stop_send_photo = InlineKeyboardButton(text='Готово', callback_data='end_send_photo')


class UserKeyboards(Buttons):
    '''Клавиатуры пользователей'''


    def check_pay_markup(
            self,
            purchase_id: int | str
    ):
        return self.inline_markup_from_buttons(
            InlineKeyboardButton(
                text=self.check_pay.text,
                callback_data=f'{self.check_pay.callback_data}_{purchase_id}'
            )
        )


    def inline_markup_from_buttons(
            self,
            *buttons: InlineKeyboardButton,
            adjust: int = 1
    ) -> InlineKeyboardMarkup | None:
        '''
        Возвращает клаву из переданных кнопок, либо None, если кнопки не переданы
        '''
        if len(buttons) == 0:
            return

        builder = InlineKeyboardBuilder()
        builder.add(*buttons)
        builder.adjust(adjust)
        return builder.as_markup()


    def basket_markup(self, products_dict: dict) -> InlineKeyboardMarkup:
        '''Клавиатура корзины'''
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Назад', callback_data=self.to_shop.callback_data)
        )
        if len(products_dict) > 0:
            builder.row(
                self.edit_product_count,
                self.del_product,
                self.clear_basket,
                self.buy
            )
        builder.adjust(1)
        return builder.as_markup()


    def user_start_menu(self, is_admin: bool = False) -> InlineKeyboardMarkup:
        '''Клавиатура меню'''
        builder = InlineKeyboardBuilder()
        builder.add(
            self.to_shop,
            self.rewiews,
            self.questions,
            self.feedback
        )
        if is_admin:
            builder.add(self.to_admin_menu)
        builder.adjust(1)
        return builder.as_markup()


    def one_button_inline_markup(self, text: str, callback_data: str) -> InlineKeyboardMarkup:
        '''
        Клавиатура с одной кнопкой

        :param text: Текст кнопки
        :param callback_data: колбек дата кнопки
        '''
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text=text, callback_data=callback_data)
        )
        return builder.as_markup()


    def market_markup(self) -> InlineKeyboardMarkup:
        '''Клавиатура меню магаза'''
        builder = InlineKeyboardBuilder()
        builder.row(
            self.categories,
            self.purchases_history,
            self.find_by_id,
            self.open_basket,
            self.to_user_menu,
            width=2
        )
        return builder.as_markup()


    def make_category_markup(self, categories: List[str]) -> InlineKeyboardMarkup:
        '''
        Создает клаву с выбором категорий и пагинацией

        :param categories: категории, которые будут запиханы в клаву, обязательно четное количество!
        '''
        builder = InlineKeyboardBuilder()
        btns = [InlineKeyboardButton(text=i, callback_data=i) for i in categories]
        builder.row(
            *btns,
            width=2
        )
        builder.row(
            self.previous_page_category,
            InlineKeyboardButton(text='Назад', callback_data=Keyboards.to_shop.callback_data),
            self.next_page_category
        )

        return builder.as_markup()


    def make_product_makrup(self, product_id: int) -> InlineKeyboardMarkup:
        '''
        Создает клаву с выбором товара и пагинацией

        :param product_id: id товара в бд
        :parma with_open_basket: Добавить ли кнопку "открыть корзину"
        '''
        builder = InlineKeyboardBuilder()
        builder.add(
            self.previous_page_product,
            self.next_page_product
        )
        if product_id is not None:
            builder.row(InlineKeyboardButton(text='В корзину', callback_data=str(product_id)))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=Keyboards.categories.callback_data))

        return builder.as_markup()


    def make_finded_product_makrup(self, product_id: int) -> InlineKeyboardMarkup:
        '''
        Создает клаву с добавлением товара в корзину

        :param product_id: id товара в бд
        '''
        builder = InlineKeyboardBuilder()
        if product_id is not None:
            builder.row(InlineKeyboardButton(text='В корзину', callback_data=str(product_id)))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=Keyboards.to_shop.callback_data))

        return builder.as_markup()


    def back_to_user_menu(self) -> InlineKeyboardMarkup:
        '''Создает клаву с кнопкой назад в меню пользователя'''

        return self.inline_markup_from_buttons(
            InlineKeyboardButton(text='Назад', callback_data=self.to_user_menu.callback_data)
        )


    def stop_send_feedback_photo(self) -> InlineKeyboardMarkup:
        '''Создает клаву с кнопками "Отправить" и "Назад" в меню юзера'''
        return self.inline_markup_from_buttons(
            self.stop_send_photo,
            InlineKeyboardButton(text='Назад', callback_data=self.to_user_menu.callback_data)
        )


class AdminKeyboards(Buttons):
    '''Клавиатуры админов'''


    def inline_markup_from_buttons(
            self,
            *buttons: InlineKeyboardButton,
            adjust: int = 1
    ) -> InlineKeyboardMarkup | None:
        '''
        Возвращает клаву из переданных кнопок, либо None, если кнопки не переданы
        '''
        if len(buttons) == 0:
            return

        builder = InlineKeyboardBuilder()
        builder.add(*buttons)
        builder.adjust(adjust)
        return builder.as_markup()


    def admin_menu_markup(self, admin_id: int) -> InlineKeyboardMarkup:
        '''Возвращает клаву меню админа'''
        btns = []
        cp = CheckPrivilegies(admin_id)
        if cp.can_manage_admins():
            btns.append(self.manage_admins)
        if cp.can_manage_products():
            btns.append(self.manage_products)
        if cp.can_edit_questions():
            btns.append(self.add_question_answer)
            btns.append(self.del_question_answer)
        if cp.can_get_purchase_info():
            btns.append(self.purchase_info)
        btns.append(self.product_info)
        btns.append(
            InlineKeyboardButton(text='В меню покупателя', callback_data=self.to_user_menu.callback_data)
        )
        return self.inline_markup_from_buttons(
            *btns,
            adjust=2
        )


    def multiple_choose_markup(
            self,
            btns: list[str],
            choosed: list[str],
            back_callback: str
    ) -> InlineKeyboardButton:
        markup_btns = [InlineKeyboardButton(text=f'✅{i}' if i in choosed else f'❌{i}', callback_data=i) for i in btns]
        markup_btns.append(InlineKeyboardButton(text='Назад', callback_data=back_callback))
        return self.inline_markup_from_buttons(*markup_btns)


    def back_to_admin_menu_markup(self) -> InlineKeyboardMarkup:
        '''Клава с кнопкой назад с колбеком в админ меню'''
        return self.inline_markup_from_buttons(
            InlineKeyboardButton(
                text='Назад',
                callback_data=self.to_admin_menu.callback_data
            )
        )


    def back_to_manage_admin_markup(self) -> InlineKeyboardMarkup:
        '''Клава с кнопкой назад с колбеком в управление админами'''
        return self.inline_markup_from_buttons(
            InlineKeyboardButton(
                text='Назад',
                callback_data=self.manage_admins.callback_data
            )
        )


    def back_to_manage_products(self) -> InlineKeyboardMarkup:
        '''Клава с кнопкой назад с колбеком в управление товарами'''
        return self.inline_markup_from_buttons(
            InlineKeyboardButton(
                text='Назад',
                callback_data=self.manage_products.callback_data
            )
        )


    def manage_admins_markup(self, admin_id: int) -> InlineKeyboardMarkup:
        '''Возвращает клаву управления админами'''

        btns = []
        cp = CheckPrivilegies(admin_id)

        if cp.can_add_del_role():
            btns.append(self.add_role)
            btns.append(self.del_role)
        if cp.can_get_role_info():
            btns.append(self.role_info)
        if cp.can_edit_role_privilegies():
            btns.append(self.edit_role_privilegies)
        if cp.can_add_del_admin():
            btns.append(self.add_admin)
            btns.append(self.del_admin)
        if cp.can_get_admin_info():
            btns.append(self.admin_info)
        if cp.can_get_role_list():
            btns.append(self.roles)
        if cp.can_get_admin_list():
            btns.append(self.admins)

        btns.append(InlineKeyboardButton(text='Назад', callback_data=self.to_admin_menu.callback_data))
        return self.inline_markup_from_buttons(*btns)


    def stop_send_product_photo_markup(self) -> InlineKeyboardMarkup:
        '''Клава на этапе отправки медиа товара'''
        return self.inline_markup_from_buttons(
            self.stop_send_photo,
            InlineKeyboardButton(text='Назад', callback_data=self.manage_products.callback_data)
        )


    def stop_send_product_media_to_edit_markup(self) -> InlineKeyboardMarkup:
        '''Клава на отправку медиа при изменении товара'''
        return self.inline_markup_from_buttons(
            self.stop_send_photo,
            self.back_to_edit_product_card,
            self.manage_products
        )


    def manage_products_markup(self, admin_id: int) -> InlineKeyboardMarkup:
        '''Возвращает клаву управления товарами'''

        btns = []
        cp = CheckPrivilegies(admin_id)

        if cp.can_add_del_cat():
            btns.append(self.add_cat)
            btns.append(self.del_cat)
        if cp.can_add_del_product():
            btns.append(self.add_product)
            btns.append(self.del_product_from_shop)
        if cp.can_edit_product_card():
            btns.append(self.edit_product_card)
        if cp.can_add_product_count():
            btns.append(self.add_product_count)

        btns.append(InlineKeyboardButton(text='Назад', callback_data=self.to_admin_menu.callback_data))
        return self.inline_markup_from_buttons(*btns)


    def edit_product_card_markup(self) -> InlineKeyboardMarkup:
        '''Клава с кнопками изменения карточки товара'''

        return self.inline_markup_from_buttons(
            self.edit_name,
            self.edit_category,
            self.edit_description,
            self.edit_price,
            self.edit_minimum_to_sell,
            self.edit_media,
            InlineKeyboardButton(text='Назад', callback_data=self.manage_products.callback_data)
        )


    def back_to_edit_product_card_markup(self) -> InlineKeyboardMarkup:
        '''Клава с кнопкой назад к изменению товара на этап, где айди товара уже принят'''
        return self.inline_markup_from_buttons(
            self.back_to_edit_product_card,
            self.manage_products
        )


    def rewiew_buy(self, purchase_id, with_none_product: bool = False):
        if with_none_product:
            return None
        return self.inline_markup_from_buttons(
            InlineKeyboardButton(
                text=self.accept.text,
                callback_data=f'{self.accept.callback_data}_{purchase_id}'
            ),
            InlineKeyboardButton(
                text=self.reject.text,
                callback_data=f'{self.reject.callback_data}_{purchase_id}'
            )
        )


class Keyboards(UserKeyboards, AdminKeyboards):
    '''Все клавиатуры бота'''
