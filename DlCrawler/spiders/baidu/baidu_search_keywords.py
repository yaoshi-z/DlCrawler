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
from DlCrawler.items import BaiduSearchKeywordsItem
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
    success_count = 0

    current_page = 1  # 当前页码

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.c-container[id]", timeout=10000),
                        PageMethod("wait_for_timeout",random.randint(1000,3000)),#子列表加载完成
                    ],
                    "playwright_include_page": True # 包含页面对象
                }
            )

    async def parse(self, response):
        page = response.meta['playwright_page']
       
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
        await page.wait_for_timeout(random.randint(2000, 5000))  # 随机延迟

        html = await page.content()
        selector = scrapy.Selector(text=html)

        #  # 临时调试,需要时自行取消注释
        try:
            debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
            debug_dir.mkdir(parents=True, exist_ok=True)
            with open(f"{debug_dir}/{self.name}_{self.current_page}.html", "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            self.logger.info(f"保存文件失败：{e}")

        # 终止条件1: 非首页无div.c-container[id]元素 
        item_nodes = selector.css('div.c-container[id]')
        if not item_nodes:
            # 非首页无结果时终止
            if self.current_page > 1:
                self.logger.info(f"第{self.current_page}页无有效数据，终止爬取")
                await page.close()
                return


        # 核心解析逻辑
        for item_node in selector.css('div.c-container[id]'):
            item = BaiduSearchKeywordsItem()
            
            # 搜索关键词
            item['keyword'] = self.keywords  

            # 批次ID
            item['batch_id'] = self.now  
            
            # 标题提取
            item['title'] = ''.join(
                item_node.css('h3 a *::text').getall()
            ).strip()
            
            # 链接处理
            item['bd_url'] = item_node.css('h3 a::attr(href)').get() or '' # 页面的百度跳转链接
            item['raw_url'] = item_node.css('::attr(mu)').get() or '' # 页面的原始链接
            
            
            # 广告检测
            item['is_ad'] = 1 if 'result-op' in item_node.css('::attr(class)').get(default='') else 0
            
            # 摘要提取
            summary_texts = []
            for text in item_node.css('::text').getall():
                clean_text = text.strip()
                if (clean_text 
                    and not clean_text.startswith('<!--') 
                    and len(clean_text) > 5
                    and clean_text not in ['百度首页', '设置', '登录']):
                    summary_texts.append(clean_text)

            item['summary'] = '...'.join(summary_texts[:20])  # 限制20个有效段落

            self.success_count += 1
            yield item

        # 终止条件2: 达到最大条目数则停止
            if self.success_count >= self.max_count:
                self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                await page.close()
                return
                
        await self.random_sleep(page)  # 随机休眠

        # 构造下一页请求
        self.current_page += 1
        next_url = f"https://www.baidu.com/s?wd={self.encode_keywords}&pn={(self.current_page-1)*10}"
        yield scrapy.Request(
            url=next_url,
            meta={"playwright": True,
                  "playwright_include_page": True,
                  "playwright_page": page,
            },
            callback=self.parse,
        )
    async def random_sleep(self,page):
        """随机休眠，避免被封禁"""
        sleep_time = random.uniform(1, 3)
        await page.wait_for_timeout(int(sleep_time * 1000))
                
        

