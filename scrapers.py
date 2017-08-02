import time
import re
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
    """Simple helper function, checking whether an element on a page exists."""
    try:
        driver.find_element_by_css_selector(selectors)
    except NoSuchElementException:
        return False
    return True


def decode_time_stamps(time_stamp, website):
    """Takes a string and converts it to the universally used time format."""
    if website in {"Zeit", "NOZ", "Welt"}:
        current_time = datetime.now()
        minutes_which_have_passed = re.findall(
         "[a-zA-Z]+\s([0-9]+)\sMinute", time_stamp)
        hours_which_have_passed = re.findall(
         "[a-zA-Z]+\s([0-9]+)\sStunde", time_stamp)
        seconds_which_have_passed = re.findall(
         "[a-zA-Z]+\s([0-9]+)\sSekunde", time_stamp)
        months_which_have_passed = re.findall(
         "[a-zA-Z]+\s([0-9]+)\sMonat", time_stamp)
        days_which_have_passed = re.findall(
         "[a-zA-Z]+\s([0-9]+)\sTag", time_stamp)
        if minutes_which_have_passed:
            timedelta_difference = timedelta(minutes=int("".join(
             minutes_which_have_passed)))
        elif hours_which_have_passed:
            timedelta_difference = timedelta(hours=int("".join(
             hours_which_have_passed)))
        elif seconds_which_have_passed:
            timedelta_difference = timedelta(seconds=int("".join(
             seconds_which_have_passed)))
        elif months_which_have_passed:
            timedelta_difference = timedelta(weeks=int("".join(
             months_which_have_passed*4)))
        elif days_which_have_passed:
            timedelta_difference = timedelta(days=int("".join(
             days_which_have_passed)))
        else:
            raise ValueError("This seems to be an improper time format: "
                             + time_stamp)
        correct_time = current_time - timedelta_difference
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "Handelsblatt":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S%z")))
        return correct_time.isoformat()
    elif website == "TAZ":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp[:-6] + "+0200",
                                   "%Y-%m-%dT%H:%M:%S%z")))
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "RP":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp[:-6] + "+0200",
                                   "%Y-%m-%dT%H:%M%z")))
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "TZ" or website == "Merkur" or website == "FR":
        # set locale to recognise German terms
        locale.setlocale(locale.LC_TIME, "de_DE")
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, "%A, %d. %B %Y %H:%M Uhr")))
        # reset locale, for whatever purpose
        locale.resetlocale()
        return correct_time.replace(microsecond=0).isoformat()
    elif website in {"Spiegel", "TAZ"}:
        minutes_today = re.findall(
         "heute,\s[0-9][0-9]:([0-9][0-9])", time_stamp)
        hours_today = re.findall(
         "heute,\s([0-9][0-9]):[0-9][0-9]", time_stamp)
        minutes_yesterday = re.findall(
         "gestern,\s[0-9][0-9]:([0-9][0-9])", time_stamp)
        hours_yesterday = re.findall(
         "gestern,\s([0-9][0-9]):[0-9][0-9]", time_stamp)
        previous_date = re.findall(
         "([0-9][0-9].[0-9][0-9].[0-9][0-9])", time_stamp)
        if minutes_today:
            correct_time = datetime.now()
            correct_time = correct_time.replace(
             hour=int("".join(hours_today)),
             minute=int("".join(minutes_today)))
        elif minutes_yesterday:
            correct_time = datetime.now()
            correct_time = correct_time.replace(
             hour=int("".join(hours_yesterday)),
             minute=int("".join(minutes_yesterday)))
            correct_time = correct_time - timedelta(days=1)
        elif previous_date:
            correct_time = datetime.fromtimestamp(
             time.mktime(time.strptime("".join(previous_date) + "T00:01",
                                       "%d.%m.%yT%H:%M")))
        else:
            raise ValueError("This seems to be an improper time format :"
                             + time_stamp)
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "FAZ":
        # strip of one whitespace character, one minus sign and
        # one whitespace character
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp[3:], "%d.%m.%Y %H:%M")))
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "NW":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, "%d.%m.%Y %H:%M")))
        return correct_time.replace(microsecond=0).isoformat()
    elif website == "TA":
        correct_time = datetime.fromtimestamp(
         time.mktime(time.strptime(time_stamp, "%d.%m.%Y - %H:%M")))
        return correct_time.replace(microsecond=0).isoformat()
    else:
        raise ValueError("This website argument seems to be wrong :"
                         + website)


