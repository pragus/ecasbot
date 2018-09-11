#!/usr/bin/python3
# coding=utf-8

# EC AntiSpam bot for Telegram Messenger
# Copyright (c) 2017 - 2018 EasyCoding Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time
import telebot

from .scorers import ScoreUser
from .settings import Settings


class FmtMsg:
    def __init__(self, text, extractor=None):
        self.__t = text
        self.__e = extractor

    def __call__(self, *args, **kwargs):
        fmt_args, fmt_kwargs = args, kwargs
        if self.__e:
            fmt_args, fmt_kwargs = self.__e(args, kwargs)
        return self.__t.format(*fmt_args, **fmt_kwargs)


class Transformers:
    Alog = lambda args, kwargs: (
        (
            args[0].new_chat_member.first_name,
            args[0].new_chat_member.id,
            args[1]
            ),
        {}
        )

    Amsgrm = lambda args, kwargs: (
        (
            args[0].from_user.first_name,
            args[0].from_user.id,
            args[0].reply_to_message.from_user.first_name,
            args[0].reply_to_message.from_user.id
            ),
        {}
        )

    MuteBan = lambda args, kwargs: (
        (
            args[0].from_user.first_name,
            args[0].from_user.id,
            args[1].username,
            args[1].userid
            ),
        {}
        )
    Aunres = lambda args, kwargs: (
        (
            args[0].from_user.first_name,
            args[0].from_user.id,
            args[0].reply_to_message.from_user.first_name,
            args[0].reply_to_message.from_user.id
            ),
        {}
        )


class Messages:
    Welcome = FmtMsg('Add me to supergroup and give me admin rights. I will try to block spammers automatically.')
    Alog = FmtMsg(
        'New user {} with ID {} has joined group. Score: {}.',
        Transformers.Alog
        )
    Restex = FmtMsg('Cannot restrict a new user with ID {} due to missing admin rights.')
    Msgex = FmtMsg('Exception detected while handling spam message from {}.')
    Notoken = FmtMsg('No API token entered. Cannot proceed. Fix this issue and run this bot again!')
    Joinhex = FmtMsg('Failed to handle join message.')
    Banned = FmtMsg('Permanently banned user with ID {} (score: {}).')
    Msgrest = FmtMsg(
        'Removed message from restricted user {} with ID {}.',
        lambda args, kwargs: (
            (
                args[0].from_user.first_name,
                args[0].from_user.id
                ),
            {}
            )
        )

    Amsgrm = FmtMsg(
        'Admin {} ({}) removed message from user {} with ID {}.',
        Transformers.Amsgrm
        )
    Amute = FmtMsg(
        'Admin {} ({}) permanently muted user {} with ID {}.',
        Transformers.MuteBan
        )
    Aunres = FmtMsg(
        'Admin {} ({}) removed all restrictions from user {} with ID {}.',
        Transformers.Aunres
        )
    Aban = FmtMsg(
        'Admin {} ({}) permanently banned user {} with ID {}.',
        Transformers.MuteBan
        )
    Admerr = FmtMsg('Failed to handle admin command.')
    Chkme = FmtMsg('Checking of account {} successfully completed. Your score is: {}.')
    Pmex = FmtMsg('Failed to handle command in private chat with bot.')


class Perm:
    New = dict(
        can_send_messages=True,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
        )
    Unrest = dict(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
        )
    Rest = dict(
        can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False,
        can_add_web_page_previews=False
        )


class Msg:
    def __init__(self, message, settings):
        self.__m = message
        self.__s = settings

    @property
    def username(self):
        if self.__m.reply_to_message.new_chat_member:
            return self.__m.reply_to_message.new_chat_member.first_name
        else:
            return self.__m.reply_to_message.from_user.first_name

    @property
    def userid(self):
        if self.__m.reply_to_message.new_chat_member:
            return self.__m.reply_to_message.new_chat_member.id
        else:
            return self.__m.reply_to_message.from_user.id

    @property
    def is_forward(self):
        return self.__m.forward_from or self.__m.forward_from_chat

    @property
    def is_entities_ok(self):
        if self.__m.entities:
            for entity in self.__m.entities:
                if entity.type in self.__s.restent:
                    return False
        return True

    @staticmethod
    def is_private_chat(message) -> bool:
        return message.chat.type == 'private'


