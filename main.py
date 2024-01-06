from typing import Any
from bs4 import BeautifulSoup as bs
from datetime import date
import requests
import time
import boto3

class Scraper:

    def __init__(self, done, page):
        self.request = done
        self.page = page
        self.url = self.request + str(self.page)

    def __call__(self):
        jobs = []

        request = requests.get(self.url)
        soup = bs(request.content, 'html.parser')

        for d in soup.find_all('a', {'class': 'anchorClass_aqdsolh'}):
            title = d.find_all('h2', {'data-test': 'text-jobTitle'})
            t_list = []
            for t in title:
                t = t.text.strip()
                t_list.append(t)
            salary = d.find_all('span', {'class': 'boldText_b1wsb650'})
            s_list = []
            for s in salary:
                s = s.text.strip()
                s_list.append(s)
                s_1_min = s_list[0].split('–')[0]
                s_1_max = s_list[0].split('–')[1]
                try:
                    s_2_min = s_list[1].split('–')[0]
                    s_2_max = s_list[1].split('–')[1]
                except:
                    s_2_min = 0
                    s_2_max = 0
            contract_type = d.find_all('span', {'class': 'mainText_m15w0023'})
            c_list = []
            for c in contract_type:
                c = c.text.strip()
                c_list.append(c)
                c1 = c_list[0].strip(" zł()")
                clast = c_list[-1].strip(" zł()")
            jobs.append([t_list, [s_1_min, s_1_max, s_2_min, s_2_max], [c1, clast]])
        return jobs

today = date.today()
d = today.strftime("Y%m%d")

add_divs = []
with open('jobs'+d+'.txt', 'w', encoding="utf-8") as f:
    for page in range(1, 20):
        scrape = Scraper(done = 'https://theprotocol.it/filtry/1;s?pageNumber=', page = page)
        item = scrape()
        add_divs.append(item)
        f.write("%s\n" % item)
f.close()

s3 = boto3.resource('s3')
s3.Bucket("hamlet07-test-001").put_object(Key="jobs_"+d+".txt", Body=str(add_divs))