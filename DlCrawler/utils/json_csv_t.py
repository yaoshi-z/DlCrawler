import pandas as pd
import pathlib

dir_path = pathlib.Path(__file__).parent.parent / "exports"
file_name = "taobao_search_keywords_音响_20250625151931.json"

file_path = dir_path / file_name
df = pd.read_json(file_path)
df.to_csv(dir_path / "taobao_search_keywords_音响_20250625151931.csv", index=False)