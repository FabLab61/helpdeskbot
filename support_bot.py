#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   This file is part of Support Bot.
#   Copyright (C) 2017  Sergey Sherkunov <leinlawun@openmailbox.org>
#
#   This Support Bot is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This Support Bot is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

from os import environ
from logging import basicConfig, warning, INFO
from functools import wraps
from gettext import translation
from redis import StrictRedis
from redis.exceptions import ConnectionError
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, ConversationHandler, MessageHandler, CommandHandler, Filters

def language(fn):
    @wraps(fn)
    def wrapper(bot, update, *args, **kwargs):
        language = None
        try:
            language = db.get(str(update.message.chat_id))
        except ConnectionError as error:
            exception(error)
            language = 'ru_RU'
            pass

        global _

        try:
            _ = translation('support_bot',
                            localedir = 'locale',
                            languages = [language]).gettext
        except AttributeError as error:
            exception(error)
            _ = lambda message: message
            pass

        return fn(bot, update, *args, **kwargs)
    return wrapper

@language
def display_keyboard(bot, update, keyboard):
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_text(_('Please choose:'), reply_markup = reply_markup)

@language
def start(bot, update):
    keyboard = [[_('Settings'), _('Support'), _('Help')]]

    display_keyboard(bot, update, keyboard)

    return START_PRESSED

@language
def start_pressed(bot, update):
    data = update.message.text

    if data == _('Settings'):
        return settings(bot, update)
    elif data == _('Support'):
        return support(bot, update)
    elif data == _('Help'):
        return help(bot, update)
    else:
        return start(bot, update)

@language
def settings(bot, update):
    keyboard = [[_('Language')]]

    display_keyboard(bot, update, keyboard)

    return SETTING_PRESSED

@language
def settings_pressed(bot, update):
    data = update.message.text

    if data == _('Language'):
        return select_language(bot, update)
    else:
        return settings(bot, update)

@language
def select_language(bot, update):
    keyboard = [[_('en_US'), _('ru_RU')]]

    display_keyboard(bot, update, keyboard)

    return SELECT_LANGUAGE_PRESSED

@language
def select_language_pressed(bot, update):
    message = update.message
    chat_id = message.chat_id
    data = message.text

    try:
        db.set(str(chat_id), data)
    except ConnectionError as err:
        exception(error)
        pass

    return start(bot, update)

@language
def support(bot, update):
    update.message.reply_text(_('Please tell us, what is your problem.'))

    return SUPPORT_PRESSED

@language
def support_pressed(bot, update):
    if update.message.reply_to_message and \
       update.message.reply_to_message.forward_from:
        bot.send_message(chat_id = update.message.reply_to_message.forward_from.id,
                         text = update.message.text)
    else:
        update.message.forward(chat_id = environ['CHAT_ID'])
        update.message.reply_text(_('Thanks for the feedback! We will answer you as soon as possible.'))

    return start(bot, update)

@language
def help(bot, update):
    update.message.reply_text(_('Use /start to use this bot.'))

    return HELP_PRESSED

@language
def help_pressed(bot, update):
    return start(bot, update)

def error(bot, update, error):
    warning('Update "%s" caused error "%s"' % (update, error))

def exception(error):
    warning('Support Bot caused exception "%s"' % error)

basicConfig(format = '[%(asctime)s] [%(levelname)s]: %(name)s: %(message)s',
            level = INFO)

_ = None

db = StrictRedis(host = environ['REDIS_HOST'],
                 port = environ['REDIS_PORT'],
                 db = environ['REDIS_DB'])

START_PRESSED, SETTING_PRESSED, SELECT_LANGUAGE_PRESSED, \
SUPPORT_PRESSED, HELP_PRESSED = range(5)

conversation_handler = ConversationHandler(
    entry_points = [CommandHandler('start', start)],

    states = {
        START_PRESSED: [CommandHandler('settings', settings),
                        CommandHandler('support', support),
                        CommandHandler('help', help),
                        MessageHandler(Filters.text, start_pressed)],

        SETTING_PRESSED: [CommandHandler('select_language', select_language),
                          MessageHandler(Filters.text, settings_pressed)],

        SELECT_LANGUAGE_PRESSED: [CommandHandler('start', start),
                                  MessageHandler(Filters.text, select_language_pressed)],

        SUPPORT_PRESSED: [CommandHandler('start', start),
                          MessageHandler(Filters.text, support_pressed)],

        HELP_PRESSED: [CommandHandler('start', start),
                       MessageHandler(Filters.text, help_pressed)],
    },

    fallbacks = [CommandHandler('start', start)]
)

if __name__ == "__main__":
    updater = Updater(environ['BOT_TOKEN'])

    updater.dispatcher.add_handler(conversation_handler)
    updater.dispatcher.add_error_handler(error)

    updater.start_polling()

    updater.idle()
