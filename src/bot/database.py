import json
import os 

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

    def updateBudget(self, chatId, categoryName, value):
        chat = self._getChatDB(chatId)
        if "budgets" not in chat:
            chat["budgets"] = {}
        chat["budgets"][categoryName] = value
        print("Updated category budget" + str(self.database))


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