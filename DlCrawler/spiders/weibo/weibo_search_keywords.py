import scrapy


class WeiboSearchKeywordsSpider(scrapy.Spider):
    name = "weibo_search_keywords"
    allowed_domains = ["m.weibo.cn"]
    start_urls = ["https://m.weibo.cn"]

    def parse(self, response):
        pass
