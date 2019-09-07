import telegram
'''
# authenticate bot
bot = telegram.Bot(token='978817218:AAFcuFVe9YH7PWrtpCbqanQZffXBjbUCezc')

# get messages i.e. photos
updates = bot.get_updates()

# get file_id
fid = updates[len(updates) - 1].message.document.file_id

# download photo to local folder
bot.get_file(fid).download()
'''

# continuous download receipts
import json
import requests
import time

TOKEN = '978817218:AAFcuFVe9YH7PWrtpCbqanQZffXBjbUCezc'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

bot = telegram.Bot(token=TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        fid = update["message"]["document"]["file_id"]
        chat = update["message"]["chat"]["id"]
        #url = URL + "getfile?file_id=" + fid
        #js = get_json_from_url(url)
        #file_path = js["result"]["file_path"].split("/")[-1]
        bot.get_file(fid).download("file_2.png")
        #return file_path


def get_last_chat_id_and_photo(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    photo = updates["result"][last_update]["message"]["document"]["file_name"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (photo, chat_id)


#test api
#import json
from receipt_recognition.receipt_recognition_api import ReceiptRecognitionApi
from receipt_recognition.post_processors import LineMergerPostprocessor, ItemPostprocessor, LanguageModelPostprocessor
from receipt_recognition.receipt_visualizer import ReceiptTextVisualizer
import pprint


def classify():
	with open('./receipt_recognition/dictionary.json') as dictFile:
		knownWords = set(json.load(dictFile))
		with open('./config.json') as json_file:
			config = json.load(json_file)
			postProcessors = [LineMergerPostprocessor(), ItemPostprocessor(), LanguageModelPostprocessor(knownWords)]
			api = ReceiptRecognitionApi(config, postProcessors, ReceiptTextVisualizer())
			result = api.recognize("./file_2.png")

			pp = pprint.PrettyPrinter(indent=4)
			pp.pprint(result)

def main():
    last_update_id = None
    # bot continuously listening for receipt upload from user
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
            classify()
        time.sleep(0.5)

#test api
#import json
#from receipt_recognition.receipt_recognition_api import ReceiptRecognitionApi
#from receipt_recognition.post_processors import LineMergerPostprocessor, ItemPostprocessor, LanguageModelPostprocessor
#from receipt_recognition.receipt_visualizer import ReceiptTextVisualizer
#import pprint

if __name__ == "__main__":
    '''
    with open('./receipt_recognition/dictionary.json') as dictFile:
        knownWords = set(json.load(dictFile))
        with open('./config.json') as json_file:
            config = json.load(json_file)
            postProcessors = [LineMergerPostprocessor(), ItemPostprocessor(), LanguageModelPostprocessor(knownWords)]
            api = ReceiptRecognitionApi(config, postProcessors, ReceiptTextVisualizer())
            result = api.recognize("./file_2.png")

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)
    '''
    main()