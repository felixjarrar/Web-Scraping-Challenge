from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time
import re


def scrape_everything():

    # Initiate headless driver
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "News_Title": news_title,
        "News_Paragraph": news_paragraph,
        "Featured_Image": featured_image(browser),
        "Hemispheres": hemispheres(browser),
        "Weather": twitter_weather(browser),
        "Facts": mars_facts(),
        "Last_Modified": dt.datetime.now()
    }

    # quit and then return data
    browser.quit()
    return data

def news_about_mars(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_element = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_element.find("div", class_="content_title").get_text()
        news_p = slide_element.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def image_featured(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # Find image button
    full_image_element = browser.find_by_id("full_image")
    full_image_element.click()

    # Find info button and click
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_element = browser.links.find_by_partial_text("more info")
    more_info_element.click()

    # Parse
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    # Find the relative image url
    img = img_soup.select_one("figure.lede a img")

    try:
        img_url_rel = img.get("src")

    except AttributeError:
        return None

    # create an absolute url
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    return img_url


def hemispheres_for_web(browser):

    # break long strings
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    # return the href
    hemisphere_image_urls = []
    for i in range(4):

        # loop and avoid element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemisphere_data = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere_data)

        # Finally, we navigate backwards
        browser.back()

    return hemisphere_image_urls


def weather_twitter(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    # Pause
    time.sleep(5)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    # find a tweet with 'Mars weather"
    tweet_attributes = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_soup.find("div", attrs=tweet_attributes)

    try:
        weather_on_mars = mars_weather_tweet.find("p", "tweet-text").get_text()

    except AttributeError:

        pattern = re.compile(r'sol')
        weather_on_mars = weather_soup.find('span', text=pattern).text

    return weather_on_mars


def hemisphere_scraping(html_text):
    # Soupify
    hemisphere_soup = BeautifulSoup(html_text, "html.parser")

    try:
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # better front-end handling
        title_element = None
        sample_element = None

    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }

    return hemisphere


def facts_about_mars():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
