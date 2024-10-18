import logging
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy_playwright.page import PageMethod

from .proxy import get_proxy
from ..items import LeagueItem

class LeaguesSpider(CrawlSpider):
    name = 'leagues'
    allowed_domains = ['footballant.cn', 'footballant.com']
    start_urls = [
        'https://www.footballant.cn/football-data/league/36',
    ]

    def __init__(self, *args, **kwargs):
        super(LeaguesSpider, self).__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)
        self.proxy = get_proxy()

    def start_requests(self):
        for url in self.start_urls:
            self._logger.info('Visit %s', url)
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', 'body')
                    ],
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
            )

    async def parse(self, response):
        resp = response.text
        # Replace specified HTML comments with spaces
        resp = resp.replace('<!--]-->', ' ').replace('<!--[-->', ' ').replace('<!---->', ' ')
        # self._logger.info('############\n #################\n Modified response text: %s\n #################\n #################', resp)
        # Create a new HtmlResponse object with the modified text
        response = scrapy.http.HtmlResponse(url=response.url, body=resp, encoding='utf-8')
        # self._logger.info('Parsing page content: %s', response.text)

        try:
            hot_leagues_root_selector = response.xpath('//div[@class="container"]/div/div[@class="el-col el-col-24 el-col-md-6 is-guttered col1 hidden-sm-and-down"]/div/div[@class="hidden-sm-and-down"]/div')
            self._logger.info('############## Hot leagues root selector: %s', hot_leagues_root_selector)
            hot_leagues_selector = hot_leagues_root_selector[1]
            self._logger.info('############## Hot leagues selector: %s', hot_leagues_selector)
            hot_leagues_info = hot_leagues_selector.xpath('div/div')[1]
            self._logger.info('############## Hot leagues info: %s', hot_leagues_info)
            hot_leagues = hot_leagues_info.xpath('ul/li')
            self._logger.info('############## Hot leagues final\n: %s\n  #################', hot_leagues)
        except Exception as e:
            self._logger.error('############## Failed to parse hot leagues: %s', e)
            return

        for league in hot_leagues[:5]:
            league_item = LeagueItem()
            league_item['name'] = league.xpath('./a/@title').extract_first()
            league_url = league.xpath('./a/@href').extract_first()
            league_item['id'] = int(league_url.split('/')[-1])
            img_url = league.xpath('./a/img/@src').extract_first()
            league_item['file_urls'] = [img_url.split('!')[0]]
            self._logger.info('Hot League resolved: %s', league_item)
            yield league_item