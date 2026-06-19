"""Selenium pytest 重构版 — 登录功能 UI 自动化测试
第3周Day5：接入 conftest fixture + parametrize 参数化

## 重构改动（vs 原版）
| 原版 | 重构后 | 理由 |
|------|--------|------|
| 硬编码 LOGIN_URL / VALID_USERNAME 等 | selenium_config fixture（conftest.py） | 集中管理配置 |
| 硬编码 CHROMIUM_PATH / CHROMEDRIVER_PATH | selenium_config["chromium_path"] | 路径变更只改一处 |
| test_login_success 单个账号 | @parametrize 多账号驱动 | 一次写，多组数据跑 |
| test_login_wrong_username 单个错用户名 | @parametrize 多组错误数据 | 用例瘦身 |
| @pytest.mark.selenium | 同时保留 @pytest.mark.selenium + @pytest.mark.web | 兼容两种运行方式 |

## 运行方式
```bash
pytest tests/test_login_pytest.py -v                # 跑全部 Web 测试
pytest tests/test_login_pytest.py -v -k "success"   # 只看成功场景
pytest tests/test_login_pytest.py -v -k "wrong"     # 只看失败场景
pytest -m web                                        # 只跑 Web UI 测试
pytest -m "selenium or web"                          # 两种标记都跑
pytest -m "not (selenium or web)"                    # 跳过 Web 测试（仅 API）
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


# ── 辅助函数 ────────────────────────────────────────

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


# ── Fixtures（使用 conftest selenium_config）──────

@pytest.fixture(scope="class")
def driver(selenium_config):
    """创建 Chrome WebDriver（从 conftest 读取浏览器路径）

    scope="class" = 整个测试类共用一个浏览器实例。
    如果 Chrome/chromedriver 不可用，自动 skip 相关测试。
    """
    options = Options()
    options.binary_location = selenium_config["chromium_path"]
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")

    try:
        service = Service(executable_path=selenium_config["chromedriver_path"])
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        pytest.skip(f"浏览器不可用: {e}")

    logger.info("浏览器已启动 (chromium: %s)", selenium_config["chromium_path"])

    yield driver

    driver.quit()
    logger.info("浏览器已关闭")


@pytest.fixture(scope="class")
def logged_in_driver(driver, selenium_config):
    """登录后的 driver（给后续需要登录态的测试用）

    使用 selenium_config 中的主账号自动登录。
    """
    login_url = selenium_config["login_url"]
    username = selenium_config["valid_username"]
    password = selenium_config["valid_password"]
    captcha_retry = selenium_config["captcha_retry"]

    driver.get(login_url)
    driver.maximize_window()
    time.sleep(2)

    # 填入用户名密码
    user = WebDriverWait(driver, 10, 1).until(
        lambda x: x.find_element(By.ID, "member_name")
    )
    user.send_keys(username)

    pwd = WebDriverWait(driver, 10, 1).until(
        lambda x: x.find_element(By.ID, "member_password")
    )
    pwd.send_keys(password)

    # 验证码识别重试
    ocr = ddddocr.DdddOcr()
    for attempt in range(captcha_retry):
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
            if account.text == username:
                logger.info("登录成功 (第 %d 次尝试)", attempt + 1)
                yield driver
                return
        except Exception:
            logger.warning("第 %d 次验证码识别失败，重试...", attempt + 1)
            continue

    pytest.fail(f"验证码重试 {captcha_retry} 次后仍未能登录成功")


# ── parametrize 数据 ────────────────────────────────

LOGIN_SUCCESS_DATA = [
    pytest.param(
        "18062031483", "mfm543200",
        id="主账号-正常登录",
    ),
    # 可扩展更多有效账号对
]

LOGIN_FAILURE_DATA = [
    pytest.param(
        "wrong_user_123", "mfm543200", "错误用户名+正确密码",
        id="异常-错误用户名",
    ),
    pytest.param(
        "18062031483", "wrongpassword", "正确用户名+错误密码",
        id="异常-错误密码",
    ),
    pytest.param(
        "", "mfm543200", "空用户名+正确密码",
        id="边界-空用户名",
    ),
    pytest.param(
        "18062031483", "", "正确用户名+空密码",
        id="边界-空密码",
    ),
]


# ── 测试类：正向登录（parametrize）──────────────

@pytest.mark.selenium
@pytest.mark.web
class TestLoginSuccess:
    """正向登录测试 — parametrize 驱动多账号"""

    @pytest.mark.parametrize("username,password", LOGIN_SUCCESS_DATA)
    def test_login_success_parametrize(self, driver, selenium_config, username, password):
        """parametrize: 多组有效账号登录验证"""
        captcha_retry = selenium_config["captcha_retry"]

        driver.get(selenium_config["login_url"])
        driver.maximize_window()
        time.sleep(2)

        # 填入用户名密码
        user = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_name")
        )
        user.send_keys(username)

        pwd = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_password")
        )
        pwd.send_keys(password)

        ocr = ddddocr.DdddOcr()
        login_success = False
        for i in range(captcha_retry):
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
                if account.text == username:
                    login_success = True
                    logger.info("登录成功 (第 %d 次验证码尝试)", i + 1)
                    break
            except Exception:
                logger.warning("第 %d 次验证码错误，重试中...", i + 1)
                continue

        assert login_success, (
            f"验证码重试 {captcha_retry} 次后仍未登录成功 "
            f"(user={username})"
        )


# ── 测试类：反向登录（parametrize）───────────────

@pytest.mark.selenium
@pytest.mark.web
class TestLoginFailure:
    """反向登录测试 — parametrize 驱动多组错误数据"""

    @pytest.mark.parametrize("username,password,desc", LOGIN_FAILURE_DATA)
    def test_login_failure_parametrize(
        self, driver, selenium_config, username, password, desc
    ):
        """parametrize: 多组错误凭证验证登录失败"""
        captcha_retry = selenium_config["captcha_retry"]

        driver.get(selenium_config["login_url"])
        driver.maximize_window()
        time.sleep(2)

        user = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_name")
        )
        user.send_keys(username)

        pwd = WebDriverWait(driver, 10, 1).until(
            lambda x: x.find_element(By.ID, "member_password")
        )
        pwd.send_keys(password)

        ocr = ddddocr.DdddOcr()
        login_failed = False
        for i in range(captcha_retry):
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
                    logger.info("检测到登录失败提示 (符合预期: %s)", desc)
                    break
            except Exception:
                logger.warning("第 %d 次未检测到错误提示，重试中...", i + 1)
                continue

        assert login_failed, (
            f"[{desc}] 验证码重试 {captcha_retry} 次后仍未出现预期的登录失败提示"
        )


# ── 测试类：登录后状态验证（fixture 依赖注入）───

@pytest.mark.selenium
@pytest.mark.web
class TestAfterLogin:
    """登录后页面状态验证 — 使用 logged_in_driver fixture"""

    def test_after_login_page_has_account(self, logged_in_driver, selenium_config):
        """登录成功后页面显示正确的账号"""
        driver = logged_in_driver
        account_elem = driver.find_element(
            By.XPATH, "/html/body/div[8]/div/div[2]/div[2]/div[1]/div[1]/div[4]/div"
        )
        expected = selenium_config["valid_username"]
        assert account_elem.text == expected, (
            f"期望账号 {expected}，实际显示 {account_elem.text}"
        )

    def test_after_login_url_changed(self, logged_in_driver, selenium_config):
        """登录成功后 URL 应跳转（不再停留在登录页）"""
        driver = logged_in_driver
        current_url = driver.current_url
        login_url = selenium_config["login_url"]
        assert current_url != login_url, (
            f"登录后 URL 应变化，但仍停留在 {current_url}"
        )
