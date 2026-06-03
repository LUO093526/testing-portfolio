"""pytest 迁移版本 - 登录功能自动化测试

## 从 unittest 迁移的改动

| unittest 写法 | pytest 写法 | 理由 |
|--------------|------------|------|
| `setUp(self)` / `tearDown(self)` | `@pytest.fixture(scope="class")` | 复用 driver，节省启动时间 |
| `self.assertEqual(...)` | `assert ...` | pytest 自带详细断言输出 |
| `input("按任意键继续")` | 删掉 | 自动化测试不需要交互 |
| 硬编码 `E:\chromedriver.exe` | Selenium 4.x 自动管理 | 跨平台不依赖路径 |
| 无测试标记 | `@pytest.mark.selenium` | 可按需跳过 `-m "not selenium"` |
| 裸 `except: pass` | 记录日志 | 方便排查问题 |

## 运行方式

```bash
# 跑所有登录测试
pytest tests/test_login_pytest.py -v

# 跑但显示 print 输出
pytest tests/test_login_pytest.py -v -s

# 跳过 selenium（仅 API 测试）
pytest -m "not selenium"

# 生成 HTML 报告
pytest tests/test_login_pytest.py --html=reports/login_report.html
```
"""

import time
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import ddddocr

logger = logging.getLogger(__name__)

# ── 常量 ─────────────────────────────────────────
LOGIN_URL = "http://124.223.155.95:8088/home/login/login.html"
VALID_USERNAME = "18062031483"
VALID_PASSWORD = "mfm543200"
CAPTCHA_RETRY = 10  # 验证码最多重试次数

# Chromium 路径（Playwright 安装的）
CHROMIUM_PATH = "/home/luo/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
# Chromedriver 路径（从 npmmirror 下载）
CHROMEDRIVER_PATH = "/home/luo/.local/bin/chromedriver"


def _recognize_captcha(ocr: ddddocr.DdddOcr, driver) -> str:
    """识别验证码图片，返回识别的文本"""
    code_img = WebDriverWait(driver, 10, 1).until(
        lambda x: x.find_element(By.XPATH, '//*[@id="codeimage"]')
    )
    text = ocr.classification(code_img.screenshot_as_png)
    return text


def _fill_captcha(driver, ocr: ddddocr.DdddOcr) -> None:
    """识别验证码并填入输入框"""
    text = _recognize_captcha(ocr, driver)
    logger.info("验证码识别结果: %s", text)

    code_input = WebDriverWait(driver, 10, 1).until(
        lambda x: x.find_element(By.ID, "captcha_normal")
    )
    code_input.click()
    time.sleep(1)
    code_input.clear()
    time.sleep(1)
    code_input.send_keys(text)
    time.sleep(1)


# ── Fixtures ─────────────────────────────────────

@pytest.fixture(scope="class")
def driver():
    """创建 Chrome WebDriver，测试类结束后自动退出

    scope="class" = 整个测试类共用一个浏览器实例（等价于原 setUp/tearDown 的类级别效果）
    如果 Chrome/chromedriver 不可用，自动 skip 相关测试。
    """
    options = Options()
    options.binary_location = CHROMIUM_PATH
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")

    try:
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        pytest.skip(f"浏览器不可用: {e}")

    logger.info("浏览器已启动")

    yield driver  # ← 这里返回给测试方法

    # teardown：测试类结束后执行
    driver.quit()
    logger.info("浏览器已关闭")


@pytest.fixture(scope="class")
def logged_in_driver(driver):
    """登录后的 driver（给后续需要登录态的测试用）"""
    driver.get(LOGIN_URL)
    driver.maximize_window()
    time.sleep(2)

    # 定位用户名和密码
    user = WebDriverWait(driver, 10, 1).until(
        lambda x: x.find_element(By.ID, "member_name")
    )
    user.send_keys(VALID_USERNAME)

    pwd = WebDriverWait(driver, 10, 1).until(
        lambda x: x.find_element(By.ID, "member_password")
    )
    pwd.send_keys(VALID_PASSWORD)

    # 验证码识别重试
    ocr = ddddocr.DdddOcr()
    for attempt in range(CAPTCHA_RETRY):
        _fill_captcha(driver, ocr)

        # Tab 切换到登录按钮
        code_input = driver.find_element(By.ID, "captcha_normal")
        code_input.send_keys(Keys.TAB)
        time.sleep(1)

        # 点击登录
        login_btn = driver.find_element(
            By.XPATH, '//*[@id="login_normal_form"]/div[5]/input[2]'
        )
        login_btn.click()
        time.sleep(3)

        # 检查是否登录成功
        try:
            account = driver.find_element(
                By.XPATH, "/html/body/div[8]/div/div[2]/div[2]/div[1]/div[1]/div[4]/div"
            )
            if account.text == VALID_USERNAME:
                logger.info("登录成功 (第 %d 次尝试)", attempt + 1)
                yield driver
                return
        except Exception:
            logger.warning("第 %d 次验证码识别失败，重试...", attempt + 1)
            continue

    pytest.fail(f"验证码重试 {CAPTCHA_RETRY} 次后仍未能登录成功")


