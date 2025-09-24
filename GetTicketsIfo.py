# -----------------------------------------------------------------------------------
# 免责声明：此脚本仅用于学习Python爬虫技术
# 不得将其用于商业目的或在12306.cn上自动购买真实车票
# -----------------------------------------------------------------------------------

import time
import requests
import pandas as pd
from datetime import datetime
import json
import urllib.parse # 用于URL编码

# --- 配置 ---
# 使用更完整的请求头字典是模仿真实浏览器的常见做法。
# Accept-Language 设置为中文，因为我们是在模拟访问中文网站
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8", # 优先中文，兼容英文
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}

# --- 核心函数 ---

def get_provinces_data():
    """从12306获取并保存省份数据。"""
    # 修正：移除URL末尾的空格
    url = "https://kyfw.12306.cn/otn/userCommon/allProvince"
    try:
        session = requests.Session()
        response = session.get(url=url, headers=BASE_HEADERS, timeout=10)
        response.raise_for_status()
        content_json = response.json()

        print("Waiting 3 seconds to prevent detection...")
        time.sleep(3)

        content_list = pd.json_normalize(content_json['data'], errors='ignore')

        if not content_list.empty:
            curr_time = datetime.now()
            timestamp = datetime.strftime(curr_time, '%Y-%m-%d_%H-%M-%S')
            filename = f"national_train_agency_provinces-{timestamp}.xlsx"
            content_list.to_excel(filename, index=False)
            print(f"Province data saved to {filename}!")

            rows, cols = content_list.shape
            print(f"Retrieved data shape: {rows} rows, {cols} columns.")
            return content_list, session
        else:
            print("No province data found in the response.")
            return None, session
    except requests.exceptions.RequestException as e:
        print(f"Error fetching province data: {e}")
        return None, None
    except KeyError as e:
        print(f"Error parsing JSON response: Missing key {e}")
        return None, None
    except Exception as e: # 捕获其他潜在错误
        print(f"An unknown error occurred: {e}")
        return None, None

def get_station_codes(session):
    """获取热门车站代码字典。实际应用中可能需要更完整的列表或实时查询。"""
    # 注意：12306的热门车站列表API可能会变化，需要根据实际情况调整
    # 修正：移除URL末尾的空格
    url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
    try:
        response = session.get(url, headers=BASE_HEADERS)
        response.raise_for_status()
        # 响应内容类似：var station_names ='@bjb|北京北|VAP|beijingbei|bjb|0@bjd|北京东|BOP|beijingdong|bjd|1@bji|北京|BJP|beijing|bj|2@...';
        raw_data = response.text
        # 提取车站信息
        if raw_data.startswith("var station_names ='"):
            # 移除前缀和后缀
            stations_str = raw_data[20:-3]
            # 分割每个车站
            stations_list = stations_str.split('@')
            station_dict = {}
            for station in stations_list:
                if station:
                    parts = station.split('|')
                    if len(parts) >= 5: # 确保有足够的部分
                         # 简体中文站名: parts[1], 代码: parts[2]
                        station_dict[parts[1]] = parts[2]
            print(f"Loaded codes for {len(station_dict)} stations.")
            return station_dict
        else:
            print("Failed to parse station code data.")
            return {}
    except Exception as e:
        print(f"Error fetching station codes: {e}")
        return {}

