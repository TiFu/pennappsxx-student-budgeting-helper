from . import Postprocessor
import Levenshtein

class LanguageModelPostprocessor(Postprocessor):

    def __init__(self, knownWords):
        self.knownWords = knownWords
        for i in range(0, 100):
            self.knownWords.add(str(i))
        
    def process(self, image, text, prevOutput):
        if "items" not in prevOutput:
            return

        for item in prevOutput["items"]:
            item["name"] = self._spellcheckSentence(item["name"])
            item["description"] = self._spellcheckSentence(item["description"])
        return text

    def _spellcheckSentence(self, text):
        print("Original: " + str(text))
        result = ""
        for word in text.split(" "):
            correctedWord = self._correctWord(word)
            print("Corrected word: " + str(correctedWord))
            result += correctedWord + " "
        print("Result: " + str(result))
        return result.strip()

    def _correctWord(self, word):
        print("Checking word " + str(word))
        if word in self.knownWords:
            return word
        else:
            minWords = set()
            minDist = 1500
            for correction in self.knownWords:
                if abs(len(correction) - len(word)) > 2:
                    continue
                dist = Levenshtein.distance(word.lower(), correction.lower())
                if dist < minDist:
                    minDist = dist
                    minWords = set()
                    minWords.add(correction) 
                elif dist == minDist:
                    minWords.add(word)
            if minDist <= 2 and len(minWords) == 1:
                return next(iter(minWords))
            elif len(minWords) == 0:
                return word
            else:
                if minDist <= 2:
                    print("Min Words are: " + str(minWords))
                    # TODO should use frequency list to determine most likely word instead of returning first word lol
                    return next(iter(minWords))
                else:
                    return word