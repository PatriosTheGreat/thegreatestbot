import logging
import configparser

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from profanity_filter import ProfanityFilter

config = configparser.ConfigParser()
config.read('bot_config.ini')

pf = ProfanityFilter(languages=['ru', 'en'])

token = config['DEFAULT']['BotToken']
updater = Updater(token=token, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def censor(update, context):
    if not pf.is_clean(update.message.text):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Аккуратнее с языком молодой человек!')

censor_handler = MessageHandler(Filters.text & (~Filters.command), censor)
dispatcher.add_handler(censor_handler)

updater.start_polling()