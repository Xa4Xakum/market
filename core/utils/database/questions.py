from typing import List

from sqlalchemy import Column, String

from core.utils.database.base_db_parametrs import Base, Session


class QuestionsTable():
    Session = Session


    class Questions(Base):
        __tablename__ = 'questions'

        question = Column(String(), primary_key=True)
        answer = Column(String())


    # -------------------------
    # ---------- add ----------
    # -------------------------


    def add_question(
        self,
        question: str,
        answer: str
    ) -> None:
        '''
        добавляет вопрос с ответом в бд

        :param question: вопрос
        :param answer: ответ
        '''

        with self.Session() as s:
            q = self.Questions(
                question=question,
                answer=answer
            )
            s.add(q)
            s.commit()


    # -------------------------
    # ---------- get ----------
    # -------------------------


    def get_questions(self) -> List[Questions]:
        '''
        Возвращает список вопросов с ответами
        '''

        with self.Session() as s:
            return s.query(self.Questions).all()


    def get_question(
            self,
            question: str
    ) -> None | Questions:
        '''
        Возвращает вопрос-ответ из бд

        :param question: вопрос
        '''

        with self.Session() as s:
            return s.query(self.Questions).filter(
                self.Questions.question == question
            ).first()


    # -------------------------
    # ---------- del ----------
    # -------------------------


    def del_question(
            self,
            question: str
    ) -> None:
        '''
        Удаляет вопрос-ответ

        :param question: вопрос для удаления
        '''

        with self.Session() as s:
            s.query(self.Questions).filter(
                self.Questions.question == question
            ).delete()
            s.commit()
