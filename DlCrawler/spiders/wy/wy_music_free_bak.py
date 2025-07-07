# -*- coding: utf-8 -*-
"""
模板名称
    * 模板编号: 0801
    * 模板名称: 网易云音乐免费歌单模板
--------------------
功能：提取指定URL的的帖子详情信息（批次号/歌单ID/歌单标题/歌曲ID/歌曲标题/时长/歌手/专辑/歌曲url）
使用：
    * 爬取前需在wy_music_free_config.py中设置推荐的配置参数
    * start_urls需从data/start_urls/wy_music_free_urls.csv文件读取;
        - 需手动添加url至csv文件
        - url是指歌单url,示例:https://music.163.com/#/playlist?id=2233842197 
    * 增加并发数量,减少或禁用人类模拟行为可以提升抓取效率,但会增加反爬虫风险,需根据实际情况自行调整
        - 起始urls为1个时,有效并发数量始终为1
    * 本模板是否登录均可,但推荐登录
"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import WyMusicFreeItem
from DlCrawler.configs.wy.wy_music_free_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import asyncio
import datetime

class WyMusicFreeSpider(scrapy.Spider):
    # 基础参数
    name = "wy_music_free_bak"
    allowed_domains = ["music.163.com"]
    start_urls = []
    current_page = 1  # 当前页码
    
    '''
    keywords构建的start_urls逻辑最终需要调整到统一的csv文件中
    这里做一下标记,后期进行处理
    '''
    # keywords及encode_keywords参数不适用于本模板
    # keywords = CUSTOM_SETTINGS['KEYWORDS']  # 贴吧名称
    # encode_keywords = quote(keywords)
    
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
    template_no = CUSTOM_SETTINGS['TEMPLATE_NO'] # 模板编号
    is_download_music = CUSTOM_SETTINGS['IS_DOWNLOAD_MUSIC']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化读取URL列表
        self.start_urls = self.read_start_urls() or []
        
        # 添加日志输出
        self.logger.info(f"成功加载 {len(self.start_urls)} 个起始URL")
        if self.start_urls:
            self.logger.debug(f"前3个URL: {self.start_urls[:3]}")

    def read_start_urls(self):
        try:
            # 读取urls列表
            start_urls_path = pathlib.Path(__file__).parent.parent.parent / "data" / "start_urls" / f"{self.name}_urls.csv"  
            with open(start_urls_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[1:]
                start_urls = [line.strip() for line in lines if line.strip()]
                
            # 过滤掉空行和注释行
            valid_urls = [url for url in start_urls if url and not url.startswith("#")]
            return valid_urls
        except Exception as e:
            self.logger.error(f"读取urls列表失败：{e}")
            return None

    def start_requests(self):
        # 发起登录请求
        # 判断是否存在cookies文件,并发送对应的登录请求
        for target_url in self.start_urls:
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
        
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # 本模板无需登录也可采集,若需要登录,可取消注释
        # 登录检测及cookies保存
        # try:   
        #     self.logger.info("正在等待登录状态,请在60秒内完成登录") 
        #     await page.wait_for_selector("a.name.f-thide.f-fl",timeout=60000)
        #     await page.context.storage_state(path=self.cookies_file)
        # except Exception as e:
        #     self.logger.info(f'''等待元素超时,登录失败{e})''')
        #     await page.close()
        #     return
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

        # 人类行为模拟,会降低抓取速度,依据实际情况自行注释
        # await self.random_scroll(page)  # 分段滚动
        # await self.random_sleep(page)  # 随机停顿
        # await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容

        # async for item in self.parse_page_content(page,response):
        #     yield item

        # 翻页逻辑不适用于本模板 
        # while True:
        #     # 检查第一终止条件: 成功条目数 >= 最大设置条目数
        #     if self.success_count >= self.max_count:
        #         self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
        #         await page.close()
        #         return
            
        #     try:
        #         # 定位下一页按钮
        #         next_button = page.locator("li.l_pager.pager_theme_5.pb_list_pager a:has-text('下一页')")
        #         # 检查第二终止条件: 下一页按钮是否可用
        #         if await next_button.count() == 0:
        #             self.logger.info("已到达最后一页，结束爬取")
        #             await page.close()
        #             return
                
        #         # 点击下一页,常用的方式,但不适用于本站
        #         # await next_button.click()
                
        #         # 百度贴吧专用翻页逻辑
        #         next_selector = "li.l_pager.pager_theme_5.pb_list_pager a:has-text('下一页')"
        #         next_page_link = await page.locator(next_selector).first.get_attribute("href")
        #         next_page_url = response.urljoin(next_page_link)
        #         await page.goto(next_page_url, wait_until="domcontentloaded") 
                
                
        #         # 人类行为模拟,会降低抓取速度,依据实际情况自行注释
        #         await self.random_sleep(page) # 随机停顿
        #         # await self.random_scroll(page) # 分段滚动
        #         await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
                
        #         # 等待新内容加载
        #         try:
        #             await page.wait_for_selector("div.l_post.l_post_bright.j_l_post.clearfix", state="attached", timeout=30000)
        #         except Exception as e:
        #             self.logger.warning(f"等待新页面内容超时: {e}")
                
        #         # 更新页码
        #         self.current_page += 1
        #         self.logger.info(f"成功翻页到第{self.current_page}页")
                
        #         # 处理新页面内容
        #         async for item in self.parse_page_content(page,response):
        #             yield item
                
        #     except Exception as e:
        #         self.logger.error(f"分页失败: {e}")
        #         if not page.is_closed():
        #             await page.close()
        #         return
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

        playlist_id = page.url.split('=')[1].strip()
        playlist_title = selector.css('h2.f-ff2.f-brk::text').get('').strip()
        
        for tr in selector.css('tbody tr'):  # 遍历每行信息
            if self.success_count >= self.max_count:
                self.logger.info(f"达到上限{self.max_count}, 终止当前页解析")
                break 
            item = WyMusicFreeItem()
            
            item['batch_id'] = self.now
            item['playlist_id'] = playlist_id
            item['playlist_title'] = playlist_title
            item['song_id'] = tr.xpath('./td[1]//span[@class="ply"]/@data-res-id').get('').strip()
            item['song_title'] = tr.xpath('./td[2]//b/@title').get('').strip()
            item['song_duration'] = tr.css('./td[3]//span.u-dur::text').get('').strip()
            item['song_author'] = tr.xpath('./td[4]//div[@class="text"]/@title').get('').strip()
            item['song_album'] = tr.xpath('./td[5]//a/@title').get('').strip()


            self.success_count += 1
           
            self.logger.info(f'''已爬取 第{self.success_count} 条数据:
                             playlist_id:{item['playlist_id']}
                             song_id:{item['song_id']}
                             song_title:{item['song_title']}
                             ...
''')
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