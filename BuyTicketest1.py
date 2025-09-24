# -----------------------------------------------------------------------------------
# 免责声明：此脚本仅用于学习Python爬虫技术。
# 不得将其用于商业目的或在12306.cn上自动购买真实车票，
# 因为这可能违反其服务条款。
# -----------------------------------------------------------------------------------

import time
import requests
import pandas as pd
from datetime import datetime
import json
import urllib.parse  # 用于URL编码
import webbrowser  # 用于打开浏览器（登录用）
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import getpass  # 用于隐藏密码输入

# --- 配置 ---
# 使用更完整的请求头字典是模仿真实浏览器的常见做法。
# Accept-Language 设置为中文，因为我们是在模拟访问中文网站
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",  # 优先中文，兼容英文
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}

# 全局变量存储车站代码
station_codes = {}


# --- 核心函数 ---

def get_provinces_data():
    """从12306获取并保存省份数据。"""
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
        print(f"Error fetching province  {e}")
        return None, None
    except KeyError as e:
        print(f"Error parsing JSON response: Missing key {e}")
        return None, None
    except Exception as e:  # 捕获其他潜在错误
        print(f"An unknown error occurred: {e}")
        return None, None


def get_station_codes(session):
    """获取热门车站代码字典。实际应用中可能需要更完整的列表或实时查询。"""
    global station_codes  # 使用全局变量
    # 注意：12306的热门车站列表API可能会变化，需要根据实际情况调整
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
            station_codes = {}
            for station in stations_list:
                if station:
                    parts = station.split('|')
                    if len(parts) >= 5:  # 确保有足够的部分
                        # 简体中文站名: parts[1], 代码: parts[2]
                        station_codes[parts[1]] = parts[2]
            print(f"Loaded codes for {len(station_codes)} stations.")
            return station_codes
        else:
            print("Failed to parse station code data.")
            return {}
    except Exception as e:
        print(f"Error fetching station codes: {e}")
        return {}


def get_user_input(station_codes_dict):
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
        from_station_code = station_codes_dict.get(from_station_name, "")
        if not from_station_code:
            # 尝试模糊匹配
            matches = [name for name in station_codes_dict.keys() if from_station_name in name]
            if matches:
                print(f"No exact match found. Similar stations: {matches[:5]} (showing first 5)")
                # 可以让用户选择，这里简化处理
            print("Station not found. Please check the name.")

    while not to_station_code:
        to_station_name = input("Enter arrival station (e.g., Shanghai): ").strip()
        to_station_code = station_codes_dict.get(to_station_name, "")
        if not to_station_code:
            matches = [name for name in station_codes_dict.keys() if to_station_name in name]
            if matches:
                print(f"No exact match found. Similar stations: {matches[:5]} (showing first 5)")
            print("Station not found. Please check the name.")

    print(
        f"Query Info: Date={date_str}, From={from_station_name}({from_station_code}), To={to_station_name}({to_station_code})")
    return date_str, from_station_code, to_station_code, from_station_name, to_station_name


def get_station_code_by_name(station_dict, station_name):
    """根据站名从字典中查找代码。"""
    for name, code in station_dict.items():
        if name == station_name:
            return code
    return None  # 如果找不到，返回 None


