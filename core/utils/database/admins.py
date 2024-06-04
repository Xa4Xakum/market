from sqlalchemy import Column, BigInteger, String

from core.utils.database.base_db_parametrs import Base, Session


class AdminsTable():
    Session = Session


    class Admins(Base):
        __tablename__ = 'admins'

        admin_id = Column(BigInteger(), primary_key=True)
        role = Column(String())
        name = Column(String())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_admin(
            self,
            admin_id: int,
            role: str,
            name: str
    ) -> None:
        '''
        Добавление записи об админе в бд

        :param admin_id: айди админа в тг
        :param role: роль админа
        :param name: имя админа
        '''

        with self.Session() as session:
            admin = self.Admins(
                admin_id=admin_id,
                role=role,
                name=name
            )
            session.add(admin)
            session.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_admin(
            self,
            admin_id: int
    ) -> Admins | None:
        '''
        Возвращает запись об админе

        :param admin_id: айди админа
        '''

        with self.Session() as session:
            return session.query(self.Admins).filter(
                self.Admins.admin_id == admin_id
            ).first()


    def get_all_admins(self) -> list[Admins]:
        '''Возвращает список всех админов'''

        with self.Session() as session:
            return session.query(self.Admins).all()


    def get_all_admins_with_role(
            self,
            role: str
    ) -> list[Admins]:
        '''
        Список админов с этой ролью

        :param role: роль админов
        '''

        with self.Session() as session:
            return session.query(self.Admins).filter(
                self.Admins.role == role
            ).all()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_admin(
            self,
            admin_id: int
    ) -> None:
        '''Удаляет админа из бд'''

        with self.Session() as session:
            session.query(self.Admins).filter(
                self.Admins.admin_id == int(admin_id)
            ).delete()
            session.commit()
