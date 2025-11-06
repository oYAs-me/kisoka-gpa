import csv
import glob
import json
from pprint import pprint

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

# 評定を数値に変換する関数
def convert_grade_to_number(g):
  if isinstance(g, (int, float)):
    return float(g)
  if g is None:
    return 0.0
  return grade_info.get(str(g).strip(), 0.0)

# 成績のCSVデータを解析して，配属用成績all_classesや卒業単位graduated_classesと学生IDを返す関数
def parse_csv_data(filename, all_classes, hantei):
  """
  CSVデータ（Shift-JIS or UTF-8(with BOM)）を解析して
  compulsory_classes / elective_classes / elective_compulsory_classes を更新する。
  all_classes: [compulsory_classes, elective_classes, elective_compulsory_classes]
  返り値: 更新したall_classes, student_id, edited_probability_flag（UTF-8(with BOM)のときExcelで開いて編集した可能性が高いため）, graduated_classes
  """
  print((f'{filename} を解析中...'))

  edited_probability_flag = False # UTF-8(with BOM)で読み込んだ場合に（Excelで編集した疑惑が高いため）Trueにするフラグ
  graduated_classes = [] # 配属GPA計算に含まれないが卒業単位としてカウントする科目リスト
  
  hantei_set = set(hantei) # 卒業単位判定用の科目名set

  try: # Shift-JISで読み込みを試みる
    with open(filename, 'r', encoding='cp932') as f:
      csv_reader = csv.reader(f)
      lines = [','.join(row) for row in csv_reader]
  except UnicodeDecodeError: # エラーを吐いたらUTF-8(with BOM)で再読み込み
    with open(filename, "r", encoding='utf-8-sig') as f:
      csv_reader = csv.reader(f)
      lines = [','.join(row) for row in csv_reader]
      print(" Excel等で編集した可能性あり")
      edited_probability_flag = True


  # 1行目の 学生番号 をチェック（"学籍番号"の次の要素を取得）
  student_id = lines[0].split(',')[3].strip() if len(lines) > 0 else ''

  # 2行目に "理学部基礎化学科" が含まれているかチェック
  if len(lines) < 2 or "理学部基礎化学科" not in lines[1]:
    print(" 対象外の学科です。")
    return ""  # 対象外なら積極的にエラーを出す

  for i in range(5, len(lines)):  # 最初の数行（メタ情報）とヘッダをスキップ
    line = lines[i].strip()
    if not line:
      continue
    line = line.replace('"', '')  # ダブルクォート除去
    split_line = line.split(',')
    if len(split_line) < 6:
      continue

    course_title = split_line[4].strip() # 科目名
    grade = split_line[-3].strip() if len(split_line) >= 3 else '' # 評定

    # 科目名が各辞書（必修・選択・選択必修）に存在する場合、評価を数値に変換して上書き更新
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
      # 卒業単位判定用データに含まれている科目で，かつ単位を取得している場合，graduated_classesに追加
      if convert_grade_to_number(grade) > 0.0:
        for hantei_title in hantei_set:
          if hantei_title in course_title:
            graduated_classes.append(hantei_title)
      continue

  # 更新した辞書などとstudent_idとflagとを返す
  return [compulsory_classes, elective_classes, elective_compulsory_classes], student_id, edited_probability_flag, graduated_classes

