from bs4 import BeautifulSoup
import pprint
import psycopg2
from psycopg2 import Error
import settings
import glob
import datetime

path_list=glob.glob("archived_scraped_data/syllabus_econ_2022/*")
# pprint.pprint(path_list)

class SyllabusDetail:
    def __init__(self, classYear):
        self.classYear = classYear

syllabus_details_list = [None] * (len(path_list))
# シラバスリストのパス
for i, path in enumerate(path_list):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    tables = soup.find("table", class_="c-table-line")
    #<table>で取れる情報
    t_list = [i.text.replace("\n", "").replace("\u3000", "") for i in tables.find_all("td")]

    dayOfWeek1 = None
    period1 = None
    dayOfWeek2 = None
    period2 = None

    if len(t_list[9]) > 0 and str(t_list[9]) == "集中講義":
        dayOfWeek1 = str(t_list[9])
    elif len(t_list[9]) == 2:
        dayOfWeek1 = str(t_list[9])[0]
        period1 = int(str(t_list[9])[1])
    if len(t_list[9]) == 5:
        dayOfWeek2 = str(t_list[9])[3]
        period2 = int(str(t_list[9])[4])
    lesson = t_list[1]
    lessonClass = t_list[2]
    instructor = t_list[3]
    grade = t_list[5]
    semester = t_list[7]
    semesterAlt = t_list[8]
    lessonCategory = t_list[10]
    subjectCategory = t_list[11]
    unitCategory = t_list[12]
    numberOfUnits = t_list[13]
    preparations = t_list[14]
    remarks = t_list[15]
    specialProgram = t_list[16]
    # 現在の時刻
    date = datetime.datetime.now()
    registration_date = date

    #授業方法を取得
    lesson_method_div = soup.select_one("body > div > main > div > div > div:nth-child(3) > div > div.c-contents-body > div > p")
    lesson_method = lesson_method_div.text
    #講義情報をhtmlのまま取得
    lesson_info_html = soup.select_one("body > div > main > div > div > div:nth-child(4) > div > div.c-contents-body")
    lesson_info_html = str(lesson_info_html)
    syllabus_detail_list = [
        lesson,
        lessonClass,
        instructor,
        grade,
        semester,
        semesterAlt,
        dayOfWeek1,
        period1,
        dayOfWeek2,
        period2,
        lessonCategory,
        subjectCategory,
        unitCategory,
        numberOfUnits,
        preparations,
        remarks,
        specialProgram,
        lesson_method,
        lesson_info_html,
        registration_date
    ]
    syllabus_details_list[i] = syllabus_detail_list

# PostgreSQLへログイン
setting = settings.DATABASES['test']

connection = psycopg2.connect(
    host=setting['HOST'],
    user=setting['USER'],
    password=setting['PASSWORD'],
    database=setting['DATABASE']

)


with connection:
    try:
        with connection.cursor() as cursor:
            #sql = 'INSERT INTO "SyllabusList" ("年度", "カテゴリ", "科目区分", "単位区分", "講義名", "担当教員", "学年", "開講時期", "曜日1", "時限1", "曜日2", "時限2", "科目コード", "ナンバリング", syllabus_detail_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            sql = 'INSERT INTO "SyllabusDetails"("講義名", "クラス", "担当教員", "学年", "開講学期", "開講時期", "曜日1", "時限1", "曜日2", "時限2", "科目種別", "科目区分", "単位区分", "単位数", "準備事項", "備考", "特殊プログラム", "授業方法", "講義情報", registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING syllabus_detail_id;'
            cursor.executemany(sql, syllabus_details_list)
    except Error as error:
        print(error)

    #コミットしてトランザクション実行
    connection.commit()

# 終了処理
cursor.close()