# ── 测试类 ───────────────────────────────────────

@pytest.mark.selenium
class TestLogin:
    """登录功能自动化测试（pytest 版本）

    对比原 unittest 版本改进点：
    1. setUp/tearDown → fixture（driver 复用）
    2. print → logger（可控输出）
    3. 验证码识别提取为独立函数
    4. assert 替代 bare if/print
    """

    def test_login_success(self, driver):
        """正向：正确用户名+密码+验证码，登录成功"""
        driver.get(LOGIN_URL)
        driver.maximize_window()
        time.sleep(2)

        # 输入用户名
        user = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_name")
        )
        user.send_keys(VALID_USERNAME)

        # 输入密码
        pwd = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_password")
        )
        pwd.send_keys(VALID_PASSWORD)

        ocr = ddddocr.DdddOcr()
        login_success = False
        for i in range(CAPTCHA_RETRY):
            _fill_captcha(driver, ocr)

            code_input = driver.find_element(By.ID, "captcha_normal")
            code_input.send_keys(Keys.TAB)
            time.sleep(1)

            login_btn = driver.find_element(
                By.XPATH, '//*[@id="login_normal_form"]/div[5]/input[2]'
            )
            login_btn.click()
            time.sleep(3)

            try:
                account = driver.find_element(
                    By.XPATH, "/html/body/div[8]/div/div[2]/div[2]/div[1]/div[1]/div[4]/div"
                )
                if account.text == VALID_USERNAME:
                    login_success = True
                    logger.info("登录成功 (第 %d 次验证码尝试)", i + 1)
                    break
            except Exception:
                logger.warning("第 %d 次验证码错误，重试中...", i + 1)
                continue

        assert login_success, f"验证码重试 {CAPTCHA_RETRY} 次后仍未登录成功"

    def test_login_wrong_username(self, driver):
        """反向：错误用户名，正确密码，预期登录失败"""
        driver.get(LOGIN_URL)
        driver.maximize_window()
        time.sleep(2)

        # 错误的用户名
        user = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_name")
        )
        user.send_keys("wrong_user_123")

        # 正确的密码
        pwd = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_password")
        )
        pwd.send_keys(VALID_PASSWORD)

        ocr = ddddocr.DdddOcr()
        login_failed = False
        for i in range(CAPTCHA_RETRY):
            _fill_captcha(driver, ocr)

            code_input = driver.find_element(By.ID, "captcha_normal")
            code_input.send_keys(Keys.TAB)
            time.sleep(1)

            login_btn = driver.find_element(
                By.XPATH, '//*[@id="login_normal_form"]/div[5]/input[2]'
            )
            login_btn.click()
            time.sleep(2)

            try:
                error_elem = WebDriverWait(driver, 5, 1).until(
                    lambda x: x.find_element(By.CSS_SELECTOR, ".layui-layer-content")
                )
                if error_elem.text == "登录失败":
                    login_failed = True
                    logger.info("检测到登录失败提示 (符合预期)")
                    break
            except Exception:
                logger.warning("第 %d 次未检测到错误提示，重试中...", i + 1)
                continue

        assert login_failed, f"验证码重试 {CAPTCHA_RETRY} 次后仍未出现预期的登录失败提示"


@pytest.mark.selenium
class TestLoginWithFixture:
    """使用 logged_in_driver 夹具 — 展示 fixture 依赖注入"""

    def test_after_login_page_has_account(self, logged_in_driver):
        """登录成功后页面显示正确的账号"""
        driver = logged_in_driver
        account_elem = driver.find_element(
            By.XPATH, "/html/body/div[8]/div/div[2]/div[2]/div[1]/div[1]/div[4]/div"
        )
        assert account_elem.text == VALID_USERNAME, (
            f"期望账号 {VALID_USERNAME}，实际显示 {account_elem.text}"
        )
