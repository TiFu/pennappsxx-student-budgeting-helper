
import json
from bot import Bot
from database import Database

with open("../config.json") as f:
    config = json.load(f)  
    database = Database("./db.json")
    bot = Bot(config["telegram"]["token"], database)
    bot.run()