import csv
import os
import glob

# 評定を数値に変換するための辞書
grade_info = {
    'S': 4.0,
    'A+': 3.5,
    'A': 3.0,
    'B+': 2.5,
    'B': 2.0,
    'C+': 1.5,
    'C': 1.0,
    'D': 0.0,
    'F': 0.0,
  }

# 必修科目、選択必修科目、選択科目のリスト（科目名をキー、GPが値）
compulsory_classes = {
  "微分積分学基礎Ⅰ": 0.0,
  "微分積分学基礎Ⅱ": 0.0,
  "線形代数基礎": 0.0,
  "力学基礎": 0.0,
  "電磁気学基礎": 0.0,
  "物理化学Ⅰ": 0.0,
  "無機化学Ⅰ": 0.0,
  "有機化学Ⅰ": 0.0,
  "基礎化学物理Ⅰ": 0.0,
  "基礎化学物理Ⅱ": 0.0,
  "物理化学Ⅱ": 0.0,
  "物理化学Ⅲ": 0.0,
  "物理化学Ⅳ": 0.0,
  "分析化学": 0.0,
  "無機化学Ⅱ": 0.0,
  "無機化学Ⅳ": 0.0,
  "有機化学Ⅱ": 0.0,
  "有機化学Ⅲ": 0.0,
  "有機化学Ⅳ": 0.0,
  "有機機器分析": 0.0,
  "化学演習Ⅰ": 0.0,
  "化学演習Ⅱ": 0.0,
  "英語化学文献講読Ⅰ": 0.0,
  "英語化学文献講読Ⅱ": 0.0,
  "化学基礎実験Ⅰ": 0.0,
  "化学基礎実験Ⅱ": 0.0,
  "合成・解析化学実験Ⅰ": 0.0
}
elective_classes = {
  "化学結合論": 0.0,
  "熱力学・統計熱力学": 0.0,
  "機器分析": 0.0,
  "固体化学": 0.0,
  "量子化学": 0.0,
  "物性化学": 0.0,
  "反応物理化学": 0.0,
  "地球化学": 0.0,
  "放射化学": 0.0,
  "天然物化学": 0.0,
  "有機反応化学Ⅰ": 0.0,
  "有機反応化学Ⅱ": 0.0
}
elective_compulsory_classes = {
  "生物学基礎": 0.0,
  "基礎生化学": 0.0,
  "基礎分子生物学": 0.0,
  "基礎細胞生物学": 0.0,
  "基礎生体適応学": 0.0,
  "基礎生体機能学": 0.0,
  "基礎生体情報制御学": 0.0
}

all_classes = [compulsory_classes, elective_classes, elective_compulsory_classes]

# csvの名前
filename = "SIRS23RC007.csv"

def convert_grade_to_number(g):
  """評定文字列または数値を数値に変換（未登録は0.0）。"""
  if isinstance(g, (int, float)):
    return float(g)
  if g is None:
    return 0.0
  return grade_info.get(str(g).strip(), 0.0)

