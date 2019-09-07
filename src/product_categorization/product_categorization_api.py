from model import ProductCategorizer
import torch
import json
from Dataset import Dataset

class ProductCategorizationApi:
    
    def __init__(self, modelPath, vocabMappingPath, categoryPath):
        with open(vocabMappingPath) as vocab_mapping:
            self.vocacbMapping = json.load(vocab_mapping)
        with open(categoryPath) as category_file:
            self.categories = json.load(category_file)
        self.model = ProductCategorizer(len(self.vocacbMapping) + 1, 21)
        self.model.load_state_dict(torch.load(modelPath))

    def predictCategory(self, items):
        productNames = list(map(lambda x: x["name"], items))

        dataSet = self._mapStringToIndices(productNames)
        indices = [i for i, val in enumerate(dataSet) if val is None]
        dataSet = list(filter(lambda x: x is not None, dataSet))
        dataSet = Dataset(dataSet, None, 999999, batch_size_sents=999999)
        dataSet.create_order(random=False)
        batch = dataSet.next()[0]

        src = batch.get("source")
        src = src.transpose(0, 1)
        src_mask = batch.get("src_mask")
        src_lengths = batch.get("src_length")
        pred = self.model(src, src_mask, src_lengths)
        max_index = pred.max(dim = 1)[1]
        
        categories = self._mapMaxIndexToCategoryName(max_index)
        categories = self._fillWithUnknownCats(categories, indices)
        i = 0
        while i < len(items):
            items[i]["category"] = categories[i]
            i += 1
        return items

    def _fillWithUnknownCats(self, categories, indices):
        output = []
        i = 0
        categoryPointer = 0
        indexPointer = 0
        while i < len(categories) + len(indices):
            if i < len(indices) and i == indices[indexPointer]:
                output.append(None)
                indexPointer += 1
            else:
                output.append(categories[categoryPointer])
                categoryPointer += 1
            i += 1

        return output


    def _mapMaxIndexToCategoryName(self, maxIndex):
        categories = list(map(lambda x: self.categories[x], maxIndex))
        return categories
        

    def _mapStringToIndices(self, productNames):
        data = []

        for productName in productNames:
            mappedProd = []
            for word in productName.split():
                word = word.replace(",", "")
                word = word.replace("'", "")
                word = word.replace("\\", "")
                word = word.replace("\"", "")
                word = word.replace("®", "")
                word = word.replace("\xa0", "")
                word = word.lower()
                word = word.split("/")
                for subword in word:
                    if subword in self.vocacbMapping:
                        if subword == "org":
                            subword = "organica"
                        mappedProd.append(self.vocacbMapping[subword])
            if len(mappedProd) == 0:
                data.append(None)    
            else:
                data.append(torch.LongTensor(mappedProd))
        return data