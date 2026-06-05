import requests
import base64
import json
import os
import re
import socket
import concurrent.futures
from datetime import datetime
from urllib.parse import quote, unquote

# ================= ⚙️ 核心配置区 ⚙️ =================
IPINFO_TOKEN = "0d0e75c597bed0"  # 👈 请将你的 ipinfo.io Token 填在这里

# 节点订阅源库
SOURCE_URLS = [
    "https://cdn.jsdelivr.net/gh/Pawdroid/Free-servers@main/sub",
    "https://cdn.jsdelivr.net/gh/mfuu/v2ray@master/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202605312",
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/list.txt",
    "https://github.cmliussss.net/https://raw.githubusercontent.com/qmqv/jd07/refs/heads/main/v207-1010.txt",
    "https://ghfast.top/https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt",
    "https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
    "https://sub.proxygo.org/v2ray.php?key=191c91f624a800e83942463fd667bba5",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_BASE64.txt",
    "https://app.sublink.works/x/ZrVEXNV",
    "https://gcore.jsdelivr.net/gh/aews/jd2/v20528.txt",
    "https://mm.mibei77.com/202606/06.0564bacrt.txt",
    "https://mm.mibei77.com/202606/06.0664bacrt.txt",
    "https://mm.mibei77.com/202606/06.0764bacrt.txt",
    "https://mm.mibei77.com/202606/06.0864bacrt.txt",
    "https://gt.1155555.xyz/https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt"
    ]

SUPPORTED_PROTOCOLS = ("vmess://", "vless://", "trojan://", "ss://", "ssr://")
BLACKLIST_KEYWORDS = ["广告", "官网", "群", "频道", "最新", "更新", "VIP", "网址", "剩余"]

# 全球国家/地区代码对照表 (适配 ipinfo.io 的 ISO 2位字母代码)
COUNTRY_MAP = {
    # 亚洲
    "CN": "🇨🇳中国", "TW": "🇹🇼台湾", "HK": "🇭🇰香港", "MO": "🇲🇴澳门", 
    "JP": "🇯🇵日本", "KR": "🇰🇷韩国", "KP": "🇰🇵朝鲜",
    "SG": "🇸🇬新加坡", "MY": "🇲🇾马来西亚", "ID": "🇮🇩印度尼西亚", 
    "TH": "🇹🇭泰国", "VN": "🇻🇳越南", "PH": "🇵🇭菲律宾", 
    "KH": "🇰🇭柬埔寨", "MM": "🇲🇲缅甸", "LA": "🇱🇦老挝", "BN": "🇧🇳文莱",
    "IN": "🇮🇳印度", "PK": "🇵🇰巴基斯坦", "BD": "🇧🇩孟加拉国", 
    "LK": "🇱🇰斯里兰卡", "NP": "🇳🇵尼泊尔",
    "KZ": "🇰🇿哈萨克斯坦", "UZ": "🇺🇿乌兹别克斯坦", "MN": "🇲🇳蒙古",
    
    # 欧洲
    "GB": "🇬🇧英国", "DE": "🇩🇪德国", "FR": "🇫🇷法国", "IT": "🇮🇹意大利", 
    "ES": "🇪🇸西班牙", "PT": "🇵🇹葡萄牙", "NL": "🇳🇱荷兰", "BE": "🇧🇪比利时", 
    "CH": "🇨🇭瑞士", "AT": "🇦🇹奥地利", "IE": "🇮🇪爱尔兰",
    "SE": "🇸🇪瑞典", "NO": "🇳🇴挪威", "DK": "🇩🇰丹麦", "FI": "🇫🇮芬兰", "IS": "🇮🇸冰岛",
    "RU": "🇷🇺俄罗斯", "UA": "🇺🇦乌克兰", "PL": "🇵🇱波兰", "CZ": "🇨🇿捷克", 
    "HU": "🇭🇺匈牙利", "RO": "🇷🇴罗马尼亚", "BG": "🇧🇬保加利亚", "GR": "🇬🇷希腊",
    "RS": "🇷🇸塞尔维亚", "HR": "🇭🇷克罗地亚", "SK": "🇸🇰斯洛伐克", "LT": "🇱🇹立陶宛",
    "LV": "🇱🇻拉脱维亚", "EE": "🇪🇪爱沙尼亚", "BY": "🇧🇾白俄罗斯",

    # 美洲
    "US": "🇺🇸美国", "CA": "🇨🇦加拿大", "MX": "🇲🇽墨西哥",
    "BR": "🇧🇷巴西", "AR": "🇦🇷阿根廷", "CL": "🇨🇱智利", "CO": "🇨🇴哥伦比亚",
    "PE": "🇵🇪秘鲁", "VE": "🇻🇪委内瑞拉", "EC": "🇪🇨厄瓜多尔", "UY": "🇺🇾乌拉圭",
    "CR": "🇨🇷哥斯达黎加", "PA": "🇵🇦巴拿马", "CU": "🇨🇺古巴",

    # 大洋洲
    "AU": "🇦🇺澳大利亚", "NZ": "🇳🇿新西兰", "FJ": "🇫🇯斐济",

    # 中东
    "AE": "🇦🇪阿联酋", "SA": "🇸🇦沙特阿拉伯", "IL": "🇮🇱以色列",
    "TR": "🇹🇷土耳其", "IR": "🇮🇷伊朗", "IQ": "🇮🇶伊拉克", "QA": "🇶🇦卡塔尔",
    "KW": "🇰🇼科威特", "OM": "🇴🇲阿曼", "BH": "🇧🇭巴林", "LB": "🇱🇧黎巴嫩",

    # 非洲
    "ZA": "🇿🇦南非", "EG": "🇪🇬埃及", "NG": "🇳🇬尼日利亚", "KE": "🇰🇪肯尼亚",
    "MA": "🇲🇦摩洛哥", "DZ": "🇩🇿阿尔及利亚", "TN": "🇹🇳突尼斯", "GH": "🇬🇭加纳",
    "TZ": "🇹🇿坦桑尼亚", "SN": "🇸🇳塞内加尔", "UG": "🇺🇬乌干达", "AO": "🇦🇴安哥拉"
}

