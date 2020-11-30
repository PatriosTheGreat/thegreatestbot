import configparser
import logging
import sys

from forex_python.bitcoin import BtcConverter
from forex_python.converter import CurrencyRates
from profanity_filter import ProfanityFilter
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

config = configparser.ConfigParser()
config.read('bot_config.ini')

pf = ProfanityFilter(languages=['ru', 'en_core_web_sm'])

token = config['DEFAULT']['BotToken']
updater = Updater(token=token, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def censor(update, context):
    if not pf.is_clean(update.message.text):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Аккуратнее с языком молодой человек!')

currency_exchange = CurrencyRates()

def usd_to_rub(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(round(currency_exchange.get_rates('USD')['RUB'], 2))

def eur_to_rub(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(round(currency_exchange.get_rates('EUR')['RUB'], 2))
    
btc_exchange = BtcConverter()
def btc_to_usd(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(round(btc_exchange.get_latest_price('USD'), 2))

def main():
    """Run bot."""
    censor_handler = MessageHandler(Filters.text & (~Filters.command), censor)

    dispatcher.add_handler(CommandHandler("usd2rub", usd_to_rub))
    dispatcher.add_handler(CommandHandler("eur2rub", eur_to_rub))
    dispatcher.add_handler(CommandHandler("btc2usd", btc_to_usd))
    dispatcher.add_handler(censor_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
