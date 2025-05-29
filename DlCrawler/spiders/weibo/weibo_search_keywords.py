import scrapy
import pathlib
from DlCrawler.configs.weibo.search_keywords_config import CUSTOM_SETTINGS, MAXCOUNT,KEYWORDS
from scrapy_playwright.page import PageMethod
import random

class WeiboSearchKeywordsSpider(scrapy.Spider):
    name = "weibo_search_keywords"
    allowed_domains = ["m.weibo.cn"]
    start_urls = ["https://m.weibo.cn"]
    current_page = 1
    custom_settings = CUSTOM_SETTINGS
    maxcount = MAXCOUNT
    keywords = KEYWORDS

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.pannelwrap", timeout=10000),
                        PageMethod("wait_for_timeout",random.randint(1000,3000)),#子列表加载完成
                    ],
                    "playwright_include_page": True # 包含页面对象
                }
            )

    async def parse(self, response):
        # 临时调试,需要时自行取消注释
        # try:
        #     debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
        #     debug_dir.mkdir(parents=True, exist_ok=True)
        #     with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
        #         f.write(response.text)
        # except Exception as e:
        #     self.logger.info(f"保存文件失败：{e}")
        page = response.meta['playwright_page']
        self.logger.info(f"当前页：{self.current_page}_{page}")