def fetch_and_decode(url):
    """抓取并解码订阅内容"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text.strip()
        try:
            missing_padding = len(text) % 4
            if missing_padding != 0:
                text += '=' * (4 - missing_padding)
            decoded_text = base64.b64decode(text).decode('utf-8')
            return decoded_text.splitlines()
        except Exception:
            return text.splitlines()
    except Exception as e:
        print(f"[!] 获取失败: {url} | 错误: {e}")
        return []

def get_host_from_link(link):
    """提取 IP 或 域名"""
    host = ""
    try:
        if link.startswith("vmess://"):
            b64_str = link[8:]
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            data = json.loads(base64.b64decode(b64_str).decode('utf-8'))
            host = data.get('add', '')
        elif link.startswith(("vless://", "trojan://")):
            match = re.search(r'@[^:]+:(?:\d+)', link)
            if match:
                host = match.group(0)[1:].split(':')[0]
        elif link.startswith("ss://"):
            if '@' in link:
                match = re.search(r'@[^:]+:(?:\d+)', link)
                if match:
                    host = match.group(0)[1:].split(':')[0]
            else:
                b64_str = link[5:].split('#')[0]
                b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
                decoded = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
                match = re.search(r'@[^:]+:(?:\d+)', decoded)
                if match:
                    host = match.group(0)[1:].split(':')[0]
    except Exception:
        pass
    return host

def resolve_host(host):
    """将域名解析为 IP，如果是纯 IP 则直接返回"""
    if not host: return host, None
    # 判断是否已经是 IPv4 地址
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        return host, host
    try:
        ip = socket.gethostbyname(host)
        return host, ip
    except Exception:
        return host, None

def batch_get_countries_ipinfo(hosts):
    """使用 ipinfo.io 的 Token 批量查询 IP 归属地"""
    unique_hosts = list(set([h for h in hosts if h]))
    host_to_ip = {}
    
    print(f"[*] 检测到 {len(unique_hosts)} 个独立主机地址，正在进行多线程 DNS 解析...")
    
    # 开启20个线程光速解析域名
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(resolve_host, unique_hosts)
        for host, ip in results:
            if ip: host_to_ip[host] = ip

    unique_ips = list(set(host_to_ip.values()))
    ip_to_country = {}
    
    print(f"[*] 解析完成，获得 {len(unique_ips)} 个有效 IP，正在通过 ipinfo.io 查询归属地...")
    
    # ipinfo.io 的 batch 接口每次最多处理 1000 个，这里我们切片 500 一次以保稳定
    for i in range(0, len(unique_ips), 500):
        batch = unique_ips[i:i+500]
        try:
            url = f"https://ipinfo.io/batch?token={IPINFO_TOKEN}"
            res = requests.post(url, json=batch, timeout=15).json()
            
            for query_ip in batch:
                info = res.get(query_ip, {})
                if isinstance(info, dict) and 'country' in info:
                    country_code = info['country']
                    # 从字典匹配，没有的直接返回国家代码
                    country_zh = COUNTRY_MAP.get(country_code, f"📍{country_code}")
                    ip_to_country[query_ip] = country_zh
                else:
                    ip_to_country[query_ip] = "🌍未知区域"
        except Exception as e:
            print(f"[!] ipinfo.io API 请求失败: {e}")
            for query_ip in batch:
                ip_to_country[query_ip] = "🌍未知区域"
                
    # 将结果映射回最初的域名/IP
    ip_cache = {}
    for host in unique_hosts:
        ip = host_to_ip.get(host)
        if ip and ip in ip_to_country:
            ip_cache[host] = ip_to_country[ip]
        else:
            ip_cache[host] = "🌍未知区域"
            
    return ip_cache

def rename_node(link, new_name):
    """根据协议格式重写节点名称"""
    try:
        if link.startswith("vmess://"):
            b64_str = link[8:]
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            data = json.loads(base64.b64decode(b64_str).decode('utf-8'))
            data['ps'] = new_name
            new_b64 = base64.b64encode(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
            return f"vmess://{new_b64}"
            
        elif link.startswith(("vless://", "trojan://", "ss://", "ssr://")):
            if "#" in link:
                base_link = link.split("#", 1)[0]
            else:
                base_link = link
            return f"{base_link}#{quote(new_name)}"
    except Exception:
        return link
    return link

def main():
    if IPINFO_TOKEN == "在这里填入你的Token":
        print("[!] 严重警告: 你还没有配置 IPINFO_TOKEN！脚本可能会无法获取归属地。")
        
    print(f"=== 开始执行高级抓取与清洗任务 (ipinfo版) {datetime.now()} ===")
    all_lines = []
    
    for url in SOURCE_URLS:
        all_lines.extend(fetch_and_decode(url))
        
    valid_nodes = []
    
    for line in all_lines:
        line = line.strip()
        if not line.startswith(SUPPORTED_PROTOCOLS): continue
        is_bad = any(keyword.lower() in line.lower() for keyword in BLACKLIST_KEYWORDS)
        if is_bad: continue
        valid_nodes.append(line)
        
    valid_nodes = list(set(valid_nodes))
    print(f"[*] 成功获取并去重，共计 {len(valid_nodes)} 个节点")
    
    hosts = [get_host_from_link(node) for node in valid_nodes]
    ip_cache = batch_get_countries_ipinfo(hosts)
    
    print("[*] 分析完毕，正在按国家分配序号并进行整理排序...")
    
    node_objects = []
    country_counters = {}
    
    for i, node in enumerate(valid_nodes):
        host = hosts[i]
        country = ip_cache.get(host, "🌍未知区域")
        
        if country not in country_counters:
            country_counters[country] = 1
        else:
            country_counters[country] += 1
            
        new_name = f"{country} {country_counters[country]:02d}"
        renamed_node = rename_node(node, new_name)
        
        node_objects.append({
            "country": country,
            "link": renamed_node
        })
        
    # 按照国家名称自动合并归类并排序
    node_objects.sort(key=lambda x: x["country"])
    final_nodes = [item["link"] for item in node_objects]
        
    print(f"[*] 排序与重命名完成，共生成 {len(final_nodes)} 个定制化节点！")
    
    os.makedirs('output', exist_ok=True)
    raw_text = "\n".join(final_nodes)
    
    with open('output/nodes.txt', 'w', encoding='utf-8') as f:
        f.write(raw_text)
        
    sub_base64 = base64.b64encode(raw_text.encode('utf-8')).decode('utf-8')
    with open('output/sub.txt', 'w', encoding='utf-8') as f:
        f.write(sub_base64)

if __name__ == "__main__":
    main()
