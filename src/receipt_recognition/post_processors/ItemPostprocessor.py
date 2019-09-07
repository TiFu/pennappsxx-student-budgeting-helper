from . import Postprocessor
import re 
from PIL import Image

class ItemPostprocessor(Postprocessor):

    def __init__(self):
        self.dollarPattern = re.compile("[0-9]+\.[0-9][0-9]")
        self.lineThreshold = 5
        self.items = None

    def getOutput(self):
        return { "items": self.items }

    def process(self, image, text, prevOutput):
        potentialItems = self._findPotentialItems(image, text)
        print("")
        print("Potential Items: " + str(potentialItems))
        print("")
        # Transform potential items to items
        self.items = []
        i = 0
        while i < len(potentialItems):
            item = potentialItems[i]
            if not item["isItem"]:
                continue
            
            price = self._getPriceFromItemLine(item["DetectedText"])
            descriptionLine = ""
            while i+1 < len(potentialItems) and not potentialItems[i + 1]["isItem"]:
                descriptionLine += potentialItems[i + 1]["DetectedText"] + "\n"
                i += 1
            name = self._rreplace(item["DetectedText"], str(price), "", 1)
            name = self._rreplace(name, "$", "", 1)

            finalItem = self._getItem(name, price, descriptionLine)
            self.items.append(finalItem)
            i += 1
        return text

    def _rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def _getPriceFromItemLine(self, text):
        match = self.dollarPattern.search(text)
        print("Match: " + str(match))
        if match:
            matches = self.dollarPattern.findall(text)
            dollarAmount = float(matches[len(matches) - 1])
            return dollarAmount
        else:
            return None
            
    def _getItem(self, text, dollar, descriptionLine):
        return {
            "name": text.strip(),
            "dollar": dollar,
            "description": descriptionLine.strip()
        }

    def _findPotentialItems(self, image, text):
        image=Image.open(image)
        imgWidth, imgHeight = image.size

        # TODO determine width based on having d.dd in it AND similar width
        sizeMap = {}
        maxWidth = None
        for entry in text:
            if not self.dollarPattern.search(entry["DetectedText"]):
                continue
            w = str(int(entry["Geometry"]["BoundingBox"]["Width"] * imgWidth))
            sizeMap[w] = 1 if w not in sizeMap else (sizeMap[w] + 1)
            if maxWidth is None or sizeMap[w] > sizeMap[maxWidth]:
                maxWidth = w
        print("Max width is : " + str(maxWidth))
        maxWidth = float(maxWidth)

        # Also includes lines in between i.e. count numbers
        potentialItems = []

        countEntries = []
        didItemsStart = False
        didItemsEnd = False
        lastItemCounter = 0
        for entry in text:
            w = entry["Geometry"]["BoundingBox"]["Width"] * imgWidth
            if abs(maxWidth - w) < self.lineThreshold:
                print(entry["DetectedText"] + "is item!")
                didItemsStart = True
                entry["isItem"] = True

                potentialItems.extend(countEntries)
                countEntries = []
                potentialItems.append(entry)
                lastItemCounter = 0
            else:
                print(entry["DetectedText"] + " is not an item!")
                entry["isItem"] = False
                print("Did Start: " + str(didItemsStart))
                print("Did End:"  + str(didItemsEnd))
                if didItemsStart and not didItemsEnd:
                    print("adding entry to count entries")
                    countEntries.append(entry)

            if lastItemCounter > 1:
                print("Items ended")
                didItemsEnd = True
            if didItemsStart:
                lastItemCounter += 1

        if not didItemsEnd:
            potentialItems.extend(countEntries)

        print(potentialItems)
        return potentialItems