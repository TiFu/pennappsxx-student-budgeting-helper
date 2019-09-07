import boto3
from PIL import Image, ImageDraw
import io
import json
import pprint
import cv2
import math

class ReceiptRecognitionApi:

    def __init__(self, config, receiptVisualizer):
        self.client = boto3.client('rekognition', aws_access_key_id=config["aws"]["key_id"], aws_secret_access_key=config["aws"]["secret_access_key"], region_name="us-east-2")
        self.receiptVisualizer = receiptVisualizer

    def recognize(self, inputImagePath):
        image = Image.open(inputImagePath)

        stream = io.BytesIO()
        image.save(stream,format="png")
        image_binary = stream.getvalue()


        with open('./cache.json') as json_file:
            response = json.load(json_file)
        #response = self.client.detect_text(Image={'Bytes':image_binary})        
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(response)
            self.receiptVisualizer.visualize(inputImagePath, response["TextDetections"])

class ReceiptTextVisualizer:

    def __init__(self):
        pass

    def _scaleEntry(self, point, imageSize):
        return (int(point[0] * imageSize[0]), int(point[1] * imageSize[1]))
    
    def visualize(self, image, text):
        image=cv2.imread(image)
        imgWidth, imgHeight, _ = image.shape
        
        for entry in text:
            if entry["Type"] != "LINE":
                continue
            box = entry["Geometry"]['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']
                    

            print("Entry: " + str(entry["DetectedText"]))
            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Face Width: ' + "{0:.0f}".format(width))
            print('Face Height: ' + "{0:.0f}".format(height))

            points = (
                (int(left),int(top)),
                (left + width, top),
                (math.ceil(left + width), math.ceil(top + height)),
                (left , top + height),
                (left, top)

            )
            middle = (left + 0.5 * width,top + 0.5 * height)
            color = (255, 0 ,0)
            cv2.rectangle(image, points[0], points[2], color, 1)
            #leftTop = (entry["Geometry"]["BoundingBox"]["Left"], entry["Geometry"]["BoundingBox"]["Top"])
            #rightBottom = (entry["Geometry"]["BoundingBox"]["Left"] + entry["Geometry"]["BoundingBox"]["Width"], entry["Geometry"]["BoundingBox"]["Height"] + entry["Geometry"]["BoundingBox"]["Top"])
            #leftTop = self._scaleEntry(leftTop, img.shape)
            #rightBottom = self._scaleEntry(rightBottom, img.shape)
            #print(leftTop)
            #print(rightBottom)
            #cv2.rectangle(img, (int(left), int(top)), (int(left + width), int(top + height)), color, 2)
            #break
        
        cv2.imshow("Receipt Text", image)
        cv2.waitKey(0)


if __name__ == "__main__":
    with open('../config.json') as json_file:
        config = json.load(json_file)
        api = ReceiptRecognitionApi(config, ReceiptTextVisualizer())
        api.recognize("/home/mohammad/Downloads/1.png.png")