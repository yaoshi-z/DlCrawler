# -*- coding: utf-8 -*-

"""
- 模板名称
    模板编号: 6001
    模板名称: 淘宝_搜索_关键字商品信息爬虫模板
--------------------
功能：提取指定搜索关键词的图片信息（
    批次号,关键词,店铺名称,地理位置,产品名称,产品价格,
    付款人数,店铺链接,图片链接,商品链接,商品ID,当前页面网址,页码
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

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    cookies_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "cookies"
    cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
    cookies_file = cookies_dir / f"{name}_cookies.json"
    def start_requests(self):
        # 搜索模式请求
        # 淘宝网登录后再去搜索,否则将无法搜索
        # 这里判断是否有cookies文件,没有则使用发起登录模式的请求
        if self.cookies_file.exists():  # 判断cookies文件是否存在
            target_url = self.start_urls[1]
            yield scrapy.Request(
            target_url,
            meta={
                "playwright": True,  # 启用Playwright处理
                "playwright_context_kwargs": {
                    "storage_state": str(self.cookies_file)
                },  
                "playwright_include_page": True # 包含页面对象
            }
        )
        else:
            # 登录模式请求
            target_url = self.start_urls[0]
            yield scrapy.Request(
            target_url,
            meta={
                "playwright": True,  # 启用Playwright处理  
                "playwright_include_page": True # 包含页面对象
            }
        )
        

    async def parse(self, response):
        page = response.meta['playwright_page']
        try:
            # 登录模式
            # 首次登录或无效cookies删除后---> 获取cookies的逻辑
            # 注意:这里获取cookies后会退出爬虫,需要再次运行爬虫进入搜索模式
            if self.cookies_file.exists() == False:
                await page.wait_for_timeout(60000) # 等待60秒登录,验证码处理等可能出现的人工操作
                await page.context.storage_state(path=self.cookies_file)
                await page.close()
                self.logger.info("已获取cookies")
                return
            
            # 验证现有cookies是否有效
            # 有效则继续执行,无效则抛出异常,并重新发起登录模式请求
            await page.wait_for_selector('div#content_wrapper',timeout=60000) 
            self.logger.info("cookies登录成功,开始获取数据")


            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
            await page.wait_for_load_state("networkidle")  # 等待网络空闲

            # 初始化一些必要对象
            seen_bd_urls = set()
            previous_height = await page.evaluate("document.body.scrollHeight")
            


            # 核心解析逻辑
            # while True:
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
                

                # items_cards = selector.css('div.img-cell_2OJEU')
                # for item_node in items_cards:
                #     item = TaobaoSearchKeywordsItem()

                #     item['keyword'] = self.keywords
                #     item['batch_id'] = self.now
                    
                #     data_show_ext = item_node.css('::attr(data-show-ext)').get()
                    
                #     if not data_show_ext:
                #         continue
                    
                #     data = json.loads(data_show_ext)

                #     # bd_url获取含重复链接过滤逻辑
                #     item['bd_url'] = data.get('url','')    
                #     if item['bd_url'] in seen_bd_urls:
                #         continue

                #     seen_bd_urls.add(item['bd_url'])

                #     item['title'] = data.get('title','')
                #     item['raw_url'] = data.get('objurl','')
                #     item['is_ad'] = 1 if data.get('isAd',True) else 0
                    

                #     self.success_count += 1
                #     yield item

                # # 终止条件2: 达到最大条目数则停止
                #     if self.success_count >= self.max_count:
                #         self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                #         await page.close()
                #         return
                
                            
                # await self.random_sleep(page)  # 随机休眠

                # # 构造滚动加载逻辑
                # await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                # await page.wait_for_load_state("networkidle")
                # new_height = await page.evaluate("document.body.scrollHeight")

                # # 终止条件1：滚动高度不变
                # if new_height == previous_height:
                #     self.logger.info("页面无新内容加载，结束滚动。")
                #     await page.close()
                #     return

                # previous_height = new_height
                # html = await page.content()
                # selector = scrapy.Selector(text=html)
        except Exception as e:
            self.logger.error(f"无效地cookies,登录失败: {e}")
            if self.cookies_file.exists():  # 删除无效cookies
                self.cookies_file.unlink()
            await page.close()

            yield scrapy.Request(
                self.start_urls[0],
                meta = {'playwright': True, 
                        'playwright_page_coroutine': 'goto'},
                callback=self.parse, 
                dont_filter=True)


    async def random_sleep(self,page):
        """随机休眠，避免被封禁"""
        sleep_time = random.uniform(1, 3)
        await page.wait_for_timeout(int(sleep_time * 1000))