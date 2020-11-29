# coding=UTF-8
import logging
import configparser
import sys
import json
import os.path

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from profanity_filter import ProfanityFilter
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter

config = configparser.ConfigParser()
config.read('bot_config.ini')

pf = ProfanityFilter(languages=['ru', 'en'])

token = config['DEFAULT']['BotToken']
updater = Updater(token=token, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

class ChatMemberCensorRepository:
    repository_file = 'cencored_users'
    censored_users = set()

    def __init__(self):
        self.load_data()

    def need_censor(self, user_id, chat_id):
        return (user_id, chat_id) in self.censored_users

    def add_to_censor(self, user_id, chat_id):
        if not self.need_censor(user_id, chat_id):
            self.censored_users.add((user_id, chat_id))
            self.save_data()

    def remove_from_censor(self, user_id, chat_id):
        if self.need_censor(user_id, chat_id):
            self.censored_users.remove((user_id, chat_id))
            self.save_data()

    def save_data(self):
        with open(self.repository_file, 'w') as f:
            f.write(json.dumps(list(self.censored_users)))

    def load_data(self):
        if os.path.isfile(self.repository_file):
            with open(self.repository_file, 'r') as f:
                self.censored_users = set(json.loads(f.read()))

currency_exchange = CurrencyRates()

def usd_to_rub(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(round(currency_exchange.get_rates('USD')['RUB'], 2))

def eur_to_rub(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(round(currency_exchange.get_rates('EUR')['RUB'], 2))
    
btc_exchange = BtcConverter()
def btc_to_usd(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(round(btc_exchange.get_latest_price('USD'), 2))


chat_member_censor_repo = ChatMemberCensorRepository()

def start_censor_me(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    chat_member_censor_repo.add_to_censor(user_id, chat_id)
    update.message.reply_text('Теперь ты под моим надзором')

def stop_censor_me(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    chat_member_censor_repo.remove_from_censor(user_id, chat_id)
    update.message.reply_text('Ты больше не под моим надзором')
    
def censor(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if chat_member_censor_repo.need_censor(user_id, chat_id) and not pf.is_clean(update.message.text):
        update.message.reply_text('Аккуратнее с языком молодой человек!')

def main():
    """Run bot."""
    censor_handler = MessageHandler(Filters.text & (~Filters.command), censor)

    dispatcher.add_handler(CommandHandler("usd2rub", usd_to_rub))
    dispatcher.add_handler(CommandHandler("eur2rub", eur_to_rub))
    dispatcher.add_handler(CommandHandler("btc2usd", btc_to_usd))
    dispatcher.add_handler(CommandHandler("startcensorme", start_censor_me))
    dispatcher.add_handler(CommandHandler("stopcensorme", stop_censor_me))
    dispatcher.add_handler(censor_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()