def search_tickets_selenium(driver, date, from_station_name, to_station_name, station_codes_dict):
    """使用Selenium在浏览器中完成车票查询和预订流程。"""
    print(f"\nUsing Selenium to search for tickets on {date} from {from_station_name} to {to_station_name}...")

    try:
        # 1. 导航到查询页面
        query_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        print(f"Navigating to {query_url}...")
        driver.get(query_url)

        # 2. 等待页面加载，使用更通用的等待条件
        print("Waiting for page to load completely...")
        # 等待页面标题包含特定内容，或等待某个页面结构元素出现
        WebDriverWait(driver, 30).until(
            lambda d: "12306" in d.title or d.find_element(By.ID, "from_station_text") or d.find_element(By.ID,
                                                                                                         "from_station")
            # 等待标题或关键元素之一出现
        )
        print("Page loaded.")

        # 3. 尝试定位输入框 - 使用更灵活的定位方法
        print("Locating input fields...")

        # 尝试查找出发站输入框 (文本显示框)
        from_input_text = None
        from_input_code = None
        try:
            # 尝试最常见的ID
            from_input_text = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "from_station_text"))
            )
        except TimeoutException:
            print("Could not find 'from_station_text' by ID. Trying alternative selectors...")
            # 尝试其他可能的选择器 (需要根据实际页面结构调整)
            try:
                from_input_text = driver.find_element(By.CSS_SELECTOR,
                                                      "input[placeholder='请输入出发地']")  # 根据placeholder
            except NoSuchElementException:
                try:
                    from_input_text = driver.find_element(By.CSS_SELECTOR, "input#from_station_text")  # 确认ID
                except NoSuchElementException:
                    # 如果都找不到，可能需要等待更长时间或页面有其他加载逻辑
                    print(
                        "Warning: Could not locate 'from_station_text' element. The page structure might have changed.")
                    # 尝试查找隐藏的代码输入框
                    try:
                        from_input_code = driver.find_element(By.ID, "from_station")
                    except NoSuchElementException:
                        print("Could not locate 'from_station' code input either.")
                        raise TimeoutException("Could not find departure station input fields.")

        # 尝试查找到达站输入框 (文本显示框)
        to_input_text = None
        to_input_code = None
        try:
            to_input_text = driver.find_element(By.ID, "to_station_text")
        except NoSuchElementException:
            print("Could not find 'to_station_text' by ID. Trying alternative selectors...")
            try:
                to_input_text = driver.find_element(By.CSS_SELECTOR,
                                                    "input[placeholder='请输入目的地']")  # 根据placeholder
            except NoSuchElementException:
                try:
                    to_input_text = driver.find_element(By.CSS_SELECTOR, "input#to_station_text")  # 确认ID
                except NoSuchElementException:
                    print("Warning: Could not locate 'to_station_text' element. The page structure might have changed.")
                    try:
                        to_input_code = driver.find_element(By.ID, "to_station")
                    except NoSuchElementException:
                        print("Could not locate 'to_station' code input either.")
                        raise TimeoutException("Could not find destination station input fields.")

        # 尝试查找日期输入框
        date_input = None
        try:
            date_input = driver.find_element(By.ID, "train_date")
        except NoSuchElementException:
            print("Could not find 'train_date' by ID. Trying alternative selectors...")
            try:
                date_input = driver.find_element(By.CSS_SELECTOR, "input#train_date")  # 确认ID
            except NoSuchElementException:
                print("Could not locate 'train_date' element.")
                raise TimeoutException("Could not find date input field.")

        # 4. 填充表单 - 根据找到的元素进行操作
        print(f"Entering departure: {from_station_name}")
        if from_input_text:
            from_input_text.clear()
            from_input_text.send_keys(from_station_name)
            # 等待并点击车站列表中的匹配项
            # **重要**: 你需要使用浏览器开发者工具 (F12) 找到准确的XPATH或CSS选择器
            # 示例XPATH: //div[@id='panel_cfx_fromStation']//li[contains(., '北京')]//a
            # 示例CSS: #panel_cfx_fromStation li:contains('北京') a (注意: :contains 在CSS中不标准，Selenium支持)
            # 请将 '北京' 替换为 {from_station_name}
            station_suggestion_xpath = f"//div[@id='panel_cfx_fromStation']//li[contains(., '{from_station_name}')]//a"
            # 例如，如果车站列表在 #citem_fromStation 中
            # station_suggestion_xpath = f"//div[@id='citem_fromStation']//li[contains(., '{from_station_name}')]//a"
            try:
                station_suggestion = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, station_suggestion_xpath))
                )
                station_suggestion.click()
                print(f"Selected departure station: {from_station_name}")
            except TimeoutException:
                print(
                    f"Warning: Could not click on the station suggestion for '{from_station_name}'. It might auto-select or require manual selection.")
                # 如果找不到，尝试填充隐藏的代码框 (如果存在)
                if from_input_code:
                    from_code = get_station_code_by_name(station_codes_dict, from_station_name)
                    if from_code:
                        driver.execute_script(f"arguments[0].value = '{from_code}';", from_input_code)
                        print(f"Filled departure station code: {from_code}")
                    else:
                        print(
                            f"Warning: Could not find code for station '{from_station_name}'. Cannot fill code input.")
        elif from_input_code:  # 如果只找到了代码输入框
            from_code = get_station_code_by_name(station_codes_dict, from_station_name)
            if from_code:
                driver.execute_script(f"arguments[0].value = '{from_code}';", from_input_code)
                print(f"Filled departure station code: {from_code}")
            else:
                print(f"Warning: Could not find code for station '{from_station_name}'. Cannot fill code input.")
                raise TimeoutException("Could not fill departure station.")

        print(f"Entering destination: {to_station_name}")
        if to_input_text:
            to_input_text.clear()
            to_input_text.send_keys(to_station_name)
            # **重要**: 你需要使用浏览器开发者工具 (F12) 找到准确的XPATH或CSS选择器
            # 示例XPATH: //div[@id='panel_cfx_toStation']//li[contains(., '上海')]//a
            station_suggestion_to_xpath = f"//div[@id='panel_cfx_toStation']//li[contains(., '{to_station_name}')]//a"
            try:
                station_suggestion_to = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, station_suggestion_to_xpath))
                )
                station_suggestion_to.click()
                print(f"Selected destination station: {to_station_name}")
            except TimeoutException:
                print(
                    f"Warning: Could not click on the station suggestion for '{to_station_name}'. It might auto-select or require manual selection.")
                if to_input_code:
                    to_code = get_station_code_by_name(station_codes_dict, to_station_name)
                    if to_code:
                        driver.execute_script(f"arguments[0].value = '{to_code}';", to_input_code)
                        print(f"Filled destination station code: {to_code}")
                    else:
                        print(f"Warning: Could not find code for station '{to_station_name}'. Cannot fill code input.")
        elif to_input_code:
            to_code = get_station_code_by_name(station_codes_dict, to_station_name)
            if to_code:
                driver.execute_script(f"arguments[0].value = '{to_code}';", to_input_code)
                print(f"Filled destination station code: {to_code}")
            else:
                print(f"Warning: Could not find code for station '{to_station_name}'. Cannot fill code input.")
                raise TimeoutException("Could not fill destination station.")

        print(f"Entering date: {date}")
        if date_input:
            # 尝试移除只读属性并直接输入
            driver.execute_script("arguments[0].removeAttribute('readonly');", date_input)
            date_input.clear()
            date_input.send_keys(date)
            # 有时需要点击日期输入框来触发日历选择器，然后选择日期
            # date_input.click()
            # 然后可能需要在日历中选择日期，这比较复杂，直接输入通常更可靠
            print(f"Filled date: {date}")
        else:
            raise TimeoutException("Could not find date input field.")

        # 5. 点击查询按钮
        print("Clicking query button...")
        query_button = driver.find_element(By.ID, "query_ticket")
        query_button.click()

        # 6. 等待查询结果加载 - 使用更通用的等待条件
        print("Waiting for search results...")
        # 等待不再显示加载动画，或者车次列表出现
        # 12306页面可能有加载提示，例如包含 '查询中' 或 'search-loading' 类的元素
        # WebDriverWait(driver, 20).until_not(
        #     EC.presence_of_element_located((By.CLASS_NAME, "search-loading")) # 假设加载时有此类
        # )
        # 或者等待结果表格出现 - 等待查询按钮不再可点击（表示正在查询）然后查询完成
        WebDriverWait(driver, 20).until_not(
            EC.element_to_be_clickable((By.ID, "query_ticket"))  # 等待查询按钮变为不可点击或禁用
        )
        # 再等待结果表格行出现
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#queryLeftTable tbody tr"))  # 等待结果表格行出现
        )

        print("\n--- Search Results Loaded ---")
        print("The search results are now displayed in the browser.")
        print("Please select the desired train and click the '预订' (Book) button.")
        print("The script will wait for you to complete the booking process up to the payment page.")

        # 7. 等待用户在浏览器中完成后续操作（选择车次、乘客、座位、提交订单）
        # 例如，等待跳转到确认页面
        try:
            WebDriverWait(driver, 300).until(
                EC.url_contains("confirmPassenger")  # 等待跳转到确认乘客页面
            )
            print("\n--- Booking Process Reached Confirmation Page ---")
            print("You have reached the order confirmation page in the browser.")
            print("Please select passengers, seat type, and complete the order submission manually.")
            print("Payment will need to be completed manually on the final page.")
            print(
                "\nPress Enter in this terminal after you have completed the booking and payment steps in the browser...")
            input()  # 等待用户完成浏览器中的操作
            return True
        except TimeoutException:
            print("\n--- Timeout ---")
            print("Did not reach the confirmation page within the expected time. Please check the browser.")
            print(
                "Press Enter in this terminal after you have completed the booking and payment steps in the browser...")
            input()
            # 即使超时，也假设用户完成了操作
            return True

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during Selenium booking process: {e}")
        print("The booking process may need manual intervention.")
        # 可以添加一个断点，让用户检查浏览器状态
        print("The script has paused. Please check the browser window for the current state.")
        print("Press Enter in this terminal to continue and close the browser...")
        input()
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("The booking process may need manual intervention.")
        print("The script has paused. Please check the browser window for the current state.")
        print("Press Enter in this terminal to continue and close the browser...")
        input()
        return False


