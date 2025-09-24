# Ticket Booking Assistant

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Educational%20Use%20Only-yellow)](#license)

A Python script designed for educational purposes to learn web scraping and browser automation techniques with Selenium.

## Important Disclaimer

> **This script is strictly for educational purposes to learn Python programming, web scraping, and browser automation techniques.**
> 
> **It should NOT be used for commercial purposes or to automatically purchase real tickets on 12306.cn.** This likely violates the 12306.cn Terms of Service and can result in account penalties or other consequences. Use responsibly and at your own risk.
> 
> The script automates the process up to the payment page. The user must manually complete the payment step in the browser.

## Description

This script demonstrates how to interact with the 12306.cn website using Python's `requests` and `selenium` libraries. It automates:

- Manual login process (user logs in via controlled browser)
- Station code retrieval and validation
- Ticket search and selection
- Navigation to order confirmation page

It addresses the common issue where direct API calls (like `queryZ`, `getQueueCount`) return "网络可能存在问题，请您重试一下！" by using Selenium to drive a real browser, mimicking user interactions.

## Prerequisites

Before running the script, ensure you have:

- [x] **Python 3.7+** - [Download from python.org](https://www.python.org/downloads/)
- [x] **Google Chrome Browser** - [Download Chrome](https://www.google.com/chrome/)
- [x] **ChromeDriver** - [Download matching version](https://chromedriver.chromium.org/downloads)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/12306-ticket-booking.git
cd 12306-ticket-booking
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install requests pandas selenium openpyxl
```

### 3. Configure ChromeDriver

- If ChromeDriver is **not** in your system PATH:
  1. Open `12306_script_final.py` in your text editor
  2. Locate the `login_to_12306_selenium` function
  3. Uncomment and modify the service path:
  
  ```python
  # For Linux/Mac:
  service = Service('/path/to/chromedriver')
  
  # For Windows:
  service = Service('C:\\path\\to\\chromedriver.exe')
  
  driver = webdriver.Chrome(service=service)
  ```
  
  4. Comment out `driver = webdriver.Chrome()`

## ▶️ Usage

1. **Run the script**:
   ```bash
   python 12306_script_final.py
   ```

2. **Follow the prompts**:
   - Enter travel date (YYYY-MM-DD)
   - Enter departure and arrival stations (full Chinese names, e.g., "北京", "上海")
   - A browser window will open to 12306 login page
   - **Manually log in** to your 12306 account
   - Press `Enter` in terminal after successful login
   - The script will fill search details and click search button
   - **In browser**: Select desired train and click "预订" (Book)
   - Complete passenger selection and submit order until payment page
   - Press `Enter` in terminal after reaching payment page

3. **Complete payment**:
   - Manually complete payment on 12306 website

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Element Not Found** | 12306 website HTML structure may have changed. Use browser dev tools (F12) to find correct selectors and update `search_tickets_selenium` function |
| **ChromeDriver Error** | Verify ChromeDriver is in PATH or correctly configured in script |
| **API Errors** | This script avoids direct API calls. If errors occur, they're likely due to timing issues - increase wait times in script |
| **Station Name Issues** | Ensure you're using full Chinese station names (e.g., "北京" not "BJ") |

## Notes

- The script includes delays (`time.sleep`) as basic anti-crawler measures
- Designed specifically for the Chinese 12306 website
- Ensure your 12306 account is verified with sufficient balance before booking
- The script cannot bypass 12306's captcha or security measures

## FAQ

**Q: Why does the script stop at the payment page?**  
A: The script is designed for educational purposes only. Completing payment automatically would violate 12306's terms of service.

**Q: Why do I get "网络可能存在问题" errors when using direct API calls?**  
A: 12306 has robust security measures that prevent direct API access without proper session management and token validation.

**Q: Can this script handle captchas automatically?**  
A: No, and attempting to do so would violate 12306's terms of service. The script relies on manual login to maintain a valid session.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is for educational use only. It is not intended for production use or commercial applications.

> **Note**: Using this script to automate ticket purchasing on 12306.cn may violate their terms of service and could result in account suspension.