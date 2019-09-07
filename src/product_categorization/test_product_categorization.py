from product_categorization_api import ProductCategorizationApi

api = ProductCategorizationApi("./model_e4000.pt", "./vocab_mapping.json", "./categories.json")

input = [
    { "name": "SLICED WHITE BREAD" },
    { "name": "GNOCCHI ALLA SORRENTINA" },
    { "name": "LINGUINE WITH PESTO & TOMATOES" },
    { "name": "BANANA EACH ORGANIC" }
]
results = api.predictCategory(input)

print(results)