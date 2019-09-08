from product_categorization.product_categorization_api import ProductCategorizationApi
from receipt_recognition.receipt_recognition_api import ReceiptRecognitionApi
from receipt_recognition.post_processors import LineMergerPostprocessor, ItemPostprocessor, LanguageModelPostprocessor
from receipt_recognition.receipt_visualizer import ReceiptTextVisualizer
import re 
import json

def setUpStateMachine(config, productCategories, database):
    idleState = IdleState(None, None)
    createBudgetState = CreateBudgetState(idleState, database, productCategories)
    initialState = StartState(createBudgetState)
    checkBudgetState = BudgetCheckState(idleState, database)

    api = ProductCategorizationApi("./product_categorization/model_e4000.pt", "./product_categorization/vocab_mapping.json", "./product_categorization/categories.json")        
    textTransactionState = TextTransactionState(checkBudgetState, idleState, database, api)
    correctReceiptState = State()   
    correctReceiptState = CorrectReceiptState(database, checkBudgetState)
    recogReceiptState = RecogReceiptState(config, correctReceiptState, checkBudgetState, database, api)
    
    idleState.textTransactionState = textTransactionState
    idleState.receiptTransactionState = recogReceiptState

    nameToStateMap = {
    }
    nameToStateMap[type(initialState).__name__] = initialState
    nameToStateMap[type(createBudgetState).__name__] = createBudgetState
    nameToStateMap[type(idleState).__name__] = idleState
    nameToStateMap[type(checkBudgetState).__name__] = checkBudgetState
    nameToStateMap[type(textTransactionState).__name__] = textTransactionState
    nameToStateMap[type(recogReceiptState).__name__] = recogReceiptState
    nameToStateMap[type(correctReceiptState).__name__] = correctReceiptState

    print("name to state map" + str(nameToStateMap))
    return StateMachine(nameToStateMap, database)

class StateMachine:

    def __init__(self, nameToStateMap, database):
        self.currentState = None
        self.database = database
        self.nameToStateMap = nameToStateMap
        
    def begin(self, message, context):
        self.currentState = self.nameToStateMap[self.database.getCurrentState(message.message.chat.id)]

        if self.currentState == self.nameToStateMap["StartState"]:
            newState = self.currentState.enter(message, context)
            self.changeState(newState, message, context)

    def process(self, message, context):
        nextState = self.currentState.transition(message, context)
        self.changeState(nextState, message, context)

    def changeState(self, nextState, message, context):
        if nextState != self.currentState:
            print("Leaving " + str(type(self.currentState).__name__))
            self.currentState.leave(message, context)
            print("Entering " + str(type(nextState).__name__))
            result = nextState.enter(message, context)
            self.currentState = nextState
            self.database.setCurrentState(message.message.chat.id, type(self.currentState).__name__)
            self.database.persist()
            # Change state again if wanted
            self.changeState(result, message, context)

class State:

    def enter(self, message, context):
        return self

    def leave(self, message, context):
        pass

    def transition(self, message, context):
        return self


class CorrectReceiptState(State):
    def __init__(self, database, checkBudgetState):
        self.database = database
        self.checkBudgetState = checkBudgetState

    def enter(self, message, context):
        return self._check(message, context)


    def transition(self, message, context):
        # Read price for item
        chatId = message.message.chat.id
        itemIdx = self.database.getLastAskedItem(chatId)
        self.database.setItem(chatId, itemIdx, float(message.message.text))
        return self._check(message, context)

    def _check(self, message, context):
        chatId = message.message.chat.id
        items = self.database.getCurrentitems(chatId)
        for idx, item in enumerate(items):
            if item["dollar"] is None:
                self.database.setLastAskedItem(chatId, idx) 
                self.database.persist()
                context.bot.send_message(chat_id=message.message.chat_id, text="Seems like we had problems recognizing the price for " + str(item["name"]) + ". How much did it cost?")
                return self

        return self.checkBudgetState


class RecogReceiptState(State):

    def __init__(self, config, correctReceiptState, budgetCheckState, database, categorizer):
        self.correctReceiptState = correctReceiptState
        self.budgetCheckState = budgetCheckState
        self.database = database
        self.config = config
        self.categorizer = categorizer
        with open('./receipt_recognition/dictionary.json') as dictFile:
            self.knownWords = set(json.load(dictFile))

        postProcessors = [LineMergerPostprocessor(), ItemPostprocessor(), LanguageModelPostprocessor(self.knownWords)]
        self.api = ReceiptRecognitionApi(self.config, postProcessors, ReceiptTextVisualizer())

        
    def enter(self, message, context):
        fid = message.message.document.file_id
        context.bot.get_file(fid).download("file_2.png")

        result = self.api.recognize("./file_2.png")
        result = self.categorizer.predictCategory(result['items'])

        # hohho fake
        result[3]["dollar"] = None

        print("Result of recogniye api: " + str(result))
        items = result
        self.database.setCurrentitems(message.message.chat.id, items)
        self.database.persist()

        for item in items:
            cost = item["dollar"]
            if cost is None:
                return self.correctReceiptState

        return self.budgetCheckState

    def transition(self, message, context):
        return self.enter(message, context)

