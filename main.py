import requests
import os
import csv
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASS = os.getenv('PASS')


def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.maximize_window()
    driver.get(base_url)
    time.sleep(5)
    wait_for(driver, (By.ID, 'session_key')).send_keys(EMAIL)
    driver.find_element_by_id('session_password').send_keys(PASS)
    driver.find_element_by_class_name('sign-in-form__submit-button').click()
    time.sleep(5)
    return driver


def wait_for(driver, condition):
    delay = 3  # seconds
    try:
        return WebDriverWait(driver, delay).until(EC.presence_of_element_located(condition))
    except TimeoutException:
        pass


def read():
    with open(file='mix.csv', encoding='utf-8', mode='r') as csv_file:
        rows = list(csv.reader(csv_file))
    return rows


def write(lines, file_name):
    with open(file=file_name, encoding='utf-8', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)


def main():
    driver = get_driver()
    driver.get(base_url)
    wait_for(driver, (By.ID, 'session_key')).send_keys(EMAIL)
    driver.find_element_by_id('session_password').send_keys(PASS)
    driver.find_element_by_class_name('sign-in-form__submit-button').click()
    time.sleep(5)
    for i in range(100):
        url = scrape_url + str(i+1)
        print(url)
        driver.get(url)
        wait_for(driver, (By.CLASS_NAME, 'search-results__list'))
        items = driver.find_elements_by_class_name('search-result__occluded-item')
        for item in items:
            line = []
            try:
                if item.find_element_by_class_name('actor-name'):
                    name = item.find_element_by_class_name('actor-name').text.strip()
                    job = item.find_element_by_class_name('search-result__truncate').text.strip()
                    line.append(name)
                    line.append(job)
                    if name == 'LinkedIn Member':
                        print('LinkedIn Member')
                        continue
                    anchor = item.find_element_by_tag_name('a')
                    if anchor:
                        link = anchor.get_attribute('href')
                        if link == '#':
                            print('#')
                            continue
                        if 'http' in link:
                            user_url = link + 'detail/contact-info'
                        else:
                            user_url = 'https://linkedin.com' + link + 'detail/contact-info/'
                        line.append(user_url)
                print(line)
                write(lines=[line], file_name='Result.csv')
            except:
                continue
    if driver:
        driver.quit()


def detail():
    records = read()
    driver = get_driver()
    for record in records:
        try:
            print(record[2])
            line = [record[0], record[1]]
            driver.get(record[2])
            wait_for(driver, (By.CLASS_NAME, 'core-rail'))
            snippets = driver.find_elements_by_class_name('pv-contact-info__ci-container')
            for snippet in snippets:
                try:
                    if snippet.find_element_by_tag_name('a') is not None:
                        line.append(snippet.find_element_by_tag_name('a').get_attribute('href'))
                except:
                    continue
            print(line)
            write(lines=[line], file_name='Save.csv')
        except:
            continue


def divide():
    records = read()
    for record in records:
        mailto = ''
        for ind, rec in enumerate(record):
            if 'mailto' in rec:
                mailto = rec.replace('mailto:', '')
                record.remove(rec)
                break
        record.insert(2, mailto)
        print(record)
        write(lines=[record], file_name='Linkedin.csv')


if __name__ == '__main__':
    base_url = 'https://linkedin.com'
    scrape_url = 'https://www.linkedin.com/search/results/people/?keywords=%22automotive%20marketing%22&page='
    divide()
