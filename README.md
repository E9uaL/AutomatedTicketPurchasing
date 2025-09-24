# Ticket Booking Script (Educational Purpose)

## Disclaimer

**This script is strictly for educational purposes to learn Python programming, web scraping, and browser automation techniques.**

**It should NOT be used for commercial purposes or to automatically purchase real tickets on 12306.cn. This likely violates the 12306.cn Terms of Service and can result in account penalties or other consequences. Use responsibly and at your own risk.

The script automates the process up to the payment page. The user must manually complete the payment step in the browser.**

---

## Description

This Python script demonstrates how to use `requests` and `selenium` to interact with the 12306.cn website. It automates the process of logging in (manually by the user in a controlled browser), searching for train tickets, and navigating to the order confirmation page. The final payment step must be completed manually by the user.

It addresses the common issue where direct API calls (like `queryZ`, `getQueueCount`) return "网络可能存在问题，请您重试一下！" by using Selenium to drive a real browser, mimicking user interactions.

---

## Prerequisites

Before running the script, ensure you have the following installed:

1.  **Python 3.x**: Make sure Python is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
2.  **Chrome Browser**: The script uses Selenium with Chrome. Ensure you have Google Chrome installed.
3.  **ChromeDriver**:
    *   Download the ChromeDriver executable that matches your Chrome browser version from the [official ChromeDriver site](https://chromedriver.chromium.org/downloads).
    *   Place the `chromedriver` executable in a directory that is included in your system's `PATH` environment variable, or note down its exact path for configuration in the script.

---

## Installation

1.  **Clone or Download the Script**:
    *   Save the provided Python script code as `12306_script_final.py` in a new directory on your computer.

2.  **Install Python Dependencies**:
    *   Open a terminal or command prompt.
    *   Navigate to the directory where you saved the script.
    *   Run the following command to install the required Python libraries:

      ```bash
      pip install requests pandas openpyxl selenium
      ```

3.  **Configure ChromeDriver** (if not in PATH):
    *   Open the `12306_script_final.py` file in a text editor (like Notepad, VS Code, PyCharm, etc.).
    *   Find the `login_to_12306_selenium` function.
    *   Look for the commented lines near the beginning of the `try` block:

        ```python
        # service = Service('/path/to/chromedriver') # Linux/Mac
        # service = Service('C:\\path\\to\\chromedriver.exe') # Windows
        # driver = webdriver.Chrome(service=service)
        ```

    *   Uncomment these lines and modify the path (`/path/to/chromedriver` or `C:\\path\\to\\chromedriver.exe`) to point to the exact location of your downloaded `chromedriver` executable on your system.
    *   Comment out the line `driver = webdriver.Chrome()` (the one without the `service` argument).

---

## Usage

1.  **Run the Script**:
    *   Open a terminal or command prompt.
    *   Navigate to the directory containing `12306_script_final.py`.
    *   Execute the script by running:

        ```bash
        python 12306_script_final.py
        ```

2.  **Follow the Prompts**:
    *   The script will first load station codes.
    *   It will then prompt you to enter the travel date, departure station, and arrival station. Use the full Chinese names (e.g., "北京", "上海").
    *   A browser window will open, directing you to the 12306 login page.
    *   **Manually log in** to your 12306 account in the opened browser window.
    *   After logging in, **do not close the browser window**. Return to the terminal and press `Enter`.
    *   The script will navigate to the ticket search page, fill in the details you provided, and click the search button.
    *   **In the browser**, select the desired train and click the "预订" (Book) button.
    *   Continue with the steps in the browser: select passengers, seat type, and submit the order until you reach the payment page.
    *   **Return to the terminal** and press `Enter` after you have reached the payment page in the browser.
    *   The script will then close the browser window.

3.  **Complete Payment**:
    *   Manually complete the payment process on the 12306 website in the browser.

---

## Troubleshooting

*   **Element Not Found**: If the script fails to find input fields (like `from_station_text`), it's likely due to changes in the 12306 website's HTML structure. You will need to inspect the page using your browser's developer tools (F12) to find the correct element IDs or selectors and update the `search_tickets_selenium` function accordingly (specifically the `station_suggestion_xpath` variables).
*   **ChromeDriver Error**: If you get an error about ChromeDriver not being found, ensure it's either in your system's `PATH` or that you've correctly configured the path in the script.
*   **API Errors (e.g., "网络可能存在问题")**: This script avoids direct API calls for booking steps. If errors occur during the Selenium-driven process, they are likely related to page structure changes or timing issues handled by Selenium's waits.

---

## Notes

*   The script includes delays (`time.sleep`) as a basic anti-crawler measure.
*   The script is designed for the Chinese 12306 website.
*   Ensure your 12306 account is verified and has sufficient balance or linked payment methods before attempting to book.

---

## License

This project is for educational use only.
