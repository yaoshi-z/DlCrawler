# -*- coding: utf-8 -*-

"""
- 模板名称
    模板编号: 6001
    模板名称: 淘宝_搜索_关键字商品信息爬虫模板
--------------------
功能：提取指定搜索关键词的图片信息（
    批次号,关键词,店铺名称,地理位置,产品名称,产品价格,
    付款人数,店铺链接,图片链接,商品链接,商品ID,付款人数,页码
）
使用：爬取前需在taobao_search_keywords_config.py中设置推荐的配置参数
"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import TaobaoSearchKeywordsItem
from DlCrawler.configs.taobao.taobao_search_keywords_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import datetime
import asyncio

class TaobaoSearchKeywordsSpider(scrapy.Spider):
    name = "taobao_search_keywords"
    allowed_domains = ["taobao.com"]
    keywords = CUSTOM_SETTINGS['KEYWORDS']  # 搜索关键词
    encode_keywords = quote(keywords)
    
    start_urls = [
                f"https://login.taobao.com/",
                f"https://s.taobao.com/search?q={encode_keywords}"
                ]
    
    # 加载配置参数
    custom_settings = CUSTOM_SETTINGS

    # 最大获取数量
    max_count = CUSTOM_SETTINGS['MAXCOUNT']
    success_count = 0

    current_page = 1  # 当前页码
    retries = 0

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    cookies_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "cookies"
    cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
    cookies_file = cookies_dir / f"{name}_cookies.json"
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
            callback=self.verify_login
        )
        else:
            yield scrapy.Request(
            target_url,
            meta={
                "playwright": True,  # 启用Playwright处理  
                "playwright_include_page": True # 包含页面对象
            },
            callback=self.verify_login
        )
        

    async def verify_login(self, response):
        page = response.meta['playwright_page']
        try:
            # 登录成功逻辑

            # 验证登录是否成功
            await page.wait_for_selector("div[class*='accountInfo']",timeout=60000) 
            await page.context.storage_state(path=self.cookies_file)
            self.logger.info("已登录并更新cookies,开始采集数据")
                
            #登录后发起搜索模式请求
            yield scrapy.Request(
                self.start_urls[1],
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_context_kwargs": {
                        "storage_state": str(self.cookies_file)
                    },  
                    "playwright_include_page": True,
                     "playwright_page": page # 包含页面对象
                },
                callback=self.parse
            )
            
           
        except Exception as e:
            self.logger.error(f"登录失败: {e},请检查cookies或账号密码是否正确")
            if self.cookies_file.exists():  # 删除无效cookies
                self.cookies_file.unlink()

            # 计数当前失败次数
            self.retries += 1
            if self.retries >= 2:
                self.logger.error("登录失败次数过多，请检查cookies或账号密码是否正确")
                await page.close()
                raise scrapy.exceptions.CloseSpider("登录失败")

            yield scrapy.Request(
                self.start_urls[0],
                meta = {'playwright': True, 
                        'playwright_page_coroutine': 'goto'},
                callback=self.verify_login, 
                dont_filter=True,
                max_retry_times=3
                )

    async def parse(self, response):
        page = response.meta['playwright_page']

        # 增强的人类形为模拟
        await self.random_scroll(page)  # 分段滚动
        # await self.random_mouse_actions(page)  # 鼠标交互
        await self.random_sleep(page)  # 随机停顿

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容


        # 初始化必要对象
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

        cards_selector = '//div[contains(@class, "tbpc-col") and contains(@class, "search-content-col")]'
        
        items_cards = selector.xpath(cards_selector)

        for item_node in items_cards:
            item = TaobaoSearchKeywordsItem()

            item['keywords'] = self.keywords
            item['batch_id'] = self.now
            item['shop_name'] = item_node.css('span.shopNameText--DmtlsDKm::text').get('').strip()
            item['shop_url'] = response.urljoin(item_node.css('a.shopName--hdF527QA::attr(href)').get('').strip())

            location_parts = item_node.css('div.procity--wlcT2xH9 span::text').getall()
            item['location'] = ' '.join(location_parts)

            item['product_id'] = item_node.css('a[data-spm-protocol]::attr(id)').get('').strip()
            item['product_url'] = response.urljoin(item_node.css('a[data-spm-protocol]::attr(href)').get('').strip())

            title_parts = item_node.xpath('.//div[contains(@class,"title")]//text()').getall()
            item['product_title'] = ''.join([text.strip() for text in title_parts if text.strip()])

            item['product_img'] = item_node.css('img.mainImg--sPh_U37m::attr(src)').get('').strip()

            price_parts = item_node.xpath('.//div[@class="innerPriceWrapper--aAJhHXD4"]//text()').getall()
            item['product_price'] = ''.join([text.strip() for text in price_parts if text.strip()])

            item['paid_count'] = item_node.css('span.realSales--XZJiepmt::text').get('').strip()
            item['page_num'] = self.current_page


            self.success_count += 1
            yield item

        # 终止条件2: 达到最大条目数则停止
            if self.success_count >= self.max_count:
                self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                await page.close()
                return
            
                        
        await self.random_sleep(page)  # 随机休眠

        # 分页逻辑
        try:
            # 定位下一页按钮
            next_button = page.locator("button:has-text('下一页')")
            
            # 检查按钮是否可点击
            is_disabled = await next_button.is_disabled()
            if is_disabled:
                self.logger.info("已到达最后一页，结束爬取")
                await page.close()
                raise scrapy.exceptions.CloseSpider("已到达最后一页")

            # 执行点击操作并等待导航完成
            await next_button.click()
            
            
            # 等待页面加载完成（根据实际页面调整选择器）
            await page.wait_for_selector("div.tbpc-col.search-content-col", timeout=30000)

            self.current_page += 1
            
            new_url = page.url
            self.logger.info(f"已切换到第{self.current_page}页，当前URL：{new_url}")
            
            # 增加随机等待时间模拟人类行为
            await self.random_sleep(page)
            
            # 继续解析当前页面内容
            yield scrapy.Request(
                url=new_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page": page,
                },
                callback=self.parse,
                dont_filter=True
            )
            
        except Exception as e:
            # 检测验证码
            html = await page.content()
            if "验证码" in html or "auth" in page.url:
                self.logger.warning("检测到反爬验证，暂停爬取")
                await page.wait_for_timeout(60_000)
            else:
                self.logger.error(f"分页失败: {e}")
                await page.close()
                
    

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

    async def random_mouse_actions(self, page):
        """模拟人类鼠标行为"""
        viewport_size_dict = await page.viewport_size()
        width, height = viewport_size_dict['width'], viewport_size_dict['height']
        
        # 随机移动鼠标（2-4次）
        for _ in range(random.randint(2, 4)):
            x = random.uniform(100, width - 100)  # 限制在可视区域中间
            y = random.uniform(100, height - 100)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.2, 0.5))  # 短暂停顿
        
        # 50%概率悬停商品卡片
        if random.random() > 0.5:  
            cards = await page.query_selector_all('xpath=//div[contains(@class, "tbpc-col") and contains(@class, "search-content-col")]')
            if cards:
                target = random.choice(cards)  # 随机选择一个商品
                await target.hover()
            await asyncio.sleep(random.uniform(0.5, 1.2))  # 悬停时间