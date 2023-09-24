from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time

def login(username, password):
    driver = webdriver.Chrome()
    # driver = webdriver.Firefox()
    url = 'https://lms.dgist.ac.kr/ultra'
    driver.get(url)
    driver.implicitly_wait(5)
    driver.find_element(By.ID, "agree_button").click()
    driver.find_element(By.ID, "portal_username").send_keys(username)
    driver.find_element(By.ID, "portal_password").send_keys(password)
    driver.find_element(By.ID, "portal").click()
    return driver


def get_homework_list(driver):
    burden_list = []
    wait = WebDriverWait(driver, 5)
    driver.get('https://lms.dgist.ac.kr/ultra/stream')
    time.sleep(4)
    while True:
        if None != driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/main/div/div/div[1]/div/div/div/div[2]/div/ul/li[2]/a'):
            break
    driver.find_element(By.ID, "filter-stream-value").click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/main/div/div/div[1]/div/div/div/div[2]/div/ul/li[2]/a').click()    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    datetime_format = "마감일: %y. %m. %d. %H:%M"

    soups = soup.find("div", attrs={"class":"js-upcomingStreamEntries"}).find_all("div", attrs={"class":"element-card"})
    for soupy in soups:
        burden = {}
        burden["course"] = re.match(r"(.+)\[",soupy.find("a", attrs={"ng-switch-when":"linkToCourse"}).get_text()).group(1)
        burden["homework"] = re.match(r"마감: (.+)", soupy.find("a", attrs={"class":"js-title-link"}).get_text()).group(1)
        burden["due"] = datetime.strptime(soupy.find("span", attrs={"class":"due-date"}).get_text().strip(), datetime_format)

        burden_list.append(burden)

    return burden_list

def get_course_list(driver):
    wait = WebDriverWait(driver, 5)
    driver.get('https://lms.dgist.ac.kr/ultra/course')
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/main/div/div/div[2]/div[1]/div/div/div[7]/div/nav/h2/div/bb-dropdown/div/ul/li[3]/a/span')))
    
    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/bb-base-layout/div/main/div/div/div[2]/div[1]/div/div/div[7]/div/nav/h2/div/button").click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/main/div/div/div[2]/div[1]/div/div/div[7]/div/nav/h2/div/bb-dropdown/div/ul/li[3]/a/span').click()
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    soups = soup.find("div", attrs={"class":"course-org-list"})
    return re.findall(r"(.+)\[", soups.get_text())