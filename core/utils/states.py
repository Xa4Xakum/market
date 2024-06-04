from aiogram.fsm.state import StatesGroup, State


class FeedBack(StatesGroup):
    get_description = State()
    get_media = State()
    check = State()


class Shop(StatesGroup):
    choose_category = State()
    choose_product = State()
    get_count = State()
    del_product = State()
    get_count_to_edit = State()
    get_product_to_edit = State()
    get_id_to_find = State()


class AddProdCount(StatesGroup):
    get_id = State()
    get_new_count = State()


class AddCategory(StatesGroup):
    get_category = State()


class DelCategory(StatesGroup):
    get_category = State()


class DelProduct(StatesGroup):
    get_id = State()


class ProductInfo(StatesGroup):
    get_info = State()


class PurchaseInfo(StatesGroup):
    get_info = State()


class FAQ(StatesGroup):
    get_question = State()
    get_answer = State()


class DelFAQ(StatesGroup):
    get_question = State()


class AddRole(StatesGroup):
    get_role = State()


class DelRole(StatesGroup):
    get_role = State()


class RoleInfo(StatesGroup):
    get_role = State()


class EditRolePrivilegies(StatesGroup):
    get_role = State()
    get_privilegie = State()


class AdminInfo(StatesGroup):
    get_id = State()


class AddAdmin(StatesGroup):
    get_id = State()
    get_name = State()
    get_role = State()


class DelAdmin(StatesGroup):
    get_id = State()


class AddProduct(StatesGroup):
    get_category = State()
    get_name = State()
    get_description = State()
    get_count = State()
    get_media = State()
    get_price = State()
    get_minimum_to_sell = State()


class EditProductCard(StatesGroup):
    get_product_id = State()
    get_name = State()
    get_category = State()
    get_description = State()
    get_media = State()
    get_price = State()
    get_minimum_to_sell = State()


class MakingPurchaseStates(StatesGroup):
    get_address = State()
    get_fullname = State()
    get_phone_number = State()
