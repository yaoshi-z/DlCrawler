import scrapy
from DlCrawler.items import DlcrawlerItem


class QuoteSpider(scrapy.Spider):
    name = "quote"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    # spider(quote)爬虫配置
    custom_settings = {
        "MONGODB_DATABASE": "scrapytutorial",   
        "MONGODB_COLLECTION": "quotes",  
        "ITEM_PIPELINES": {
            "DlCrawler.pipelines.MongoDBPipeline": 400
        }
    }

    def parse(self, response):
        quotes = response.css(".quote")
        for quote in quotes:
            item = DlcrawlerItem()
            item["text"] = quote.css(".text::text").get()
            item["author"] = quote.css(".author::text").get()
            item["tags"] = quote.css(".tag::text").getall()
            yield item
        
        next_page = response.css(".pager .next a::attr(href)").get()
        url = response.urljoin(next_page)
        if next_page:
            yield scrapy.Request(url, callback=self.parse)