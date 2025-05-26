import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BaiduTiebaTopicItem

class BaiduTiebaTopicSpider(scrapy.Spider):
    name = "baidu_tieba_topic"
    allowed_domains = ["baidu.com"]
    topic_name = "郑州地铁"
    encode_topic_name = quote(topic_name)
    start_urls = [f"https://tieba.baidu.com/f?kw={encode_topic_name}&ie=utf-8"]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 5,
        "MONGODB_DATABASE": "baidu",         # 数据库名
        "MONGODB_COLLECTION": "topic_list",  # 集合名
        'DOWNLOAD_HANDLERS':  {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },

        'PLAYWRIGHT_BROWSER_TYPE': "chromium",
        'PLAYWRIGHT_LAUNCH_OPTIONS':  {
            "headless": False,  # 关键参数！关闭无头模式显示浏览器窗口
            "slow_mo": 1000,    # 将每个操作放慢1秒方便观察
            "devtools": True    # 自动打开开发者工具面板
        },

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler': 543,
        },
        'ITEM_PIPELINES': {
            'DlCrawler.pipelines.MongoDBPipeline': 300
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "span.u_username_title"),
                    ],
                    "playwright_include_page": True
                }
            )

    def parse(self, response):
        # 临时调试代码
        # with open("debug_files/baidu_tieba_topic.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        # 提取吧名（从<title>标签）
        bar_name = unquote(response.xpath('//title/text()').get().split('-')[0].strip())
        
        for post in response.css('div.threadlist_detail:not(.ylh-ad-container)'):  # 增加广告过滤
            item = BaiduTiebaTopicItem()
            
            # 使用规范字段赋值方式
            item['bar_name'] = bar_name
            item['title'] = post.css('a.j_th_tit::text').get('').strip()
            item['content'] = post.css('div.threadlist_abs::text').get('').strip()
            item['author'] = post.css('span.tb_icon_author a.frs-author-name::text').get('').strip()
            item['reply_count'] = int(post.css('span.threadlist_rep_num::text').get('0'))
            item['last_reply_date'] = self.parse_date(
                post.css('span.threadlist_reply_date::text, span.is_show_create_time::text').get()
            )
            
            yield item

    def parse_date(self, raw_date):
        """处理不同日期格式"""
        current_year = datetime.now().year
        
        if not raw_date:
            return datetime.now().strftime("%Y-%m-%d")
        
        raw_date = raw_date.strip()
        
        # 处理完整日期格式（如2024-09）
        if '-' in raw_date and len(raw_date) > 5:
            return datetime.strptime(raw_date, "%Y-%m-%d").date()
        
        # 处理缺失年份的格式（如5-24）
        if '-' in raw_date:
            return datetime.strptime(f"{current_year}-{raw_date}", "%Y-%m-%d").date()
        
        # 处理纯月份格式（如5月）
        if '月' in raw_date:
            return datetime.strptime(f"{current_year}-{raw_date.replace('月','')}", "%Y-%m").date()
        
        return datetime.now().strftime("%Y-%m-%d")