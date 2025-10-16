import requests, re, json,time, random, os
from datetime import datetime, timedelta

corpid = os.getenv("WX_CORPID")
corpsecret = os.getenv("WX_CORPSECRET")
BarkKey = os.getenv("BARK_KEY")

def get_request():
    BOSHI_msgs = ""
    AUTD_msgs = ""
    # 配置请求头
    headers = {
        'User-Agent': '',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    user_agents = [
        # 这里放置至少5个不同的浏览器UA
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; HarmonyOS; HUAWEI LIO-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (HarmonyOS; Tablet; HUAWEI MRX-W09) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.0.0 Safari/537.36'
    ]
    try:
        # 动态设置UA
        headers['User-Agent'] = random.choice(user_agents)

        response = requests.get(
            'https://www.huilvbiao.com/api/gold_indexApi',
            headers=headers,
            timeout=10
        )

        if response.ok:
            binary_data = response.content  # 二进制原始数据[8](@ref)
            decoded_str = binary_data.decode('utf-8', errors='ignore')  # 强制解码并忽略错误
            # print(f"decoded_str: {decoded_str}\n类型: {type(decoded_str)}")
            # 解析数据内容
            # 新增解析逻辑
            for line in decoded_str.split(';'):
                if 'hq_str_gds_AUTD' in line:
                    # 黄金实时价格
                    autd_value = line.split('=')[1].split(',')[0].strip('"')
                    # 今日开盘价格
                    today_start_value = line.split('=')[1].split(',')[8].strip('"')
                    # 计算涨幅百分比 (当前价-开盘价)/开盘价*100%
                    increase_percent = (float(autd_value) - float(today_start_value)) / float(today_start_value) * 100
                    BOSHI_msgs = get_price()
                    AUTD_msgs = f"[{time.strftime('%H:%M:%S')}] 国内黄金实时价格：{autd_value} 今日开盘价格：{today_start_value} 当前涨幅：{increase_percent:.2f}%  "
                elif 'hq_str_hf_XAU' in line:
                    # 现货黄金实时价格
                    autd_value = line.split('=')[1].split(',')[0].strip('"')
                    # 今日开盘价格
                    today_start_value = line.split('=')[1].split(',')[8].strip('"')
                    # 计算涨幅百分比 (当前价-开盘价)/开盘价*100%
                    increase_percent = (float(autd_value) - float(today_start_value)) / float(today_start_value) * 100
                    XAU_msgs = f"[{time.strftime('%H:%M:%S')}] 现货黄金实时价格：{autd_value} 今日开盘价格：{today_start_value} 当前涨幅：{increase_percent:.2f}%  "
                    msg = f"{BOSHI_msgs}\n{XAU_msgs}\n{AUTD_msgs}"
                    # msg = BOSHI_msgs + '\n' + XAU_msgs + '\n' + AUTD_msgs
                    print(msg)
                    return msg
                else:
                    print(f"数据解析失败：无hq_str_gds_AUTD和hq_str_hf_XAU字段")
        else:
            print(f"服务器返回异常：{response.status_code}")

    except Exception as e:
        print(f"请求出错：{str(e)}")

def get_price():
    url = "https://covo.bsmatrix.com/gold-api/api/gold/real"
    headers = {
        "Host": "covo.bsmatrix.com",
        "Connection": "keep-alive",
        "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.61(0x18003d2e) NetType/4G Language/zh_CN",
        "Referer": "https://servicewechat.com/wx56b297f34fb1e3e1/9/page-frame.html"
    }

    res = requests.get(url, headers=headers).json()
    currentGoldPrice = res['data']['currentGoldPrice']
    percent = res['data']['percent']
    msgs = f"[{time.strftime('%H:%M:%S')}] 上海黄金实时价格：{currentGoldPrice} 当前涨幅：{percent}%  "
    # print(msgs)
    return msgs


def fetch_gold_9999_data():
    """爬取上海黄金交易所黄金9999的实时行情数据"""
    url = "https://api.jijinhao.com/quoteCenter/realTime.htm"

    params = {'codes': 'JO_71'}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://quote.cngold.org/gjs/jjs.html',
        'Accept': '*/*',
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")

        content = response.text.strip()

        # JSONP格式: var quote_json = {...};
        if 'quote_json' in content:
            # 找到 = 后面的内容
            start_idx = content.find('=') + 1
            json_str = content[start_idx:].strip()

            # 移除末尾的分号
            if json_str.endswith(';'):
                json_str = json_str[:-1].strip()

            print(f"提取JSON长度: {len(json_str)} 字符")

            # 解析JSON
            data = json.loads(json_str)
            print(f"JSON解析成功")

            if 'JO_71' in data:
                print("找到JO_71数据")
                return parse_gold_data(data['JO_71'])
            else:
                print("JO_71不在数据中")
                return None

        print("未能解析到数据")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def parse_gold_data(raw_data):
    """解析从API获取的黄金数据"""
    try:
        print("\n开始解析数据...")
        print(f"原始数据示例: q63={raw_data.get('q63')}, q80={raw_data.get('q80')}")

        def format_value(val, precision=2):
            try:
                if val is None or val == '':
                    return None
                num_val = float(val)
                return round(num_val, precision)
            except:
                return None

        # 时间转换为北京时间
        update_time = None
        if raw_data.get('time'):
            try:
                timestamp = int(raw_data.get('time')) / 1000  # 转为秒
                update_time_utc = datetime.utcfromtimestamp(timestamp)  # 获取 UTC 时间
                update_time_beijing = update_time_utc + timedelta(hours=8)  # 转为北京时间
                update_time = update_time_beijing.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
            except Exception as e:
                print(f"时间转换失败: {e}")
                update_time = str(raw_data.get('time'))

        parsed_data = {
            '商品名称': raw_data.get('showName', '黄金9999'),
            '商品代码': raw_data.get('code', 'JO_71'),
            '最新价': format_value(raw_data.get('q63')),
            '买入价': format_value(raw_data.get('q5')),
            '卖出价': format_value(raw_data.get('q6')),
            '涨跌额': format_value(raw_data.get('q70')),
            '涨跌幅(%)': format_value(raw_data.get('q80'), 2),
            '开盘价': format_value(raw_data.get('q1')),
            '最高价': format_value(raw_data.get('q3')),
            '最低价': format_value(raw_data.get('q4')),
            '昨收价': format_value(raw_data.get('q2')),
            '单位': raw_data.get('unit', '元/克'),
            '更新时间': update_time
        }

        print(f"解析完成，最新价: {parsed_data['最新价']}")
        return parsed_data

    except Exception as e:
        print(f"解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_telegram_message(data):
    """格式化为 Telegram 消息"""
    if not data:
        return "❌ 获取黄金价格失败"

    # 判断涨跌
    change_pct = data.get('涨跌幅(%)')
    if change_pct and change_pct > 0:
        trend = "📈"
    elif change_pct and change_pct < 0:
        trend = "📉"
    else:
        trend = "➖"

    message = f"{trend} 上海黄金交易所 - 黄金9999\n\n"

    # 关键数据
    latest_price = data.get('最新价')
    change_amount = data.get('涨跌额')
    change_pct = data.get('涨跌幅(%)')

    if latest_price:
        message += f"💰 最新价: {latest_price:.2f} {data.get('单位', '元/克')}\n"

    if change_amount is not None and change_pct is not None:
        sign = "+" if change_amount >= 0 else ""
        message += f"📊 涨跌: {sign}{change_amount:.2f} ({sign}{change_pct:.2f}%)\n"

    message += "\n"

    # 详细数据
    if data.get('开盘价'):
        message += f"开盘价: {data['开盘价']:.2f}，"
    if data.get('最高价'):
        message += f"最高价: {data['最高价']:.2f}\n"
    if data.get('最低价'):
        message += f"最低价: {data['最低价']:.2f}，"
    if data.get('昨收价'):
        message += f"昨收价: {data['昨收价']:.2f}\n"

    # 获取更新时间并转换为北京时间
    if data.get('更新时间'):
        message += f"\n🕒 更新时间: {data['更新时间']} (北京时间)"
        print(message, type( message))

    return message


def send_telegram_message(message, XAU_msg):
    """发送消息到 Telegram"""
    # 发送至企业微信
    corpid = os.getenv("WX_CORPID")  # 企业ID
    corpsecret = os.getenv("WX_CORPSECRET")  # Secret
    Agentid = "1000003"
    if not corpid or not corpsecret:
        print("⚠️ 企业微信环境变量未设置")
        return False
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    }
    get_access_token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}'
    access_token = requests.get(get_access_token_url).json()['access_token']
    push_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    match = re.search(r'💰 最新价:\s*(\d+\.\d+)\s*元/克', message).group()
    # print(f'match: {match}')
    # print( match,type( match))
    data = {
        "touser": "@all",
        "msgtype": "mpnews",
        "agentid": int(Agentid),
        "mpnews": {
            "articles": [
                {
                    "title": match,
                    "thumb_media_id": "2olmh7kAnR5KVR0BuHzAiOuWEFkBF8ITqi6AQxTUR3bQiFpnP2UukUn9xNtk-LvIm",
                    "author": "锐大神",
                    "content_source_url": "https://www.fglt.net/index.php",
                    "content": XAU_msg.replace(" ", "<br>"),
                    "digest": message,
                }
            ]
        },
    }

    try:
        response = requests.post(url=push_url, json=data, headers=headers)
        if response.status_code == 200:
            print("✅ 企业微信 消息发送成功")
            return True
        else:
            print(f"❌ 企业微信 发送失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 企业微信 发送异常: {e}")
        return False