class IdleState(State):
    def __init__(self, textTransactionState, receiptTransactionState):
        self.textTransactionState = textTransactionState
        self.receiptTransactionState = receiptTransactionState
        
    def enter(self, message, context):
        return self

    def leave(self, message, context):
        pass

    def transition(self, message, context):
        if message.message.text:
            print("Text was set - going to textTransaction State")
            return self.textTransactionState
        if message.message.document:
            return self.receiptTransactionState
        return self

class StartState(State):

    def __init__(self, budgetingState):
        self.budgetingState = budgetingState
    
    def enter(self, message, context):
        context.bot.send_message(chat_id=message.message.chat_id, text="Hi! Welcome to your personal budgeting helper.")
        return self.budgetingState

    def transition(self, _, context):
        pass

class CreateBudgetState(State):

    def __init__(self, idleState, database, categories):
        self.idleState = idleState
        self.database = database
        self.categories = categories
        self.dollarPattern = re.compile("[1-9][0-9]*(\.[0-9][0-9])?")

    def enter(self, message, context):
        context.bot.send_message(chat_id=message.message.chat_id, text="Let's first create the budget you want to stick to. For that I will be asking you how much you want to spend in each category")
        self._askNextCategory(message, context)
        return self
    
    # message.message.chat.id
    def transition(self, message, context):
        chatId = message.message.chat.id
        lastAskedCat = self.database.getLastAskedBudgetCategory(chatId)

        if self.database.getBudgetCount(chatId) == len(self.categories):
            return self.idleState
        else:
            if not message.message.text:
                context.bot.send_message(chat_id=message.message.chat_id, text="Sorry that didn't work. How much do you want to budget for " + lastAskedCat  + "?")
                return self

            # Process message
            match = self.dollarPattern.search(message.message.text)
        
            if match:
                match = match.group()
                self.database.updateBudget(chatId, lastAskedCat, float(match))
                self.database.setLastAskedBudgetCategory(chatId, None)
                self.database.persist()
                if not self._askNextCategory(message, context):
                    return self.idleState
            else:
                context.bot.send_message(chat_id=message.message.chat_id, text="Sorry that didn't work. How much do you want to budget for " + lastAskedCat  + "?")

            return self

    def _askNextCategory(self, update, context):
        chatId = update.message.chat.id
        possibleCats = list(filter(lambda x: not self.database.isCategoryBudgetedFor(chatId, x), self.categories))
        if len(possibleCats) == 0:
            return False
        print("POSSIBLE CATS: "+ str(possibleCats))
        self.database.setLastAskedBudgetCategory(chatId, possibleCats[0])
        self.database.persist()

        context.bot.send_message(chat_id=update.message.chat_id, text="How much do you want to spend monthly on " + str(possibleCats[0]) + "?")
        return True

    def leave(self, message, context):
        context.bot.send_message(chat_id=message.message.chat_id, text="Thank your for setting up a budget. You can now upload pictures of receipts and/or register expenses using a simple text message. I will keep track of your expenses and notify you if you exhaust your budget.")

class TextTransactionState(State):
    def __init__(self, budgetCheckState, idleState, database, api):
        self.budgetCheckState = budgetCheckState
        self.idleState = idleState
        self.database = database
        self.api = api
    def enter(self, message, context):
        if not re.match("I bought.*".lower(), message.message.text.lower()):
            print("Message does not match")
            return self.idleState
        chatId = message.message.chat.id
        a = message.message.text.split("bought")
        b = a[1].split("for")
        message.message.text.replace("a", "", 1)
        message.message.text.replace("n", "", 1)        
        item = b[0]
        price = float(b[1].replace(".", "").replace("$", ""))       
        input = [{"name":item, "dollar": price}]
        results = self.api.predictCategory(input)        
        self.database.setCurrentitems(chatId, results)        
        self.database.persist()
        context.bot.send_message(chat_id=message.message.chat_id, text="Your item has succesfully been added")
        return self.budgetCheckState

    def transition(self, message, context):
        return self.enter(message, context)

class BudgetCheckState(State):

    def __init__(self, idleState, database):
        self.idleState = idleState
        self.database = database

    def enter(self, update, context):
        chatId = update.message.chat.id
        currentReceipt = self.database.getCurrentitems(chatId)
        self.database.updateTransactionSum(chatId, currentReceipt)
        self.database.clearCurrentReceipt(chatId)
        self.database.persist()

        # Check for critical budgets

        transactionSum = self.database.getCurrentTransactionSum(chatId)
        budgets = self.database.getBudget(chatId)

        if transactionSum is not None and budgets is not None:
            resultStr = ""
            for key in budgets:
                if not key in transactionSum:
                    continue

                fractionUsed = transactionSum[key] / budgets[key]
                diff = transactionSum[key] - budgets[key]
                if fractionUsed > 1.0:
                    resultStr += "You have exceeded your monthly budget for " + str(key) + ". You spent $" + str(transactionSum[key]) + ", $" + str(diff) + " more than your budget of $" + str(budgets[key])
                    resultStr += "\n"
                elif fractionUsed > 0.8:
                    resultStr += "You have consumed " + str(int(fractionUsed * 100)) + "% of your monthly budget for " + str(key) + ". , $" + str(diff) + " of $" + str(budgets[key]) + " remaining."
                    resultStr += "\n"
        if resultStr != "":
            context.bot.send_message(chat_id=update.message.chat_id, text=resultStr)
            
        return self.idleState

    def transition(self, update, context):
        return self.enter(update, context)