def login_to_12306_selenium():
    """处理登录过程：使用Selenium打开浏览器让用户手动登录。"""
    print("\n--- Manual Login Required ---")
    print("A browser window will open for you to log in to 12306.cn.")
    print("Please complete the login process in the browser.")

    # 使用Selenium打开浏览器
    try:
        # --- 重要：请在此处配置你的ChromeDriver路径 ---
        # service = Service('/path/to/chromedriver') # Linux/Mac
        # service = Service('C:\\path\\to\\chromedriver.exe') # Windows
        # driver = webdriver.Chrome(service=service)
        # 或者，如果ChromeDriver在系统PATH中
        driver = webdriver.Chrome()

        login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        driver.get(login_url)

        print("Browser opened. Please log in and wait for the main page to load.")

        # 等待用户完成登录（可以检测登录后的元素）
        try:
            # 等待"我的12306"元素出现，表示登录成功
            WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.LINK_TEXT, "我的12306"))
            )
            print("Login detected in browser. Proceeding with booking...")
            return True, driver
        except TimeoutException:
            print("Login timed out in browser. Please try again.")
            driver.quit()
            return False, None

    except Exception as e:
        print(f"Error opening browser with Selenium: {e}")
        print("Please ensure ChromeDriver is installed and in your PATH, or configured correctly in the script.")
        print("Alternatively, you can try manual login in a separate browser window.")
        print("Press Enter in this terminal after you have logged in in a browser window...")
        input()
        return True, None  # 假设用户已登录，但不返回driver，后续步骤可能失败