def Bark(message):
    BarkKey = os.getenv("BARK_KEY")
    if not bark_key:
        print("⚠️ 未设置 BARK_KEY，跳过 Bark 通知")
        return False
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    url = f"https://api.day.app/{BarkKey}"
    title = message
    message = message.replace("<div>", "").replace("</div>", "").replace("<ul>",  "").replace("</ul>", "").replace("<li>", "").replace("</li>", "").replace("<span>", "\n").replace("</span>", "")
    if "最新价" in message:
        data = {
            "title": re.search(r'💰 最新价:\s*(\d+\.\d+)\s*元/克', message).group().strip(),
            "body": message.strip()
        }
    else:
        data = {
            "title": re.search(r'(上海黄金实时价格：(\d+\.\d+))', title).group(1).strip(),
            "body": message.strip()
        }
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"状态码: {response.status_code}\n响应内容: {response.text}")
    except requests.RequestException as e:
        print("请求失败:", e)

def run():
    print("正在获取黄金9999实时数据...\n")
    gold_data = fetch_gold_9999_data()
    if gold_data:
        print("\n" + "=" * 50)
        print("数据获取成功，准备发送到 Telegram...")
        print("=" * 50 + "\n")
        # 格式化消息
        telegram_msg = format_telegram_message(gold_data)
        XAU_msg = get_request()
        # 发送到 Telegram
        # send_telegram_message(telegram_msg, XAU_msg)
        # Bark(XAU_msg)
        # Bark(telegram_msg)
    else:
        print("\n❌ 获取数据失败")
        # 发送失败通知
        error = "❌ 黄金价格获取失败，请检查日志"
        send_telegram_message(error, error)
        # Bark("❌ 黄金价格获取失败，请检查日志")

if __name__ == "__main__":

    run()

