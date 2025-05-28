# scrapy==2.12.0
# playwright==1.52.0

import scrapy
from urllib.parse import quote,unquote
from datetime import datetime
from scrapy_playwright.page import PageMethod
from DlCrawler.items import BaiduTiebaTopicItem
from configs.baidu.baidu_tieba_topic_config import CUSTOM_SETTINGS, MAXPAGE,TOPIC_NAME
import random

class BaiduTiebaTopicSpider(scrapy.Spider):
    name = "baidu_tieba_topic"
    allowed_domains = ["baidu.com"]
    topic_name = TOPIC_NAME  # 贴吧主题名称
    encode_topic_name = quote(topic_name)
    start_urls = [f"https://tieba.baidu.com/f?kw={encode_topic_name}&ie=utf-8"]

    # 最大翻页数
    max_page = MAXPAGE
    current_page = 1

    custom_settings = CUSTOM_SETTINGS

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.t_con.cleafix", timeout=10000),
                        PageMethod("wait_for_timeout",random.randint(1000,3000)) #子列表加载完成
                    ],
                    "playwright_include_page": True # 包含页面对象
                }
            )

    async def parse(self, response):
        page = response.meta['playwright_page']
        

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滚动到底部加载更多内容
        await page.wait_for_timeout(random.randint(2000, 5000))  # 随机延迟
        
        # # 临时调试,需要时自行取消注释
        # with open(f"debug_files/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        # 提取吧名（从<title>标签）
        bar_name = unquote(response.xpath('//title/text()').get().split('-')[0].strip())
        
        for post in response.css('div.t_con.cleafix'):  # 遍历每个帖子
            item = BaiduTiebaTopicItem()

            item['bar_name'] = bar_name
            item['title'] = post.css('div.threadlist_title a.j_th_tit::text').get('').strip()
            item['content'] = post.css('div.threadlist_text div.threadlist_abs::text').get('').strip()
            item['author'] = post.css('div.threadlist_author span.tb_icon_author a.frs-author-name::text').get('').strip()
            item['reply_count'] = int(post.css('div.col2_left span.threadlist_rep_num::text').get('0'))
            yield item
          
        # 翻页逻辑
        if self.current_page <= self.max_page:
            try:
                next_page_link = await page.locator("a.pagination-item.next").first.get_attribute("href")
                next_page_url = response.urljoin(next_page_link)
        
                await page.goto(next_page_url, wait_until="networkidle")     
                
                self.current_page += 1
                yield scrapy.Request(
                    url=page.url,
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
                    page.wait_for_timeout(60_000)
                else:
                    self.logger.error(f"翻页失败: {e}")
                
        
