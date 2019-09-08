import json
import os 
from datetime import datetime

# USAGE
# a) update database by accessing db.database
# b) call persist
#
#
class Database:

    def __init__(self, databaseFilePath):
        self.databaseFilePath = databaseFilePath

        print("Loading db " + str(databaseFilePath))
        if os.path.exists(databaseFilePath):
            print("USING EXISTING DB")
            with open(databaseFilePath, 'r') as db:
                self.database = json.load(db)
                print("DB2: " + str(self.database))
        else:
            print("USING OTHER DB")
            self.database = {}
        print("SELF: " + str(self))


    def getBudgetCount(self, chatId):
        chat = self._getChatDB(chatId)
        return 0 if "budgets" not in chat else len(chat["budgets"])
    
    def getCurrentState(self, chatId):
        chat = self._getChatDB(chatId)
        print("Chat Id: " + str(chatId))
        print("Chat: " + str(chat))
        result = chat["currentState"] if "currentState" in chat and chat["currentState"] is not None else "StartState"
        print("Returning current state: " + result)
        return result

    def setCurrentState(self, chatId, state):
        chat = self._getChatDB(chatId)
        chat["currentState"] = state

    def isCategoryBudgetedFor(self, chatId, category):
        chat = self._getChatDB(chatId)
        return "budgets" in chat and category in chat["budgets"] and chat["budgets"][category] is not None

    def setLastAskedBudgetCategory(self, chatId, category):
        chat = self._getChatDB(chatId)
        chat["lastAskedBudgetCategory"] = category
        print("Setting last budget cat: " + str(self.database))

    def getLastAskedBudgetCategory(self, chatId):
        chat = self._getChatDB(chatId)
        print("Chat: "  + str(chat))
        if "lastAskedBudgetCategory" not in chat:
            chat["lastAskedBudgetCategory"] = None
        return chat["lastAskedBudgetCategory"]

    def getBudget(self, chatId):
        chat = self._getChatDB(chatId)
        if "budgets" not in chat:
            return None
        return chat["budgets"]


    def updateBudget(self, chatId, categoryName, value):
        chat = self._getChatDB(chatId)
        if "budgets" not in chat:
            chat["budgets"] = {}
        chat["budgets"][categoryName] = value
        print("Updated category budget" + str(self.database))

    def setItem(self, chatId, idx, dollarValue):
       chat = self._getChatDB(chatId)
       chat["currentReceiptItems"][idx]["dollar"] = dollarValue # if "currentReceiptItems" in chat else []


    def getLastAskedItem(self, chatId):
        chat = self._getChatDB(chatId)
        return chat["lastAskedItem"] if "lastAskedItem" in chat else None

    def setLastAskedItem(self, chatId, index):
       chat = self._getChatDB(chatId)
       chat["lastAskedItem"] = index

    def getCurrentitems(self, chatId):
       chat = self._getChatDB(chatId)
       return chat["currentReceiptItems"] if "currentReceiptItems" in chat else []

    def setCurrentitems(self, chatId, input):
       chat = self._getChatDB(chatId)
       chat["currentReceiptItems"] = input

    def clearCurrentReceipt(self, chatId):
        chat = self._getChatDB(chatId)
        if "currentReceiptItems" in chat:
            del chat["currentReceiptItems"]

    def getCurrentTransactionSum(self, chatId):
        chat = self._getChatDB(chatId)
        today = datetime.today()
        key = str(today.month) + str(today.year)
        if "transactionSum" not in chat:
            return None

        today = datetime.today()
        key = str(today.month) + str(today.year)
        if key not in chat["transactionSum"]:
            return None
        return chat["transactionSum"][key]

        
    def updateTransactionSum(self, chatId, items):
        chat = self._getChatDB(chatId)
        if "transactionSum" not in chat:
            chat["transactionSum"] = {}

        today = datetime.today()
        key = str(today.month) + str(today.year)
        if key not in chat["transactionSum"]:
            chat["transactionSum"][key] = {}
        
        for item in items:
            cat = item["category"]
            if cat not in chat["transactionSum"][key]:
                chat["transactionSum"][key][cat] = 0
            chat["transactionSum"][key][cat] += item["dollar"]

    def _getChatDB(self, chatId):
        if str(chatId) not in self.database:
            self.database[str(chatId)] = {}
        print("SELF: " + str(self))
        print("DB: " + str(self.database))
        return self.database[str(chatId)]

    def persist(self):
        with open(self.databaseFilePath, 'w+') as db:
            json.dump(self.database, db, indent=4)
            print("AFTER DUMP: " + str(self.database))