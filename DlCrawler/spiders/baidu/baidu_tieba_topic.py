# -*- coding: utf-8 -*-
"""
- 模板名称
    模板编号: 0101
    模板名称: 百度贴吧指定吧主题帖爬虫模板
--------------------
功能：提取指定贴吧的帖子列表信息（标题、内容、作者、回复数等）
使用：爬取前需在baidu_tieba_topic_config.py中设置推荐的配置参数
"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BaiduTiebaTopicItem
from DlCrawler.configs.baidu.baidu_tieba_topic_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import asyncio
import datetime

class BaiduTiebaTopicSpider(scrapy.Spider):
    # 基础参数
    name = "baidu_tieba_topic"
    allowed_domains = ["tieba.baidu.com"]
    current_page = 1  # 当前页码
    topic_name = CUSTOM_SETTINGS['KEYWORDS']  # 贴吧主题名称
    encode_topic_name = quote(topic_name)
    start_urls = [f"https://tieba.baidu.com/f?kw={encode_topic_name}&ie=utf-8"]

    # 加载配置参数
    custom_settings = CUSTOM_SETTINGS

    # 最大获取数量
    max_count = CUSTOM_SETTINGS['MAXCOUNT']
    success_count = 0
    
    # cookies文件路径初始化
    cookies_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "cookies"
    cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
    cookies_file = cookies_dir / f"{name}_cookies.json"

    # 其它参数
    
    retries = 0
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def start_requests(self):

        # 发起登录请求
        # 判断是否存在cookies文件,并发送对应的登录请求
        target_url = self.start_urls[0]
        if self.cookies_file.exists(): 
            yield scrapy.Request(
            target_url,
            meta={
                "playwright": True,  # 启用Playwright处理
                "playwright_context_kwargs": {
                    "storage_state": str(self.cookies_file)
                },  
                "playwright_include_page": True # 包含页面对象
            },
            callback=self.parse
        )
        else:
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

        # 登录检测及cookies保存
        try:    
            await page.wait_for_selector("div.t_con.cleafix",timeout=60000)
            await page.context.storage_state(path=self.cookies_file)
        except Exception as e:
            self.logger.info(f"等待元素超时,登录失败,程序即将关闭,稍候重试：{e}")
            await page.close()
            return

        # 人类行为模拟,会降低抓取速度,依据实际情况自行注释
        await self.random_scroll(page)  # 分段滚动
        await self.random_sleep(page)  # 随机停顿
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容

        async for item in self.parse_page_content(page,response):
            yield item
          
        while True:
            # 检查第一终止条件: 成功条目数 >= 最大设置条目数
            if self.success_count >= self.max_count:
                self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                await page.close()
                return
            
            try:
                # 定位下一页按钮
                next_button = page.locator("a.next.pagination-item:has-text('下一页')")
                # 检查第二终止条件: 下一页按钮是否可用
                if await next_button.count() == 0:
                    self.logger.info("已到达最后一页，结束爬取")
                    await page.close()
                    return
                
                # 点击下一页,常用的方式,但不适用于本站
                # await next_button.click()
                
                # 百度贴吧专用翻页逻辑
                next_page_link = await page.locator("a.pagination-item.next").first.get_attribute("href")
                next_page_url = response.urljoin(next_page_link)
                await page.goto(next_page_url, wait_until="networkidle") 
                
                
                # 人类行为模拟,会降低抓取速度,依据实际情况自行注释
                await self.random_sleep(page) # 随机停顿
                # await self.random_scroll(page) # 分段滚动
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
                
                # 等待新内容加载
                try:
                    await page.wait_for_selector("div.t_con.cleafix", state="attached", timeout=30000)
                except Exception as e:
                    self.logger.warning(f"等待新页面内容超时: {e}")
                
                # 更新页码
                self.current_page += 1
                self.logger.info(f"成功翻页到第{self.current_page}页")
                
                # 处理新页面内容
                async for item in self.parse_page_content(page,response):
                    yield item
                
            except Exception as e:
                self.logger.error(f"分页失败: {e}")
                if not page.is_closed():
                    await page.close()
                return
    async def parse_page_content(self,page, response):
        # 初始化必要对象
        html = await page.content()
        selector = scrapy.Selector(text=html)

        # 临时调试,需要时自行取消注释
        # try:
        #     debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
        #     debug_dir.mkdir(parents=True, exist_ok=True)
        #     with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
        #         f.write(html)
        # except Exception as e:
        #     self.logger.info(f"保存文件失败：{e}")

        
        for post in selector.css('div.t_con.cleafix'):  # 遍历每个帖子
            item = BaiduTiebaTopicItem()

            item['batch_id'] = self.now
            item['bar_name'] = self.topic_name
            item['title'] = post.css('div.threadlist_title a.j_th_tit::text').get('').strip()
            item['title_url'] = response.urljoin(post.css('div.threadlist_title a.j_th_tit::attr(href)').get())
            item['content'] = post.css('div.threadlist_text div.threadlist_abs::text').get('').strip()
            item['author'] = post.css('div.threadlist_author span.tb_icon_author a.frs-author-name::text').get('').strip()
            item['reply_count'] = int(post.css('div.col2_left span.threadlist_rep_num::text').get('0'))
            item['page_num'] = self.current_page

            self.success_count += 1
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