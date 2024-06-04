from typing import List

from sqlalchemy import Column, BigInteger, String

from core.utils.database.base_db_parametrs import Base, Session


class ProductsMediaTable():
    Session = Session


    class ProductsMedia(Base):
        __tablename__ = 'products_media'

        file_id = Column(String(), primary_key=True)
        product_id = Column(BigInteger())
        media_type = Column(String())

    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_product_media(
            self,
            file_id: str,
            product_id: int,
            media_type: str
    ) -> None:
        '''
        Добавляет медиа файл товара в бд

        :param file_id: айди файла в тг
        :param product_id: айди репорта, к которому прикреплен файл
        :param media_type: тип медиафайла(photo/video)
        '''

        with self.Session() as s:
            product = self.ProductsMedia(
                file_id=file_id,
                product_id=product_id,
                media_type=media_type
            )
            s.add(product)
            s.commit()
            return


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_all_media_by_product_id(
            self,
            product_id: int
    ) -> List[ProductsMedia]:
        '''
        Получение всех медиафайлов по айди товара

        :param product_id: айди товара
        '''

        with self.Session() as session:
            return session.query(self.ProductsMedia).filter(
                self.ProductsMedia.product_id == int(product_id)
            ).order_by(
                self.ProductsMedia.media_type
            ).all()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_all_product_media(
            self,
            product_id: int
    ) -> None:
        '''
        Удаляет все медиа продукта из бд

        :param product_id: айди товара для удаления
        '''

        with self.Session() as s:
            s.query(self.ProductsMedia).filter(
                self.ProductsMedia.product_id == product_id
            ).delete()
            s.commit()


    def del_media_by_file_id(
            self,
            file_id: str
    ) -> None:
        '''
        Удаление медиа по айди

        :param file_id: айди медиафайла
        '''

        with self.Session() as session:
            session.query(self.ProductsMedia).filter(
                self.ProductsMedia.file_id == file_id
            ).delete()
            session.commit()
