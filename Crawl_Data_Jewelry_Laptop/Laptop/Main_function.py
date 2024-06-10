import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from tqdm import tqdm

## Customize chrome displayLa
# Customize Chrome browser settings
chrome_options = Options()                                     
chrome_options.add_argument('--no-sandbox')                     #Them tuy chon de chay Chrome ko co sandbox, thuong duoc su dung de tranh cac van de ve quyen truy cap he thong
chrome_options.add_argument('--disable-notifications')          #Tat thong bao tu trinh duyet
chrome_options.add_argument('--disable-infobars')               #Tat thanh thong tin cua trinh duyet

path = 'chromedriver.exe'
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service, options=chrome_options)

#Crawl the information displayed on the outside of the page
def get_Data_On_Page(driver):
    #The information is definitely there
    Type = [elem.get_attribute("value") for elem in driver.find_elements(By.CSS_SELECTOR, ".search-box__input--O34g")]
    Title = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".RfADt [href]")]
    Link = [elem.get_attribute('href') for elem in driver.find_elements(By.CSS_SELECTOR, ".RfADt [href]")]
    Price_sale = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".ooOxS")]
    Sale_off = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR , ".WNoq3")]

    
    #The information may or may not be available
    #If not, assign None
    Total_sold, Preview = [], []
    for i in range(1, len(Title)+1):
        try:
            one_total_sold = driver.find_element("xpath", "/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[2]/div[{}]/div/div/div[2]/div[5]/span[1]/span[1]".format(i))
            Total_sold.append(one_total_sold.text)
        except NoSuchElementException:
            Total_sold.append(None)

        try:
            one_preview = driver.find_element("xpath", "/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[2]/div[{}]/div/div/div[2]/div[5]/div/span".format(i))
            Preview.append(one_preview.text)
        except NoSuchElementException:
            Preview.append(None)
    
    Location = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".oa6ri")]
    if len(Type) == 1:
        Type = Type * len(Title)

    #Create a dictionary with the lists
    data = {
        "Type": Type,
        "Title": Title,
        "Link": Link,
        "Price_sale": Price_sale,
        "Sale_off": Sale_off,
        "Total_sold": Total_sold,
        "Preview": Preview,
        "Location": Location
    }

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data)
    return df

#Get the link and access each product to get more features
def get_Data_OneProduct_Link(driver, link):
    driver.get(link)                            #Get link
    sleep(random.uniform(3, 5))                 #Random sleep to mimic human behavior and avoid getting blocked
    
    Price_original = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".notranslate.pdp-price.pdp-price_type_deleted.pdp-price_color_lightgray.pdp-price_size_xs")]
    Ship_price = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".delivery-option-item.delivery-option-item_type_standard .delivery-option-item__body .delivery-option-item__shipping-fee.no-subtitle")]
    Return = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".delivery-option-item.delivery-option-item_type_returnPolicy30 .delivery-option-item__body .delivery-option-item__info .delivery-option-item__title")]

    # Sale_rating & Ship_on_time & Chat_respone
    percentage = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".seller-info-value ")]
    Sale_rating = percentage[0] if len(percentage) > 0 else None
    Ship_on_time = percentage[1] if len(percentage) > 1 else None
    Chat_response = percentage[2] if len(percentage) > 2 else None


    #Cuộn trang từ từ để tải phần đánh giá sao
    while True:
        driver.execute_script("window.scrollBy(0, 400);")
        sleep(1)  #Đợi một chút để nội dung tải
        try:
            stars = driver.find_elements(By.CSS_SELECTOR, ".detail .percent")
            if len(stars) >= 5:
                break
        except NoSuchElementException:
            continue
    
    One_star, Two_star, Three_star, Four_star, Five_star = [], [], [], [], []
    stars = [elem.text for elem in stars]

    One_star.append(stars[4] if len(stars) > 4 else 'N/A')
    Two_star.append(stars[3] if len(stars) > 3 else 'N/A')
    Three_star.append(stars[2] if len(stars) > 2 else 'N/A')
    Four_star.append(stars[1] if len(stars) > 1 else 'N/A')
    Five_star.append(stars[0] if len(stars) > 0 else 'N/A')


    #Create a dictionary with the lists
    One_Product = {
        "Price_original": Price_original[0] if Price_original else None,
        "Ship_price": Ship_price[0] if Ship_price else None,
        "Return": Return[0] if Return else None,
        "Sale_rating": Sale_rating,
        "Ship_on_time": Ship_on_time,
        "Chat_response": Chat_response,
        "One_star": One_star,
        "Two_star": Two_star,
        "Three_star": Three_star,
        "Four_star": Four_star,
        "Five_star": Five_star
    }
    
    return One_Product 