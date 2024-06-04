from core.utils.database.database import db
from config import RolePrivilegies


class CheckPrivilegies():
    '''проверки прав админов'''


    def __init__(self, admin_id: int) -> None:
        self.admin = db.get_admin(admin_id)
        self.privilegies = []
        if self.admin is not None:
            privilegies = db.get_all_role_privilegies(self.admin.role)
            user_privilegies = [i.privilegies for i in privilegies]
            rp = RolePrivilegies()
            privilegies = rp.get_all_privilegies()
            for i in user_privilegies:
                if i in privilegies:
                    self.privilegies.append(i)


    def have_any_privilegies(self) -> bool:
        '''Имеет ли права админа пользователь'''
        if len(self.privilegies) == 0:
            return False
        return True


    def have_privilegie(self, privilegie: str) -> bool:
        '''Имеет ли право на'''
        return privilegie in self.privilegies


    def can_manage_admins(self) -> bool:
        '''Может ли управлять админами'''
        checkers = [
            self.can_add_del_admin,
            self.can_add_del_role,
            self.can_get_admin_info,
            self.can_get_role_info,
            self.can_get_admin_list,
            self.can_get_role_list,
            self.can_edit_role_privilegies
        ]
        can = False
        for i in checkers:
            if i():
                can = True
        return can


    def can_manage_products(self) -> bool:
        '''Может ли управлять товарами'''
        checkers = [
            self.can_get_purchase_info,
            self.can_add_del_cat,
            self.can_add_del_product,
            self.can_add_product_count,
            self.can_edit_product_card
        ]
        can = False
        for i in checkers:
            if i():
                can = True
        return can


    def can_rewiew_pay(self) -> bool:
        '''Может ли принимать и отклонять оплату'''
        return self.have_privilegie(RolePrivilegies.privilegie_rewiew_pay)


    def can_answer_tickets(self) -> bool:
        '''Может ли отвечать на обращения в поддержку'''
        return self.have_privilegie(RolePrivilegies.privilegie_answer_tickets)


    def can_edit_questions(self) -> bool:
        '''Может ли добавлять и удалять ответы на вопросы'''
        return self.have_privilegie(RolePrivilegies.privilegie_edit_questions)


    def can_get_purchase_info(self) -> bool:
        '''Может ли получать информацию о покупке'''
        return self.have_privilegie(RolePrivilegies.privilegie_get_purchase_info)


    def can_add_product_count(self) -> bool:
        '''Может ли добавлять кол-во товаров'''
        return self.have_privilegie(RolePrivilegies.privilegie_add_product_count)


    def can_edit_product_card(self) -> bool:
        '''Может ли изменять карточки товара'''
        return self.have_privilegie(RolePrivilegies.privilegie_edit_product_card)


    def can_add_del_product(self) -> bool:
        '''Может ли удалять и добавлять товары'''
        return self.have_privilegie(RolePrivilegies.privilegie_add_del_product)


    def can_add_del_cat(self) -> bool:
        '''Может ли удалять и добавлять категории'''
        return self.have_privilegie(RolePrivilegies.privilegie_add_del_cat)


    def can_edit_role_privilegies(self) -> bool:
        '''Может ли изменять права ролей'''
        return self.have_privilegie(RolePrivilegies.privilegie_edit_role_privilegies)


    def can_get_role_list(self) -> bool:
        '''Может ли получать список ролей'''
        return self.have_privilegie(RolePrivilegies.privilegie_get_roles_list)


    def can_get_admin_list(self) -> bool:
        '''Может ли получать список админов'''
        return self.have_privilegie(RolePrivilegies.privilegie_get_admin_list)


    def can_get_role_info(self) -> bool:
        '''Может ли получать инфу о роли'''
        return self.have_privilegie(RolePrivilegies.privilegie_get_role_info)


    def can_add_del_admin(self) -> bool:
        '''Может ли удалять и добавлять админов'''
        return self.have_privilegie(RolePrivilegies.privilegie_add_del_admin)


    def can_add_del_role(self) -> bool:
        '''Может ли удалить и добавлять роли'''
        return self.have_privilegie(RolePrivilegies.privilegie_add_del_role)


    def can_get_admin_info(self) -> bool:
        '''Может ли получать инфу об админе'''
        return self.have_privilegie(RolePrivilegies.privilegie_get_admin_info)
