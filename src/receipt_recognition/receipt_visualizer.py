from PIL import Image, ImageDraw
class ReceiptTextVisualizer:

    def __init__(self):
        pass

    def _scaleEntry(self, point, imageSize):
        return (int(point[0] * imageSize[0]), int(point[1] * imageSize[1]))
    
    def visualize(self, image, text):
        image=Image.open(image)
        draw = ImageDraw.Draw(image)  
        imgWidth, imgHeight = image.size
        print("Image Size:" + str(imgWidth) + ", " + str(imgHeight))
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
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top)

            )
            draw.line(points, fill='#00d400', width=1)
            #leftTop = (entry["Geometry"]["BoundingBox"]["Left"], entry["Geometry"]["BoundingBox"]["Top"])
            #rightBottom = (entry["Geometry"]["BoundingBox"]["Left"] + entry["Geometry"]["BoundingBox"]["Width"], entry["Geometry"]["BoundingBox"]["Height"] + entry["Geometry"]["BoundingBox"]["Top"])
            #color = (255, 0 ,0)
            #leftTop = self._scaleEntry(leftTop, img.shape)
            #rightBottom = self._scaleEntry(rightBottom, img.shape)
            #print(leftTop)
            #print(rightBottom)
            #cv2.rectangle(img, (int(left), int(top)), (int(left + width), int(top + height)), color, 2)
            #break
        image.show()
        #cv2.imshow("Receipt Text", img)
        #cv2.waitKey(0)