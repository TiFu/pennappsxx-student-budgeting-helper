from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
from .state import setUpStateMachine
from telegram.ext import MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
class Bot:

    def __init__(self, botToken, database):
        print("Using bot token " + str(botToken))
        self.updater = Updater(token=botToken, use_context=True)
        self.database = database
        self._registerCommands()
        self.userStateMachines = {}
        self.categories = [ "frozen", "produce", "dairy"]

    def _registerCommands(self):
        print("Registering command")
        start_handler = CommandHandler('start', lambda u, c: self._start(u, c))
        self.updater.dispatcher.add_handler(start_handler)

        echo_handler = MessageHandler(Filters.all, lambda u, c: self._onMessage(u, c))
        self.updater.dispatcher.add_handler(echo_handler)


    def _start(self, update, context):
        #context.bot.send_message(chat_id=update.message.chat_id, text="Hi! Welcome to our budgeting helper bot. We will first need to set up some basic data.")
        self.userStateMachines[update.message.chat_id] = setUpStateMachine(self.categories, self.database)
        self.userStateMachines[update.message.chat_id].begin(update, context)

    def _onMessage(self, update, context):
        print("Processing on message callback")
        if update.message.chat.id not in self.userStateMachines:
            self.userStateMachines[update.message.chat.id] = setUpStateMachine(self.categories, self.database)
            self.userStateMachines[update.message.chat.id].begin(update, context)

        self.userStateMachines[update.message.chat_id].process(update, context)


    def run(self):
        print("Polling")
        self.updater.start_polling()
