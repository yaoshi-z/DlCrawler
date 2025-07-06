import pymongo

def test_connection():
    try:
        # 使用与 Scrapy 相同的配置
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["scrapytutorial"]
        
        # 验证连接
        print("Server version:", client.server_info()["version"])
        print("Database list:", client.list_database_names())
        print("Connection successful!")
    except Exception as e:
        print("Connection failed:", str(e))

if __name__ == "__main__":
    test_connection()