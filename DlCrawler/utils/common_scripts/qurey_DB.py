import csv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pathlib

spider_name = input("请输入爬虫名称(例:baidu_tieba_topic)：")

database_name,collection_name = spider_name.split("_",1)
# MongoDB配置（来自上下文）
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGODB_DATABASE = database_name
MONGODB_COLLECTION = collection_name

def query_and_export_to_csv():
    """从MongoDB查询数据并导出为CSV文件"""
    try:
        # 连接数据库
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE]
        collection = db[MONGODB_COLLECTION]
        
        client.admin.command('ping')
        print("✅ 成功连接MongoDB")
        
        # 1. 获取批次ID
        batch_id_input = input("请输入批次ID(留空使用最新批次): ")

        # 2. 获取集合所有字段名作为参考
        sample_doc = collection.find_one()
        if not sample_doc:
            print("❌ 集合为空，请检查数据库内容")
            return
            
        all_fields = list(sample_doc.keys())
        # 移除系统字段_id
        if "_id" in all_fields:
            all_fields.remove("_id")
            
        print(f"📋 可用字段参考: {', '.join(all_fields)}")
        
        # 3. 获取用户输入的查询参数（带智能回退）
        fields_input = input("请输入需要导出的字段(多个用逗号分隔，留空导出所有字段): ")
        
        # 4. 智能处理batch_id
        batch_id = batch_id_input
        if not batch_id_input:
            # 查找最大的batch_id
            latest_batch = collection.find_one(
                sort=[("batch_id", -1)],
                projection={"batch_id": 1}
            )
            
            if latest_batch:
                batch_id = latest_batch["batch_id"]
                print(f"ℹ️ 使用最新批次ID: {batch_id}")
            else:
                print("⚠️ 未找到任何批次数据，使用空查询条件")
                batch_id = None
        
        # 5. 构建查询条件
        query = {"batch_id": batch_id} if batch_id else {}
        
        # 验证batch_id是否存在（如果用户提供了特定batch_id）
        if batch_id_input and batch_id_input != batch_id:
            count = collection.count_documents(query)
            if count == 0:
                print(f"⚠️ 警告: batch_id={batch_id_input} 不存在，已使用最新批次 {batch_id}")
        
        # 6. 构建投影条件
        projection = {}
        if fields_input:
            fields = [f.strip() for f in fields_input.split(",")]
            valid_fields = []
            
            for field in fields:
                if field in all_fields:
                    projection[field] = 1
                    valid_fields.append(field)
                else:
                    print(f"⚠️ 忽略无效字段: {field}")
            
            # 自动包含batch_id（如果查询中使用了batch_id）
            if batch_id and "batch_id" not in projection and "batch_id" in all_fields:
                projection["batch_id"] = 1
                valid_fields.append("batch_id")
            
            if not valid_fields:
                print("⚠️ 所有指定字段无效，将导出所有字段")
                projection = {}  # 回退到所有字段
        else:
            # 导出所有字段（排除_id）
            projection = {"_id": 0}
        
        # 7. 执行查询
        cursor = collection.find(query, projection)
        documents = list(cursor)
        
        if not documents:
            print(f"❌ 未找到匹配记录 (batch_id={batch_id or '所有批次'})")
            return
        
        # 导出CSV
        output_dir = pathlib.Path(__file__).parent / "query_db_output"
        csv_file = f"{spider_name}_batch_{batch_id or 'all'}.csv"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = output_dir / csv_file
        fieldnames = documents[0].keys()  # 使用第一个文档的键作为列头
        
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(documents)
            
        print(f"💾 数据已导出到 {csv_file} (共 {len(documents)} 条记录)")
        
    except ConnectionFailure:
        print("❌ 连接数据库失败，请检查配置并重新运行")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    query_and_export_to_csv()