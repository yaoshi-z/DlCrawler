import pandas as pd
import pathlib

file_name = "模板列表.csv"
dir_path = pathlib.Path(__file__).parent.parent.parent
dir_path.mkdirs(parents=True,exist_ok=True)
file_path = dir_path / file_name

try:
    df = pd.read_csv(file_path,encoding="gbk")
    df.to_csv(file_path, index=False,encoding="utf-8-sig")
    print(f"{file_name} 文件转换完成,gbk编码转换成utf-8-sig编码")
except Exception as e:
    print(f"{file_name} 文件转换失败: {e},源文件非gbk编码")