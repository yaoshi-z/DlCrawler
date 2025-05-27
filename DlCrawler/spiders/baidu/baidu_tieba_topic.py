import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BaiduTiebaTopicItem
from configs.baidu.baidu_tieba_topic_config import CUSTOM_SETTINGS, MAXPAGE,TOPIC_NAME

class BaiduTiebaTopicSpider(scrapy.Spider):
    name = "baidu_tieba_topic"
    allowed_domains = ["baidu.com"]
    topic_name = TOPIC_NAME  # 贴吧主题名称
    encode_topic_name = quote(topic_name)
    start_urls = [f"https://tieba.baidu.com/f?kw={encode_topic_name}&ie=utf-8"]

    # 最大翻页数
    max_page = MAXPAGE
    current_page = 0

    custom_settings = CUSTOM_SETTINGS

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
        with open("debug_files/baidu_tieba_topic.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # 提取吧名（从<title>标签）
        bar_name = unquote(response.xpath('//title/text()').get().split('-')[0].strip())
        
        for post in response.css('div.t_con.cleafix'):  # 增加广告过滤
            item = BaiduTiebaTopicItem()
            
            # 使用规范字段赋值方式
            item['bar_name'] = bar_name
            item['title'] = post.css('div.threadlist_title a.j_th_tit::text').get('').strip()
            item['content'] = post.css('div.threadlist_text div.threadlist_abs::text').get('').strip()
            item['author'] = post.css('div.threadlist_author span.tb_icon_author a.frs-author-name::text').get('').strip()
            item['reply_count'] = int(post.css('div.col2_left span.threadlist_rep_num::text').get('0'))
            yield item
