import numpy as np
from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

def initializeChrome():
    # Customize Chrome browser settings
    chrome_options = Options()                                     
    chrome_options.add_argument('--no-sandbox')                     #Them tuy chon de chay Chrome ko co sandbox, thuong duoc su dung de tranh cac van de ve quyen truy cap he thong
    chrome_options.add_argument('--disable-notifications')          #Tat thong bao tu trinh duyet
    chrome_options.add_argument('--disable-infobars')               #Tat thanh thong tin cua trinh duyet

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    return driver

# Lấy thông tin từ 1 page (về sản phẩm)
def getDataIn1Page(driver):
    # Get link/title
    elems = driver.find_elements(By.CSS_SELECTOR , ".RfADt [href]")
    titles = [elem.text for elem in elems]
    links = [elem.get_attribute('href') for elem in elems]

    # Get type
    type_name = [elem.get_attribute("value") for elem in driver.find_elements(By.CSS_SELECTOR, ".search-box__input--O34g")]
    type_name = type_name * len(titles)

    # Get price sale
    elems_price_sale = driver.find_elements(By.CSS_SELECTOR , ".aBrP0")
    price = [elem_price.text for elem_price in elems_price_sale]

    # Get discount, sold, preview
    discount_percent_list, sold_list, preview_list = [], [], []
    for i in range(1, len(titles)+1):
        try:
            discount_percent = driver.find_element("xpath", "/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[2]/div[{}]/div/div/div[2]/div[4]/span".format(i))
            discount_percent_list.append(discount_percent.text)
        except NoSuchElementException:
            discount_percent_list.append(None)

        try:
            sold = driver.find_element("xpath", "/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[2]/div[{}]/div/div/div[2]/div[5]/span[1]/span[1]".format(i))
            sold_list.append(sold.text)
        except NoSuchElementException:
            sold_list.append(None)

        try:
            preview = driver.find_element("xpath", "/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[2]/div[{}]/div/div/div[2]/div[5]/div/span".format(i))
            preview_list.append(preview.text)
        except NoSuchElementException:
            preview_list.append(None)
    
    # Get Location
    elems_locations = driver.find_elements(By.CSS_SELECTOR , ".oa6ri ")
    locations = [elem.text for elem in elems_locations]

    # Create a dictionary items
    data = {
        "Type": type_name,
        "Title": titles,
        "Links": links,
        "Price": price,
        "Discount_percent": discount_percent_list,
        "Sold": sold_list,
        "Preview": preview_list,
        "Location": locations
    }

    return data


# Lấy thông tin từ nhiều page
def getDataInNPage(driver, link, n):
    # Access
    driver.get(link)
    driver.implicitly_wait(2)

    dataProducts = {
        "Type": [],
        "Title": [],
        "Links": [],
        "Price": [],
        "Discount_percent": [],
        "Sold": [],
        "Preview": [],
        "Location": []
    }

    print("Collecting data:\n")
    for i in range(1, n + 1):
        data = getDataIn1Page(driver)
        for key in dataProducts.keys():
            for item in data[key]:
                dataProducts[key].append(item)
        print(f"Crawling data page {i} successful.")
        if (i == n):
            print(f"Stopped in page {i}.")
            break
        try:
            element_click = driver.find_element(By.CSS_SELECTOR, ".ant-pagination-next .ant-pagination-item-link")
            element_click.click()
            sleep(2)
        except ElementClickInterceptedException:
            print(f"Stopped in page {i}.")
            break
            
    return dataProducts

# Hàm cuộn từ từ xuống dưới cùng của trang cho đến khi get element được thì dừng
def getStarItem(driver, step=200, wait_time=0.1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    
    while current_position < last_height:
        driver.execute_script(f"window.scrollBy(0, {step});")
        sleep(wait_time)
        current_position += step
        elems_stars = driver.find_elements(By.CSS_SELECTOR, ".percent")
        if not (elems_stars == []):
            break
    if not (elems_stars == []):
        return [elem.text for elem in elems_stars]
    else :
        return ['N/A'] * 5
    
def getDetailItems(driver, link):
    driver.get(link)
    driver.implicitly_wait(2)
    # get original price
    try:
        elems_original = driver.find_element("xpath", "/html/body/div[4]/div/div[3]/div[2]/div/div[1]/div[10]/div/div/div/span[1]")
        original = elems_original.text
    except NoSuchElementException:
        original = None
    # get ship price
    try:
        elems_ship_price = driver.find_element("xpath", "/html/body/div[4]/div/div[3]/div[2]/div/div[2]/div[1]/div/div/div[3]/div/div[1]/div/div[1]/div[2]")
        ship_price = elems_ship_price.text
    except NoSuchElementException:
        ship_price = None
    # get return_
    try:
        elems_return = driver.find_element("xpath", "/html/body/div[4]/div/div[3]/div[2]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div")
        return_ = elems_return.text
    except NoSuchElementException:
        return_ = None
    # get positive review
    try:
        elems_positive_review = driver.find_element("xpath", "/html/body/div[4]/div/div[3]/div[2]/div/div[2]/div[6]/div/div[2]/div[1]/div[2]")
        positive_review = elems_positive_review.text
    except NoSuchElementException:
        positive_review = None
    # get ship on time
    try:
        elems_ship_on_time = driver.find_element("xpath", "/html/body/div[4]/div/div[3]/div[2]/div/div[2]/div[6]/div/div[2]/div[2]/div[2]")
        ship_on_time = elems_ship_on_time.text
    except NoSuchElementException:
        ship_on_time = None
    # get rate response
    try:
        elems_rate_response = driver.find_element("xpath", "/html/body/div[4]/div/div[3]/div[2]/div/div[2]/div[6]/div/div[2]/div[3]/div[2]")
        rate_response = elems_rate_response.text
    except NoSuchElementException:
        rate_response = None
    # get stars
    stars = getStarItem(driver)
    star_5 = stars[0]
    star_4 = stars[1]
    star_3 = stars[2]
    star_2 = stars[3]
    star_1 = stars[4]
    # into a record
    data = {
        "Original": original,
        "Ship_price": ship_price,
        "Return": return_,
        "Positive_review": positive_review,
        "Ship_on_time": ship_on_time,
        "Rate_response": rate_response,
        "One_star": star_1,
        "Two_star": star_2,
        "Three_star": star_3,
        "Four_star": star_4,
        "Five_star": star_5
    }
    return data    