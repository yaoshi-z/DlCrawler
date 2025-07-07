# -*- coding: utf-8 -*-
"""
模板名称
    * 模板编号: 0801
    * 模板名称: 网易云音乐榜单免费模板
--------------------
功能：提取指定URL的的帖子详情信息（批次号/歌单ID/歌单标题/歌曲ID/歌曲标题/时长/歌手/专辑/歌曲url）
使用：
    * 爬取前需在wy_music_free_config.py中设置推荐的配置参数
    * start_urls需从data/start_urls/wy_music_free_urls.csv文件读取;
        - 需手动添加url至csv文件
        🔴特别注意: url中不能带"#"; 若录入歌单URL,可能出现数据获取不全现象
            榜单URL,示例:https://music.163.com/discover/toplist?id=991319590
            歌单URL,示例:https://music.163.com/playlist?id=991319590 
    * 增加并发数量,减少或禁用人类模拟行为可以提升抓取效率,但会增加反爬虫风险,需根据实际情况自行调整
        - 起始urls为1个时,有效并发数量始终为1
    * 本模板是否登录均可,但推荐登录
"""
import scrapy
from datetime import datetime
from DlCrawler.items import WyMusicFreeItem
from DlCrawler.configs.wy.wy_music_free_config import CUSTOM_SETTINGS
import random
import pathlib
import datetime
import re
import requests
import time

class WyMusicFreeSpider(scrapy.Spider):
    # 基础参数
    name = "wy_music_free"
    allowed_domains = ["music.163.com"]
    start_urls = []
    current_page = 1  # 当前页码
    
    # 加载配置参数
    custom_settings = CUSTOM_SETTINGS

    # 最大获取数量
    max_count = CUSTOM_SETTINGS['MAXCOUNT']
    success_count = 0
    
    # cookies文件路径初始化
    cookies_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "cookies"
    cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
    cookies_file = cookies_dir / f"{name}_cookies.txt"

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
    def parse_cookies(self, cookies_file):
        try:
            with open(cookies_file, "r") as f:
                raw_cookies = f.read().strip()
            cookies_dict = {}
            for item in raw_cookies.split(";"):
                item = item.strip()
                key, value = item.split("=", 1)
                cookies_dict[key] = value
            return cookies_dict
        except Exception as e:
            self.logger.error(f"解析cookies文件失败：{e}")
            return None
    def start_requests(self):
        # 发起登录请求
        for target_url in self.start_urls:
            if self.cookies_file.exists(): 
                cookies = self.parse_cookies(self.cookies_file)
                yield scrapy.Request(
                target_url,
                cookies=cookies,
                callback=self.parse
            )
    def parse(self, response):
        for item in self.parse_page_content(response):
            yield item
    def parse_page_content(self, response):
        # 初始化必要对象
        html = response.text

        # # 临时调试,需要时自行取消注释
        # try:
        #     debug_dir = pathlib.Path(__file__).parent.parent.parent / "debug_files"
        #     debug_dir.mkdir(parents=True, exist_ok=True)
        #     with open(f"{debug_dir}/{self.name}_p{self.current_page}.html", "w", encoding="utf-8") as f:
        #         f.write(html)
        # except Exception as e:
        #     self.logger.info(f"保存文件失败：{e}")

        playlist_id = response.url.split('=')[-1]

        title_line = response.xpath('//title').get()
        pattern = r'<title>(.*?) - .*?</title>'
        match = re.search(pattern, title_line)
        playlist_title = match.group(1).strip() if match else "Unknown Playlist"
       
        song_infos = re.findall(r'<a href="/song\?id=(\d+)">(.*?)</a>', html)

        for song_id,song_title in song_infos:  # 遍历每首歌曲信息
            if self.success_count >= self.max_count:
                self.logger.info(f"达到上限{self.max_count}, 终止当前页解析")
                break 
            item = WyMusicFreeItem()
            
            item['batch_id'] = self.now
            item['playlist_id'] = playlist_id
            item['playlist_title'] = playlist_title
            item['song_id'] = song_id
            item['song_title'] = song_title
            item['song_url'] = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

            self.success_count += 1
           
            self.logger.info(f'''已获取 第{self.success_count} 条数据:
                             playlist_id:{item['playlist_id']}
                             song_id:{item['song_id']}
                             song_title:{item['song_title']}
                             ...
''')
            
            if self.is_download_music:
                self.download_music(item['song_url'], item['song_title'],self.cookies_file)
            yield item

    def download_music(self, song_url, song_title,cookies_file):
        download_dir = pathlib.Path(__file__).parent.parent.parent / "download" / self.name
        download_dir.mkdir(parents=True, exist_ok=True)
        file_path = download_dir / f"{song_title}.mp3"
        with open(cookies_file, "r") as f:
            raw_cookies = f.read().strip()

        response = requests.get(song_url,headers={
                                'User-Agent': self.custom_settings['USER_AGENT'],
                                'cookies': raw_cookies,
                                'Referer': 'https://music.163.com/'
                                },
                                stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            self.logger.info(f"✅成功下载音乐: {song_title}.mp3")
        else:
            self.logger.error(f"❌下载失败: {song_title} (状态码: {response.status_code})")

        time.sleep(random.uniform(0.5, 1.5))
        print(f"🕑随机休眠0.5-1.5秒")