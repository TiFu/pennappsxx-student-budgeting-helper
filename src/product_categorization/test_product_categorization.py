from product_categorization_api import ProductCategorizationApi

api = ProductCategorizationApi("./model_e96000.pt", "./vocab_mapping.json", "./categories.json")

input = [
    "SLICED WHITE BREAD",
    "GNOCCHI ALLA SORRENTINA",
    "LINGUINE WITH PESTO & TOMATOES"
]
results = api.predictCategory(items)

print(results)