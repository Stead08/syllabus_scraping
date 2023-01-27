from bs4 import BeautifulSoup
import re
import pprint
import psycopg2
import settings

class SyllabusList:
    def __init__(self, classYear, category, subjectCode, numbering, lesson, instructor, grade, semester, dayOfWeek1, period1, dayOfWeek2, period2, subjectCategory, unitCategory):
        self.classYear = classYear
        self.category = category
        self.subjectCode = subjectCode
        self.numbering = numbering
        self.lesson = lesson
        self.instructor = instructor
        self.grade = grade
        self.semester = semester
        self.dayOfWeek1 = dayOfWeek1
        self.period1 = period1
        self.dayOfWeek2 = dayOfWeek2
        self.period2 = period2
        self.subjectCategory = subjectCategory
        self.unitCategory = unitCategory
# シラバスリストのパス
path = "SyllabusListData/SC_06001B00_21"
with open(path, encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
# <tr _index="0" class="is-unread"><td class="content is-source" data-label="タイトル" id="content"><div class="c-omitted-wrap js-c-column-tooltip"><p class="c-omitted-text">2022年度シラバス</p></div></td><td class="content is-source" data-label="カテゴリ" id="content"><div class="c-omitted-wrap js-c-column-tooltip"><p class="c-omitted-text">経済経営学類</p></div></td><td class="content is-source -center" data-label="科目コード" id="content">32200010</td><td class="content is-source -center" data-label="ナンバリング" id="content"></td><td class="content is-source" data-label="講義名" id="content"><div class="c-omitted-wrap js-c-column-tooltip"><p class="c-omitted-text">キャリア形成論(旧カリ) </p></div></td><td class="content is-source" data-label="担当教員" id="content"><div class="c-omitted-wrap js-c-column-tooltip"><p class="c-omitted-text">岩井　秀樹</p></div></td><td class="content is-source -center" data-label="学年" id="content">4年</td><td class="content is-source -center" data-label="クラス" id="content">経</td><td class="content is-source -center" data-label="開講学期" id="content">前期</td><td class="content is-source" data-label="曜日・時限" id="content"><div class="c-omitted-wrap js-c-column-tooltip"><p class="c-omitted-text">水２</p></div></td><td class="content is-source" data-label="" id="content">キャリアケイセイロン</td><td class="content is-source" data-label="" id="content">イワイヒデキ</td><td class="content is-source" data-label="" id="content">4</td><td class="content is-source" data-label="" id="content">1W</td><td class="content is-source" data-label="" id="content">1</td><td class="content is-source" data-label="" id="content">32</td></tr>
tables = soup.find_all("tr", class_="is-unread")
Syllabus_list = [None] * len(tables)
#<td>で取れる情報
for i, table in enumerate(tables):
    t_list = table.find_all("td")
    classYear = int(re.sub(r"\D", "", t_list[0].text))
    category = t_list[1].text
    subjectCode = t_list[2].text
    numbering = t_list[3].text
    lesson = t_list[4].text
    instructor = t_list[5].text
    grade = None
    if len(str(t_list[6].text)) > 0:
        grade = int(str(t_list[6].text)[0])
    semester = t_list[8].text
    dayOfWeek1 = None
    period1 = None
    dayOfWeek2 = None
    period2 = None

    if len(t_list[9].text) > 0 and str(t_list[9].text) == "集中講義":
        dayOfWeek1 = str(t_list[9].text)
    elif len(t_list[9].text) == 2:
        dayOfWeek1 = str(t_list[9].text)[0]
        period1 = int(str(t_list[9].text)[1])
    if len(t_list[9].text) == 5:
        dayOfWeek1 = str(t_list[9].text)[0]
        period1 = int(str(t_list[9].text)[1])
        dayOfWeek2 = str(t_list[9].text)[3]
        period2 = int(str(t_list[9].text)[4])
    Syllabus_list[i] = [classYear,
                        category,
                        None,
                        None,
                        lesson,
                        instructor,
                        grade,
                        semester,
                        dayOfWeek1,
                        period1,
                        dayOfWeek2,
                        period2,
                        subjectCode,
                        numbering,
                        None,
                        ]


# PostgreSQLへログイン
setting = settings.DATABASES['test']

connection = psycopg2.connect(
    host=setting['HOST'],
    user=setting['USER'],
    password=setting['PASSWORD'],
    database=setting['DATABASE']

)

pprint.pprint(Syllabus_list)
with connection:
    with connection.cursor() as cursor:
        sql = 'INSERT INTO "SyllabusList" ("年度", "カテゴリ", "科目区分", "単位区分", "講義名", "担当教員", "学年", "開講時期", "曜日1", "時限1", "曜日2", "時限2", "科目コード", "ナンバリング", syllabus_detail_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        cursor.executemany(sql, Syllabus_list)

    #コミットしてトランザクション実行
    connection.commit()

# 終了処理
cursor.close()