def handelsblatt_comments(driver, url):
    # tested and works: 17th July 2017
    driver.get(url)
    if driver.find_elements_by_class_name(
     "vhb-paywall-new"):
        return "Premium-Content"
    try:
        comments_url = driver.find_element_by_id(
         "discussionurlRH").get_attribute("href")
    except NoSuchElementException:
        return "Keine Kommentare fuer diese URL " + url
    driver.get(comments_url)
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    for index, comment_page in enumerate(driver.find_elements_by_css_selector(
     ".paging-item")):
        list_of_comment_elements = soup.find_all(class_="col-md-offset-1")
        list_of_comment_elements.extend(soup.find_all(
         class_="col-md-offset-2"))
        for comment_elements in list_of_comment_elements:
            if comment_elements.find("p", class_="vhb-comment-content"):
                comment_text = comment_elements.find(
                 "p", class_="vhb-comment-content").get_text()
            if comment_elements.find("span", class_="vhb-user"):
                user_name = comment_elements.find(
                 "span", class_="vhb-user").get_text()
            if comment_elements.find("time", class_="vhb-time"):
                time_stamp = decode_time_stamps(comment_elements.find(
                 "time", class_="vhb-time")["content"], "Handelsblatt")
            scraped_comments.append({
                'name': user_name,
                'text': comment_text,
                'time': time_stamp
                })
        if index+1 == len(
         driver.find_elements_by_css_selector(".paging-item")):
            return scraped_comments
        driver.find_elements_by_css_selector(
         ".paging-item")[index+1].find_element_by_css_selector(
         "a").send_keys('\n')
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')


def spiegel_comments(driver, url):
    try:
        driver.get(url)
    except TimeoutException:
        pass
    # tested and works: 17th July 2017
    if not driver.find_elements_by_css_selector(
     ".module-subtitle.forum-title"):
        return "Comments are disabled for this article."
    # not necesary to open comments, as their text is contained in html source
    try:
        driver.find_element_by_css_selector(
         '.js-article-comments-toggle-all.button.plus-fa').click()
    except NoSuchElementException:
        return "No comments yet."
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    scraped_comments = []
    while True:
        for comment_elements in soup.find_all(class_="article-comment"):
            if comment_elements.find(
             "div", class_="js-article-post-full-text"):
                comment_text = comment_elements.find(
                 "div", class_="js-article-post-full-text").get_text()
            if comment_elements.find("div", class_="article-comment-user"):
                user_name = comment_elements.find(
                 "div", class_="article-comment-user").a.b.get_text()
            if comment_elements.find("span", class_="date-time"):
                time_stamp = decode_time_stamps(comment_elements.find(
                 "span", class_="date-time").get_text(), "Spiegel")
            scraped_comments.append({
                'name': user_name,
                'text': comment_text,
                'time': time_stamp
                })
        # breaks when the last page of the comments is reached
        # otherwise, new page gets reloaded into BeautifulSoup
        if driver.find_element_by_css_selector(
         ".js-article-comments-box-page-next.page-next").get_attribute(
          "style") == "display: none;":
            break
        driver.find_element_by_css_selector(
         ".js-article-comments-box-page-next.page-next").click()
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    return scraped_comments


