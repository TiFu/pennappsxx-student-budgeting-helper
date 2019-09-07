import telegram

# authenticate bot
bot = telegram.Bot(token='978817218:AAFcuFVe9YH7PWrtpCbqanQZffXBjbUCezc')

# get messages i.e. photos
updates = bot.get_updates()

# get file_id
fid = updates[len(updates) - 1].message.document.file_id

# download photo to local folder
bot.get_file(fid).download()

#test api
import json
from receipt_recognition.receipt_recognition_api import ReceiptRecognitionApi
from receipt_recognition.post_processors import LineMergerPostprocessor, ItemPostprocessor, LanguageModelPostprocessor
from receipt_recognition.receipt_visualizer import ReceiptTextVisualizer
import pprint

if __name__ == "__main__":
    with open('./receipt_recognition/dictionary.json') as dictFile:
        knownWords = set(json.load(dictFile))
        with open('./config.json') as json_file:
            config = json.load(json_file)
            postProcessors = [LineMergerPostprocessor(), ItemPostprocessor(), LanguageModelPostprocessor(knownWords)]
            api = ReceiptRecognitionApi(config, postProcessors, ReceiptTextVisualizer())
            result = api.recognize("./file_2.png")

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)