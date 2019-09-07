from product_categorization_api import ProductCategorizationApi

api = ProductCategorizationApi("./model_e4000.pt", "./vocab_mapping.json", "./categories.json")

input = [
    "SLICED WHITE BREAD",
    "GNOCCHI ALLA SORRENTINA",
    "LINGUINE WITH PESTO & TOMATOES",
    "BANANA EACH ORGANIC"
]
results = api.predictCategory(input)

print(results)