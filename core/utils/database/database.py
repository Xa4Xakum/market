from core.utils.database import (
    products,
    products_media,
    categories,
    purchase,
    purchase_products,
    questions,
    feedback,
    roles,
    roles_privilegies,
    admins
)
from core.utils.database.base_db_parametrs import Base, engine


class DataBase(
    products.ProductsTable,
    products_media.ProductsMediaTable,
    categories.CategoriesTable,
    purchase.PurchaseTable,
    purchase_products.PurchaseProductsTable,
    questions.QuestionsTable,
    feedback.FeedBackTable,
    roles.RolesTable,
    roles_privilegies.RolesPrivilegiesTable,
    admins.AdminsTable
):
    '''
    Класс для работы с базой данных
    '''
    Base.metadata.create_all(engine, checkfirst=True)


db = DataBase()
