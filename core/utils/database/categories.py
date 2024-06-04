from typing import List

from sqlalchemy import Column, String

from core.utils.database.base_db_parametrs import Base, Session


class CategoriesTable():
    Session = Session


    class Categories(Base):
        __tablename__ = "categories"

        name = Column(String(), primary_key=True)


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_category(
            self,
            name: str
    ) -> None:
        '''
        Добавляет категорию товаров

        :param name: Название категории
        '''

        with self.Session() as s:
            category = self.Categories(
                name=name
            )
            s.add(category)
            s.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_category(
            self,
            name: str
    ) -> Categories | None:
        '''
        Возвращает запись о категории из бд, либо нон

        :param name: Название категории
        '''

        with self.Session() as s:
            return s.query(self.Categories).filter(
                self.Categories.name == name
            ).first()


    def get_all_categories(self) -> List[Categories]:
        '''
        Возвращает список категорий из бд
        '''

        with self.Session() as s:
            return s.query(self.Categories).all()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_category(
            self,
            category: str
    ) -> None:
        '''
        Удаляет категорию
        '''

        with self.Session() as s:
            s.query(self.Categories).filter(
                self.Categories.name == category
            ).delete()
            s.commit()
