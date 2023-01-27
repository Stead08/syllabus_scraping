from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# firefoxを開く
driver = webdriver.Firefox()
driver.implicitly_wait(10) # 秒
# 最大の読み込み時間を設定
wait = WebDriverWait(driver=driver, timeout=30)
try:
    # シラバスページを開く
    driver.get("https://livecampus.adb.fukushima-u.ac.jp/syllabus/")
    # 学類選択ボックスを探す
    major_select_box = driver.find_element(by=By.NAME, value="category")
    # 検索ボタンを探す
    submit_button = driver.find_element(by=By.XPATH, value="/html/body/div[1]/main/div/div/div[2]/div[1]/div/div/form/div[2]/ul/li[2]/button")
    # 学類選択ボックスを選択
    major_select = Select(major_select_box)
    # 経済経営学類を選択
    major_select.select_by_value('047100000738')
    # 検索ボタンをおす
    submit_button.click()
    # 一番初めの科目を探す
    select_first_on_table = driver.find_element(by=By.CSS_SELECTOR, value="tr.is-unread:nth-child(1) > td:nth-child(5)")
    # 科目をクリック
    select_first_on_table.click()
    time.sleep(15)
    html = driver.page_source
    getLessonTitle = driver.find_element(By.CSS_SELECTOR, ".c-table-line > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > div:nth-child(1) > p:nth-child(1)")
    LessonTitle = getLessonTitle.text
    index = 1
    with open("./scraped_data/syllabus_econ_2022/{}.html".format(str(index).zfill(5)), 'w', encoding='utf-8') as f:
        f.write(html)
    index += 1
    counter = 0
    for _ in range(551):
        wait.until(EC.presence_of_element_located)
        time.sleep(10)
        try:
            next_button = driver.find_element(By.XPATH, "/html/body/div/main/div/div/div[2]/div/div[2]/div/ul/li[3]/button")
            next_button.click()
        except Exception as e:
            print(e)
            driver.refresh()
            next_button = driver.find_element(By.XPATH,
                                              "/html/body/div/main/div/div/div[2]/div/div[2]/div/ul/li[3]/button")
            next_button.click()

        html = driver.page_source
        getLessonTitle = driver.find_element(By.CSS_SELECTOR,
                                             ".c-table-line > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > div:nth-child(1) > p:nth-child(1)")
        LessonTitle = getLessonTitle.text

        with open("./scraped_data/syllabus_econ_2022/{}.html".format(str(index).zfill(5)), 'w', encoding='utf-8') as f:
            f.write(html)
        index += 1
#エラーが発生した時はエラーメッセージを吐き出す
except Exception as e:
    print(e)
    print("エラーが発生しました")
finally:
    driver.close()
    driver.quit()