from typing import List

from sqlalchemy import Column, BigInteger, String

from core.utils.database.base_db_parametrs import Base, Session


class ProductsTable():
    Session = Session


    class Products(Base):
        __tablename__ = 'products'

        product_id = Column(BigInteger(), primary_key=True, autoincrement=True)
        name = Column(String())
        category = Column(String())
        description = Column(String())
        price = Column(BigInteger())
        count = Column(BigInteger())
        minimum_to_sell = Column(BigInteger())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_product(
            self,
            name: str,
            category: str,
            description: str,
            price: int,
            count: int,
            minimum_to_sell: int,
            **kwargs
    ) -> None:
        '''
        Добавляет карточку товара в бд

        :param name: Название товара
        :param category: Категория товара(из бд)
        :param description: Описание товара
        :param price: цена товара
        :param count: количество на складе
        :param minimum_to_sell: Минимальное количество для покупки
        '''

        with self.Session() as s:
            product = self.Products(
                name=name,
                category=category,
                description=description,
                price=price,
                count=count,
                minimum_to_sell=minimum_to_sell
            )
            s.add(product)
            s.commit()
            return product.product_id


    # -------------------------
    # ---------- edit ---------
    # -------------------------


    def edit_product_count(
            self,
            product_id: int,
            count: int
    ) -> None:
        '''
        Изменяет число товара

        :param product_id: id товара для изменения
        :param count: новое кол-во товара
        '''

        with self.Session() as s:
            s.query(self.Products).filter(
                self.Products.product_id == product_id
            ).update({
                self.Products.count: count
            })
            s.commit()


    def edit_product_parametr(
            self,
            product_id: int,
            parametr: str,
            value: str
    ) -> None:
        '''
        Изменение параметра товара

        :param product_id: айди товара
        :param parametr: параметр для изменения
        '''

        with self.Session() as session:
            session.query(self.Products).filter(
                self.Products.product_id == int(product_id)
            ).update({
                parametr: value
            })
            session.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_product_by_name_and_category(
            self,
            name: str,
            category: str
    ) -> None:
        '''
        Возвращает продукт с определенным именем в определенной категории

        :param name: название товара
        :param category: категория товара
        '''

        with self.Session() as s:
            return s.query(self.Products).filter(
                self.Products.category == category,
                self.Products.name == name
            ).first()


    def get_product_by_id(
            self,
            product_id: int
    ) -> Products | None:
        '''
        Возвращает товар из бд, если найдет

        :param product_id: айди товара
        '''

        with self.Session() as s:
            return s.query(self.Products).filter(
                self.Products.product_id == int(product_id)
            ).first()


    def get_all_products_with_category(
            self,
            category: str
    ) -> List[Products]:
        '''
        Возвращает список продуктов определенной категории

        :param category: Категория товара(она должна быть в бд)
        '''

        with self.Session() as s:
            return s.query(self.Products).filter(
                self.Products.category == category
            ).order_by(
                self.Products.product_id
            ).all()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_product(
            self,
            product_id: int
    ) -> None:
        '''
        Удаляет продукт из бд

        :param product_id: айди товара для удаления
        '''

        with self.Session() as s:
            s.query(self.Products).filter(
                self.Products.product_id == product_id
            ).delete()
            s.commit()
