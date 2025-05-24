import logging
from pyrogram import Client
from pyrogram.types import Message

import globals as g

log = logging.getLogger("rhgTGBot:info:help")



default_help_message = "Привет! Это информационное сообщение с короткой сводкой по командам.\n" \
                        "Ты можешь написать /help $category\n" \
                        "Если ты хочешь подробнее узнать о категории комманд\n" \
                        "Вот какие категории я знаю: gemini\n" \
                        "/start - Приветственное сообщение\n" \
                        "/help - эта справка или справка по категории\n" \
                        # "Коммандой же /set_token $token ты можещь добавить свой gemini токен, и тогда я буду разговаривать\n\n" \
                        # "**Внимание:** Весь процесс требует полного доверия ко мне, так как ты будешь вводить свои данные для входа."

register_help_message = "В данном боте можно зарегистрироваться вручную. \n" \
                        "Для этого просто введите команду /register" \

ai_help_message = "Информация о командах секции ai:\n" \
                    "/set_token $token - установить Gemini token на твою учетную запись\n" \
                    "/del_token - удалить Gemini token из учетной запись\n" \
                    "/set_gmn_arg $arg $val - Установить $arg в конфигурации на значение $val\n" \
                    " - forgot - Каждый раз забывать историю сообщений (y/n)\n" \
                    " - search - Каждый раз использовать Google search (y/n)\n" \
                    " - model - Какую модель использовать по умолчанию (1.5/2.0/2.5)\n" \
                    " - delete - Удалять сообщение после того как на него ответить (y/n)" \
                    " - skip_msg - Не добавлять пару сообщений в историю.\n" \
                    " - study_me - Изучение пользователя.\n" \
                    " - system_instruction - Системный промт (Любой текст)\n" \
                    " - max_chat_size - Максимальноая длинна чата. (Любое целое число. По умолчанию 15)\n" \
                    "/del_gmn_arg $arg $val - Удалить $arg из конфигурации\n" \
                    "Ключи которые можно переать прямо во время запроса (Они работают только на 1 пару сообщений):\n" \
                    " - f = forgot\n" \
                    " - s = search\n" \
                    " - d = delete\n" \
                    " - n = Не добавлять эту пару сообщений в историб\n" \
                    " - 0 = gemini-1.5-flash\n" \
                    " - 1 = gemini-2.0-flash\n" \
                    " - 2 = gemini-2.5-pro\n\n" \
                    "Пример запроса:\n" \
                    "@bot/flags=±N\n" \
                    " - = - Поймать сообщения только указанного пользователя\n" \
                    " - + - Читать на указанное колличество сообщений вверх\n" \
                    " - - - Читать на указанное колличество сообщений вниз\n" \
                    " - ~ - Читать от этого сообщения\n" \
                    " - N - На какое колличество сообщений читать\n"

async def help_command(client: Client, message: Message):
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) вызвал помощь")
    match message.command[1]:
        case "gemini":
            await message.reply_text(ai_help_message)
        case _:
            pass