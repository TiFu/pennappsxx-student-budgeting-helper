from product_categorization.product_categorization_api import ProductCategorizationApi
import re 

def setUpStateMachine(productCategories, database):
    idleState = IdleState()
    createBudgetState = CreateBudgetState(idleState, database, productCategories)
    initialState = StartState(createBudgetState)
    checkBudgetState = BudgetCheckState(idleState, database)
    textTransactionState = TextTransactionState(checkBudgetState, database)

    idleState.textTransactionState = idleState

    nameToStateMap = {
    }
    nameToStateMap[type(initialState).__name__] = initialState
    nameToStateMap[type(createBudgetState).__name__] = createBudgetState
    nameToStateMap[type(idleState).__name__] = idleState
    nameToStateMap[type(checkBudgetState).__name__] = checkBudgetState
    nameToStateMap[type(textTransactionState).__name__] = textTransactionState

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
            self.currentState.leave(message, context)
            nextState.enter(message, context)
            self.currentState = nextState
            self.database.setCurrentState(message.message.chat.id, type(self.currentState).__name__)
            self.database.persist()


class State:

    def enter(self, message, context):
        return self

    def leave(self, message, context):
        pass

    def transition(self, message, context):
        return self

class IdleState(State):
    def __init__(self, textTransactionState):
        self.textTransactionState = textTransactionState
        
    def enter(self, message, context):
        return self

    def leave(self, message, context):
        pass

    def transition(self, message, context):
        if message.message.text:
            return self.textTransactionState

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
        self.leave(None, None)
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
            if not selfmessage.message.text:
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
        context.bot.send_message(chat_id=update.message.chat_id, text="Thank your for setting up a budget. You can now upload pictures of receipts and/or register expenses using a simple text message. I will keep track of your expenses and notify you if you exhaust your budget.")

class TextTransactionState(State):
    def __init__(self, budgetCheckState, database):
        self.budgetCheckState = budgetCheckState
        self.database = database

    def transition(self, message, context):
        chatId = message.message.chat.id
        a = message.message.text.split("bought")
        b = a[1].split("for")
        message.message.text.replace("a", "", 1)
        message.message.text.replace("n", "", 1)        
        item = b[0]
        price = float(b[1].replace(".", "").replace("$", ""))       
        api = ProductCategorizationApi("./model_e4000.pt", "./vocab_mapping.json", "./categories.json")        
        input = [{"name":item, "dollar": price}]
        results = api.predictCategory(input)        
        self.database.setCurrentitems(self, chatId, results)        
        self.database.persist()
        context.bot.send_message(chat_id=update.message.chat_id, text="Your item has succesfully been added")
        return self.budgetCheckState


class BudgetCheckState(State):

    def __init__(self, idleState, database):
        self.idleState = idleState
        self.database = database

    def enter(self, update, context):
        chatId = update.message.chat.id
        currentReceipt = self.database.getCurrentReceipt(chatId)
        self.database.updateTransactionSum(chatId, currentReceipt)
        self.database.clearCurrentReceipt(chatId)
        self.database.persist()

        # Check for critical budgets

        transactionSum = self.database.getCurrentTransactionSum(chatId)
        budgets = self.database.getBudgets(chatId)

        if transactionSum is not None and budgets is not None:
            resultStr = ""
            for key in budgets:
                if not key in transactionSum:
                    continue

                fractionUsed = transactionSum[key] / budgets[key]
                diff = transactionSum[key] - budgets[key]
                if fractionUsed > 1.0:
                    resultStr += "You have exceeded your monthly budget for " + str(key) + ". You spent **$" + str(transactionSum[key]) + "**, $" + str(diff) + " more than your budget of $" + str(budgets[key])
                    resultStr += "\n"
                if fractionUsed > 0.8:
                    resultStr += "You have consumed " + int(fractionUsed) + "\% of your monthly budget for " + str(key) + ". **, $" + str(diff) + "** of $" + str(budgets[key]) + " remaining."
                    resultStr += "\n"
        if resultStr != "":
            context.bot.send_message(chat_id=update.message.chat_id, text=resultStr)
            
        return self.idleState

            


    def transition(self, update, context):
        pass

    def leave(self, update, context):
        pass

