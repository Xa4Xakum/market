from sqlalchemy import Column, BigInteger

from core.utils.database.base_db_parametrs import Base, Session


class PurchaseProductsTable():
    Session = Session


    class PurchaseProducts(Base):
        __tablename__ = 'purchase_products'

        enter_id = Column(BigInteger(), primary_key=True, autoincrement=True)
        purchase_id = Column(BigInteger())
        product_id = Column(BigInteger())
        count = Column(BigInteger())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_purchase_products(
            self,
            purchase_id: int,
            product_id: int,
            count: int
    ) -> None:
        '''
        Добавляет товар покупки

        :param purchase_id: айди покупки
        :param product_id: айди товара
        :param count: количество
        '''

        with self.Session() as s:
            product = self.PurchaseProducts(
                purchase_id=purchase_id,
                product_id=product_id,
                count=count
            )
            s.add(product)
            s.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_purchase_products(
            self,
            purchase_id: int
    ) -> PurchaseProducts:
        '''
        Возвращает все товары определенной покупки

        :param purchase_id: айди покупки
        '''

        with self.Session() as s:
            return s.query(self.PurchaseProducts).filter(
                self.PurchaseProducts.purchase_id == purchase_id
            ).all()
