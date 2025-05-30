import scrapy


class WeiboSearchKeywordsSpider(scrapy.Spider):
    name = "weibo_search_keywords"
    allowed_domains = ["s.weibo.com"]
    start_urls = ["https://s.weibo.com"]

    def parse(self, response):
        pass
