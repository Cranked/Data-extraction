import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

url_list = []
prices_list = []
shop_list = []
propTitles = []
propValues = []
shop_points_list = []

session = HTMLSession()
url = "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
df = pd.DataFrame([])


def get_page_contents(base_url, paging_extra, url_list, propTitles, propValues, prices_list):
    url = base_url + paging_extra
    r = session.get(url)
    source = BeautifulSoup(r.content, "lxml")  # Extracting the content of the requested page
    urls = source.find_all("div", attrs={"class": "pro"})
    for i in range(len(urls)):
        url_phone = urls[i].a.get("href")  # Finding links to data
        url_list.append(url_phone)  # Saving links
        print(url_phone)

        r_phone = requests.get(url_phone, headers=headers)  # Sending a request to the found link again
        source_phone = BeautifulSoup(r_phone.content, "lxml")  # Extraction of data content
        properties = source_phone.find_all("li", attrs={"class": "unf-prop-list-item"})  # Finding all the features

        for prop in properties:
            title = prop.findNext("p", attrs={'class': 'unf-prop-list-title'}).text
            propTitles.append(title)


    prices = source.find_all("ins")
    for price in prices:
        prices_list.append(price.text)  # Navigating and typing to list in the found features


def update_contents(url_phone,index):
    r_phone = requests.get(url_phone, headers=headers)  # Sending a request to the found link again
    source_phone = BeautifulSoup(r_phone.content, "lxml")  # Extraction of data content
    sellers = source_phone.find_all("a", attrs={"class": "main-seller-name"})  # Finding all shops
    shop_points = source_phone.find_all("span", attrs={"class": "point"})
    properties = source_phone.find_all("li", attrs={"class": "unf-prop-list-item"})  # Finding all the features

    for prop in properties:
        title = prop.findNext("p", attrs={'class': 'unf-prop-list-title'}).text
        value = prop.findNext("p", attrs={'class': 'unf-prop-list-prop'}).text

        print(title+value)
        df[title].loc[index] = value

    for shop in sellers:
        shop_name = shop.text
        shop_list.append(shop_name)

    shop_point = shop_points[0].text
    shop_points_list.append(shop_point)


try:
    for i in range(1, 3):
        paging_extra = "?pg=" + str(i)
        get_page_contents(url, paging_extra, url_list, propTitles, propValues, prices_list)
    print("{} adet ürün url bulundu".format(len(url_list)))
    columns = np.unique(np.array(propTitles))
    df = pd.DataFrame(columns=columns)
    df["url"] = url_list
    df["price"] = prices_list
    for i,temp_url in enumerate(url_list):
        print("------------------------------")
        update_contents(temp_url,i)
        print("******************************")


    df["ShopName"] = shop_list
    df["ShopPoint"] = shop_points_list
    print(df.head())
    df.to_csv("./data/phone_data.csv")
except Exception as e:
    print(e)
