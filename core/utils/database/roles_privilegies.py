from sqlalchemy import Column, BigInteger, String

from core.utils.database.base_db_parametrs import Base, Session


class RolesPrivilegiesTable():
    Session = Session


    class RolesPrivilegies(Base):
        __tablename__ = 'roles_privilegies'

        enter_id = Column(BigInteger(), primary_key=True)
        role = Column(String())
        privilegies = Column(String())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_privilegie(
            self,
            role: str,
            privilegie: str
    ) -> None:
        '''
        Добавляет привелегию роли

        :param role: роль
        :param privilegie: привилегия
        '''

        with self.Session() as session:
            new_privilegie = self.RolesPrivilegies(
                role=role,
                privilegies=privilegie
            )
            session.add(new_privilegie)
            session.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_all_role_privilegies(
            self,
            role: str
    ) -> list[RolesPrivilegies]:
        '''
        Возвращает привилегии роли

        :param role: роль, привилегии которой надо получить
        '''

        with self.Session() as session:
            return session.query(self.RolesPrivilegies).filter(
                self.RolesPrivilegies.role == role
            ).all()


    def get_privilegie(
            self,
            role: str,
            privilegie: str
    ) -> RolesPrivilegies | None:
        '''
        Возвращает запись о праве

        :param role: роль
        :param privilegie: право
        '''

        with self.Session() as session:
            return session.query(self.RolesPrivilegies).filter(
                self.RolesPrivilegies.role == role,
                self.RolesPrivilegies.privilegies == privilegie
            ).first()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_role_privilegie(
            self,
            role: str,
            privilegie: str
    ) -> None:
        '''Удаление привилегии роли'''

        with self.Session() as session:
            session.query(self.RolesPrivilegies).filter(
                self.RolesPrivilegies.role == role,
                self.RolesPrivilegies.privilegies == privilegie
            ).delete()
            session.commit()
