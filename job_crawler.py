from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import psycopg2

from database_config import Database


def openPage():
    chromeBrowser = webdriver.Chrome()
    chromeBrowser.get("https://www.seek.com.au/")


# find value from html elements
def find_job_value(bs_title):
    result = ''
    for string in bs_title.stripped_strings:
        result += repr(string)
    # print(result)
    return result


def find_job_values(bs_job):
    meta = bs_job.find(attrs={"property": "og:url"})
    id_pattern = re.compile(r'\d+')
    job_id = re.findall(id_pattern, meta['content'])[0]
    job_values = {'job_id': job_id}
    bs_job_title = bs_job.find(attrs={"data-automation": "advertiser-name"})

    if bs_job_title is not None:
        company = bs_job_title.span.string
    else:
        company = 'Private Advertiser'

    job_values['company'] = company
    job_title = find_job_value(bs_job.find(attrs={"data-automation": "job-detail-title"}))
    job_values['job_title'] = job_title
    job_content = find_job_value(bs_job.find(attrs={"data-automation": "mobileTemplate"}))  # div.p
    if job_content is None:
        job_content = find_job_value(bs_job.find(attrs={"class": "templatetext"}))  # div.p
    job_values['content'] = job_content
    publish_date = find_job_value(bs_job.find(attrs={"data-automation": "job-detail-date"}))
    # job_salary = find_job_value(bs_job.find(attrs={"data-automation": "job-detail-date"}))
    job_values['publish_date'] = publish_date
    return job_values


def check_job_id_from_database(job_id, job_values):
    try:
        db = Database('db_config', 'dev', 'postgres')
        results = db.check_ad_is_exist(job_id)
        if len(results) == 0:
            job_data = [job_values]
            inserted_rows = db.persist_data_to_table('public.job', job_data)
            print('inserted ' + str(inserted_rows))
        else:
            return print("exist for job id " + str(job_id))
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)


def process_job(bs_job):
    meta = bs_job.find(attrs={"property": "og:url"})
    id_pattern = re.compile('\d+')
    job_id = re.findall(id_pattern, meta['content'])
    job_values = find_job_values(bs_job)
    return check_job_id_from_database(job_id[0], job_values)


def release_crawler(job_url):
    req = Request(job_url, None, {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 '
                      'Safari/537.36'})

    job_html = urlopen(req)
    bs_job = BeautifulSoup(job_html, features="lxml")
    process_job(bs_job)
    pass


def cal_total_pages_for_jobs(url):
    req = Request(url, None, {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 '
                      'Safari/537.36'})
    html = urlopen(req)
    bs_job = BeautifulSoup(html, features="lxml")
    total_value = bs_job.find(attrs={"data-automation": "totalJobsCount"}).string
    total_value = int(total_value.replace(',', ''))
    mod = (1, 0)[total_value % 20 == 0]
    page = int(total_value / 20) + mod
    return page


def openWebSite(url):
    req = Request(url, None, {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 '
                      'Safari/537.36'})
    html = urlopen(req)
    bs = BeautifulSoup(html, features="lxml")
    aList = bs.findAll(attrs={"data-automation": "jobTitle"})
    job_base_url = "https://www.seek.com.au"
    for a in aList:
        job_url = job_base_url + str(a['href'])
        print(str(job_url))
        release_crawler(job_url)


# openWebSite("https://www.seek.com.au/developer-jobs-in-information-communication-technology/in-All-Sydney-NSW")


def createUrlWithPageNumber(basUrl, pageNum):
    basUrl += str("?page=" + pageNum)
    openWebSite(basUrl)


def start_crawler():
    base_url = "https://www.seek.com.au/developer-jobs-in-information-communication-technology/in-All-Sydney-NSW"

    # page items = 20
    # total items = ??
    total = cal_total_pages_for_jobs(base_url)
    for i in range(9, total + 1):
        createUrlWithPageNumber(base_url, str(i))
    print("##########finished########")


start_crawler()