def parse_csv_data(filename=filename, all_classes=all_classes):
  edited_probability_flag = False
  """
  CSVデータ（bytesならshift_jisでデコード、strならそのまま）を解析して
  compulsory_classes / elective_classes / elective_compulsory_classes を更新する。
  学科判定に失敗したら空リストを返す。
  """
  print((f'{filename} を解析中...'))
  try:
    with open(filename, 'r', encoding='cp932') as f:
      csv_reader = csv.reader(f)
      lines = [','.join(row) for row in csv_reader]
  except UnicodeDecodeError:
    with open(filename, "r", encoding='utf-8-sig') as f:
      csv_reader = csv.reader(f)
      lines = [','.join(row) for row in csv_reader]
      print("Excel等で編集した可能性あり")
      edited_probability_flag = True


  # 1行目の 学生番号 をチェック（"学籍番号"の次の要素を取得）
  student_id = lines[0].split(',')[3].strip() if len(lines) > 0 else ''

  # 2行目に "理学部基礎化学科" が含まれているかチェック
  if len(lines) < 2 or "理学部基礎化学科" not in lines[1]:
    print("対象外の学科です。")
    return [all_classes]  # 対象外

  for i in range(5, len(lines)):  # 最初の数行とヘッダをスキップ
    line = lines[i].strip()
    if not line:
      continue
    line = line.replace('"', '')  # ダブルクォート除去
    split_line = line.split(',')
    if len(split_line) < 6:
      continue

    course_title = split_line[4].strip()
    # grade は末尾から3番目の要素（元のJSロジックに合わせる）
    grade = split_line[-3].strip() if len(split_line) >= 3 else ''

    if course_title in compulsory_classes:
      if compulsory_classes[course_title] <= convert_grade_to_number(grade):
        compulsory_classes[course_title] = convert_grade_to_number(grade)
    elif course_title in elective_classes:
      if elective_classes[course_title] <= convert_grade_to_number(grade):
        elective_classes[course_title] = convert_grade_to_number(grade)
    elif course_title in elective_compulsory_classes:
      if elective_compulsory_classes[course_title] <= convert_grade_to_number(grade):
        elective_compulsory_classes[course_title] = convert_grade_to_number(grade)
    else:
      continue

  # 更新した辞書とstudent_idを返す（必要な形に適宜変更してください）
  return [compulsory_classes, elective_classes, elective_compulsory_classes], student_id, edited_probability_flag

# all_classesからGPAを計算する関数
def calculate_gpa(all_classes):
  total_points = 0.0
  total_courses = 0

  # 必修科目は全部参入する
  for course, grade in all_classes[0].items():
    total_points += grade
    total_courses += 1
  # 選択科目は4科目分参入する
  elective_grades = sorted(all_classes[1].values(), reverse=True)[:4]
  for grade in elective_grades:
    total_points += grade
    total_courses += 1
  # 選択科目の4科目に算入されなかったが単位を取得している科目数分だけ加算
  for grade in all_classes[1].values():
    if grade > 0.0 and grade not in elective_grades:
      total_points += 1
  # 選択必修科目は1科目分参入する
  elective_compulsory_grades = sorted(all_classes[2].values(), reverse=True)[:1]
  for grade in elective_compulsory_grades:
    total_points += grade
    total_courses += 1

  # 実際にGPAを計算する
  if total_courses == 0:
    return 0.0
  gpa = total_points / total_courses
  return gpa

# all_classesを初期化する関数
def initialize_all_classes(all_classes):
  for class_dict in all_classes:
    for key in class_dict.keys():
      class_dict[key] = 0.0
  return all_classes

if __name__ == "__main__":
  print("csvフォルダ内のすべてにGPA計算を開始します。")

  # 学籍番号とGPAのペアを格納するリスト
  gpa_results = []

  print(glob.glob('*.csv'))

  # このpyファイルと同じ階層に存在するCSVファイルに対してそれぞれのGPAを計算する
  for filename in glob.glob('*.csv'):
    # filenameがgpa_results.csvの場合はスキップ
    if filename == "gpa_results.csv":
      continue
    initialize_all_classes(all_classes)
    if filename.endswith(".csv"):
      all_classes, student_id, edited_probability_flag = parse_csv_data(filename, all_classes)
      gpa = calculate_gpa(all_classes)

      print(f"学生番号: {student_id}, GPA: {gpa:.3f}")
      gpa_results.append((student_id, gpa, edited_probability_flag))
  print("すべてのGPA計算が完了しました。")

  # 最後に学籍番号とGPAのみをまとめたCSVファイルを出力する
  output_filename = "gpa_results.csv"
  with open(output_filename, 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['学生番号', 'GPA', 'csv編集の可能性の高さ'])
    for student_id, gpa, edited_probability_flag in gpa_results:
      csv_writer.writerow([student_id, f"{gpa:.3f}", edited_probability_flag])
  print(f"GPA結果が {output_filename} に保存されました。")