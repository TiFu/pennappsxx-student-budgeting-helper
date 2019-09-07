from . import Postprocessor
from PIL import Image

class LineMergerPostprocessor(Postprocessor):

    def __init__(self):
        self.lineThreshold = 5

    def process(self, image, text, prevOutput):
        image=Image.open(image)
        imgWidth, imgHeight = image.size
        lines = []
        # TODO: sort by top distance

        prevEntry = None
        prevMiddle = None
        currentLine = None
        for entry in text:
            if entry["Type"] != "LINE":
                continue
            box = entry["Geometry"]['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            middleT = top + 0.5 * height
            print("Text: " + str(entry["DetectedText"]))
            print("Distance: " + str((abs(middleT - prevMiddle) if prevMiddle is not None else None)))
            if prevMiddle is None or abs(middleT - prevMiddle) < self.lineThreshold:
                currentLine = self._merge(currentLine, entry)
            else:
                if currentLine is not None:
                    lines.append(currentLine)
                currentLine = entry

            prevMiddle = middleT
        if currentLine is not None:
            lines.append(currentLine)
        return lines

    def _merge(self, entry1, entry2):
        if entry1 is None:
            return entry2
        else:
            print("Entry1: " + str(entry1["DetectedText"]) + " and " + str(entry2["DetectedText"]))
            entry1["DetectedText"] += " " + str(entry2["DetectedText"])
            right1 = entry1["Geometry"]["BoundingBox"]["Left"] +  entry1["Geometry"]["BoundingBox"]["Width"]
            right2 = entry2["Geometry"]["BoundingBox"]["Left"] +  entry2["Geometry"]["BoundingBox"]["Width"]

            bottom1 = entry1["Geometry"]["BoundingBox"]["Top"] +  entry1["Geometry"]["BoundingBox"]["Height"]
            bottom2 = entry2["Geometry"]["BoundingBox"]["Top"] +  entry2["Geometry"]["BoundingBox"]["Height"]

            for goal in ["Left", "Top"]:
                entry1["Geometry"]["BoundingBox"][goal] = min(entry1["Geometry"]["BoundingBox"][goal], entry2["Geometry"]["BoundingBox"][goal])
            
            entry1["Geometry"]["BoundingBox"]["Width"] = max(right1, right2) - entry1["Geometry"]["BoundingBox"]["Left"]  
            entry1["Geometry"]["BoundingBox"]["Height"] = max(bottom1, bottom2) - entry1["Geometry"]["BoundingBox"]["Top"]
            return entry1