import json
from receipt_recognition_api import ReceiptRecognitionApi
from post_processors import LineMergerPostprocessor, ItemPostprocessor, LanguageModelPostprocessor
from receipt_visualizer import ReceiptTextVisualizer
import pprint

if __name__ == "__main__":
    with open('./dictionary.json') as dictFile:
        knownWords = set(json.load(dictFile))
        with open('../config.json') as json_file:
            config = json.load(json_file)
            postProcessors = [LineMergerPostprocessor(), ItemPostprocessor(), LanguageModelPostprocessor(knownWords)]
            api = ReceiptRecognitionApi(config, postProcessors, ReceiptTextVisualizer())
            result = api.recognize("/home/mohammad/Downloads/2.png")

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)
