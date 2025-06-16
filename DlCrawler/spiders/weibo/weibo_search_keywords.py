import scrapy
from DlCrawler.configs.weibo.weibo_search_keywords_config import CUSTOM_SETTINGS, MAXSCOUNT,KEYWORDS
from scrapy_playwright.page import PageMethod
from DlCrawler.items import WeiboSearchKeywordsItem
import pathlib
from urllib.parse import quote
from datetime import datetime, timedelta
import re
import json
import random

class WeiboSearchKeywordsSpider(scrapy.Spider):
    name = "weibo_search_keywords"
    allowed_domains = ["s.weibo.com"]
    custom_settings = CUSTOM_SETTINGS
    maxscount = MAXSCOUNT
    keywords = KEYWORDS
    current_page = 1
    success_count  = 0
    encode_keywords = quote(keywords)
    start_urls = [f"https://s.weibo.com/weibo?q={encode_keywords}"]

        
    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_include_page": True, # 包含页面对象
                }
            )

    async def parse(self, response):
        page = response.meta['playwright_page']

        # 登录逻辑
        try:
            # 等待登录成功标志
            await page.wait_for_selector("//div[@class='card-wrap']", timeout=60000)
            self.logger.info("登录成功并检测搜索内容")
        except Exception as e:
            if self.success_count == 0:
                self.logger.error(f"等待登录超时或页面未正确加载: {e}")
                await page.close()
                self.crawler.engine.close_spider(self, reason="登录失败或超时加载")
            elif self.success_count <= self.maxscount:
                self.logger.info(f"已达到最大爬取数量或没有更多内容可爬取: {e}")
                await page.close()
                self.crawler.engine.close_spider(self, reason="页面无更多内容")
            
            return
        
        # 初始化必要对象 
        html = await page.content()
        selector = scrapy.Selector(text=html)
        
        seen_mid = set()  # 记录已采集的mid

        # 临时调试,需要时自行取消注释
        # try:
        #     debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
        #     debug_dir.mkdir(parents=True, exist_ok=True)
        #     with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
        #         f.write(html)
        # except Exception as e:
        #     self.logger.info(f"保存文件失败：{e}")

        cards_xpath = '//div[contains(@class, "card-wrap")]'
        cards = selector.xpath(cards_xpath)

        for card in cards:

            mid = card.xpath('./@mid').get(default='')

            # 跳过已采集的mid
            if mid in seen_mid:
                self.logger.info(f"已跳过重复的 mid: {mid}")
                continue

            seen_mid.add(mid)  # 添加到已采集集合中

            item = WeiboSearchKeywordsItem()
            item['mid'] = mid
            item['keyword'] = self.keywords 
            item['content_link'] = f"https://weibo.com/detail/{mid}"
            item['user_name'] = card.xpath('.//a[contains(@class, "name")]/@nick-name').get()

            # 提取认证类型
            vip_icon = card.xpath('.//div[@class="user_vip_icon_container"]/img/@src').get()
            if vip_icon:
                verified_type = pathlib.Path(vip_icon).stem
            else:
                verified_type = "普通用户"
            item['verified_type'] = verified_type
            
            # 优先提取 full 版本的 p 标签，否则回退到非 full 版本
            content_p = card.xpath('.//p[@node-type="feed_list_content_full"] | .//p[@node-type="feed_list_content"]')

            if content_p:
                # 提取文本并过滤 a 标签内容
                content_parts = content_p.xpath('.//text()[not(parent::a)]').getall()
                content = ' '.join([p.strip() for p in content_parts if p.strip()])
            else:
                content = "无内容"
            item['content'] = content
            
             # 提取原始时间文本
            time_elem = card.xpath('.//div[@class="from"]/a[1]')
            time_str = ''.join(time_elem.xpath('.//text()').getall()).strip()
             # 解析时间并格式化
            try:
                post_time = self.parse_weibo_time(time_str)
            except Exception as e:
                self.logger.warning(f"时间解析失败: {e}")
                post_time = datetime.now().strftime("%Y%m%d%H%M")  # 回退到当前时间

            item['post_time'] = post_time

            # 提取设备来源
            device = card.xpath('.//div[@class="from"]/a[2]/text()').get()
            item['device_source'] = device.strip() if device and device.strip() else "未知设备"

            # 定位互动区域并按顺序提取转发、评论、点赞
            base_path = './/div[@class="card-act"]/ul/li'

            # 转发量
            reposts_elem = card.xpath(f'{base_path}[1]//text()').getall()
            item['reposts'] = self.extract_interactions(reposts_elem, r'转发')
            
            # 评论量
            comments_elem = card.xpath(f'{base_path}[2]//text()').getall()
            item['comments'] = self.extract_interactions(comments_elem, r'评论')
            
            # 点赞量
            likes_elem = card.xpath(f'{base_path}[3]//text()').getall()
            item['likes'] = self.extract_interactions(likes_elem, r'赞')
            self.success_count += 1  # 全局计数器自增
            yield item

            # 达到最大条目数则停止
            if self.success_count >= self.maxscount:
                self.logger.info(f"已爬取 {self.success_count} 条数据，达到上限，停止爬取。")
                await page.close()
                return
            
        await self.random_sleep(page)  # 随机休眠

        # 新增：构造下一页请求
        self.current_page += 1
        next_url = f"https://s.weibo.com/weibo?q={self.encode_keywords}&page={self.current_page}"
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
    # 简单数据清洗
    def extract_numeric_value(self,text_list):
        combined = ''.join([t.strip() for t in text_list if t.strip()])
        numeric = ''.join(filter(str.isdigit, combined))
        return int(numeric) if numeric else 0
    def parse_weibo_time(self,time_str):
        """解析微博时间格式"""
        now = datetime.now()
        parsed_time = now  # 默认当前时间
        
        # 情况1: x分钟前/x秒前
        minute_match = re.search(r'(\d+)分钟前', time_str)
        second_match = re.search(r'(\d+)秒前', time_str)
        
        if minute_match:
            minutes = int(minute_match.group(1))
            parsed_time = now - timedelta(minutes=minutes)
        elif second_match:
            seconds = int(second_match.group(1))
            parsed_time = now - timedelta(seconds=seconds)
        
        # 情况2: 今天HH:mm
        today_match = re.search(r'今天(\d{2}:\d{2})', time_str)
        if today_match:
            time_part = today_match.group(1)
            parsed_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {time_part}", "%Y-%m-%d %H:%M")
        
        # 情况3: MM月DD日
        date_match = re.search(r'(\d{2})月(\d{2})日', time_str)
        if date_match:
            month, day = map(int, date_match.groups())
            parsed_time = datetime(now.year, month, day)
            
            # 处理跨年场景（如1月日期大于当前月份）
            if parsed_time.month > now.month:
                parsed_time = parsed_time.replace(year=now.year - 1)
        
        # 情况4: 完整日期（含年月日时分）
        full_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', time_str)
        if full_match:
            parsed_time = datetime.strptime(full_match.group(1), "%Y-%m-%d %H:%M")
        
        return parsed_time.strftime("%Y%m%d%H%M")
    
    # 交互数据解析方法
    def extract_interactions(self, text_list, keyword):
        """提取互动数，若含指定关键词则返回 0"""
        raw_text = ''.join([t.strip() for t in text_list if t.strip()])
        if re.search(keyword, raw_text):
            return 0
        return self.extract_numeric_value(text_list)