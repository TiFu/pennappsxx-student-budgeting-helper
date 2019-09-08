import boto3
from PIL import Image, ImageDraw
import cv2
import io
import re
import json
import pprint
import Levenshtein
import numpy as np
import imutils

class ReceiptRecognitionApi:

    def __init__(self, config, postProcessors, receiptVisualizer):
        self.client = boto3.client('rekognition', aws_access_key_id=config["aws"]["key_id"], aws_secret_access_key=config["aws"]["secret_access_key"], region_name="us-east-2")
        self.receiptVisualizer = receiptVisualizer
        self.postProcessors = postProcessors

    def preprocessImage(self, inputImagePath):
        origImg = cv2.imread(inputImagePath)
        outputCopy = origImg.copy()
        origImg2 = origImg.copy()

        image = cv2.cvtColor(origImg, cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(image, (5, 5), 0)
        image = cv2.Canny(image, 75, 80)
        #kernel = np.ones((5,5),np.uint8)
        #image = cv2.dilate(image,kernel,iterations = 1)
        #kernel = np.ones((3,3),np.uint8)
        #image = cv2.erode(image,kernel,iterations = 1)
        img_resize = cv2.resize(image, (0,0), fx=.5, fy=.5) 
        image = cv2.GaussianBlur(image, (5, 5), 0)


        cnts = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)
        
        origImg = origImg.copy()
        cv2.drawContours(origImg, cnts, -1, (0, 255, 0), 2)

        # loop over the contours
        maxArea = 0
        sceneCnt = None
        for c in cnts:
            minX = 1000000
            maxX = 0
            minY = 1000000
            maxY = 0
            for point in c:
                x = point[0][0]
                y = point[0][1]
                if x > maxX:
                    maxX = x
                elif x < minX:
                    minX = x
                
                if y > maxY:
                    maxY = y
                elif y < minY:
                    minY = y


            area = (maxY - minY) * (maxX - minX)
            c_ = cv2.convexHull(c)
            contourArea = cv2.contourArea(c_)
            print("relative: " + str(area / contourArea))
            print("area: " + str(area))
            relative = area / contourArea
            if (relative - 1) < 0.1 and area > maxArea:
                sceneCnt = c_
                maxArea = area
            else:
                continue
                #break

            # if our approximated contour has four points, then we
            # can assume that we have found our screen
            #print(len(approx))
            origImg3 = origImg2.copy()
            cv2.rectangle(origImg3, (minX, minY), (maxX, maxY), (0, 255, 0), 1)
            #cv2.drawContours(origImg3, [], -1, (0, 255, 0), 2)
            #if len(approx) == 4:
            #    screenCnt = approx
            #    break
        
        if sceneCnt is None or maxArea < 100000:
            outputPath = inputImagePath.replace("jpeg", "processed.jpg")
            cv2.imwrite(outputPath, outputCopy)
            return outputPath
        else:
            areaRect = cv2.minAreaRect(sceneCnt)
            angle = areaRect[-1]

            if angle < -45:
            	angle = -(90 + angle)
            # otherwise, just take the inverse of the angle to make
            # it positive
            else:
                angle = -angle


            center, size = areaRect[0], areaRect[1]
            center, size = tuple(map(int, center)), tuple(map(int, size))
    
            outputCopy = cv2.getRectSubPix(outputCopy, (size[1], size[0]), center)
            (h, w) = outputCopy.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, -angle, 1.0)
            outputCopy = cv2.warpAffine(outputCopy, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        # show the contour (outline) of the piece of paper

        cv2.drawContours(origImg2, [sceneCnt], -1, (0, 255, 0), 2)
        outputPath = inputImagePath.replace("jpeg", "processed.jpg")
        cv2.imwrite(outputPath, outputCopy)
        return outputPath

    def _update(self, output1, output2):
        for key in output2:
            if key not in output1:
                output1[key] = output2[key]
            else:
                if type(output2[key]) == list:
                    output1[key].extend(output2[key])
                else:
                    output1[key] = output2[key]
        return output1

    def recognize(self, inputImagePath):
        inputImagePath = self.preprocessImage(inputImagePath)

        output = {}
        i = 0
        for postProcessor in self.postProcessors:
            postProcessor.reset()
        while True:
            image = Image.open(inputImagePath)
            stream = io.BytesIO()
            image.save(stream,format="png")
            image_binary = stream.getvalue()


            #with open('./cache.json') as json_file:
            #response = json.load(json_file)
            # get next image        
            response = self.client.detect_text(Image={'Bytes':image_binary})        

            # Postprocessing
            detections = response["TextDetections"]
            for postProcessor in self.postProcessors:
                detections = postProcessor.process(inputImagePath, detections, output)
                processorOutput = postProcessor.getOutput()
                if processorOutput is not None:
                    output = self._update(output, postProcessor.getOutput())
                    print("Output: " + str(postProcessor.getOutput()))
            self.receiptVisualizer.visualize(inputImagePath, detections)

            # Check if we want to continue
            max = 0
            for detection in response["TextDetections"]:
                row = detection["Geometry"]["BoundingBox"]["Top"] + detection["Geometry"]["BoundingBox"]["Height"]
                if row > max:
                    max = row

            width, height = image.size   # Get dimensions
            left = 0
            top = max * height
            right = width
            bottom = height

            print("Distance remaining: " + str(abs(bottom - top)))
            if abs(bottom - top) < 50:
                break
            image = image.crop((left, top, right, bottom))
            inputImagePath = inputImagePath.replace(".jpg", str(i) + ".jpg")
            image.save(inputImagePath, "JPEG")
            i += 1

        print("FINAL OUTPUT: ")
        print(output)
        return output