def zeit_comments(driver, url):
    driver.get(url)
    actions = ActionChains(driver)
    scraped_comments = []
    more_comments = True
    while more_comments:
        for index in range(len(driver.find_elements_by_css_selector(
         '.comment-overlay__wrap'))):
            driver.execute_script(
             "document.querySelectorAll('.comment-overlay__cta')[" + str(
              index) + "].click()")
            # driver.find_elements_by_css_selector('.comment-overlay__wrap')[index].click()
            # actions.move_to_element(driver.find_elements_by_css_selector('.comment-overlay__cta')[index]).click().perform()
        # for more_comments_button in driver.find_elements_by_css_selector(
        # '.comment-overlay__wrap'):
            # driver.implicitly_wait(4)
        #    more_comments_button.click()
        driver.implicitly_wait(6)
        html = driver.page_source
        soup = BeautifulSoup(html)
        # find all comment divs
        for comment_div in soup.find_all("div", class_="comment__container"):
            # find the user name in the link in the div
            if comment_div.find('div', class_='comment-meta__name'):
                user_name = comment_div.find(
                 'div', class_='comment-meta__name').a.get_text()
            # get the timestamp
            if comment_div.find('a', class_='comment-meta__date'):
                time_stamp_div = decode_time_stamps(comment_div.find(
                 'a', class_='comment-meta__date').get_text(), "Zeit")
            # find the div containing the text paragraphs
            if comment_div.find("div", class_="comment__body"):
                comment_body_div = comment_div.find(
                 "div", class_="comment__body")
                comment_text = ""
                # connocate all p elements
                for comment_line in comment_body_div.find_all("p"):
                    comment_text += comment_line.get_text()
            # add the final result to the dictionary
            scraped_comments.append({
                'name': user_name,
                'text': comment_text,
                'time': time_stamp_div
            })

        if not does_element_exist(driver,
                                  ".pager__button.pager__button--next"):
            return scraped_comments
        else:
            driver.execute_script("document.querySelectorAll" +
                                  "('.pager__button.pager__button--next')["
                                  + str(0) + "].click()")
            # driver.find_element_by_css_selector(".pager__button.pager__button--next").click()
            # actions.move_to_element(driver.find_element_by_css_selector(".pager__button.pager__button--next")).click().perform()
            # print("Kein Problem bei der naechsten Seite")
            # driver.find_element_by_css_selector(".pager__button.pager__button--next").click()
            # try:
            #     driver.find_element_by_css_selector(".pager__button.pager__button--previous")
            #     print("no more comments!")
            #     return scraped_comments
            # except NoSuchElementException:
            #     print("More comments still!")
    return scraped_comments


def tz_comments(driver, url):
    # finds no comments
    driver.get(url + "#idAnchComments")
    # driver.get(url)
    # if driver.find_elements_by_css_selector(
    # ".id-Comment-button.id-Icon--arrowDown.id-js-commentHideAfterLoad.id-open"):
    # driver.find_element_by_css_selector(".id-Comment-button.id-Icon--arrowDown.id-js-commentHideAfterLoad.id-open").click()
    driver.implicitly_wait(5)
    html = driver.page_source
    # html = str(driver.execute_script(
    # "document.getElementsByTagName('html')[0].innerHTML"))
    soup = BeautifulSoup(html, 'lxml')
    scraped_comments = []
    print("BS findet so viele Kommentare: " + str(len(soup.find_all(
     "div", class_="post-message "))))
    print("Selenium findet so viele Kommentare: " + str(len(
     driver.find_elements_by_css_selector("div.post-message "))))
    for comment_elements in soup.find_all(class_="post-body"):
        if comment_elements.find(class_='author publisher-anchor-color'):
            user_name = comment_elements.find(
             class_='author publisher-anchor-color').a.get_text()
        if comment_elements.find("div", class_="post-message "):
            comment_body_div = comment_elements.find(
             "div", class_="post-message ")
            comment_text = ""
            # connocate all p elements
            for comment_line in comment_body_div.find_all("p"):
                comment_text += comment_line.get_text()
        if comment_elements.find(class_='time-ago'):
            time_stamp = decode_time_stamps(
             comment_elements.find(class_='time-ago')["title"], "TZ")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
        })
    return scraped_comments


