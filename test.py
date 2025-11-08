import json, csv
from pprint import pprint

with open('nessesary4graduate-credits.json', 'r', encoding='utf-8') as file:
  data = json.load(file)
# pprint(data)

# 分類ごとに辞書を分ける（）
large_categories = {}
midium_categories = {}
small_categories = {}

for large_category, l1 in data.items():
  large_categories[large_category] = l1['credits']
  for midium_category, l2 in l1.items():
    if midium_category == 'credits':
      continue
    midium_categories[midium_category] = {"credits": l2['credits'], "large_category": large_category}
    for small_category, l3 in l2.items():
      if small_category == 'credits':
        continue
      small_categories[small_category] = {"credits": l3['credits'], "midium_category": midium_category}

pprint(large_categories)
pprint(midium_categories)
pprint(small_categories)


      