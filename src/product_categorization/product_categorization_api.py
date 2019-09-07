from model import ProductCategorizer
import torch
import json

class ProductCategorizationApi:
    
    def __init__(self, modelPath, vocabMappingPath, categoryPath):
        with open(vocabMappingPath) as vocab_mapping:
            self.vocacbMapping = json.load(vocab_mapping)
        with open(categoryPath) as category_file:
            self.categories = json.load(category_file)
        self.model = ProductCategorizer(len(self.vocacbMapping), 21)
        self.model.load_state_dict(torch.load(modelPath))

    def predictCategory(self, productNames):
        dataSet = self._mapStringToIndices(productNames)
        dataSet = Dataset(dataSet, None, 999999, batch_size_sents=999999)
        batch = dataSet.next()
        
        pred = self.model(batch)
        max_index = pred.max(dim = 1)[1]
        
        return self._mapMaxIndexToCategoryName(max_index)

    def _mapMaxIndexToCategoryName(self, maxIndex):
        categories = list(map(lambda x: self.categories[x], maxIndex))
        return categories
        

    def _mapStringToIndices(self, productNames):
        data = []

        for productName in productNames:
            mappedProd = []
            for word in productName.split():
                mappedProd.append(self.vocab_mapping[word])
            data.append(torch.LongTensor(mappedProd))
        return data