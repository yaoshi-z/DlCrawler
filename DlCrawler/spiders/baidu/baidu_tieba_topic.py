import scrapy
from urllib.parse import quote
import time
from scrapy_playwright.page import PageMethod

class BaiduTiebaTopicSpider(scrapy.Spider):
    name = "baidu_tieba_topic"
    allowed_domains = ["baidu.com"]
    topic_name = "郑州地铁"
    encode_topic_name = quote(topic_name)
    start_urls = [f"https://tieba.baidu.com/f?kw={encode_topic_name}&ie=utf-8"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", ".threadlist_title"),
                    ],
                    "playwright_include_page": True
                }
            )
    def parse(self, response):
        # 临时调试代码
        with open("debug_files/baidu_tieba_topic.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        # 解析页面内容
        # 这里可以根据实际需求进行解析