from scrapy.exceptions import DropItem
import pymongo 
from motor.motor_asyncio import AsyncIOMotorClient
from twisted.internet import defer
import pathlib
import datetime
import pandas as pd
        
class MongoDBPipeline(object):
    def __init__(self,connection_string):
        self.connection_string = connection_string
    
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING')
        )
    
    def open_spider(self,spider):
        self.database = spider.settings.get('MONGODB_DATABASE')
        self.collection = spider.settings.get('MONGODB_COLLECTION')
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]
    
    def process_item(self,item,spider):
        collection = self.collection
        self.db[collection].insert_one(dict(item))
        return item
    def close_spider(self,spider):
        self.client.close()

    

class AsyncMongoDBPipeline:
    def __init__(self):
        self.connection_string = None
        self.database = None
        self.collection = None
        self.client = None

    @defer.inlineCallbacks
    def open_spider(self, spider):
        # 使用 inlineCallbacks 将异步代码桥接到 Scrapy 的事件循环
        self.connection_string = yield spider.settings.get('MONGODB_CONNECTION_STRING')
        self.database = yield spider.settings.get('MONGODB_DATABASE')
        self.collection = yield spider.settings.get('MONGODB_COLLECTION')

        if not all([self.collection, self.database]):
            raise DropItem("Missing MongoDB配置: 检查settings.py中的MONGODB_COLLECTION/MONGODB_DATABASE")

        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database]

    async def process_item(self, item, spider):
        if not self.collection:
            raise DropItem("MongoDB集合未初始化")
        
        await self.db[self.collection].insert_one(dict(item))
        return item
    
class CustomExporterPipeline:
    def __init__(self):
        self.items = []
        
        
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        return pipeline
    
    def open_spider(self, spider):
        self.file_format = spider.settings.get('EXPORT_FILE_FORMAT', 'json')
        self.keywords = spider.settings.get('KEYWORDS', 'none')

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        output_dir = pathlib.Path(__file__).parent / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        formatter_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        df = pd.DataFrame(self.items)
        if df.empty:
            spider.logger.warning("没有数据可导出")
            return
        try:
            if self.file_format.lower() == 'json':
                json_file_path = output_dir / f"{spider.name}_{self.keywords}_{formatter_now}.json"
                df.to_json(json_file_path, orient='records', force_ascii=False, indent=4)

            elif self.file_format.lower() == 'csv':
                csv_file_path = output_dir / f"{spider.name}_{self.keywords}_{formatter_now}.csv"
                df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            spider.logger.error(f"导出文件时发生错误: {e}")