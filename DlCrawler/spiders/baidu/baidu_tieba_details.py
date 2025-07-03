# -*- coding: utf-8 -*-
"""
模板名称
    * 模板编号: 0104
    * 模板名称: 百度贴吧帖子详情爬虫模板
--------------------
功能：提取指定URL的的帖子详情信息（批次号/贴子标题/贴子url/楼层/层主/层主等级/
主评论ID/主评论内容/主评论时间/设备来源/子评论）
使用：
    * 爬取前需在baidu_tieba_details_config.py中设置推荐的配置参数
    * start_urls需从data/start_urls/baidu_tieba_details_urls.csv文件读取
        该文件数据的两种获取方式:
        1.手动添加url至baidu_tieba_details_urls.csv文件
        2.通过utils/query_DB.py查询数据库,获取已抓取的title_url,复制添加到baidu_tieba_details_urls.csv文件
    * 增加并发数量,减少或禁用人类模拟行为可以提升抓取效率,但会增加反爬虫风险,需根据实际情况自行调整

"""

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BaiduTiebaDetailsItem
from DlCrawler.configs.baidu.baidu_tieba_details_config import CUSTOM_SETTINGS
import random
import json
import pathlib
import asyncio
import datetime

class BaiduTiebaDetailsSpider(scrapy.Spider):
    # 基础参数
    name = "baidu_tieba_details"
    allowed_domains = ["tieba.baidu.com"]
    current_page = 1  # 当前页码
    start_urls = []

    # bar_name,encode_topi_name参数不适用于本模板
    # bar_name = CUSTOM_SETTINGS['KEYWORDS']  # 贴吧名称
    # encode_topic_name = quote(bar_name)
    

    
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

        # 登录检测及cookies保存
        try:    
            await page.wait_for_selector("div.u_menu_item.u_menu_news",timeout=60000)
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
                next_button = page.locator("li.l_pager.pager_theme_5.pb_list_pager a:has-text('下一页')")
                # 检查第二终止条件: 下一页按钮是否可用
                if await next_button.count() == 0:
                    self.logger.info("已到达最后一页，结束爬取")
                    await page.close()
                    return
                
                # 点击下一页,常用的方式,但不适用于本站
                # await next_button.click()
                
                # 百度贴吧专用翻页逻辑
                next_selector = "li.l_pager.pager_theme_5.pb_list_pager a:has-text('下一页')"
                next_page_link = await page.locator(next_selector).first.get_attribute("href")
                next_page_url = response.urljoin(next_page_link)
                await page.goto(next_page_url, wait_until="networkidle") 
                
                
                # 人类行为模拟,会降低抓取速度,依据实际情况自行注释
                await self.random_sleep(page) # 随机停顿
                # await self.random_scroll(page) # 分段滚动
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
                
                # 等待新内容加载
                try:
                    await page.wait_for_selector("div.p_postlist", state="attached", timeout=30000)
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

        
        for post in selector.css('div.l_post.l_post_bright.j_l_post.clearfix'):  # 遍历每个帖子
            item = BaiduTiebaDetailsItem()

            item['batch_id'] = self.now
            item['bar_name'] = post.css('a.card_title_fname::text').get('').strip()
            item['title'] = post.css('h3.core_title_txt.pull-left.text-overflow::attr(title)').get('').strip()
            item['title_url'] = page.url
            item['floor'] = post.css('span.tail-info::text').get('').strip()
            item['author'] = post.css('a.p_author_name.j_user_card::text').get('').strip()
            item['bar_level'] = int(post.css('div.d_badge_lv::text').get('').strip())
            item['main_comment_id'] = int(post.css('::attr(data-pid)').get('').strip())
            item['main_comment'] = post.css('div.d_post_content.j_d_post_content::text').get('').strip()
            item['main_comment_time'] = post.css(
    'div.post-tail-wrap > span.tail-info:nth-last-child(1)::text'
).get('').strip()
            item['device_source'] = post.xpath(
    '//span[@class="tail-info" and a]/a//text()'
).get('').strip()

            sub_comments = []
            for comment in post.css('li.lzl_single_post.j_lzl_s_p'):
                # 提取@回复关系
                at_link = comment.css('span.lzl_content_main a.at.j_user_card')
                if at_link:
                    replied_user = at_link.css('::text').get('').strip()
                sub_item = {
                    'sub_author': comment.css('a.j_user_card::text').get('').strip(),
                    'sub_content': comment.css('span.lzl_content_main::text').get('').strip(),
                    'sub_time': comment.css('span.lzl_time::text').get('').strip(),
                    'replied_user': replied_user
                }
                sub_comments.append(sub_item)
            item['sub_comments'] = sub_comments

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