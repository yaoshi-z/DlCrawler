import json
import pathlib


cookies_str = '_ntes_nnid=73be8502eeb9e5b0e9ed8cbef591a73d,1720929779336; _ntes_nuid=73be8502eeb9e5b0e9ed8cbef591a73d; nts_mail_user=wangdeyaoshi@163.com:-1:1; NTES_P_UTID=KZW6CxiAp6R1Icnytmy9HTOOuHk4F6ji|1743753704; P_INFO=wangdeyaoshi@163.com|1743753704|0|mail163|00&99|null&null&null#hen&411600#10#0#0|&0||wangdeyaoshi@163.com; NMTID=00O7_vywF-BF_0P3keburWGeB4noeEAAAGX2ZN8BA; WEVNSM=1.0.0; WNMCID=ciodps.1751702011646.01.0; WM_TID=bF9TDI0NoORFURFRRQbXbrbC10vEUspx; sDeviceId=YD-wPDsC1UmNctEUgQBAFPWfvaXw1%2BBCD2s; ntes_utid=tid._.tCke%252BF1GD2VFUhUAEQOXbrOXgx7UWRxt._.0; __snaker__id=kudhDfWD4eoksgws; ntes_kaola_ad=1; _iuqxldmzr_=32; playerid=70619276; WM_NI=%2B8tj4teGyRsvgOwmiFln56r10eDxzTxY%2BTcOokhSuDH2TXSwt47GUXD5Fzhrcfq0EFJf%2FaAoWNkT5jL8Wm4KEqg5cmqL01iRaQvMTW7vqXrWwG8aPRFxq8Wem5gNRUmAYkg%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eedab16e8893f8d9c97a86868aa2d14a868a9fadd76af5bfa7dabb7ca5869793f22af0fea7c3b92ae9e8bc8bb780a799b7b3f27ea591b98eec4eb0b2fbd7f13bf4bb8c99f960bc87e5b5e245adb5a8b4f8508cee9cb9d27db8ecf9a8d85488eb8a9beb7aa1babfd1c84e8abae182c4659592a5b5b86290e8998eb74187afa9d6e267b39400d2ec5aa38fbaaed75df5aabfb9f15db599f882d35a86a8bfd9d66fafeba9afd15faf9f978ce637e2a3; MUSIC_U=00B8D3DD7FDB779EE96B0F8909C4BF446A0F6FA6469BD2C3EEC3F326F769C7F4BDDE183B89AF2EA698DC927811F6564CC4D01902FA189245E92409FE59C473BB816AA9370E6AE68ABDE0801D272AAA112E2FAA7E220A0BC62A976BDD4ADB07CDBB6075DE6306B57DD7380C70C8461132AA27E2AD38816037D83AFC79A609EB790C53B9E945D957FAC5224C40AAB551FD39CBA947032F505829348147DF18D6C3A1FE88BDB3F6E956BA8F9F818FD4B9736ED7E5D761CA06292BD507E07C5B433A9C348890D087446066EA7FB304B42A0CAB43511B8B3DB35DA88E71ED376EF70365D34CD2593ABEAE656D372161467A0A3B32F0C842642EB10119B7672FB653A77E609115746174AF1E49DEED958D5DC8E14B28147FC9B754EF9DEAFDC27D509014FD483A2176C3017F352C5329412B5A1D739C7398A96974EBB4F271EB2D481C0004A897E29F888B5610CAF77804FC7C5C8D60D25378B69ED59E1E1B72593411E3; __remember_me=true; __csrf=a8c4f3d5efe76ad9ed32be076f1cf662; JSESSIONID-WYYY=K%5C0IJRmpuA09Dh2iyfOxr%2FksgtOA99NG3emGo9RAblzmaNp6fk%2B1n6VQ59swdBazfK8xiz9plyRuDeAbeH4JuvKfHb4xt%2Be0Uks%2FeYXpcd7xY%2FxUIM1y%2BVEvk2BQc48Hu8Ys1DCsaQ%5ChgTnEkbIuhtXUsKtpwMnkDOdKXKzHsS73FgYJ%3A1751786172312; gdxidpyhxdE=0vIAW%2F78rcMWRyurnxMwCWSrZbQq5Ijw%2F%2FOHIQ%2B2Ap%2BVm%2F9iYj2bmrXbxltkGz%2Fd%2FDsjum462%5C8Mj601A7MGklbHQAb7mWhagzXiSKE7V2h7oxOLmLDL3U5kg8tCXftpu%2F7XCBfv77%5CqEJ50vpGl6durrNJD9%2ByQebvgUacLy6eqTvea%3A1751786023263'
# cookies = {}
# for item in cookies_str.split(';'):
#     key, value = item.strip().split('=', 1)
#     cookies[key] = value

# cookies_dir = pathlib.Path(__file__).parent.parent / "data" / "cookies"
# cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
# spider_name = "wy_music_free"
# cookies_file = cookies_dir / f"{spider_name}_cookies.json"

# with open(cookies_file, 'w', encoding='utf-8') as f:
#     json.dump(cookies, f, ensure_ascii=False, indent=4)
import json
import pathlib
from datetime import datetime, timedelta

# 原始cookie字符串
# cookies_str = '_ntes_nnid=73be8502eeb9b0e9ed8cbef591a73d,1720929779336; ...(省略)...'

# 创建符合Playwright存储状态的字典
storage_state = {
    "cookies": [],
    "origins": []
}

# 解析cookie字符串并构建符合格式的列表
for item in cookies_str.split(';'):
    key, value = item.strip().split('=', 1)
    
    # 创建cookie字典
    cookie_dict = {
        "name": key,
        "value": value,
        "domain": ".music.163.com",  # 网易云音乐的域名
        "path": "/",
        "expires": (datetime.now() + timedelta(days=365)).timestamp(),  # 1年后过期
        "httpOnly": False,
        "secure": True,  # 网易云音乐使用HTTPS
        "sameSite": "Lax"
    }
    
    # 特殊处理某些cookie
    if key in ["MUSIC_U", "__remember_me", "__csrf"]:
        cookie_dict["httpOnly"] = True
        cookie_dict["secure"] = True
    
    storage_state["cookies"].append(cookie_dict)

# 添加origins信息（可选）
storage_state["origins"].append({
    "origin": "https://music.163.com",
    "localStorage": [{"name": "user_preference", "value": "zh_CN"}]
})

# 创建cookies目录
cookies_dir = pathlib.Path(__file__).parent.parent / "data" / "cookies"
cookies_dir.mkdir(parents=True, exist_ok=True)

# 保存为JSON文件
spider_name = "wy_music_free"
cookies_file = cookies_dir / f"{spider_name}_cookies.json"

with open(cookies_file, 'w', encoding='utf-8') as f:
    json.dump(storage_state, f, ensure_ascii=False, indent=4)

print(f"Cookies已成功转换为Playwright格式并保存至: {cookies_file}")