def merkur_comments(driver, url):
    return tz_comments(driver, url)


def noz_comments(driver, url):
    # tested and works: 24th July 2017
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    try:
        list_of_page_links = driver.find_element_by_css_selector(
         "div.pagination.pagination-right").find_elements_by_css_selector(
         "a")[:-2]
    except NoSuchElementException:
        one_page = True
    # current page (first element) and two navigatio buttons excluded
    if not one_page:
        for index, comment_page in enumerate(list_of_page_links):
            comment_elements = soup.find_all(class_="user-comment level-1 ")
            comment_elements.extend(soup.find_all(
             class_="user-comment level-1 first"))
            comment_elements.extend(soup.find_all(class_="user-comment level-2"))
            for comment_element in comment_elements:
                if comment_element.find('img'):
                    user_name = comment_element.find('img')['alt']
                if comment_element.find('p'):
                    comment_text = comment_element.p.get_text()
                if comment_element.find(class_='days'):
                    time_stamp = decode_time_stamps(
                     comment_element.find(class_='days').get_text(), "NOZ")
                scraped_comments.append({
                    'name': user_name,
                    'text': comment_text,
                    'time': time_stamp
                })
            if index+1 == len(list_of_page_links):
                return scraped_comments
            list_of_page_links[index+1].send_keys('\n')
            time.sleep(4)
            html = driver.page_source
            soup = BeautifulSoup(html)
    elif one_page is True:
        comment_elements = soup.find_all(class_="user-comment level-1 ")
        comment_elements.extend(soup.find_all(
         class_="user-comment level-1 first"))
        comment_elements.extend(soup.find_all(class_="user-comment level-2"))
        for comment_element in comment_elements:
            if comment_element.find('img'):
                user_name = comment_element.find('img')['alt']
            if comment_element.find('p'):
                comment_text = comment_element.p.get_text()
            if comment_element.find(class_='days'):
                time_stamp = decode_time_stamps(
                 comment_element.find(class_='days').get_text(), "NOZ")
            scraped_comments.append({
                'name': user_name,
                'text': comment_text,
                'time': time_stamp
            })
    return scraped_comments


def faz_comments(driver, url):
    # seems to work: 1st August of 2017
    driver.get(url)
    if driver.find_elements_by_css_selector(".teaser_container"):
        return "Premium-Content"
    actions = ActionChains(driver)
    if does_element_exist(driver, ".mehr"):
        # driver.find_element_by_css_selector(".mehr").send_keys('\n')
        actions.move_to_element(
         driver.find_element_by_css_selector(".switchV.VA")).click().perform()
        # actions.send_keys("\n").perform
        # driver.find_element_by_css_selector(
        #  ".switchV.VA").find_element_by_css_selector("span").click
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    # if driver.find_elements_by_css_selector(".PagerNav.right"):
    #
    try:
        list_of_page_links = driver.find_element_by_css_selector(
         ".PagerNav.right").find_elements_by_css_selector("a")[:-1]
    except NoSuchElementException:
        single_page = True
    if not single_page:
        for index, value in enumerate(list_of_page_links):
            for comment_element in soup.find_all("div", class_="LMFuss"):
                if comment_element.find(class_='Username'):
                    user_name = comment_element.find(
                     class_='Username').a['data-loginname']
                if comment_element.find('div', class_="LMText"):
                    comment_text = comment_element.find(
                     "span", class_="LMFussLink").get_text()
                    comment_text += comment_element.find(
                     'div', class_="LMText", recursive=False).get_text()
                    # regex doesnt work
                    # comment_text = re.findall(
                    #  "(.+?)Antworten Verstoß melden", comment_text)
                if comment_element.find("span", class_='grayTxt dateTime'):
                    time_stamp = decode_time_stamps(
                     comment_element.find(
                      "span", class_='grayTxt dateTime').get_text(), "FAZ")
                scraped_comments.append({
                    'name': user_name,
                    'text': comment_text,
                    'time': time_stamp
                })
            if index+1 == len(list_of_page_links):
                return scraped_comments
            time.sleep(5)
            # always stale element message
            if index == 0:
                actions.move_to_element(
                 driver.find_element_by_css_selector(
                  ".PagerNav.right").find_elements_by_css_selector(
                  "a")[index]).click().perform()
            elif index+1 == len(list_of_page_links):
                return scraped_comments
            else:
                length_of_current_page_links = len(
                 driver.find_elements_by_css_selector(".PagerNav.right a"))
                driver.execute_script(
                 "document.querySelectorAll('.PagerNav.right a')["
                 + str(length_of_current_page_links-1) + "].click()")
                # actions.move_to_element(
                #  driver.find_element_by_css_selector(
                #   ".PagerNav.right").find_elements_by_css_selector(
                #   "a")[:-1]).click().perform()
            time.sleep(4)
            html = driver.page_source
            soup = BeautifulSoup(html)
        else:
            for comment_element in soup.find_all("div", class_="LMFuss"):
                if comment_element.find(class_='Username'):
                    user_name = comment_element.find(
                     class_='Username').a['data-loginname']
                if comment_element.find('div', class_="LMText"):
                    comment_text = comment_element.find(
                     "span", class_="LMFussLink").get_text()
                    comment_text += comment_element.find(
                     'div', class_="LMText", recursive=False).get_text()
                    # regex doesnt work
                    # comment_text = re.findall(
                    #  "(.+?)Antworten Verstoß melden", comment_text)
                if comment_element.find("span", class_='grayTxt dateTime'):
                    time_stamp = decode_time_stamps(
                     comment_element.find(
                      "span", class_='grayTxt dateTime').get_text(), "FAZ")
                scraped_comments.append({
                    'name': user_name,
                    'text': comment_text,
                    'time': time_stamp
                })
    return scraped_comments


