#!/usr/bin/python3
# coding=utf-8

from time import time
from telebot import TeleBot


class ASBot:
    def runbot(self):
        # Initialize command handlers...
        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start(message):
            if message.chat.type == "private":
                self.bot.send_message(message.chat.id, 'Приветствую вас!')

        @self.bot.message_handler(commands=['addme'])
        def handle_addme(message):
            if message.chat.type == "private":
                if message.from_user.id not in self.blacklist:
                    self.blacklist.append(message.from_user.id)
                    self.bot.send_message(message.chat.id, 'Успешно добавил ваш ID в базу!')
                else:
                    self.bot.send_message(message.chat.id, 'Ваш ID уже есть в нашей базе!')

        @self.bot.message_handler(commands=['removeme'])
        def handle_removeme(message):
            if message.chat.type == "private":
                if message.from_user.id in self.blacklist:
                    self.blacklist.remove(message.from_user.id)
                    self.bot.send_message(message.chat.id, 'Ваш ID успешно удалён из базы!')
                else:
                    self.bot.send_message(message.chat.id, 'Вашего ID нет в нашей базе. Нечего удалять!')

        @self.bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
        def handle_join(message):
            if message.from_user.id not in self.blacklist:
                self.blacklist.append(message.from_user.id)
                self.bot.reply_to(message, 'Приветствуем вас в нашем чате! Это тестовое оповещение на время тестов бота. Ваш ID записан в наш журнал. Не размещайте ссылок, иначе нам придётся вас заблокировать!')

        @self.bot.message_handler(func=lambda m: m.chat.type == 'supergroup' and m.from_user.id in self.blacklist)
        @self.bot.edited_message_handler(func=lambda m: m.chat.type == 'supergroup' and m.from_user.id in self.blacklist)
        def handle_msg(message):
            try:
                if message.entities is not None:
                    for entity in message.entities:
                        if entity.type in ['url', 'text_link', 'mention']:
                            # Removing spam message and restricting user for 30 minutes...
                            self.bot.delete_message(message.chat.id, message.message_id)
                            self.bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time() + 60 * 60)
            except Exception as ex:
                print('Exception detected while handling spam message from %s. Inner exception message was: %s.' % (message.from_user.id, ex))

        # Run bot forever...
        self.bot.polling(none_stop=True)

    def __init__(self, key):
        self.bot = TeleBot(key)
        self.blacklist = []