# 卒業単位数のうち何単位を取得しているか返す関数
def calculate_earned_credits(graduated_classes, all_classes, hantei) -> int:
  """
  基本的な方針
   - hanteiは，hantei.jsonに記載の，卒業単位として算入できそうな科目をCampus Squareからコピーして成形してきたデータ
   - all_classes（配属GPAに入る科目）に登録されている単位数をearned_creditsにカウント
   - graduated_classes（all_classes以外の卒業単位に加算できる科目）に登録されている科目と単位を，上限が存在するsmall_genre（例：外国語，人文学科目など）ごとに積算
   - small_genreのうちで卒業に必須な単位数を先にearned_creditsに加算
   - small_genreごとの上限を超えた分をbig_genre（例：教スリ，専門科目）ごとに積算
   - big_genreでの積算か上限のいずれか小さい方をearned_creditsに加算
  """
  # 科目判定用データを取得
  hantei_data = hantei["data"]# = {講義名: {genre: AA, credits: 0}, ...}

  # earned_creditsで卒業単位数をカウント
  earned_credits = 0

  # all_classes（）に登録済みの単位数をカウント
  for class_dict in all_classes:
    for course_title, grade in class_dict.items():
      if grade > 0.0:
        earned_credits += int(hantei_data[course_title]['credits'])
  
  # graduated_classesに登録されている科目を，genreごとにカウント
  big_genre = hantei["genre"] # = {big_genre_name: {genre: {small_genre_name: {credits: (int)}, ...}, credits: (int)}, ...}
  small_genre_credits = {sg: sg_data["credits"] for bg_data in big_genre.values() for sg, sg_data in bg_data["genre"].items()} # = {small_genre_name: (int), ...}

  # big_genreごとにsmall_genreをまとめる
  bg_sg_includings = {}
  for big_genre_name, bg_data in big_genre.items():
    for sg, sg_data in bg_data["genre"].items():
      try:
        bg_sg_includings[big_genre_name].append(sg)
      except KeyError:
        bg_sg_includings[big_genre_name] = [sg]

  # big_genreのうちsmall_genreに含まれている単位数をカウントし保存しておく
  bg_sg_delta_credits = {} # sgからあふれた単位数をbgとしてカウントしていい単位数の上限
  for bg, sg_list in bg_sg_includings.items():
    total_sg_credits = sum([small_genre_credits[sg] for sg in sg_list]) - 8 # 日本語と英語の単位の被りがあるのでそれを除く！
    bg_total_credits = big_genre[bg]["credits"]
    bg_sg_delta_credits[bg] = max(0, bg_total_credits - total_sg_credits)

  # 取得単位数countのためにsmall_genreをコピーして0に初期化
  counted_sg_credits = {sg: 0 for sg in small_genre_credits.keys()}

  # graduated_classesを走査してsmall_genreごとに単位数をカウント
  for course_title in graduated_classes:
    class_data = hantei_data[course_title]
    counted_sg_credits[class_data['genre']] += int(class_data['credits'])
  
  # small_genreごとに単位数を確認し，範囲内はearned_creditに追加し，超過分はadd_bg_credits_dictに加算
  add_bg_credits_dict = {bg: 0 for bg in big_genre.keys()}

  for sg, counted_credits in counted_sg_credits.items():
    earned_credits += min(counted_credits, small_genre_credits[sg])
    if counted_credits > small_genre_credits[sg]: # 超過分がある場合
      for bg, sg_list in bg_sg_includings.items(): # small_genreが含まれるbig_genreを探し
        if sg in sg_list:
          add_bg_credits_dict[bg] += (counted_credits - small_genre_credits[sg]) # 超過分を加算
          break # 1つのbig_genreにしか含まれないはずなのでbreak
      
  # bg_credits_dictとbg_sg_delta_creditsのminをearned_creditsに加算する
  for bg, add_credits in add_bg_credits_dict.items():
    earned_credits += min(add_credits, bg_sg_delta_credits[bg])

  return earned_credits

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




# ここからメイン処理（上記の関数を適切に呼び出す）
if __name__ == "__main__":
  print("csvフォルダ内のすべてにGPA計算を開始します。")

  # 学籍番号とGPAのペアを格納するリスト
  gpa_results = []

  with open("hantei.json", 'r', encoding='utf-8') as f:
    hantei = json.load(f)
  hantei_data_keys = hantei["data"].keys() # {講義名: {genre: AA, credits: 0}, ...}

  # このpyファイルと同じ階層に存在するCSVファイルに対してそれぞれのGPAを計算する
  for filename in glob.glob('*.csv'):
    # filenameがgpa_results.csvの場合はスキップ
    if filename == "gpa_results.csv":
      continue
    initialize_all_classes(all_classes) # all_classesを初期化
    if filename.endswith(".csv"): # CSVファイルのみ処理
      all_classes, student_id, edited_probability_flag, graduated_classes = parse_csv_data(filename, all_classes, hantei_data_keys) # csv解析
      gpa = calculate_gpa(all_classes) # GPA計算

      earned_credits = calculate_earned_credits(graduated_classes, all_classes, hantei) # 卒業単位のうち取得単位数を計算

      print(f" 学生番号: {student_id}, GPA: {gpa:.3f}, 取得単位数: {earned_credits}") # 結果表示
      gpa_results.append((student_id, gpa, earned_credits, edited_probability_flag)) # 結果を出力用に保存
  print("すべてのGPA計算が完了しました。")

  # gpa_resultsを学生番号順にソートする
  gpa_results.sort(key=lambda x: x[0])

  # 最後に学籍番号とGPAのみをまとめたCSVファイルを出力する
  output_filename = "gpa_results.csv"
  with open(output_filename, 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['学生番号', 'GPA', '修得単位数', 'csv編集の可能性の高さ'])
    for student_id, gpa, earned_credits, edited_probability_flag in gpa_results:
      csv_writer.writerow([student_id, f"{gpa:.3f}", earned_credits, edited_probability_flag])
  print(f"GPA結果が {output_filename} に保存されました。")