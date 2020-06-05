#attempts to click the translation button on 17track  
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


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.csvname = ""

    def create_widgets(self):
        self.button1 = tk.Button(self, text="select")
        self.button1.pack()
        self.button1.bind("<1>", self.csvselect)
        self.text = tk.StringVar()
        self.text.set("select csv")
        self.label1 = tk.Label(self, textvariable=self.text)
        self.label1.pack()
        self.button2 = tk.Button(self, text="start")
        self.button2.pack()
        self.button2.bind("<1>", self.start)
        self.p_bar = ttk.Progressbar(
            self, orient='horizontal', length=200, mode='determinate')
        self.p_bar.pack()
        self.text2 = tk.StringVar()
        self.text2.set("")
        self.label2 = tk.Label(self, textvariable=self.text2)
        self.label2.pack()
        self.text3 = tk.StringVar()
        self.text3.set("")
        self.label3 = tk.Label(self, textvariable=self.text3)
        self.label3.pack()

    def csvselect(self, event):
        filename = filedialog.askopenfilename()
        if filename != "":
            self.csvname = filename
            self.text.set(filename)

    def start(self, event):
        if self.csvname == "":
            self.text2.set("no csv file selected")
        else:
            self.main()

    def main(self):
        path_csv = self.csvname

        df = pd.read_csv(path_csv)
        df.dropna(inplace=True)
        o_nums = df["Order Number"]

        columns = ["order number", "tracking number", "status", "days in transit", "country", "Current"]
        df_new = pd.DataFrame(columns=columns)

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--user-agent=hoge')
        driver = webdriver.Chrome(options=options)

        is_finish = False
        size = len(o_nums)
        self.p_bar.configure(maximum=size)
        time_s = time.time()
        avg_time = 0
        cnt = 0
        while not is_finish:
            new_o_nums = []
            for i, o_num in enumerate(o_nums):
                nums = df[df["Order Number"] == o_num]
                nums = str(nums.iloc[0]["Tracking Numbers"])

                nums = list(set(nums.split(",")))

                for num in nums:
                    start = time.time()
                    c_id = self.get_id(num)
                    c_id = "&fc={}".format(c_id) if c_id != '' else ''
                    url = "https://t.17track.net/en#nums={}{}".format(
                        num, c_id)
                    driver.get(url)

                    time.sleep(2)
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "yqcr-ps")))
                    try:
                        data = driver.find_element_by_class_name("yqcr-ps")
                        data = data.text.split('\n')
                        if "Tracking" in data or "" in data:
                            print("kita!")
                            new_o_nums.append(o_num)
                            now = time.time()-start
                            avg_time = round((avg_time*cnt+now)/(cnt+1))
                        else:
                            print("delivered")
                            if 'Delivered' in data[1]:
                                country_to = driver.find_element_by_xpath('//*[@id="tn-{}"]/div[1]/div[2]/div[3]'.format(num)).text
                                current = ""

                                print(country_to)
                                print(current)
                                df_tmp = pd.Series(
                                    [o_num, num, 'Delivered', re.search(r'\d+', data[1]).group(), country_to, current], index=columns)
                            else:
                                print("in Transit")
                                country_to = driver.find_element_by_xpath('//*[@id="tn-{}"]/div[1]/div[2]/div[3]'.format(num)).text
                                #current =    driver.find_element_by_xpath('//*[@id="tn-{}"]/div[1]/div[3]/p/span'.format(num)).text

                                #Can I please click a button to make it in English?? Please???
                                translate = driver.find_element_by_xpath('//*[@id="tn-{}"]/div[2]/div[2]/div[1]/button[2]'.format(num))[0]
                                translate.click()
                                selectEn = driver.find_element_by_xpath('//*[@id="tn-{}"]/div[2]/div[2]/div[2]/div/button'.format(num))[0]
                                selectEn.click()

                                current =    driver.find_element_by_xpath('//*[@id="tn-{}"]/div[1]/div[3]/p/span'.format(num)).text

                                df_tmp = pd.Series(
                                    [o_num, num, data[1], -1, country_to, current], index=columns)

                            df_new = df_new.append(df_tmp, ignore_index=True)

                            tmp_time = round(time.time() - time_s)
                            now = time.time()-start
                            avg_time = round((avg_time*cnt+now)/(cnt+1))
                            avg_time_ = avg_time*(size-(cnt+1))
                            cnt += 1
                            self.text2.set(data)
                            self.text3.set(
                                "{:.2}s/it  {:02}:{:02}:{:02}/{:02}:{:02}:{:02} {}/{}".format(now, tmp_time//3600, (tmp_time-(tmp_time//3600)*3600)//60, tmp_time-((tmp_time-(tmp_time//3600)*3600)//60)*60, avg_time_//3600, (avg_time_-(avg_time_//3600)*3600)//60, avg_time_-((avg_time_-avg_time_//3600*3600+(avg_time_//3600)*3600)//60)*60, cnt, size))

                            self.p_bar.step(1)
                            self.p_bar.update()
                    except:
                        print("This one takes time ＿φ(￣ー￣ )")
                        new_o_nums.append(o_num)
                        now = time.time()-start
                        avg_time = round((avg_time*cnt+now)/(cnt+1))

            o_nums = new_o_nums
            is_finish = len(o_nums) ==0
        df_new.sort_values('order number', ascending=False)
        # df_new = df_new.replace([-1], np.nan)
        df_new.to_csv("sample.csv")
        self.text2.set("finished! the result is saved as sample.csv")
        driver.close()
        driver.quit()

    def get_id(self, n):
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
        # SunYou shipping IP is added that starts with SY-- 4th of June
        elif len(n) == 13 and n[:2] == "SY":
            return '190072'
        elif len(n) == 20 and n[:2] == '00':
            return '190002'
        else:
            return ''


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x400")
    app = Application(master=root)
    app.mainloop()
