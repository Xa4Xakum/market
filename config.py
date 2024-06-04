import os
from enum import Enum

from dotenv import load_dotenv


class Modes(Enum):
    test = 'test'
    relise = 'relise'


class Config():
    '''Настройки бота'''

    def __init__(self, mode=Modes.test.value) -> None:
        self.mode = mode
        load_dotenv()


    def get_token(self):
        '''Токен бота'''
        if self.mode == Modes.test.value:
            return os.getenv('TOKEN_TEST')
        if self.mode == Modes.relise.value:
            return os.getenv('TOKEN')


    def get_yookassa_token(self):
        '''Секретный ключ юкассы'''
        if self.mode == Modes.test.value:
            return os.getenv('YOOKASSA_TOKEN_TEST')
        if self.mode == Modes.relise.value:
            return os.getenv('YOOKASSA_TOKEN')


    def get_yookassa_shop_id(self):
        '''Айди магазина юкассы'''
        if self.mode == Modes.test.value:
            return int(os.getenv('YOOKASSA_SHOP_ID_TEST'))
        if self.mode == Modes.relise.value:
            return int(os.getenv('YOOKASSA_SHOP_ID'))


    def get_admin_id(self):
        '''Айди владельца бота'''
        if self.mode == Modes.test.value:
            return int(os.getenv('ADMIN_ID_TEST'))
        if self.mode == Modes.relise.value:
            return int(os.getenv('ADMIN_ID'))


    def get_rewiew_chat_id(self):
        '''Чат рассмотрения оплаты, куда кидать заявки на оплату'''
        if self.mode == Modes.test.value:
            return int(os.getenv('CHAT_ID_TEST'))
        if self.mode == Modes.relise.value:
            return int(os.getenv('ADMIN_ID'))


    def get_feedback_chat_id(self):
        '''Чат подержки, куда кидать обращения'''
        if self.mode == Modes.test.value:
            return int(os.getenv('CHAT_ID_TEST'))
        if self.mode == Modes.relise.value:
            return int(os.getenv('ADMIN_ID'))


    def get_db_conneciton(self):
        login = os.getenv('DB_LOGIN')
        password = os.getenv('DB_PASSWORD')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')

        if self.mode == Modes.test.value:
            return f'postgresql+psycopg2://{login}:{password}@{host}:{port}/{db_name}'
        if self.mode == Modes.relise.value:
            return f'postgresql+psycopg2://{login}:{password}@{host}:{port}/{db_name}'


class PurchaseStatuses(Enum):
    '''Статусы оплаты'''
    waiting_money = 'Ожидает оплаты'
    canceled = 'Отменено'
    on_review = 'На рассмотрении'
    geted_money = 'Деньги получены'


class RolePrivilegies():
    '''Права ролей'''
    privilegie_add_del_admin = 'Добавлять/удалять админов'
    privilegie_get_admin_list = 'Смотреть список админов'
    privilegie_get_admin_info = 'Получать инф-ю об админе'
    privilegie_add_del_role = 'Добавлять/удалять роли'
    privilegie_edit_role_privilegies = 'Изменять права ролей'
    privilegie_get_roles_list = 'Смотреть список ролей'
    privilegie_get_role_info = 'Получать инф-ю о роли'

    privilegie_add_del_cat = 'Добавлять/удалять категории'
    privilegie_add_del_product = 'Добавлять/удалять товары'
    privilegie_edit_product_card = 'Изменять карточку товара'
    privilegie_add_product_count = 'Изменять кол-во товаров'
    privilegie_get_purchase_info = 'Получать инф-ю о покупке'

    privilegie_edit_questions = 'Добавлять/удалять вопросы'
    privilegie_answer_tickets = 'Отвечать в поддержке'
    privilegie_rewiew_pay = 'Принимать оплату'


    def get_all_privilegies(self) -> list[str]:
        '''Возвращает список прав'''
        return [
            v for k, v in RolePrivilegies.__dict__.items()
            if k.startswith('privilegie_')
        ]


conf = Config()
