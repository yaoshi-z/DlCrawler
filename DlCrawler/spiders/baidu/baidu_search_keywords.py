# -*- coding: utf-8 -*-
"""
- 模板名称
    模板编号: 1002
    模板名称: 百度_搜索_关键词爬虫模板
--------------------
功能：提取指定搜索关键词的帖子列表信息（标题、内容、作者、回复数等）
使用：爬取前需在baidu_search_keywords_config.py中设置推荐的配置参数
"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BaiduTiebaTopicItem
from DlCrawler.configs.baidu.baidu_search_keywords_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import datetime

class BaiduSearchKeywordsSpider(scrapy.Spider):
    name = "baidu_search_keywords"
    allowed_domains = ["baidu.com"]
    keywords = CUSTOM_SETTINGS['KEYWORDS']  # 搜索关键词
    encode_keywords = quote(keywords)
    start_urls = [f"https://www.baidu.com/s?wd={encode_keywords}"]

    # 加载配置参数
    custom_settings = CUSTOM_SETTINGS

    # 最大获取数量
    max_count = CUSTOM_SETTINGS['MAXCOUNT']
    current_count = 0

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    # "playwright_page_methods": [
                    #     PageMethod("wait_for_selector", "div.t_con.cleafix", timeout=10000),
                    #     PageMethod("wait_for_timeout",random.randint(1000,3000)),#子列表加载完成
                    # ],
                    "playwright_include_page": True # 包含页面对象
                }
            )

    async def parse(self, response):
        page = response.meta['playwright_page']
        html = await page.content()
        selector = scrapy.Selector(text=html)
       
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
        await page.wait_for_timeout(random.randint(2000, 5000))  # 随机延迟
        
        #  # 临时调试,需要时自行取消注释
        try:
            debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
            debug_dir.mkdir(parents=True, exist_ok=True)
            with open(f"{debug_dir}/{self.name}_{self.now}.html", "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            self.logger.info(f"保存文件失败：{e}")

        # 核心解析逻辑
        for item_node in selector.css('div.toplist1-tr_1MWDu'):
            item = {}
            
            # 提取标题
            item['title'] = item_node.css('a.c-font-medium.c-color-t::text').get(default='').strip()
            
            # 提取URL
            item['url'] = item_node.css('a.c-font-medium.c-color-t::attr(href)').get(default='')
            
            # 提取排名
            item['rank'] = item_node.css('span.c-index-single::text').get(default='').strip()
            
            # 提取热点标签（热/新）
            hot_tag = item_node.css('span.c-text-hot::text').get()
            new_tag = item_node.css('span.c-text-new::text').get()
            item['tag'] = hot_tag or new_tag or ''
            
            # 解析data-click属性中的JSON数据
            data_click = item_node.css('a.c-font-medium::attr(data-click)').get(default='')
            if data_click:
                try:
                    # 解码并提取JSON部分
                    json_str = unquote(data_click).split('"clk_info":"')[1].split('"')[0]
                    item['metadata'] = json.loads(json_str.replace('\\"', '"'))
                except (IndexError, json.JSONDecodeError) as e:
                    self.logger.warning(f"解析data-click失败: {e}")
                    item['metadata'] = {}

            item['summary'] = item_node.css('span.summary-text_560AW::text').get(default='')
            item['source'] = item_node.css('a.cosc-title-a::text').get(default='')
            item['data_feedback'] = item_node.css('div::attr(data-feedback)').get(default='')
                    
            yield item  # 返回提取结果
          
        # 翻页逻辑
        # if self.current_count <= self.max_count:
        #     try:
        #         next_page_link = await page.locator("a.pagination-item.next").first.get_attribute("href")
        #         next_page_url = response.urljoin(next_page_link)
        
        #         await page.goto(next_page_url, wait_until="networkidle")     
                
        #         self.current_page += 1
        #         yield scrapy.Request(
        #             url=page.url,
        #             meta={
        #                 "playwright": True,
        #                 "playwright_include_page": True,
        #                 "playwright_page": page,
        #             },
        #             callback=self.parse,
        #             dont_filter=True
        #         )
        #     except Exception as e:
        #         # 检测验证码
        #         html = await page.content()
        #         if "验证码" in html or "auth" in page.url:
        #             self.logger.warning("检测到反爬验证，暂停爬取")
        #             page.wait_for_timeout(60_000)
        #         else:
        #             self.logger.error(f"翻页失败: {e}")
                
        