class ASBot:
    def __check_restricted_user(self, m) -> bool:
        usr = self.bot.get_chat_member(m.chat.id, m.from_user.id)
        return m.chat.type == 'supergroup' and usr.status == 'restricted'

    def __check_admin_feature(self, m) -> bool:
        usr = self.bot.get_chat_member(m.chat.id, m.from_user.id)
        return m.chat.type == 'supergroup' and (
                m.from_user.id in self.__settings.admins or usr.status == 'administrator')

    def __score_user(self, user) -> int:
        # Combining first name with last name...
        username = '{} {}'.format(user.first_name, user.last_name) if user.last_name else user.first_name
        return self.__scorer.score(username)

    def runbot(self) -> None:
        # Initialize command handlers...
        @self.bot.message_handler(func=Msg.is_private_chat, commands=['start'])
        def handle_start(message):
            try:
                self.bot.send_message(message.chat.id, Messages.Welcome())
            except:
                self.__logger.exception(Messages.Pmex())

        @self.bot.message_handler(func=Msg.is_private_chat, commands=['checkme'])
        def handle_checkme(message):
            try:
                score = self.__score_user(message.from_user)
                self.bot.send_message(message.chat.id, Messages.Chkme(message.from_user.id, score))
            except:
                self.__logger.exception(Messages.Pmex())

        @self.bot.message_handler(func=self.__check_admin_feature, commands=['remove', 'rm'])
        def handle_remove(message):
            try:
                # Remove reported message...
                if message.reply_to_message:
                    self.bot.delete_message(message.chat.id, message.reply_to_message.message_id)
                    self.__logger.warning(Messages.Amsgrm(message))
            except:
                self.__logger.exception(Messages.Admerr())

        @self.bot.message_handler(func=self.__check_admin_feature, commands=['ban', 'block'])
        def handle_banuser(message):
            try:
                if message.reply_to_message:
                    msg = Msg(message, self.__settings)
                    if message.from_user.id != msg.userid:
                        self.bot.kick_chat_member(message.chat.id, msg.userid)
                        self.__logger.warning(Messages.Aban(message, msg))
            except:
                self.__logger.exception(Messages.Admerr())

        @self.bot.message_handler(func=self.__check_admin_feature, commands=['restrict', 'mute'])
        def handle_muteuser(message):
            try:
                if message.reply_to_message:
                    msg = Msg(message, self.__settings)
                    if message.from_user.id != msg.userid:
                        self.bot.restrict_chat_member(
                            message.chat.id, msg.userid,
                            until_date=int(time.time()),
                            **Perm.Rest
                            )
                        self.__logger.warning(Messages.Amute(message, msg))
            except:
                self.__logger.exception(Messages.Admerr())

        @self.bot.message_handler(func=self.__check_admin_feature, commands=['unrestrict', 'un'])
        def handle_unrestrict(message):
            try:
                if message.reply_to_message:
                    self.bot.restrict_chat_member(
                        message.chat.id,
                        message.reply_to_message.from_user.id,
                        **Perm.Unrest
                        )
                    self.__logger.warning(Messages.Aunres(message))
            except:
                self.__logger.exception(Messages.Admerr())

        @self.bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
        def handle_join(message):
            try:
                # Check user profile using our score system...
                score = self.__score_user(message.new_chat_member)
                self.__logger.info(Messages.Alog(message, score))
                try:
                    # If user get score >= 100 - ban him, else - restrict...
                    if score >= 100:
                        # Delete join message and ban user permanently...
                        self.bot.delete_message(message.chat.id, message.message_id)
                        self.bot.kick_chat_member(message.chat.id, message.new_chat_member.id)
                        # Also ban user who added him...
                        if message.from_user.id != message.new_chat_member.id:
                            self.bot.kick_chat_member(message.chat.id, message.from_user.id)
                        # Writing information to log...
                        self.__logger.warning(Messages.Banned(message.new_chat_member.id, score))
                    else:
                        # Restrict all new users for specified in config time...
                        self.bot.restrict_chat_member(
                            message.chat.id,
                            message.new_chat_member.id,
                            until_date=int(time.time()) + self.__settings.bantime,
                            **Perm.New
                            )
                except Exception:
                    # We have no admin rights, show message instead...
                    self.__logger.exception(Messages.Restex(message.from_user.id))
            except Exception:
                self.__logger.exception(Messages.Joinhex())

        @self.bot.message_handler(func=self.__check_restricted_user)
        @self.bot.edited_message_handler(func=self.__check_restricted_user)
        def handle_msg(message):
            try:
                msg = Msg(message, self.__settings)
                # Removing messages from restricted members...
                if msg.is_forward or not msg.is_entities_ok:
                    self.bot.delete_message(message.chat.id, message.message_id)
                    self.__logger.info(Messages.Msgrest(message))
            except Exception:
                self.__logger.exception(Messages.Msgex(message.from_user.id))

        # Run bot forever...
        self.bot.polling(none_stop=True)

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.__schema = 1
        self.__logger = logging.getLogger(__name__)
        self.__settings = Settings(self.__schema)
        self.__scorer = ScoreUser(self.__settings, self.__logger)
        if not self.__settings.tgkey:
            raise Exception(Messages.Notoken())
        self.bot = telebot.TeleBot(self.__settings.tgkey)