def get_user_input(station_codes):
    """获取用户输入的行程详情。"""
    print("\n--- Ticket Booking Details ---")
    while True:
        date_str = input("Enter travel date (YYYY-MM-DD): ")
        try:
            # 简单验证日期格式
            datetime.strptime(date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    # 获取出发站和到达站代码
    from_station_name = ""
    to_station_name = ""
    from_station_code = ""
    to_station_code = ""

    while not from_station_code:
        from_station_name = input("Enter departure station (e.g., Beijing): ").strip()
        from_station_code = station_codes.get(from_station_name, "")
        if not from_station_code:
             # 尝试模糊匹配
            matches = [name for name in station_codes.keys() if from_station_name in name]
            if matches:
                print(f"No exact match found. Similar stations: {matches[:5]} (showing first 5)")
                # 可以让用户选择，这里简化处理
            print("Station not found. Please check the name.")

    while not to_station_code:
        to_station_name = input("Enter arrival station (e.g., Shanghai): ").strip()
        to_station_code = station_codes.get(to_station_name, "")
        if not to_station_code:
            matches = [name for name in station_codes.keys() if to_station_name in name]
            if matches:
                print(f"No exact match found. Similar stations: {matches[:5]} (showing first 5)")
            print("Station not found. Please check the name.")

    print(f"Query Info: Date={date_str}, From={from_station_name}({from_station_code}), To={to_station_name}({to_station_code})")
    return date_str, from_station_code, to_station_code, from_station_name, to_station_name

def search_tickets(session, date, from_code, to_code):
    """搜索可用的车票。"""
    # 实际的查询API URL (可能需要根据12306更新进行调整)
    # 查询Z开头的车次
    # 修正：移除URL末尾的空格
    search_url = f"https://kyfw.12306.cn/otn/leftTicket/queryZ"
    # 查询其他车次
    # search_url_other = f"https://kyfw.12306.cn/otn/leftTicket/query"

    # 查询参数
    params = {
        'leftTicketDTO.train_date': date,
        'leftTicketDTO.from_station': from_code,
        'leftTicketDTO.to_station': to_code,
        'purpose_codes': 'ADULT' # 成人票
    }

    print(f"\nSearching for tickets on {date} from {from_code} to {to_code}...")
    # --- 反爬虫措施 ---
    print("Applying anti-crawler delay...")
    time.sleep(2) # 添加延迟

    try:
        # 发送GET请求
        response = session.get(search_url, params=params, headers=BASE_HEADERS)
        response.raise_for_status()
        result = response.json()

        # 检查响应状态
        if result.get('status') == True and result.get('httpstatus') == 200:
            data = result.get('data', {}).get('result', [])
            # 修正：补全 if 语句
            if not data:
                print("No train information found for the query.")
                return None

            print("\n--- Search Results ---")
            available_trains = []
            # 12306返回的字段信息通常在 'data.map' 中定义
            # 例如: secretStr, buttonTextInfo, queryLeftNewDTO.*
            for i, item in enumerate(data):
                 # item 是一个包含多个字段的字符串，用 '|' 分隔
                 # 需要根据实际情况解析。这是一个简化示例。
                 # 实际上，'item' 是一个很长的 '|' 分隔的字符串，需要根据 map 来解析。
                 # 这里假设我们只关心前几个关键字段（实际远不止这些）
                fields = item.split('|')
                if len(fields) > 30: # 确保字段足够
                    secret_str = fields[0] # 预订所需密钥
                    train_no = fields[3] # 车次
                    from_station_code_in_result = fields[6]
                    to_station_code_in_result = fields[7]
                    start_time = fields[8] # 发车时间
                    arrive_time = fields[9] # 到达时间
                    duration = fields[10] # 历时
                    # 座位信息通常从索引 26 开始，不同座位类型对应不同索引
                    # 例如：二等座(26), 一等座(25), 商务座(32) 等
                    # 这里只检查二等座是否有票
                    second_class_seat = fields[26]

                    # 简单判断是否有票 (数字表示票数，'无'表示无票，'有'表示有票但数量>=30)
                    if second_class_seat != '无' and second_class_seat != '':
                        available_trains.append({
                            'index': i+1,
                            'secretStr': secret_str,
                            'train_no': train_no,
                            'start_time': start_time,
                            'arrive_time': arrive_time,
                            'duration': duration,
                            'second_class': second_class_seat
                        })
                        print(f"{i+1}. Train: {train_no}, Departs: {start_time}, Arrives: {arrive_time}, Duration: {duration}, 2nd Class: {second_class_seat}")

            if not available_trains:
                print("No available trains with tickets found.")
                return None

            # 用户选择车次
            while True:
                try:
                    choice = int(input("Please select a train number to book: "))
                    if 1 <= choice <= len(available_trains):
                        selected_train = available_trains[choice - 1]
                        print(f"Selected train: {selected_train['train_no']}")
                        return selected_train # 返回选中的车次信息
                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                     print("Please enter a numerical choice.")

        else:
            messages = result.get('messages', ['Unknown error'])
            print(f"Search failed: {', '.join(messages) if isinstance(messages, list) else messages}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network error during ticket search: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from ticket search: {e}")
        print(f"Response content snippet: {response.text[:200]}...")
        return None
    except Exception as e:
        print(f"An unknown error occurred during ticket search: {e}")
        return None


def login_to_12306(session):
    """处理登录过程：打开浏览器让用户手动登录。"""
    print("\n--- Manual Login Required ---")
    print("A browser window will open for you to log in to 12306.cn.")
    print("Please complete the login process in the browser.")

    # 更新为正确的12306登录页面URL
    # login_url = "https://kyfw.12306.cn/otn/login/init" # 旧的或可能的URL
    login_url = "https://kyfw.12306.cn/otn/resources/login.html" # 使用你提供的URL

    try:
        # 尝试打开浏览器
        webbrowser.open(login_url)
        print(f"Browser opened to {login_url}")
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")
        print(f"Please manually open your browser and go to: {login_url}")

    # 等待用户登录
    input("\nPress 'Enter' in this terminal AFTER you have successfully logged in and closed the login tab...")

    print("Checking login status...")
    # 检查登录状态 (通过访问一个需要登录的页面或API)
    # 例如，访问 'checkUser' API
    check_url = "https://kyfw.12306.cn/otn/login/checkUser" # 检查用户状态的API
    check_data = {'_json_att': ''} # 通常需要这个参数

    try:
        # 使用 POST 请求检查用户状态
        check_response = session.post(check_url, headers=BASE_HEADERS, data=check_data, timeout=10)
        check_response.raise_for_status()
        check_result = check_response.json()

        # 解析响应判断是否登录
        # 成功的响应通常类似: {"data":{"flag":true},"messages":"","status":true}
        if check_result.get('status') == True and check_result.get('data', {}).get('flag') == True:
            print("Login check successful. Proceeding...")
            return True
        else:
            # 如果 checkUser API 不可用或返回格式变了，尝试另一种方式
            # 访问个人中心首页，未登录会重定向或返回特定内容
            my12306_url = "https://kyfw.12306.cn/otn/view/index.html"
            my12306_response = session.get(my12306_url, headers=BASE_HEADERS, timeout=10)
            my12306_response.raise_for_status()
            # 检查返回内容是否包含登录用户的特征（例如“我的12306”）或不包含未登录的特征（例如“您好，请登录”）
            if "我的12306" in my12306_response.text and "您好，请登录" not in my12306_response.text:
                 print("Login check (via index page) suggests you are logged in. Proceeding...")
                 return True
            else:
                print("Login check failed. You might not be logged in. Proceeding anyway, but it might fail later.")
                # 仍然返回 True，因为用户确认已登录，让后续步骤去处理可能的错误
                return True

    except requests.exceptions.RequestException as e:
        print(f"Network error while checking login status: {e}. Proceeding anyway...")
        # 网络错误，但用户确认已登录，让后续步骤去处理
        return True
    except json.JSONDecodeError:
        print("Received unexpected response format while checking login. Proceeding anyway...")
        return True
    except Exception as e:
         print(f"An unexpected error occurred during login check: {e}. Proceeding anyway...")
         return True

    except requests.exceptions.RequestException as e:
        print(f"Network error while checking login status: {e}. Proceeding anyway...")
        # 网络错误，但用户确认已登录，让后续步骤去处理
        return True
    except json.JSONDecodeError:
        print("Received unexpected response format while checking login. Proceeding anyway...")
        return True
    except Exception as e:
         print(f"An unexpected error occurred during login check: {e}. Proceeding anyway...")
         return True

def book_ticket(session, selected_train_info):
    """自动执行预订流程直到支付页面。(占位符/示意)"""
    print(f"\nAttempting to book ticket for train {selected_train_info['train_no']}...")
    # 这是预订的核心，但也是最复杂的部分，因为它涉及到与服务器的多次交互和状态管理。
    # 通常步骤包括：
    # 1.  **检查用户状态**: 确认已登录。
    # 2.  **提交预订请求 (checkUser)**: 验证用户是否可以提交订单。
    #     URL: https://kyfw.12306.cn/otn/login/checkUser
    # 3.  **提交订单请求 (submitOrderRequest)**: 将选中的车票信息提交。
    #     URL: https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest
    #     参数: secretStr, train_date, ...
    # 4.  **确认乘客信息 (initDc)**: 获取初始化页面，提取Token和乘客信息。
    #     URL: https://kyfw.12306.cn/otn/confirmPassenger/initDc
    #     方法: POST
    # 5.  **获取乘客联系人 (getPassengerDTOs)**: 获取可预订的乘客列表。
    #     URL: https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs
    # 6.  **检查订单信息 (checkOrderInfo)**: 提交乘客和车票信息进行校验。
    #     URL: https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo
    # 7.  **获取排队信息 (getQueueCount)**: 查询当前排队人数。
    #     URL: https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount
    # 8.  **确认订单 (confirmSingleForQueue)**: 最终确认订单，进入排队。
    #     URL: https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue
    # 9.  **查询订单状态**: 循环查询订单是否成功。
    #     URL: https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime
    # 10. **完成**: 如果成功，会跳转到支付页面。

    # --- 示例：提交订单请求 (submitOrderRequest) ---
    print("Submitting order request...")
    # 修正：移除URL末尾的空格
    submit_url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
    submit_data = {
        'secretStr': urllib.parse.unquote(selected_train_info['secretStr']), # 注意需要URL解码
        'train_date': '', # 需要从查询结果或其他地方获取
        'back_train_date': '', # 返程日期，单程可为空或与train_date相同
        'tour_flag': 'dc', # 单程
        'purpose_codes': 'ADULT',
        'query_from_station_name': '', # 需要
        'query_to_station_name': '', # 需要
        'undefined': '' # 12306有时需要这个奇怪的参数
    }
    # 填充缺失的必要参数 (这些信息需要从之前的查询步骤中获取或重新输入)
    # 这是一个简化示例，实际需要更精确的参数
    submit_data['train_date'] = '2023-10-27' # 示例日期
    submit_data['back_train_date'] = submit_data['train_date']
    submit_data['query_from_station_name'] = 'Beijing'
    submit_data['query_to_station_name'] = 'Shanghai'

    time.sleep(1) # 反爬虫延迟
    try:
        submit_response = session.post(submit_url, data=submit_data, headers=BASE_HEADERS)
        submit_response.raise_for_status()
        submit_result = submit_response.json()
        print(f"Submit order response: {submit_result}")
        if submit_result.get('status') == True and submit_result.get('data') == 'N':
            # 修正：统一 if 块内的缩进为 4 个空格
            print("Order request submitted successfully. Preparing for confirmation page.")
            # 正常流程会重定向到确认页面，需要处理后续步骤...
            # 但由于复杂性，这里示意性地结束
            print("Automation stops here. Further steps (passenger, queue, payment) are complex.")
            return True
        else:
            # 修正：统一 else 块内的缩进为 4 个空格
            messages = submit_result.get('messages', ['Unknown error'])
            print(f"Failed to submit order: {', '.join(messages) if isinstance(messages, list) else messages}")
            return False
    except Exception as e:
        # 修正：统一 except 块内的缩进为 4 个空格
        print(f"Error submitting order: {e}")
        return False

    # print("预订逻辑（选择座位、添加乘客、提交订单）在此处实现。")
    # print("自动化将在支付页面之前停止。")
    # return True # 占位符


# --- 主执行流程 ---
if __name__ == '__main__':
    print("12306 Ticket Booking Automation Script (Educational Purposes Only)")
    print("=" * 70)

    # 1. 初始化会话
    main_session = requests.Session()

    # 2. 获取省份数据 (可选，用于学习)
    # provinces_df, main_session = get_provinces_data() # 注释掉，因为我们主要关注订票

    # 3. 获取车站代码
    print("Loading station codes...")
    station_codes = get_station_codes(main_session)
    if not station_codes:
        print("Failed to load station codes. Exiting script.")
        exit()

    # 4. 用户输入
    travel_date, from_code, to_code, from_name, to_name = get_user_input(station_codes)

    # 5. 登录 (预订所必需)
    is_logged_in = login_to_12306(main_session)
    if not is_logged_in:
        print("Login failed or was cancelled. Exiting.")
        exit()

    # 6. 搜索车票
    selected_train = search_tickets(main_session, travel_date, from_code, to_code)

    if selected_train:
        # 7. 预订 (直到支付)
        booking_success = book_ticket(main_session, selected_train)

        if booking_success:
            print("\n--- Booking Process Initiated ---")
            print("The ticket booking request has been submitted (or process initiated).")
            print("Please note, subsequent steps (passenger confirmation, queuing, payment) require more complex implementation and are prone to fail due to anti-crawler measures.")
            print("This script mainly demonstrates crawling techniques for querying and initial submission.")
        else:
            print("\n--- Booking Failed ---")
            print("Could not submit the booking request.")
    else:
        print("\nNo valid train selected or no tickets available for the query.")
