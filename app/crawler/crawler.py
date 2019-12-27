import requests
import random
import json
import re
import time
from lxml.html import fromstring, tostring
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from app import app
from .signals import scraping_done


def cleanhtml(raw_html):
    """Utility to clean HTML Tag."""
    clean_re = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\\n')
    clean_string = re.sub(clean_re, '', raw_html)

    white_space_re = re.compile('\s{2,}')
    clean_string = re.sub(white_space_re, '', clean_string)

    return clean_string


class Crawler:
    """Generic Base Crawler Class"""

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    ]

    def __init__(self, method='GET', headers=None):
        # Take a random User-Agent so that not blocked by Google or other search engines

        self.selected_useragent = random.choice(self.user_agents)
        app.logger.info(self.selected_useragent)
        self.method = method


class GoogleCrawler(Crawler):
    """Google Crawler Class"""
    url = 'https://www.google.com/search'

    def scrape(self, keyword, query_id):
        if not keyword:
            raise ValueError('Keyword is not provided!')
        if not query_id:
            raise ValueError('Query id is not provided!')

        start_time = time.time()

        s = requests.Session()

        # Retrying 7 times if Google returned timeout / network issue for better reliability
        retries = Retry(total=7,
                        backoff_factor=2,
                        status_forcelist=[ 500, 502, 503, 504 ])

        s.mount('https://', HTTPAdapter(max_retries=retries))

        if self.method == 'GET':
            params = { 'q': keyword }

            app.logger.info('Begin Google Scraping')
            response = s.get(self.url, params=params, headers={ 'User-Agent': self.selected_useragent})

            return self.parse(html=response.content, keyword=keyword,
                              http_status_code=response.status_code,
                              query_id=query_id, start_time=start_time)

    def parse(self, **kwargs):
        try:
            html = kwargs['html'].decode("utf-8")
            resp_xpath = fromstring(html)

            resp_container = {
                'query_id': kwargs['query_id'],
                'keyword': kwargs['keyword'],
                'results': [],
                'html': kwargs['html'],
                'http_status_code': kwargs['http_status_code']
            }

            for r in resp_xpath.xpath('//div[@class="rc"]'):
                title = r.xpath('div[@class="r"]/a/h3')
                a = r.xpath('div[@class="r"]/a/@href')
                paragraph = r.xpath('div[@class="s"]/div/span[@class="st"]')

                resp_container['status'] = 'ok'
                resp_container['results'].append({
                    'title': cleanhtml(tostring(title[0]).decode()),
                    'link': a[0],
                    'description': cleanhtml(tostring(paragraph[0]).decode())
                })

            end_time = time.time()
            time_taken= (end_time - kwargs['start_time']) * 1000

            resp_container['time_taken'] = time_taken

            print('done')
            scraping_done.send(self, search_engine='google', response=resp_container)

            return resp_container
        except Exception as e:
            app.logger.error('Scraping error {GoogleCrawler}: ' + e)
            return {
                'status': 'error',
                'search_engine': 'wikipedia',
                'message': 'Error occurred. Please check your log',
                'error_message': str(e)
            }



