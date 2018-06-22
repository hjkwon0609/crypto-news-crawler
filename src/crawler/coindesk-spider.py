#
# This script can be executed like the command below.
#
# $ cat urls.txt | parallel --no-notice --jobs 3 -X -n 1 COINDESK_SPIDER_START_URL='{}' scrapy runspider -t jsonlines -o output/`date +%Y-%m-%d_%H:%M:%S`.jsonl coindesk-spider.py
#
import os
import re
import time
import dateutil.parser

import scrapy
import requests
from bs4 import BeautifulSoup

class CoindeskSpider(scrapy.Spider):
    name = 'coindesk-spider'
    start_urls = []

    """
    start_urls = [
        'https://www.coindesk.com/category/technology-news/bitcoin/page/1/',
        'https://www.coindesk.com/category/technology-news/ethereum-technology-news/page/1/',
        'https://www.coindesk.com/category/technology-news/other-public-protocols/page/1/',
        'https://www.coindesk.com/category/technology-news/distributed-ledger-technology/page/1/',
        'https://www.coindesk.com/category/technology-news/reviews-technology-news/page/1/',
        'https://www.coindesk.com/category/markets-news/investments/venture-capital/page/1/',
        'https://www.coindesk.com/category/markets-news/investments/initial-coin-offerings/page/1/',
        'https://www.coindesk.com/category/markets-news/markets-markets-news/markets-bitcoin/page/1/',
        'https://www.coindesk.com/category/markets-news/markets-markets-news/markets-ethereum/page/1/',
        'https://www.coindesk.com/category/markets-news/markets-markets-news/markets-exchanges/page/1/',
        'https://www.coindesk.com/category/markets-news/markets-markets-news/markets-news-other-public-protocols/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/payments/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/capital-markets/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/banking/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/insurance/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/supply-chain/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/security/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/identity/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/healthcare/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/energy/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/internet-of-things/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/uses-cases-verticals-merchants/page/1/',
        'https://www.coindesk.com/category/business-news/use-cases-verticals/startups/page/1/',
        'https://www.coindesk.com/category/business-news/legal/regulation-legal/page/1/',
        'https://www.coindesk.com/category/business-news/legal/central-banking/page/1/',
        'https://www.coindesk.com/category/business-news/legal/tax/page/1/',
        'https://www.coindesk.com/category/business-news/legal/crime/page/1/',
        'https://www.coindesk.com/category/business-news/legal/us-canada/page/1/',
        'https://www.coindesk.com/category/business-news/legal/asia-pacific/page/1/',
        'https://www.coindesk.com/category/business-news/legal/europe/page/1/',
    ]
    """

    def __init__(self):
        if 'COINDESK_SPIDER_START_URL' not in os.environ:
            raise Exception('COINDESK_SPIDER_START_URL not defined!')
        self.start_urls.append(os.environ['COINDESK_SPIDER_START_URL'])

    def _extract_content(self, url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text)
        content = soup.select('div.article-content-container')[0].text
        return content

    def parse(self, response):
        soup = BeautifulSoup(response.text)

        ts_oldest = time.time()

        for post in soup.select('div.post-info'):
            title = post.select('h3 > a')[0]
            title_text = title.text
            title_link = title['href']
            content = self._extract_content(title_link)

            datetime_str = post.findChild('time')['datetime']
            dt = dateutil.parser.parse(datetime_str)
            ts = int(dt.strftime('%s'))
            ts_oldest = min(ts_oldest, ts)

            yield {'url': title_link, 'title': title_text, 'date': datetime_str, 'content': content}

        #if time.time() - ts_oldest < 60 * 60 * 3:  # 3 hours ago
        if time.time() - ts_oldest < 60 * 60 * 24 * 30:  # 1 month ago

            matched = re.match('.+/page/([0-9]+)/', response.url)
            curr_page = matched.group(1)
            next_page = str(int(curr_page) + 1)

            url = response.url.replace(curr_page, next_page)
            yield scrapy.Request(url=url, callback=self.parse)

            #for next_page in response.css('div.prev-post > a'):
            #    yield response.follow(next_page, self.parse)