def nw_comments(driver, url):
    try:
        driver.get(url)
    except TimeoutException:
        pass
    actions = ActionChains(driver)
    more_commments = True
    clicked = False
    # doesnt work
    # while more_commments:
    #     number_of_buttons = len(driver.find_elements_by_css_selector(
    #      ".btn.btn-primary.btn-sm"))
    #     for more_comments_buttons in driver.find_elements_by_css_selector(
    #      ".btn.btn-primary.btn-sm"):
    #         actions.move_to_element(more_comments_buttons).click().perform()
    #         time.sleep(3)
    #     #     clicked = True
    #     # if clicked:
    #     #     time.sleep(3)
    #     #     clicked = False
    #     number_of_buttons_after_clicking = len(
    #      driver.find_elements_by_css_selector(".btn.btn-primary.btn-sm"))
    #     if number_of_buttons_after_clicking > 0:
    #         more_commments = True
    #     else:
    #         more_commments = False

    while more_commments:
        if does_element_exist(driver, ".btn.btn-primary.btn-sm"):
            # element = WebDriverWait(driver, 20).until(
            #  EC.element_to_be_clickable((By.CSS_SELECTOR,".btn.btn-primary.btn-sm")))
            #  element.click()
            driver.execute_script(
             "document.querySelectorAll('.btn.btn-primary.btn-sm')[0].click()")
            # actions.move_to_element(driver.find_element_by_css_selector(
            #      ".btn.btn-primary.btn-sm")).click().perform()
            time.sleep(4)
        else:
            more_commments = False
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    scraped_comments = []
    if soup.find(id="em_comment_page_1"):
        central_div = soup.find(id="em_comment_page_1")
        for comment_element in central_div.find_all("div", recursive=False):
            if comment_element.find("span"):
                user_name = comment_element.find_all(
                 "span", recursive=False)[0].get_text()
            if comment_element.find("blockquote"):
                comment_text = comment_element.find("blockquote").get_text()
                if comment_element.find("span", class_="details"):
                    comment_text += comment_element.find(
                     "span", class_="details").get_text()
            if comment_element.find(
             "span", class_='update-triangle-bottom-right'):
                time_stamp = decode_time_stamps(
                 comment_element.find(
                  "span", class_='update-triangle-bottom-right').get_text(),
                 "NW")
            scraped_comments.append({
                'name': user_name,
                'text': comment_text,
                'time': time_stamp
            })
    return scraped_comments


