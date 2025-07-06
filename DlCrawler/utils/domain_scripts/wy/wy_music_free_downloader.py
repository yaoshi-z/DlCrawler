"""
网易云音乐免费歌曲采集工具
仅用于个人学习和技术研究
请勿用于商业用途或大规模传播
下载后24小时内请删除文件
"""

import requests
import re
import os
import pathlib
from urllib.parse import quote

script_name = "wy_music_free_downloader"
save_dir = pathlib.Path(__file__).parent.parent.parent.parent / "download" / script_name
save_dir.mkdir(parents=True, exist_ok=True)

headers = {
    'cookies': "_ntes_nnid=73be8502eeb9e5b0e9ed8cbef591a73d,1720929779336; _ntes_nuid=73be8502eeb9e5b0e9ed8cbef591a73d; nts_mail_user=wangdeyaoshi@163.com:-1:1; NTES_P_UTID=KZW6CxiAp6R1Icnytmy9HTOOuHk4F6ji|1743753704; P_INFO=wangdeyaoshi@163.com|1743753704|0|mail163|00&99|null&null&null#hen&411600#10#0#0|&0||wangdeyaoshi@163.com; NMTID=00O7_vywF-BF_0P3keburWGeB4noeEAAAGX2ZN8BA; WEVNSM=1.0.0; WNMCID=ciodps.1751702011646.01.0; WM_TID=bF9TDI0NoORFURFRRQbXbrbC10vEUspx; sDeviceId=YD-wPDsC1UmNctEUgQBAFPWfvaXw1%2BBCD2s; ntes_utid=tid._.tCke%252BF1GD2VFUhUAEQOXbrOXgx7UWRxt._.0; __snaker__id=kudhDfWD4eoksgws; ntes_kaola_ad=1; _iuqxldmzr_=32; WM_NI=%2B8tj4teGyRsvgOwmiFln56r10eDxzTxY%2BTcOokhSuDH2TXSwt47GUXD5Fzhrcfq0EFJf%2FaAoWNkT5jL8Wm4KEqg5cmqL01iRaQvMTW7vqXrWwG8aPRFxq8Wem5gNRUmAYkg%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eedab16e8893f8d9c97a86868aa2d14a868a9fadd76af5bfa7dabb7ca5869793f22af0fea7c3b92ae9e8bc8bb780a799b7b3f27ea591b98eec4eb0b2fbd7f13bf4bb8c99f960bc87e5b5e245adb5a8b4f8508cee9cb9d27db8ecf9a8d85488eb8a9beb7aa1babfd1c84e8abae182c4659592a5b5b86290e8998eb74187afa9d6e267b39400d2ec5aa38fbaaed75df5aabfb9f15db599f882d35a86a8bfd9d66fafeba9afd15faf9f978ce637e2a3; MUSIC_U=00B8D3DD7FDB779EE96B0F8909C4BF446A0F6FA6469BD2C3EEC3F326F769C7F4BDDE183B89AF2EA698DC927811F6564CC4D01902FA189245E92409FE59C473BB816AA9370E6AE68ABDE0801D272AAA112E2FAA7E220A0BC62A976BDD4ADB07CDBB6075DE6306B57DD7380C70C8461132AA27E2AD38816037D83AFC79A609EB790C53B9E945D957FAC5224C40AAB551FD39CBA947032F505829348147DF18D6C3A1FE88BDB3F6E956BA8F9F818FD4B9736ED7E5D761CA06292BD507E07C5B433A9C348890D087446066EA7FB304B42A0CAB43511B8B3DB35DA88E71ED376EF70365D34CD2593ABEAE656D372161467A0A3B32F0C842642EB10119B7672FB653A77E609115746174AF1E49DEED958D5DC8E14B28147FC9B754EF9DEAFDC27D509014FD483A2176C3017F352C5329412B5A1D739C7398A96974EBB4F271EB2D481C0004A897E29F888B5610CAF77804FC7C5C8D60D25378B69ED59E1E1B72593411E3; __remember_me=true; __csrf=a8c4f3d5efe76ad9ed32be076f1cf662; gdxidpyhxdE=pILlGT8SvNmv7TYzSE3vZkpeydhPBnIp1XRQXbOfhdBbjQEfjEW2APXgufAZNL9eKU1DV%2FxTGGi28Ob%5Csbg0bP2f0hw5JQiNBW33k%2FWD6h6%2BUcDsu1JolIOi17l74q63qLrp7CkDNusnU87GokYQcvsm5VbnmofNUO8P6q65XnsERDZ9%3A1751794423873; playerid=99367264; JSESSIONID-WYYY=qywTE3MaTruD0t3KIkk3IdQ%2Fmhoj6KKq9fKlM5wDgRM8M4PypetnGZrawssxMKaDf4HfcKFTZKonSAhmAoyJ7Vr4B%2FhKdMcPzg4Pwq%2BVQS3%2FpRH3jYI4UI%5C4K5nh1ouy0hNpEsbWouAmxq%2F8nzs%2FgztTNpM1%2Fwsa%2FN7mW4J4AY0SNtoA%3A1751798353879",  # 保持您的完整 cookies
    'referer': "https://music.163.com/",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

def download_music(music_id, title, save_dir=save_dir):
    """
    下载单首歌曲
    :param music_id: 歌曲ID
    :param title: 歌曲标题
    :param save_dir: 保存目录
    """
    
    # 构建下载URL,官方公开免费歌曲外链接
    download_url = f"http://music.163.com/song/media/outer/url?id={music_id}.mp3"
    
    # 发送请求下载文件
    response = requests.get(download_url, headers=headers, stream=True)
    
    if response.status_code == 200:
        # 清理文件名（移除非法字符）
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        file_path = save_dir / f"{safe_title}.mp3"
        
        # 分块写入文件
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
        print(f"✅ 下载成功: {title} | 保存位置: {file_path}")
        return True
    else:
        print(f"❌ 下载失败: {title} | 状态码: {response.status_code}")
        return False

# 主程序
if __name__ == "__main__":
    # 获取歌单信息（使用您已有的代码）
    url = "https://music.163.com/playlist?id=2511560749"
    html = requests.get(url, headers=headers).text
    
    # 提取歌曲ID和标题
    infos = re.findall(r'<a href="/song\?id=(\d+)">(.*?)</a>', html)
    
    # 下载所有歌曲
    for music_id, title in infos:
        print(f"开始下载: {title} (ID: {music_id})")
        download_music(music_id, title)