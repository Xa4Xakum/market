from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, String

from core.utils.database.base_db_parametrs import Base, Session


class FeedBackTable():
    Session = Session


    class FeedBack(Base):
        __tablename__ = 'feedback'

        ticket_id = Column(BigInteger(), primary_key=True, autoincrement=True)
        message_id = Column(BigInteger())
        sender_id = Column(BigInteger())
        date = Column(DateTime())
        ticket_text = Column(String())
        moderator_id = Column(BigInteger())
        answer_text = Column(String())
        answer_date = Column(DateTime())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_feedback(
            self,
            sender_id: int,
            date: datetime,
            ticket_text: str,
            message_id: int = None,
            moderator_id: int = None,
            answer_text: str = None,
            answer_date: datetime = None,
    ) -> int:
        '''
        Добавляет в бд обращение в поддержку

        :param message_id: айди сообщения в чате поддержки
        :param sender_id: айди, отправившего обращение
        :param date: дата и время обращения
        :param ticket_text: текст обращения
        :param moderator_id: айди ответившего на обращение
        :param answer_text: текст ответа модера
        :param answer_date: дата ответа

        :return: айди обращения
        '''

        with self.Session() as s:
            feedback = self.FeedBack(
                message_id=message_id,
                sender_id=sender_id,
                date=date,
                ticket_text=ticket_text,
                moderator_id=moderator_id,
                answer_text=answer_text,
                answer_date=answer_date
            )
            s.add(feedback)
            s.commit()
            return feedback.ticket_id


    # -------------------------
    # ---------- edit ---------
    # -------------------------


    def edit_feedback_message_id(
            self,
            ticket_id: int,
            message_id: int
    ) -> None:
        '''
        Изменение айди сообщения обращения в чате поддержки

        :param ticket_id: айди обращения
        :param message_id: айди сообщения
        '''

        with self.Session() as session:
            session.query(self.FeedBack).filter(
                self.FeedBack.ticket_id == int(ticket_id)
            ).update({
                self.FeedBack.message_id: message_id
            })
            session.commit()


    def answer_feedback(
            self,
            ticket_id: int,
            moderator_id: int,
            answer_text: str,
            answer_date: str
    ) -> None:
        '''
        Ответ на обращение

        :param ticket_id: айди обращения
        :param moderator_id: айди модератора
        :param answer_text: текст ответа
        :param answer_date: дата ответа
        '''

        with self.Session() as session:
            session.query(self.FeedBack).filter(
                self.FeedBack.ticket_id == int(ticket_id)
            ).update({
                self.FeedBack.moderator_id: moderator_id,
                self.FeedBack.answer_date: answer_date,
                self.FeedBack.answer_text: answer_text
            })
            session.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_all_admin_answers(
            self,
            admin_id: int
    ) -> list[FeedBack]:
        '''
        Все ответы админа

        :param admin_id: айди админа
        '''

        with self.Session() as session:
            return session.query(self.FeedBack).filter(
                self.FeedBack.moderator_id == int(admin_id)
            ).all()


    def get_all_admin_answers_since(
            self,
            admin_id: int,
            since: datetime,
    ) -> list[FeedBack]:
        '''
        Все ответы админа

        :param admin_id: айди админа
        :param since: дата, с которой интересуют ответы
        '''

        with self.Session() as session:
            return session.query(self.FeedBack).filter(
                self.FeedBack.moderator_id == int(admin_id),
                self.FeedBack.answer_date >= since
            ).all()


    def get_ticket_by_message_id(
            self,
            message_id: int
    ) -> FeedBack | None:
        '''
        Возвращает запись об обращении

        :param message_id: айди сообщения в чате поддержки
        '''

        with self.Session() as session:
            return session.query(self.FeedBack).filter(
                self.FeedBack.message_id == message_id
            ).first()