# --- 主执行流程 ---
if __name__ == '__main__':
    print("12306 Ticket Booking Automation Script (Educational Purposes Only)")
    print("=" * 70)

    # 1. 初始化会话 (用于获取车站代码)
    main_session = requests.Session()

    # 2. 获取车站代码
    print("Loading station codes...")
    station_codes = get_station_codes(main_session)
    if not station_codes:
        print("Failed to load station codes. Exiting script.")
        exit()

    # 3. 用户输入
    travel_date, from_code, to_code, from_name, to_name = get_user_input(station_codes)

    # 4. 登录 (预订所必需) - 使用Selenium
    is_logged_in, driver = login_to_12306_selenium()
    if not is_logged_in:
        print("Login failed or was cancelled. Exiting.")
        if driver:
            driver.quit()
        exit()

    # 5. 使用Selenium进行查询和预订
    if driver:
        booking_success = search_tickets_selenium(driver, travel_date, from_name, to_name, station_codes)

        if booking_success:
            print("\n--- Booking Process Completed ---")
            print("The script has guided the process up to the payment page.")
            print("Please complete the payment in the browser window.")
        else:
            print("\n--- Booking Process Failed ---")
            print("Could not complete the booking process in the browser.")

        # 6. 关闭浏览器
        print("Closing browser...")
        driver.quit()
    else:
        print("No browser driver available. Cannot proceed with automated booking.")
        exit()

    print("\nScript finished.")
