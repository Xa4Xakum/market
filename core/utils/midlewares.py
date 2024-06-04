from typing import Callable, Dict, Any, Awaitable
from time import perf_counter

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.dispatcher.flags import get_flag

from loguru import logger

from core.utils.database.database import db
from core.utils.keyboards import Keyboards
from core.utils.operations import is_int, is_float
from core.utils.manage_data import ManageData

from helper import bot


class CheckInDB(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        kb = Keyboards()
        user = db.get_user_by_id(data["event_from_user"].id)
        if user is None:
            await bot.send_message(
                chat_id=data['event_from_user'].id,
                text='Перед началом работы, пожалуйста, пройдите короткую регистрацию',
                reply_markup=kb.to_registration_markup()
            )
            return

        return await handler(event, data)


class PlugManageData(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['md'] = ManageData(await data['state'].get_data())
        result = await handler(event, data)
        await data['state'].set_data(data['md'].get_data())
        return result


class AddMsgsToDelList(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        md = data['md']
        if event.chat.type == 'private' and event.text != '/start':
            md.add_msg_to_del_list(event)
        return await handler(event, data)


class ClearDelList(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        md = data['md']
        await md.clear_del_list()
        return await handler(event, data)


class UpdateLogger(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = perf_counter()
        if event.message:
            msg_content_type = event.message.content_type
            event_type = f'сообщение({msg_content_type})'
            event_text = event.message.caption if msg_content_type == 'photo' else event.message.text
        elif event.callback_query:
            event_type = 'колбек'
            event_text = event.callback_query.data
        else:
            event_type = 'неизвестный'
            event_text = 'неизвестный'

        logger.info(f'Пришел апдейт типа {event_type} от @{data["event_from_user"].username} с текстом {event_text}')
        result = await handler(event, data)

        end_time = perf_counter()
        logger.info(f'Апдейт от @{data["event_from_user"].username} обработан за {round(end_time - start_time, 3)} секунд')
        return result


class Throttler(BaseMiddleware):
    def __init__(self, rate_limit: int = 1) -> None:
        self.calls = {}
        self.rate_limit = rate_limit
        super().__init__()


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        call: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        time = perf_counter()
        chat_id = call.message.chat.id
        if chat_id not in self.calls:
            self.calls[chat_id] = time
        else:
            if (time - self.calls[chat_id]) < self.rate_limit:
                await call.answer(text='Не так быстро, ковбой')
                return
            self.calls[chat_id] = time
        return await handler(call, data)


class MessageChecker(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        msg: Message,
        data: Dict[str, Any]
    ) -> Any:
        checkers = self.get_checkers()

        for checker in checkers:
            if not await checker(self, data, msg):
                return

        return await handler(msg, data)


    def get_checkers(self):
        return [
            v for k, v in MessageChecker.__dict__.items()
            if k.startswith('check_')
        ]


    async def check_words_count(self, data: dict, msg: Message) -> bool:
        '''Проверка количества слов в сообщении'''
        text = get_flag(data, 'words_count')
        if text is not None:
            count = len(msg.text.split())
            if count != text['count']:
                to_del = await msg.answer(text=text['answer'])
                data['md'].add_msg_to_del_list(to_del)
                return False
        return True


    async def check_type_photo(self, data: dict, msg: Message) -> bool:
        '''Проверка на то, что это фото'''
        text = get_flag(data, "type_photo")
        if text is not None:
            if msg.content_type != 'photo':
                to_del = await msg.answer(text=text)
                data['md'].add_msg_to_del_list(to_del)
                return False
        return True


    async def check_type_text(self, data: dict, msg: Message) -> bool:
        '''Проверка на то, что это текст'''
        text = get_flag(data, "type_text")
        if text is not None:
            if msg.content_type != 'text':
                to_del = await msg.answer(text=text)
                data['md'].add_msg_to_del_list(to_del)
                return False
        return True


    async def check_type_contact(self, data: dict, msg: Message) -> bool:
        '''Проверка на то, что это контакт'''
        text = get_flag(data, 'type_contact')
        if text is not None:
            if msg.content_type != 'contact':
                to_del = await msg.answer(text=text)
                data['md'].add_msg_to_del_list(to_del)
                return False
        return True


    async def check_type_location(self, data: dict, msg: Message) -> bool:
        '''Проверка на то, что это локация'''
        text = get_flag(data, 'type_location')
        if text is not None:
            if msg.content_type != 'location':
                to_del = await msg.answer(text=text)
                data['md'].add_msg_to_del_list(to_del)
                return False
        return True


    async def check_int_words(self, data: dict, msg: Message) -> bool:
        '''Проверка на то, что сообщение имеет формат цифры'''
        params = get_flag(data, 'int_words')

        if params is not None:
            text_params = msg.text.split()
            passed = True

            for index in params['indexes']:
                if not is_int(text_params[index]):
                    passed = False

            if not passed:
                to_del = await msg.answer(text=params['answer'])
                data['md'].add_msg_to_del_list(to_del)

            return passed
        return True


    async def check_float_words(self, data: dict, msg: Message) -> bool:
        '''Проверка на то, что сообщение имеет формат цифры'''
        params = get_flag(data, 'float_words')
        if params is not None:
            text_params = msg.text.split()
            passed = True
            for index in params['indexes']:
                if not is_float(text_params[index]):
                    passed = False

            if not passed:
                to_del = await msg.answer(text=params['answer'])
                data['md'].add_msg_to_del_list(to_del)

            return passed
        return True
