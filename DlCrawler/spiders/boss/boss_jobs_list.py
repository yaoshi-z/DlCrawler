# -*- coding: utf-8 -*-
# 本爬虫首次测试时触发了强反爬虫机制，暂停开发,等待其它爬虫开发完成后再恢复开发
"""
- 模板名称
    模板编号: 5001
    模板名称: Boss直聘_指定职位_列表信息爬虫模板
--------------------
功能：提取指定搜索关键词的图片信息（批次号,城市,职位名称,职位详情url、薪资,经验要求,学历要求,公司名称,公司url,工作区域）
使用：爬取前需在boss_jobs_list_config.py中设置推荐的配置参数
"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BossJobsListItem
from DlCrawler.configs.boss.boss_jobs_list_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import datetime

class BaiduImgKeywordsSpider(scrapy.Spider):
    name = "boss_jobs_list"
    allowed_domains = ["zhipin.com"]
    keywords = CUSTOM_SETTINGS['KEYWORDS']  # 搜索关键词
    encode_keywords = quote(keywords)
    city_code = CUSTOM_SETTINGS['CITY_CODE']
    start_urls = [
                f"https://login.zhipin.com/",
                f"https://www.zhipin.com/web/geek/jobs?city={city_code}&query={encode_keywords}"
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
        # boss直聘网必须登录后再去搜索,否则会触发反爬机制
        # 这里判断是否有cookies文件,没有则使用登录页面进行登录
        if self.cookies_file.exists():  # 判断cookies文件是否存在
            target_url = self.start_urls[1]
            yield scrapy.Request(
            target_url,
            meta={
                "playwright": True,  # 启用Playwright处理
                "playwright_context_kwargs": {
                    # 设置cookies
                    # 首次访问页面时获取cookies前应先注释掉,
                    # 成功获取cookies后取消meta->playwright_context_kwargs->storage_state的注释
                    "storage_state": str(self.cookies_file)
                },  
                "playwright_include_page": True # 包含页面对象
            }
        )
        else:
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

        # 首次访问页面时获取cookies的逻辑,执行一次后可注释掉,
        # 同时取消meta->playwright_context_kwargs->storage_state的注释
        if self.cookies_file.exists() == False:
            await page.wait_for_timeout(60000) # 等待60秒登录,验证码处理等可能出现的人工操作
            await page.context.storage_state(path=self.cookies_file)
            await page.close()
            self.logger.info("已获取cookies")
            return
        return
        try:
          wait_tags ='li.job-card-box'
          await page.wait_for_selector(wait_tags, timeout=60000)   
        except:
            await page.close()
            self.logger.info(f"未找到有效的{wait_tags}标签") 

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
        await page.wait_for_load_state("networkidle")  # 等待网络空闲

        # 初始化一些必要对象
        seen_bd_urls = set()
        previous_height = await page.evaluate("document.body.scrollHeight")
        


        # 核心解析逻辑
        while True:
            html = await page.content()
            selector = scrapy.Selector(text=html)
            # # 临时调试,需要时自行取消注释
            # try:
            #     debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
            #     debug_dir.mkdir(parents=True, exist_ok=True)
            #     with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
            #         f.write(html)
            # except Exception as e:
            #     self.logger.info(f"保存文件失败：{e}")
            

            items_cards = selector.css('div.img-cell_2OJEU')
            for item_node in items_cards:
                item = BossJobsListItem()

                item['keyword'] = self.keywords
                item['batch_id'] = self.now
                
                data_show_ext = item_node.css('::attr(data-show-ext)').get()
                
                if not data_show_ext:
                    continue
                
                data = json.loads(data_show_ext)

                # bd_url获取含重复链接过滤逻辑
                item['bd_url'] = data.get('url','')    
                if item['bd_url'] in seen_bd_urls:
                    continue

                seen_bd_urls.add(item['bd_url'])

                item['title'] = data.get('title','')
                item['raw_url'] = data.get('objurl','')
                item['is_ad'] = 1 if data.get('isAd',True) else 0
                

                self.success_count += 1
                yield item

            # 终止条件2: 达到最大条目数则停止
                if self.success_count >= self.max_count:
                    self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                    await page.close()
                    return
            
                        
            await self.random_sleep(page)  # 随机休眠

            # 构造滚动加载逻辑
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_load_state("networkidle")
            new_height = await page.evaluate("document.body.scrollHeight")

            # 终止条件1：滚动高度不变
            if new_height == previous_height:
                self.logger.info("页面无新内容加载，结束滚动。")
                await page.close()
                return

            previous_height = new_height
            html = await page.content()
            selector = scrapy.Selector(text=html)


    async def random_sleep(self,page):
        """随机休眠，避免被封禁"""
        sleep_time = random.uniform(1, 3)
        await page.wait_for_timeout(int(sleep_time * 1000))