def rp_comments(driver, url):
    #
    driver.get(url)
    more_comments = False
    if driver.find_elements_by_css_selector(
     ".read-more.more-comments.hidden.left"):
        more_comments = True
    while more_comments:
        driver.execute_script(
             "document.querySelectorAll('.read-more.more-comments" +
             ".hidden.left')[0].click()")
        time.sleep(3)
        if driver.find_elements_by_css_selector(
         ".read-more.more-comments.hidden.left")[0].get_attribute(
         "style") == "display: block;":
            more_comments = True
        else:
            more_comments = False
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    for comment_element in soup.find_all("div", class_="comment "):
        if comment_element.find("div", class_='header'):
            user_name = comment_element.find(
             "div", class_='header').h3.get_text()
        if comment_element.find('div', class_="content"):
            content_div = comment_element.find('div', class_="content")
            comment_text = ""
            for comment_paragraph in content_div.find_all("p"):
                comment_text += comment_paragraph.get_text()
        if comment_element.find("time"):
            time_stamp = decode_time_stamps(
             comment_element.find("time")["datetime"], "RP")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
        })
    return scraped_comments


def ta_comments(driver, url):
    # works: 27th July 2017
    # sample URL with actual comments: http://www.thueringer-allgemeine.de/startseite/detail/-/specific/Leitartikel-Zschaepe-als-Mittaeterin-923109066
    try:
        driver.get(url)
    except TimeoutException:
        pass
    if driver.find_elements_by_class_name("pc-info"):
        return "Premium-Content"
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    comments_div = soup.find("div", class_="comments")
    for comment_element in comments_div.find_all("div", class_="qp_item"):
        if comment_element.find("span", class_='user'):
            user_name = comment_element.find("span", class_='user').get_text()
        if comment_element.find('div', class_="comment-text"):
            comment_text = comment_element.find(
             'div', class_="comment-text").get_text()
        if comment_element.find("span", class_="user"):
            time_stamp = comment_element.find_all("span")[1].get_text()
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': decode_time_stamps(time_stamp, "TA")
        })
    return scraped_comments