class DuckduckGoCrawler(Crawler):
    """DuckduckGo Crawler Class"""

    url = 'https://duckduckgo.com/html/'


    def scrape(self, keyword, query_id):
        if not keyword:
            raise ValueError('Keyword is not provided!')
        if not query_id:
            raise ValueError('Query id is not provided!')

        start_time = time.time()
        s = requests.Session()

        # Retrying 7 times if Google returned timeout / network issue for better reliability
        retries = Retry(total=7,
                        backoff_factor=2,
                        status_forcelist=[ 500, 502, 503, 504 ])

        s.mount('https://', HTTPAdapter(max_retries=retries))

        if self.method == 'GET':
            params = { 'q': keyword }
            response = s.get(self.url, params=params, headers={ 'User-Agent': self.selected_useragent})

            return self.parse(html=response.content, keyword=keyword,
                              http_status_code=response.status_code,
                              query_id=query_id, start_time=start_time)

    def parse(self, **kwargs):
        try:
            html = kwargs['html'].decode("utf-8")
            resp_xpath = fromstring(html)

            resp_container = {
                'query_id': kwargs['query_id'],
                'keyword': kwargs['keyword'],
                'results': [],
                'html': kwargs['html'],
                'http_status_code': kwargs['http_status_code']
            }

            for r in resp_xpath.xpath('//div[contains(@class, "result__body")]'):
                title = r.xpath('h2[@class="result__title"]/a')

                link = r.xpath('h2[@class="result__title"]/a/@href')
                description = r.xpath('a[@class="result__snippet"]')

                resp_container['results'].append({
                    'title': cleanhtml(tostring(title[0]).decode()),
                    'link': link[0],
                    'description': cleanhtml(tostring(description[0]).decode())
                })

            end_time = time.time()
            time_taken= (end_time - kwargs['start_time']) * 1000

            resp_container['time_taken'] = time_taken

            scraping_done.send(self, search_engine='duck2go', response=resp_container)

            return resp_container
        except Exception as e:
            app.logger.error('Scraping error {DuckduckgoCrawler}: ' + e)

            return {
                'status': 'error',
                'search_engine': 'duck2go',
                'message': 'Error occurred. Please check your log',
                'error_message': str(e)
            }


class WikipediaCrawler(Crawler):
    """Wikipedia Crawler Class"""

    url = 'https://en.wikipedia.org/w/index.php'

    def scrape(self, keyword, query_id):
        if not keyword:
            raise ValueError('Keyword is not provided!')
        if not query_id:
            raise ValueError('Query id is not provided!')

        start_time = time.time()

        if keyword is None:
            raise Exception('Keyword is not defined')

        s = requests.Session()

        # Retrying 7 times if Google returned timeout / network issue for better reliability
        retries = Retry(total=7,
                        backoff_factor=2,
                        status_forcelist=[ 500, 502, 503, 504 ])

        s.mount('https://', HTTPAdapter(max_retries=retries))


        if self.method == 'GET':
            # Wikipedia has extra params that need to be added on
            params = {
                'sort': 'relevance',
                'search': keyword,
                'title': 'Special:Search',
                'profile': 'advanced',
                'fulltext': 1,
                'ns0': 1
            }

            response = s.get(self.url, params=params, headers={'User-Agent': self.selected_useragent})

            return self.parse(html=response.content, keyword=keyword,
                              http_status_code=response.status_code,
                              query_id=query_id, start_time=start_time)


    def parse(self, **kwargs):
        try:
            html = kwargs['html'].decode("utf-8")
            resp_xpath = fromstring(html)

            resp_container = {
                'query_id': kwargs['query_id'],
                'keyword': kwargs['keyword'],
                'results': [],
                'html': kwargs['html'],
                'http_status_code': kwargs['http_status_code']
            }

            for r in resp_xpath.xpath('//li[contains(@class, "mw-search-result")]'):
                title = r.xpath('div[@class="mw-search-result-heading"]/a')
                link = r.xpath('div[@class="mw-search-result-heading"]/a/@href')
                description = r.xpath('div[@class="searchresult"]')

                resp_container['results'].append({
                    'title': cleanhtml(tostring(title[0]).decode()),
                    'link': 'https://en.wikiepedia.org{}'.format(link[0]),
                    'description': cleanhtml(tostring(description[0]).decode())
                })

            end_time = time.time()
            time_taken= (end_time - kwargs['start_time']) * 1000

            resp_container['time_taken'] = time_taken

            scraping_done.send(self, search_engine='wikipedia', response=resp_container)

            return resp_container
        except Exception as e:
            app.logger.error('Scraping error {WikipediaCrawler}: ' + e)

            return {
                'status': 'error',
                'search_engine': 'wikipedia',
                'message': 'Error occurred. Please check your log',
                'error_message': str(e)
            }
