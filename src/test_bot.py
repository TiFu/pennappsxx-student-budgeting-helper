
import json
from bot.bot import Bot
from bot.database import Database

with open("./config.json") as f:
    config = json.load(f)  
    database = Database("./db.json")
    bot = Bot(config, config["telegram"]["token"], database)
    bot.run()