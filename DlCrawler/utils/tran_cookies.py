import json
import pathlib


cookies_str = 'SINAGLOBAL=5699850404481.164.1720929044940; SCF=Aj6DnJ_VeMkl7eSlLVNRI-hTXoZCaO-s8C_KBKhFc2t1hRlVL2KAicznkP-ZjxZ0ukNf26OtLla9AdzlHy-KnSM.; UOR=,,www.google.com; _s_tentry=-; Apache=423915468332.2455.1749646763268; ULV=1749646763303:8:5:5:423915468332.2455.1749646763268:1749431595918; SUB=_2A25FTkf3DeRhGeFL7VYT8SbPyjyIHXVmIsU_rDV8PUNbmtANLWnVkW9Nfc3w40sLht2Z75go9Y1xBFA_oTxv1gAn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFPvd6jAqcuImakb7Vz8uPf5JpX5KzhUgL.FoMfSoBEeKn0eK52dJLoIpMLxK.L1KzLBK-LxK-L12eL1KLu9PLkwntt; ALF=02_1752286375'
cookies = {}
for item in cookies_str.split(';'):
    key, value = item.strip().split('=', 1)
    cookies[key] = value

cookies_dir = pathlib.Path(__file__).parent.parent / "data" / "cookies"
cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
spider_name = "weibo_search_keywords"
cookies_file = cookies_dir / f"{spider_name}_cookies.json"

with open(cookies_file, 'w', encoding='utf-8') as f:
    json.dump(cookies, f, ensure_ascii=False, indent=4)
