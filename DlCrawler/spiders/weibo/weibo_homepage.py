import scrapy
import pathlib
from DlCrawler.configs.weibo.weibo_homepage_config import CUSTOM_SETTINGS, MAXSCOUNT
from scrapy_playwright.page import PageMethod
import random
from DlCrawler.items import WeiboHomepageItem

class WeiboSearchKeywordsSpider(scrapy.Spider):
    name = "weibo_homepage"
    allowed_domains = ["weibo.com"]
    start_urls = ["https://weibo.com"]
    current_page = 1
    custom_settings = CUSTOM_SETTINGS
    maxscount = MAXSCOUNT

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # 启用Playwright处理
                    "playwright_include_page": True # 包含页面对象
                }
            )

    async def parse(self, response):
        page = response.meta['playwright_page']
        # 等待30秒登录时间
        # 登录默认爬取"首页"标签下的内容, 不登录默认爬取"推荐-热门"下的内容
        # 关于标签的参数配置及相关逻辑,会在后续版本中添加
        await page.wait_for_timeout(30000)

        # 初始化必要对象 
        html = await page.content()
        selector = scrapy.Selector(text=html)
        success_count  = 0
        previous_height = await page.evaluate("document.body.scrollHeight")
        seen_links = set()  # 记录已采集的链接，防止重复

        # # 临时调试,需要时自行取消注释
        # try:
        #     debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
        #     debug_dir.mkdir(parents=True, exist_ok=True)
        #     with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
        #         f.write(html)
        # except Exception as e:
        #     self.logger.info(f"保存文件失败：{e}")

            
        while True:
            items_xpath = '//article[contains(@class, "Feed_wrap_3v9LH")]'
            articles = selector.xpath(items_xpath)

            for article in articles:
                time_elem = article.xpath('.//a[contains(@class, "head-info_time_6sFQg")]')
                content_link = time_elem.xpath('@href').get()

                # 跳过已采集的链接
                if content_link in seen_links:
                    continue

                seen_links.add(content_link)  # 添加到已采集集合中

                item = WeiboHomepageItem()
                item['content_link'] = content_link
                item['user_name'] = article.xpath('.//a[contains(@class, "head_name_24eEB")]/span/@title').get()
                item['verified_type'] = article.xpath('.//div[contains(@class, "head-info_source_2zcEX")]/text()').get()

                content_parts = article.xpath('.//div[contains(@class, "detail_wbtext_4CRf9")]//text()').getall()
                item['content'] = ' '.join([p.strip() for p in content_parts if p.strip()])

                item['post_time'] = time_elem.xpath('text()').get()

                # 定位互动区域并按顺序提取转发、评论、点赞
                base_path = './/div[@class="woo-box-flex woo-box-alignCenter toolbar_left_2vlsY toolbar_main_3Mxwo"]/div[contains(@class, "toolbar_item_1ky_D")]'
                item['reposts'] = article.xpath(f'({base_path})[1]//text()').getall()
                item['comments'] = article.xpath(f'({base_path})[2]//text()').getall()
                item['likes'] = article.xpath(f'({base_path})[3]//text()').getall()
                item['reposts'] = extract_numeric_value(item.get('reposts', []))
                item['comments'] = extract_numeric_value(item.get('comments', []))
                item['likes'] = extract_numeric_value(item.get('likes', []))
                yield item
                success_count += 1

                # 达到最大条目数则停止
                if success_count >= self.maxscount:
                    self.logger.info(f"已爬取 {success_count} 条数据，达到上限，停止爬取。")
                    await page.close()
                    return

            # 滚动加载
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(5000)
            new_height = await page.evaluate("document.body.scrollHeight")

            if new_height == previous_height:
                self.logger.info("页面无新内容加载，结束滚动。")
                break

            previous_height = new_height
            html = await page.content()
            selector = scrapy.Selector(text=html)
# 简单数据清洗
def extract_numeric_value(text_list):
    combined = ''.join([t.strip() for t in text_list if t.strip()])
    numeric = ''.join(filter(str.isdigit, combined))
    return int(numeric) if numeric else 0