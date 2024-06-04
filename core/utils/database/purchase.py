from typing import List

from sqlalchemy import Column, BigInteger, String

from core.utils.database.base_db_parametrs import Base, Session


class PurchaseTable():
    Session = Session


    class Purchase(Base):
        __tablename__ = 'purchase'

        purchase_id = Column(BigInteger(), primary_key=True, autoincrement=True)
        user_id = Column(BigInteger())
        status = Column(String())
        address = Column(String())
        fullname = Column(String())
        phone_number = Column(String())
        amount = Column(BigInteger())
        payment_id = Column(String())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_purchase(
        self,
        user_id: int,
        status: str,
        address: str,
        fullname: str,
        phone_number: str,
        amount: int = None,
        payment_id: str = None
    ) -> int:
        '''
        Добавляет покупку пользователя в бд

        :param user_id: айди пользователя в тг
        :param status: статус покупки
        :param address: адрес доставки
        :param fullname: полное имя получающего
        :param phone_number: телефон получающего
        :param amount: общая стоимость покупки
        :param payment_id: айди оплаты юкассы

        :return: айди покупки
        '''

        with self.Session() as s:
            purchase = self.Purchase(
                user_id=user_id,
                status=status,
                address=address,
                fullname=fullname,
                phone_number=phone_number,
                amount=amount,
                payment_id=payment_id
            )
            s.add(purchase)
            s.commit()
            return purchase.purchase_id


    # -------------------------
    # ---------- edit ---------
    # -------------------------


    def edit_purchase_amount(
            self,
            purchase_id: int,
            amount: int
    ) -> None:
        '''
        Изменяет общую стоимость покупки

        :param purchase_id: айди покупки для изменения
        :param amount: новая общая стоимость
        '''

        with self.Session() as s:
            s.query(self.Purchase).filter(
                self.Purchase.purchase_id == purchase_id
            ).update({
                self.Purchase.amount: amount
            })
            s.commit()


    def edit_purchase_payment_id(
            self,
            purchase_id: int,
            payment_id: str
    ) -> None:
        '''
        Изменяет айди оплаты

        :param purchase_id: айди покупки
        :param payment_id: новое айди оплаты
        '''

        with self.Session() as s:
            s.query(self.Purchase).filter(
                self.Purchase.purchase_id == purchase_id
            ).update({
                self.Purchase.payment_id: payment_id
            })
            s.commit()


    def edit_purchase_status(
            self,
            purchase_id: int,
            status: str
    ) -> None:
        '''
        Изменяет статус покупки

        :param purchase_id: айди покупки
        :param status: новый статус покупки
        '''

        with self.Session() as s:
            s.query(self.Purchase).filter(
                self.Purchase.purchase_id == purchase_id
            ).update({
                self.Purchase.status: status
            })
            s.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_purchase(
            self,
            purchase_id: int
    ) -> Purchase | None:
        '''
        Возвраащет запись о покупке, либо нон

        :param purchase_id: айди покупки
        '''

        with self.Session() as s:
            return s.query(self.Purchase).filter(
                self.Purchase.purchase_id == purchase_id
            ).first()


    def get_all_user_purchases(
        self,
        user_id: int
    ) -> List[Purchase]:
        '''
        Возвращает список покупок пользователя

        :param user_id: айди пользователя в тг
        '''

        with self.Session() as s:
            return s.query(self.Purchase).filter(
                self.Purchase.user_id == int(user_id)
            ).order_by(
                self.Purchase.purchase_id
            ).all()
