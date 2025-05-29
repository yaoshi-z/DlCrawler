import scrapy
import pathlib
from DlCrawler.configs.weibo.search_keywords_config import CUSTOM_SETTINGS, MAXCOUNT,KEYWORDS

class WeiboSearchKeywordsSpider(scrapy.Spider):
    name = "weibo_search_keywords"
    allowed_domains = ["m.weibo.cn"]
    start_urls = ["https://m.weibo.cn"]
    current_page = 1
    custom_settings = CUSTOM_SETTINGS
    maxcount = MAXCOUNT
    keywords = KEYWORDS

    def parse(self, response):
        
        # 临时调试,需要时自行取消注释
        try:
            debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
            debug_dir.mkdir(parents=True, exist_ok=True)
            with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
        except Exception as e:
            self.logger.info(f"保存文件失败：{e}")