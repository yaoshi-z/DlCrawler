# -*- coding: utf-8 -*-

"""
- 模板名称
    模板编号: 0701
    模板名称: 全国公共资源_搜索_关键字公示信息爬虫模板
--------------------
功能：提取指定搜索关键词的公示信息（
    批次号,关键词,标题,标题url,发布时间,省份,
    来源平台,业务类型,信息类型
）
使用：爬取前需在ggzy_search_keywords_config.py中设置推荐的配置参数
备注: 自动化工具_无登录_点击翻页
"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import GgzySearchKeywordsItem
from DlCrawler.configs.ggzy.ggzy_search_keywords_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import datetime
import asyncio

class GgzySearchKeywordsSpider(scrapy.Spider):
    name = "ggzy_search_keywords"
    allowed_domains = ["ggzy.gov.cn"]
    keywords = CUSTOM_SETTINGS['KEYWORDS']  # 搜索关键词
    start_date = CUSTOM_SETTINGS['START_DATE'] # 开始日期
    encode_date = CUSTOM_SETTINGS['END_DATE'] # 结束日期
    current_page = 1  # 当前页码
    start_urls = [
                f"https://deal.ggzy.gov.cn/ds/deal/dealList.jsp"
                ]
    
    # 加载配置参数
    custom_settings = CUSTOM_SETTINGS

    # 最大获取数量
    max_count = CUSTOM_SETTINGS['MAXCOUNT']
    success_count = 0

    
    retries = 0

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    def start_requests(self):
        target_url = self.start_urls[0]
        yield scrapy.Request(
        target_url,
        meta={
            "playwright": True,  # 启用Playwright处理  
            "playwright_include_page": True # 包含页面对象
        },
        callback=self.parse
    )

    async def parse(self, response):
        page = response.meta['playwright_page']
        if "current_page" in response.meta:
            self.current_page = response.meta["current_page"]
        try:    
            await page.wait_for_selector("div.publicont",timeout=60000)
        except Exception as e:
            self.logger.info(f"等待元素超时,可能网络不稳,程序即将关闭,稍候重试：{e}")
            await page.close()
            return

        # 人类形为模拟
        await self.random_scroll(page)  # 分段滚动
        await self.random_sleep(page)  # 随机停顿

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容

        # 初始页面解析
        async for item in self.parse_page_content(page):
            yield item

        # 分页循环
        while True:
            # 检查终止条件
            if self.success_count >= self.max_count:
                self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                await page.close()
                return
            
            try:
                # 定位下一页按钮
                next_button = page.locator("a:has-text('下一页')")
                
                # 检查是否可点击
                if await next_button.is_disabled():
                    self.logger.info("已到达最后一页，结束爬取")
                    await page.close()
                    return
                
                # 人类行为模拟
                await self.random_sleep(page)
                await self.random_scroll(page)
                
                # 点击下一页
                await next_button.click()
                
                # 等待新内容加载
                try:
                    await page.wait_for_selector("div.publicont", state="attached", timeout=30000)
                except Exception as e:
                    self.logger.warning(f"等待新页面内容超时: {e}")
                
                # 更新页码
                self.current_page += 1
                self.logger.info(f"成功翻页到第{self.current_page}页")
                
                # 处理新页面内容
                async for item in self.parse_page_content(page):
                    yield item
                
            except Exception as e:
                self.logger.error(f"分页失败: {e}")
                if not page.is_closed():
                    await page.close()
                return
        
    async def parse_page_content(self, page):
        """解析页面内容"""
        html = await page.content()
        selector = scrapy.Selector(text=html)

        # 临时调试,需要时自行取消注释
        try:
            debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
            debug_dir.mkdir(parents=True, exist_ok=True)
            with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            self.logger.info(f"保存文件失败：{e}")
        
        cards_selector = '//div[@class="publicont"]'
        items_cards = selector.xpath(cards_selector)

        for item_node in items_cards:
            item = GgzySearchKeywordsItem()
            
            # 提取字段
            item['keywords'] = self.keywords
            item['batch_id'] = self.now
            item['title'] = item_node.css('h4 a::text').get()
            item['title_url'] = item_node.css('h4 a::attr(href)').get()
            item['post_time'] = item_node.css('h4 span::text').get()
            
            spans_values = item_node.css('p.p_tw span.span_on::text').getall()
            if len(spans_values) > 0: item['province'] = spans_values[0] or ""
            if len(spans_values) > 1: item['source_platform'] = spans_values[1] or ""
            if len(spans_values) > 2: item['business_category'] = spans_values[2] or ""
            if len(spans_values) > 3: item['announcement_type'] = spans_values[3] or ""   
            if len(spans_values) > 4: item['industry'] = spans_values[4] or ""
            
            self.success_count += 1
            '''
            返回生成器对象
            注意:
            生成器对象本身必须要使用for循环迭代, 才能生成实际值!
            但在scrapy中有一个特殊机制:
            回调函数中使用生成器对象时, scrapy会自动迭代生成器对象并将yield的项目送入item pipeline中;
            非回调函数中,则不会自动迭代,其它函数调用时,必须使用async for item in func()语句来进行迭代处理
            '''
            yield item  
    async def random_sleep(self,page):
        """自然正态分布式休眠，增强反爬"""
        # 以2.5秒为中心，标准差0.5秒，范围限制在1.5-4秒
        sleep_time = random.gauss(2.5, 0.5)  
        sleep_time = max(1.5, min(4.0, sleep_time))  
        await page.wait_for_timeout(int(sleep_time * 1000))

    async def random_scroll(self, page):
        """分段滚动页面，增加随机偏移"""
        scroll_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        
        segments = random.randint(3, 5)  # 分3-5段滚动
        for i in range(segments):
            # 计算基础滚动位置
            base_scroll = (scroll_height / segments) * (i + 1)
            # 添加垂直抖动（±1/4视口高度）
            jitter = random.uniform(-viewport_height/4, viewport_height/4)
            scroll_to = max(0, base_scroll + jitter)  # 确保不为负
            
            await page.evaluate(f"window.scrollTo(0, {scroll_to})")
            await asyncio.sleep(random.uniform(0.5, 1.5))  # 每段间隔0.5-1.5秒
