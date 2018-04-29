#created by licw

import datetime
import pandas as pd
import time

def get_daylist(begin_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d',time.localtime(time.time())), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=3)
    return date_list

def get_url_data(url):
    try:
        data = pd.read_html(url)
    except:
        data = []
    return data
