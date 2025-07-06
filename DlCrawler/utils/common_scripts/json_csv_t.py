import pandas as pd
import pathlib

dir_path = pathlib.Path(__file__).parent.parent / "exports"
file_name = "weibo_search_keywords_扫地机器人_20250616_175642.json"
file_path = dir_path / file_name

if file_name.endswith(".json"):
    df = pd.read_json(file_path)
    csv_path = file_path.with_suffix(".csv")
    df.to_csv(csv_path, index=False)
    print(f"{file_name} 转换为 {csv_path.name} 成功")
elif file_name.endswith(".csv"):
    df = pd.read_csv(file_path)
    json_path = file_path.with_suffix(".json")
    df.to_json(json_path, orient="records")
    print(f"{file_name} 转换为 {json_path.name} 成功")