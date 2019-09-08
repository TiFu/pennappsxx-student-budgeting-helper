import re 

def setUpStateMachine(productCategories, database):
    idleState = State()
    createBudgetState = CreateBudgetState(idleState, database, productCategories)
    initialState = StartState(createBudgetState)

    nameToStateMap = {
    }
    nameToStateMap[type(initialState).__name__] = initialState
    nameToStateMap[type(createBudgetState).__name__] = createBudgetState
    nameToStateMap[type(idleState).__name__] = idleState
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
        return self

    def transition(self, message, context):
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