def welt_comments(driver, url):
    driver.get(url)
    while does_element_exist(
     driver, "a[style:'font-size: 0.6875rem; font-family: ffmark, " +
     "'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 800; " +
     "color: rgb(0, 58, 90); line-height: 5;]"):
        driver.find_element_by_css_selector(
         "a[style:'font-size: 0.6875rem; font-family: ffmark, " +
         "'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 800; " +
         "color: rgb(0, 58, 90); line-height: 5;]").send_keys("\n")
        time.sleep(3)
    while does_element_exist(
     driver, "a[style:'font-size: 0.6875rem; font-family: ffmark," +
             " 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight:" +
             " 500; float: right; color: rgb(120, 120, 120);']"):
        driver.find_element_by_css_selector(
          "a[style:'font-size: 0.6875rem; font-family: ffmark, " +
          "'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 800;" +
          " color: rgb(0, 58, 90); line-height: 5;]").send_keys("\n")
    # for show_answers_button in driver.find_elements_by_css_selector(
    # "a[style:'font-size: 0.6875rem; font-family: ffmark, 'Helvetica Neue',
    # Helvetica, Arial, sans-serif; font-weight: 500; float:
    # right; color: rgb(120, 120, 120);']"):
    #    show_answers_button.click()
    html = driver.page_source
    soup = BeautifulSoup(html)
    scraped_comments = []
    for comment_element in soup.find_all("div", style="margin-top: 3.125rem;"):
        if comment_element.find(
         "a", {"name": "la_community_link_to_public_profile"}):
            user_name = comment_element.find(
             "a", {"name": "la_community_link_to_public_profile"}).get_text()
        if comment_element.find(
         "div", style="font-family: freight, Georgia, serif; font-size:" +
         " 1.125rem; color: rgb(29, 29, 29); line-height: 1.875rem; " +
         "word-wrap: break-word; white-space: pre-line; padding-right: " +
         "3.125rem; margin-left: 3.75rem;"):
            comment_text = comment_element.find(
             "div", style="font-family: freight, Georgia, serif; font-size:" +
             " 1.125rem; color: rgb(29, 29, 29); line-height: 1.875rem; " +
             "word-wrap: break-word; white-space: pre-line; padding-right: " +
             "3.125rem; margin-left: 3.75rem;").get_text()
        if len(comment_element.find_all(
         "div", {"style": "line-height: 20px; padding-top: 0.125rem;"})) > 1:
            time_stamp = decode_time_stamps(comment_element.find_all(
             "div", style="line-height: 20px; padding-top: " +
             "0.125rem;")[1].span.get_text(), "Welt")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
        })
    for comment_element in soup.find_all(
     "div", style="margin-top: 0.9375rem;"):
        if comment_element.find(
         "a", {"name": "la_community_link_to_public_profile"}):
            user_name = comment_element.find(
             "a", {"name": "la_community_link_to_public_profile"}).get_text()
        if comment_element.find(
         'div', style="font-family: freight, Georgia, serif; font-size: " +
         "1.125rem; color: rgb(29, 29, 29); line-height: 1.875rem; word-wrap" +
         ": break-word; white-space: pre-line; padding-right: 3.125rem; " +
         "margin-left: 2.8125rem;"):
            comment_text = comment_element.find(
             'div', style="font-family: freight, Georgia, serif; font-size: " +
             "1.125rem; color: rgb(29, 29, 29); line-height: 1.875rem; " +
             "word-wrap: break-word; white-space: pre-line; padding-right: " +
             "3.125rem; margin-left: 2.8125rem;").get_text()
        if len(comment_element.find_all(
         "div", style="line-height: 20px; padding-top: 0.125rem;",
         recursive=False)) > 1:
            time_stamp = decode_time_stamps(comment_element.find_all(
             "div", style="line-height: 20px; padding-top: 0.125rem;",
             recursive=False)[1].span.get_text(), "Welt")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
        })
    return scraped_comments


def fr_comments(driver, url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    scraped_comments = []
    for comment_elements in soup.find_all(class_="post-body"):
        if comment_elements.find(class_='author publisher-anchor-color'):
            user_name = comment_elements.find(
             class_='author publisher-anchor-color').a.get_text()
        if comment_elements.find("div", class_="post-message "):
            comment_body_div = comment_elements.find(
             "div", class_="post-message ")
            comment_text = ""
            # connocate all p elements
            for comment_line in comment_body_div.find_all("p"):
                comment_text += comment_line.get_text()
        if comment_elements.find(class_='time-ago'):
            time_stamp = decode_time_stamps(
             comment_elements.find(class_='time-ago')["title"], "FR")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
        })
    return scraped_comments


def taz_comments(driver, url):
    # seems to work without hiccups
    driver.get(url)
    html = driver.page_source
    # if driver.find_elements_by_css_selector(".tzi-paywahl__close a"):
    #     driver.find_element_by_css_selector(".tzi-paywahl__close a").click()
    soup = BeautifulSoup(html, 'lxml')
    scraped_comments = []
    for comment_elements in soup.find_all("li", class_="member "):
        if comment_elements.find("a", class_='author person'):
            user_name = comment_elements.find(
             "a", class_='author person').h4.get_text()
        if comment_elements.find("div", class_="objlink nolead"):
            comment_text = comment_elements.find(
             "div", class_="objlink nolead").p.get_text()
        if comment_elements.find("time"):
            time_stamp = decode_time_stamps(
             comment_elements.find("time")["datetime"], "TAZ")
        scraped_comments.append({
            'name': user_name,
            'text': comment_text,
            'time': time_stamp
        })
    return scraped_comments
