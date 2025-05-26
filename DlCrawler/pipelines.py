from scrapy.exceptions import DropItem
import pymongo 
from motor.motor_asyncio import AsyncIOMotorClient
from twisted.internet import defer
        
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