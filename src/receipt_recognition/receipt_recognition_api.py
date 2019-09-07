import boto3
from PIL import Image, ImageDraw
import io
import re
import json
import pprint
import cv2
import Levenshtein

class ReceiptRecognitionApi:

    def __init__(self, config, postProcessors, receiptVisualizer):
        self.client = boto3.client('rekognition', aws_access_key_id=config["aws"]["key_id"], aws_secret_access_key=config["aws"]["secret_access_key"], region_name="us-east-2")
        self.receiptVisualizer = receiptVisualizer
        self.postProcessors = postProcessors

    def recognize(self, inputImagePath):
        image = Image.open(inputImagePath)

        stream = io.BytesIO()
        image.save(stream,format="png")
        image_binary = stream.getvalue()


        with open('./cache.json') as json_file:
            #response = json.load(json_file)
            response = self.client.detect_text(Image={'Bytes':image_binary})        
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(response)

            # Postprocessing
            detections = response["TextDetections"]
            output = {}
            for postProcessor in self.postProcessors:
                detections = postProcessor.process(inputImagePath, detections, output)
                processorOutput = postProcessor.getOutput()
                if processorOutput is not None:
                    output.update(postProcessor.getOutput())
                    print("Output: " + str(postProcessor.getOutput()))
            self.receiptVisualizer.visualize(inputImagePath, detections)
            print("FINAL OUTPUT: ")
            print(output)
        return output