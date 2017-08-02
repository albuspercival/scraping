import re
import time
import locale
from datetime import timedelta
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


def does_element_exist(driver, selectors):
    try:
        driver.find_element_by_css_selector(selectors)
    except NoSuchElementException:
        return False
    return True


def decode_time_stamps(time_stamp, website):
    if website == "PI":
        locale.setlocale(locale.LC_TIME, "de_DE")
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, "%d. %B %Y at %H:%M")))
        locale.resetlocale()
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "MMNews":
        locale.setlocale(locale.LC_TIME, "de_DE")
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, "%d. %B %Y - %H:%M")))
        locale.resetlocale()
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "Correctiv":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, " %d.%M.%Y %H:%M ")))
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "Netzfrauen":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(re.findall(
          ".(\d.*)", time_stamp)[0], "%d.%m.%y @ %H:%M")))
        return correct_time.replace(microsecond=0).isoformat()
    else:
        raise ValueError("This website argument seems to be wrong :"
                         + website)


def pi_comments(driver, url):
    # tested and works: 31th July 2017
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    list_of_comment_elements = soup.find_all(class_="comment")
    for comment_elements in list_of_comment_elements:
        if comment_elements.find("div", class_="comment-content"):
            comment_body_div = comment_elements.find(
             "div", class_="comment-content")
            comment_text = ""
            # connocate all p elements
            for comment_line in comment_body_div.find_all("p"):
                comment_text += comment_line.get_text()
        if comment_elements.find("cite"):
            user_name = comment_elements.find(
             "cite").get_text()
        if comment_elements.find("time"):
            time_stamp = decode_time_stamps(comment_elements.find(
             "time").get_text(), "PI")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
            })
    return scraped_comments


def mmnews_comments(driver, url):
    try:
        driver.get(url)
    except TimeoutException:
        pass
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    list_of_page_links = driver.find_element_by_css_selector(
     "span.hmtPageSelectButton")
    for index, page in enumerate(list_of_page_links):
        list_of_comment_elements = soup.find_all(class_="hmtCommentContent ")
        for comment_elements in list_of_comment_elements:
            if comment_elements.find('hmtCommentContent '):
                comment_text = comment_elements.find(
                 'hmtCommentContent ').get_text()
            if comment_elements.find("hmtCommentTime"):
                time_stamp = decode_time_stamps(comment_elements.find(
                 "time").get_text(), "MMNews")
            scraped_comments.append({
                'name': None,
                'text': comment_text,
                'time': time_stamp
                })
        if index+1 == len(list_of_page_links):
            return scraped_comments
        driver.find_elements_by_css_selector(
         "span.hmtPageSelectButton")[index+1].click()
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html)


def netzfrauen_comments(driver, url):
    # tested and seems to work: 31th July 2017
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    scraped_comments = []
    list_of_comment_elements = soup.find_all("article",
                                             class_="comment")
    for comment_elements in list_of_comment_elements:
        if comment_elements.find("div", class_="comment-text"):
            comment_body_div = comment_elements.find(
             "div", class_="comment-text")
            comment_text = ""
            # connocate all p elements
            for comment_line in comment_body_div.find_all("p"):
                comment_text += comment_line.get_text()
        if comment_elements.find("li", class_="comment-author"):
            user_name = comment_elements.find(
             "li", class_="comment-author").get_text()
        if comment_elements.find(class_="comment-time"):
            time_stamp = decode_time_stamps(comment_elements.find(
             class_="comment-time").a.get_text(), "Netzfrauen")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
            })
    return scraped_comments


def correctiv_comments(driver, url):
    try:
        driver.get(url)
    except TimeoutException:
        pass
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    list_of_comment_elements = soup.find_all("li",
                                             class_="comment-list__item media")
    for comment_elements in list_of_comment_elements:
        if comment_elements.find("div", class_="comment-list__body"):
            comment_body_div = comment_elements.find(
             "div", class_="comment-list__body")
            comment_text = ""
            # connocate all p elements
            for comment_line in comment_body_div.find_all("p"):
                comment_text += comment_line.get_text()
        if comment_elements.find("h4", class_="comment-list__name"):
            user_name = comment_elements.find(
             "h4", class_="comment-list__name").get_text()
        if comment_elements.find(class_="comment-list__date"):
            time_stamp = decode_time_stamps(comment_elements.find(
             class_="comment-list__date").get_text(), "Correctiv")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
            })
    return scraped_comments
