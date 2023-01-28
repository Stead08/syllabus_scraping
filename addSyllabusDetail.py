# パッケージのインポート
from bs4 import BeautifulSoup
import pprint
import psycopg2
from psycopg2 import Error
import settings
import glob
import datetime
# htmlを保存しているディレクトリでパスのリストを生成
path_list = glob.glob("scraped_data/syllabus_econ_2022/*")
# pprint.pprint(path_list)

class SyllabusDetail:
    def __init__(self, classYear):
        self.classYear = classYear
# pathリスト分の空リストを生成し、そこに要素リストを代入する。
syllabus_details_list = [None] * (len(path_list))
# シラバスリストの各パスについて
for i, path in enumerate(path_list):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    tables = soup.find("table", class_="c-table-line")
    #<table>で取れる情報
    t_list = [i.text.replace("\n", "") for i in tables.find_all("td")]

    dayOfWeek1 = None
    period1 = None
    dayOfWeek2 = None
    period2 = None

    if len(t_list[9]) > 0 and str(t_list[9]) == "集中講義":
        dayOfWeek1 = str(t_list[9])
    elif len(t_list[9]) == 2:
        dayOfWeek1 = str(t_list[9])[0]
        period1 = int(str(t_list[9])[1])
    elif len(t_list[9]) == 5:
        dayOfWeek1 = str(t_list[9])[0]
        period1 = int(str(t_list[9])[1])
        dayOfWeek2 = str(t_list[9])[3]
        period2 = int(str(t_list[9])[4])
    lesson = t_list[1]
    lessonClass = t_list[2]
    instructor = t_list[3]
    grade = t_list[5]
    semester = t_list[7]
    if semester == '前期\u3000～\u3000後期（通年）':
        semester = "前期"
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

    # 旧カリの場合
    if "旧カリ" in lesson:
        #授業方法を取得
        lesson_method_div = soup.select_one("body > div.c-wrapper > main > div > div > div:nth-child(3) > div > div.c-contents-body")
        if lesson_method_div is None:
            pass
        else:
            lesson_method = lesson_method_div.text
        #講義情報をhtmlのまま取得
        lesson_info_html = soup.select_one("body > div.c-wrapper > main > div > div > div:nth-child(4) > div > div.c-contents-body")
        lesson_info_html = str(lesson_info_html)
    # 新カリ(旧カリ以外）の場合
    else:
        lesson_method_div = soup.select_one("body > div.c-wrapper > main > div > div > div:nth-child(4) > div > div.c-contents-body")
        if lesson_method_div is None:
            pass
        else:
            lesson_method = lesson_method_div.text
        # 講義情報をhtmlのまま取得
        lesson_info_html = soup.select_one("body > div.c-wrapper > main > div > div > div:nth-child(5) > div > div.c-contents-body")
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

def insertSyllabusDetails(syllabus_details_list: list):
    '''
    :param syllabus_details_list:
    syllabus_details_listをポスグレにinsertして、インデックステーブにIDを登録
    '''
    syllabus_list_id_scraping = None
    for syllabus_detail in syllabus_details_list:
        print(syllabus_detail)
        with connection:
            try:
                with connection.cursor() as cursor:
                    sql1 = 'INSERT INTO "SyllabusDetails"("講義名", "クラス", "担当教員", "学年", "開講学期", "開講時期", "曜日1", "時限1", "曜日2", "時限2", "科目種別", "科目区分", "単位区分", "単位数", "準備事項", "備考", "特殊プログラム", "授業方法", "講義情報", registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING syllabus_detail_id;'
                    cursor.execute(sql1, syllabus_detail)
                    syllabus_detail_id = cursor.fetchone()
                    sql2 = 'SELECT "syllabus_list_id" FROM "SyllabusList" WHERE "講義名" = %s AND "担当教員" = %s AND "開講時期" = %s AND "曜日1" = %s'
                    cursor.execute(sql2, [syllabus_detail[0] ,syllabus_detail[2], syllabus_detail[4], syllabus_detail[6]])
                    syllabus_list_id_scraping = cursor.fetchone()
                    if syllabus_list_id_scraping == None:
                        print("None")
                        continue
                    syllabus_list_id_scraping = syllabus_list_id_scraping[0]

                    sql3 = 'UPDATE "SyllabusList"  SET "syllabus_detail_id" = %s, "科目区分" = %s, "単位区分" = %s WHERE "syllabus_list_id" = %s'
                    cursor.execute(sql3, [syllabus_detail_id, syllabus_detail[11], syllabus_detail[12],syllabus_list_id_scraping])

            except Error as error:
                print(error)

            #コミットしてトランザクション実行
            connection.commit()

        # 終了処理
        cursor.close()

insertSyllabusDetails(syllabus_details_list)


