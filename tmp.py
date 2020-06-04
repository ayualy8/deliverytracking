import pandas as pd
import math
import numpy as np
import re
import argparse
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time



def main():
    

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=hoge')
    driver = webdriver.Chrome(options=options)
    


    num = "LO997444888CN"
    c_id = get_id(num)
    c_id = "&fc={}".format(c_id) if c_id != '' else ''
    url = "https://t.17track.net/en#nums={}{}".format(
        num, c_id)
    driver.get(url)
    time.sleep(2)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "yqcr-ps")))
    try:
        data = driver.find_element_by_class_name("yqcr-ps")
        data = data.text.split('\n')
        print(data)
        if "Tracking" in data or "" in data:
            pass
        else:
            if 'Delivered' in data[1]:
                country_to = driver.find_element_by_xpath('//*[@id="tn-{}"]/div[1]/div[2]/div[3]'.format(num)).text
                datatimes = driver.find_elements_by_xpath('//*[@id="tn-{}"]/div[2]/div[1]/dl[2]/dd'.format(num))
                line_base = datatimes[-1].text.split("\n")[1]
                j = -2
                while datatimes[j].text.split("\n")[1]==line_base:
                    j -= 1
                print(country_to)
                print(datatimes[j].text.split("\n")[0])
                df_tmp = pd.Series(
                    [o_num, num, 'Delivered', re.search(r'\d+', data[1]).group(), country_to], index=columns)
            else:
                df_tmp = pd.Series(
                    [o_num, num, data[1], -1,""], index=columns)
            
    except:
        pass

    driver.close()
    driver.quit()

def get_id( n):
    if n[0] == 'L':
        return '03011'
    elif n[:2] == 'EV':
        return '03011'
    elif len(n) == 12 and n[0] == '3':
        return '190094'
    elif n[:2] == 'YT':
        return '190008'
    elif len(n) == 12 and n[0] == '5':
        return '100040'
    # Another 4px IP is added here for the update on the 24th of May, TN starts with 5P
    elif len(n) == 13 and n[:2] == '5P':
        return '190094'
    elif len(n) == 20 and n[:2] == '00':
        return '190002'
    else:
        return ''


if __name__ == "__main__":
    main()
