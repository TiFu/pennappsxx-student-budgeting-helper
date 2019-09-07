import json
import requests
import telegram

TOKEN = "852178738:AAF2LtUam9o_OfWwFb7lxY3tZrEQjeI8g3o"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

names = []
dollars = []

#-----Fetch_img--


# authenticate bot
bot = telegram.Bot(token='978817218:AAFcuFVe9YH7PWrtpCbqanQZffXBjbUCezc')

# get messages i.e. photos
updates = bot.get_updates()

# get file_id
#fid = updates[len(updates) - 1].message.document.file_id

# download photo to local folder
#bot.get_file(fid).download()

#test api
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
            # to_python = json.loads(result)
            #to_python[]
    #item= postProcessors

    #for item in items
    #print(postProcessors[1].items[1])#dictionaries
    item_l = postProcessors[1].items
    #print(item_l[1].get("name"))

    cost = " "
    title = " "
    count = 0
    for item in item_l:
        print(item)
        title = item_l[count].get("name")
        names.append(title)

        cost = item_l[count].get("dollar")
        dollars.append(cost)
        count += 1
    print(names)
    print(dollars)

#-------


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    introd = "Here are the items you bought: "
    cont = 0
    for nam in names:
        introd = introd + ", " + names[cont]
        print(introd)
        cont += 1
        if cont == 3:
            break

    text = introd
    print(text)
    #text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


text, chat = get_last_chat_id_and_text(get_updates())
send_message(text, chat)


#-------

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    introd = " "
    cont = 3
    for nam in names:
        introd = introd + ", " + names[cont]
        print(introd)
        cont += 1
        if (cont == 6):
            break

    text = introd
    print(text)
    #text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


text, chat = get_last_chat_id_and_text(get_updates())
send_message(text, chat)
