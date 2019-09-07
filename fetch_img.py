import telegram

# authenticate bot
bot = telegram.Bot(token='978817218:AAFcuFVe9YH7PWrtpCbqanQZffXBjbUCezc')

# get messages i.e. photos
updates = bot.get_updates()

# get file_id
for update in updates:
	print(update.message)
fid = updates[len(updates) - 1].message.document.file_id

# download photo to local folder
bot.get_file(fid).download()