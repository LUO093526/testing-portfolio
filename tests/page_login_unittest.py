import time

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import ddddocr
from selenium.webdriver.support.wait import WebDriverWait

import unittest
from parameterized import parameterized

class TestTestLogin(unittest.TestCase):
    #方法级别，即每个测试用例执行之前执行
    def setUp(self):
        print("执行登录前，首先运行")
        # 要控制浏览器，需要一个文件，称为驱动文件，相当于遥控器
        self.ser = Service(r"E:\chromedriver\chromedriver.exe")
        # 让遥控器能控制浏览器
        self.driver = webdriver.Chrome(service=self.ser)

        # 打开自定义的网页
        self.driver.get("http://124.223.155.95:8088/home/login/login.html")
        # 最大化
        self.driver.maximize_window()
        time.sleep(3)

    #方法级别，即每个测试用例执行之后执行
    def tearDown(self):
        print("执行登录后，最后运行")
        input("按任意銉继续")
        self.driver.quit()

    #登录成功测试用例
    def test_page_login(self):
        # 隐式等待
        user = self.driver.find_element(By.ID, "member_name")
        # 定位用户名
        user = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.ID, "member_name"))
        user.send_keys("18062031483")

        # 定位密码
        user = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.ID, "member_password"))
        user.send_keys("mfm543200")

        # 保存二进制数据到图片
        # with open("code.png", mode="wb") as f:
        #     f.write(bytecode)

        # 自动识别验证码ddddocr
        ocr = ddddocr.DdddOcr()

        for i in range(10):
            # 定位验证码图片,使用显式等待
            code = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.XPATH, '//*[@id="codeimage"]'))
            # code = driver.find_element(By.XPATH, '//*[@id="codeimage"]')
            # 根据图片获取二进制
            bytecode = code.screenshot_as_png
            # 识别图片
            text = ocr.classification(code.screenshot_as_png)
            print(text)
            # 定位到验证码输入框,使用显示等待
            code = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.ID, "captcha_normal"))
            # code=driver.find_element(By.ID,"captcha_normal")
            code.click()
            time.sleep(1)
            # 输入验证码
            code.clear()
            time.sleep(3)
            code.send_keys(text)
            time.sleep(3)
            # 在code元素处按tab
            code.send_keys(Keys.TAB)
            time.sleep(3)
            # 点击登录按钮
            code = self.driver.find_element(By.XPATH, '//*[@id="login_normal_form"]/div[5]/input[2]')
            code.click()
            time.sleep(5)
            try:
                account = self.driver.find_element(By.XPATH, "//html/body/div[8]/div/div[2]/div[2]/div[1]/div[1]/div[4]/div")
                t = account.text
                if t == "18062031483":
                    print("登录成功")
                    break
            except:
                continue

    #登录用户名输入错误，其它输入正确的，登录失败
    def test_page_login_fail(self):
        # 登录失败测试用例
        """用户名输入错误的测试用例"""
        ocr = ddddocr.DdddOcr()
        # 定位用户名并输入错误的用户名
        user = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.ID, "member_name"))
        user.send_keys("wrong_123")
        time.sleep(1)

        # 定位密码并输入正确密码
        password = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.ID, "member_password"))
        password.send_keys("mfm543200")
        time.sleep(1)

        # 处理验证码
        for i in range(10):
            # 定位验证码图片
            code_img = WebDriverWait(self.driver, 10, 1).until(
                lambda x: x.find_element(By.XPATH, '//*[@id="codeimage"]'))
            # 识别验证码
            text = ocr.classification(code_img.screenshot_as_png)
            print(f"识别的验证码：{text}")

            # 定位到验证码输入框
            code_input = WebDriverWait(self.driver, 10, 1).until(lambda x: x.find_element(By.ID, "captcha_normal"))
            code_input.click()
            time.sleep(1)
            code_input.clear()
            time.sleep(1)
            code_input.send_keys(text)
            time.sleep(2)

            # 按 TAB 键
            code_input.send_keys(Keys.TAB)
            time.sleep(1)

            # 点击登录按钮
            login_btn = self.driver.find_element(By.XPATH, '//*[@id="login_normal_form"]/div[5]/input[2]')
            login_btn.click()
            # time.sleep(3)

            # 验证是否出现错误提示或未能登录成功
            try:
                error_elem = WebDriverWait(self.driver, 10, 1).until(
                    lambda x: x.find_element(By.CSS_SELECTOR, ".layui-layer-content"))
                error_msg = error_elem.text
                print(error_msg)
                if error_msg == "登录失败":
                    print("登录失败，退出循环")
                    break
            except:
                pass

        print("用户名错误测试完成")

