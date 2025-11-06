import os
import csv
import json
from pprint import pprint

class_data = {}

# hantei.csvは，自己判定から閲覧できる「●教養・スキル・リテラシー科目 」と「●専門科目 」の科目一覧をExcelにコピーしてCSV形式で保存したもの
try:
    with open('hantei.csv', 'r', encoding='cp932') as csvfile:
        reader = csv.reader(csvfile)
except UnicodeDecodeError: # cp932かutf-8(BOM付き)で読めるはず
    with open('hantei.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
reader = list(reader)[1:]  # Skip header row
for row in reader:
  class_data[row[1]] = {
      'genre': row[0],
      'credits': row[2]
  }


genre = {
    '●教養・スキル・リテラシー科目 ': {
        'genre': {
            '英語Ⅰ': {'credits': 4}, '英語Ⅱ': {'credits': 4}, '日本語Ⅰ': {'credits': 4}, '日本語Ⅱ': {'credits': 4}, '必修（社会科学科目群）': {'credits': 4}, '必修（人文学科目群）': {'credits': 4}, '必修（学際領域・AL科目群）': {'credits': 2}, '必修（学部基盤科目群）': {'credits': 2}, '・選択（その他）': {'credits': 0}
        },
        'credits': 26
    },
    '●専門科目 ': {
        'genre': {
            '必修': {'credits': 66}, '選択必修': {'credits': 2}, '選択': {'credits': 14}, '他学科・工学部専門 科目': {'credits': 0}, '理学部専門基礎科目': {'credits': 0}
        },
        'credits': 98
    }
}

output = {
    'data': class_data,
    'genre': genre
}

with open('hantei.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(output, jsonfile, ensure_ascii=False, indent=4)

