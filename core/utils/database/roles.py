from sqlalchemy import Column, String

from core.utils.database.base_db_parametrs import Base, Session


class RolesTable():
    Session = Session


    class Roles(Base):
        __tablename__ = 'roles'

        role = Column(String(), primary_key=True)


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_role(
            self,
            role: str
    ) -> None:
        '''
        Добавляет роль в бд

        :param role: новая роль
        '''

        with self.Session() as s:
            role = self.Roles(
                role=role
            )
            s.add(role)
            s.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_role(
            self,
            role: str
    ) -> Roles | None:
        '''
        Возвращает запись о роли

        :param role: название роли
        '''

        with self.Session() as s:
            return s.query(self.Roles).filter(
                self.Roles.role == role
            ).first()


    def get_all_roles(self) -> list[Roles]:
        '''Возвращает список всех ролей'''

        with self.Session() as session:
            return session.query(self.Roles).all()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_role(
            self,
            role: str
    ) -> None:
        '''Удаляет роль из бд'''

        with self.Session() as session:
            session.query(self.Roles).filter(
                self.Roles.role == role
            ).delete()
            session.commit()
