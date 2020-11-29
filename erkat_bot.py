from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, MessageHandler, Filters
from profanity_filter import ProfanityFilter
import pymorphy2

pf = ProfanityFilter(languages=['ru', 'en'])

updater = Updater(token='', use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def censor(update, context):
    if not pf.is_clean(update.message.text):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Аккуратнее с языком молодой человек!')

censor_handler = MessageHandler(Filters.text & (~Filters.command), censor)
dispatcher.add_handler(censor_handler)

updater.start_polling()