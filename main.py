import random
import time
from selenium import webdriver
import pickle
from elastic import *
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()
es = connect_elasticsearch()


def parser(soup):
    d = soup.select("article._2vCnw.cia-vs.cia-cs")
    all_data = []
    for j in d:
        c = j.select_one("h3._2UHry._2vVOc")
        a_tag = c.find("a")
        price = j.select_one("div._3NaXx._33ZFz._2m5MZ span span")
        href = "https://market.yandex.ru" + a_tag["href"]
        span = a_tag.find("span").text
        specs = j.select("ul.fUyko._2LiqB li")
        clear_specs = []
        for spec in specs:
            try:
                clear_specs.append({
                    spec.text.split(":")[0]: spec.text.split(":")[1]
                })
            except:
                pass
        if price:
            all_data.append({"url": href, "naming": span, "img": [], "specs": clear_specs, "price": price.text})
        else:
            all_data.append({"url": href, "naming": span, "img": [], "specs": clear_specs, "price": None})
    return all_data


def prepare_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument(f'--host=http://{os.environ.get("STARTING_PAGE")}')
    _driver = webdriver.Remote(
        command_executor=f'http://{os.environ.get("ROUTER")}:{os.environ.get("ROUTER_PORT")}/wd/hub', options=options)
    if os.path.exists('yandex.pkl'):
        cookies = pickle.load(open("yandex.pkl", "rb"))
        for cookie in cookies:
            print(f'cookie added {cookie}!')
            try:
                _driver.add_cookie(cookie)
            except:
                pass
    return _driver


driver = prepare_driver()

data = match_all_orgs(es)["hits"]["hits"]

for ind, i in enumerate(data):
    category = i["class"]
    driver.get(i["_source"]["url"].split("?")[0])
    if ind == 0:
        time.sleep(300)
    if "Что-то пошло не так" in driver.page_source:
        break
    time.sleep(random.randint(2, 7))
    while "Подтвердите, что запросы отправляли вы, а не робот" in driver.page_source:
        print("captcha!!!!!!")
        time.sleep(5)
    try:
        time.sleep(120)
        soup = BeautifulSoup(driver.page_source, "lxml")
        datasa = parser(soup)
        print(datasa)
        for d in datasa:
            d["class"] = category
            insert_product(es, d)
        pickle.dump(driver.get_cookies(), open("yandex.pkl", "wb"))
    except:
        pass
driver.close()
es.close()
