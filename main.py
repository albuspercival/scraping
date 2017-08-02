import time
import re
from datetime import datetime
import json
import scrapers
import site_resources
import xml.etree.ElementTree as ET
import requests
from urllib.error import URLError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

# this is the directory where all temporary helper files will be stored
PATH_TO_DATA = "/Users/marvinstecker/Development/Scraping/virtual_3/data/"
# grab ressources like all RSS-URLs etc
references_dict = site_resources.ressources_reference


def init_driver():
    """Initialises the WebDriver (Chrome) and sets up any custom options."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    path_to_chromedriver = ("/Users/marvinstecker/Development/" +
                            "Scraping/virtual_3/chromedriver_new")
    driver = webdriver.Chrome(executable_path=path_to_chromedriver,
                              chrome_options=chrome_options)
    driver.wait = WebDriverWait(driver, 5)
    driver.set_page_load_timeout(10)
    return driver


def getRSSFeed(feed_url):
    """Gets an RSS-Feed and returns it iterable."""
    u = requests.get(feed_url)
    tree = ET.fromstring(u.content)
    return tree


def extract_data_from_RSS(feed_url):
    """Extracts pub time, title and URL of all articles in an RSS-Feed."""
    feed_extracted = []
    try:
        wurzelRSS = getRSSFeed(feed_url)
    except URLError as e:
        print("Fehler bei dieser URL: " + feed_url)
        print(str(e.reason))
        return []
    for rssItem in wurzelRSS.iter('item'):
        url = rssItem.find('link').text
        title = rssItem.find('title').text
        pubDate = rssItem.find('pubDate').text
        if len(re.findall(",", pubDate)) == 0:
            time_struct = time.strptime(pubDate, "%d %b %Y %H:%M:%S %z")
        elif len(re.findall("GMT", pubDate)) == 0:
            time_struct = time.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %z")
        else:
            time_struct = time.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %Z")
        date_datetime = datetime.fromtimestamp(
         time.mktime(time_struct))
        feed_extracted.append({
            "url": url,
            "title": title,
            "date": date_datetime.isoformat()
        })
    return feed_extracted


def refresh_RSS_data():
    """Grabs current RSS-data, checks for duplicates and saves to files"""
    # get the feed URLs
    references_dict = site_resources.ressources_reference
    for website in references_dict:
        # take this path if multiple feeds are checked
        if type(references_dict[website]["feedurl"]) is not str:
            # open list of articles to be scraped
            try:
                with open(PATH_TO_DATA + website +
                          "_articles_to_be_scraped.txt") as outfile:
                    article_data = json.load(outfile)
            except FileNotFoundError:
                article_data = []
            # grab all saved RSS feeds
            for feed in references_dict[website]["feedurl"]:
                for article in extract_data_from_RSS(feed):
                    # check for duplicates
                    if article["url"] not in [item['url'] for
                                              item in article_data]:
                        article_data.append(article)
            # sort articles by date
            article_data.sort(key=lambda x: x["date"])
            with open(PATH_TO_DATA + website +
                      "_articles_to_be_scraped.txt", "w") as outfile:
                json.dump(article_data, outfile)
        # path for a single feed
        else:
            try:
                with open(PATH_TO_DATA + website +
                          "_articles_to_be_scraped.txt") as outfile:
                    article_data = json.load(outfile)
            except FileNotFoundError:
                article_data = []
            for article in extract_data_from_RSS(references_dict
                                                 [website]["feedurl"]):
                if article["url"] not in [item['url'] for
                                          item in article_data]:
                    article_data.append(article)
            # sort articles by date
            article_data.sort(key=lambda x: x["date"])
            with open(PATH_TO_DATA + website +
                      "_articles_to_be_scraped.txt", "w") as outfile:
                json.dump(article_data, outfile)


def grab_articles_within_timelimit(driver):
    """Checks files for old articles and saves their comments."""
    references_dict = site_resources.ressources_reference
    for website in references_dict:
        temp_scraped_data = []
        list_of_scraped_articles = []
        with open(PATH_TO_DATA + website +
                  "_articles_to_be_scraped.txt") as f:
            article_list = json.load(f)
        current_time = datetime.now()
        for article in article_list:
            time_difference = current_time - datetime.fromtimestamp(
             time.mktime(time.strptime(article["date"], "%Y-%m-%dT%H:%M:%S")))
            # 5 hours arbitrarily set, value must be in seconds
            if time_difference.seconds > 18000:
                if website == "Spiegel":
                    temp_scraped_data.append({
                        "url": article["url"],
                        "headline": article["title"],
                        "comments": references_dict[website]["scraper"](
                         driver, article["url"])
                                })
                    print("Now I would be scraping this article: " +
                          article["url"])
                    # list_of_scraped_articles.append(article["url"])
        article_list_minus_scraped = [
         article for article in article_list if
         article["url"] not in list_of_scraped_articles]
        article_list_minus_scraped
        with open(PATH_TO_DATA + website +
                  "articles_to_be_scraped.txt", "w") as f:
            json.dump(article_list_minus_scraped, f)
        try:
            with open(PATH_TO_DATA + website + "_comments.txt") as f:
                complete_data = json.load(f)
                for article in temp_scraped_data:
                    complete_data.append(article)
            with open(PATH_TO_DATA + website + "_comments.txt", "w") as f:
                json.dump(temp_scraped_data, f)
        except FileNotFoundError:
            with open(PATH_TO_DATA + website + "_comments.txt", "w") as f:
                json.dump(temp_scraped_data, f)


if __name__ == "__main__":
    """Main function, will be executed on calling this file."""
    driver = init_driver()
    # print("Grabbing new RSS-data! Current time: " + str(datetime.now().time()
    # refresh_RSS_data()
    with open("currenttest.txt", "w") as f:
        json.dump(scrapers.spiegel_comments(driver, "http://www.spiegel.de/netzwelt/web/diesel-gipfel-deutschland-das-gelobte-land-des-dinglichen-kolumne-a-1161001.html"), f)
    # grab_articles_within_timelimit(driver)
    driver.quit()
