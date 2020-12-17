from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from io import BytesIO
from PIL import Image
from selenium.webdriver import ActionChains
import time
from selenium.common.exceptions import TimeoutException


BORDER = 93


class CrackGeetest():
    def __init__(self, url):
        self.url = url
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.browser = webdriver.Chrome(
            options=options)
        self.browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
             {
                "source":
                        """
                            Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                            })
                        """
            }
        )
        self.wait = WebDriverWait(self.browser, 5)

    def open(self):
        self.browser.get(self.url)

    def get_geetest_button(self):
        button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.geetest_wait')))
        return button

    def get_screenshot(self, full):
        if full:
            geetest_canvas_fullbg = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_fullbg')))
            self.browser.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', geetest_canvas_fullbg,
                                        'style', '')
        else:
            geetest_canvas_fullbg = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_fullbg')))
            self.browser.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', geetest_canvas_fullbg,
                                        'style', 'display:none')
            geetest_canvas_slice = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_slice')))
            self.browser.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', geetest_canvas_slice,
                                        'style', 'display: none;')
        screenshot = self.browser.get_screenshot_as_png()
        self.browser.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', geetest_canvas_fullbg,
                                    'style', '')
        geetest_canvas_slice = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_slice')))
        self.browser.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', geetest_canvas_slice,
                                    'style', '')
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_position(self):
        image = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_slice')))
        size = image.size
        location = image.location
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        return left, top, right, bottom

    def get_geetest_image(self, full, name):
        left, top, right, bottom = self.get_position()
        print('图片的位置:', left, top, right, bottom)
        screenshot = self.get_screenshot(full)
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save('utils/' + name + '.png')
        return captcha

    def get_gap(self, image1, image2):
        left = 135
        for i in range(left, image1.size[0]):
            for j in range(0, image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_track(self, distance):
        track = []
        distance += 20
        mid = distance * 4 / 5
        current = 0
        t = 1
        v = 0
        while current < distance:
            if current < mid:
                a = 15
            else:
                a = -10
            v0 = v
            v = v0 + a * t
            move = v0 * t + a * t * t / 2
            track.append(round(move))
            current += round(move)
        x = sum(track) - distance
        track.append(-x)
        for move in [-3, -2, -1, -1, -1, -2, -3, -2, -1, -1, -1, -2]:
            track.append(move)

        print(sum(track))
        return track

    def get_slider(self):
        slider = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.geetest_slider_button')))
        return slider

    def move_gap(self, slider, track):
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        ActionChains(self.browser).release().perform()

    def crack(self):
        captcha1 = self.get_geetest_image(True, 'captcha1')
        captcha2 = self.get_geetest_image(False, 'captcha2')
        gap = self.get_gap(captcha1, captcha2)
        print('缺口位置:', gap)
        gap -= BORDER
        print('移动距离', gap)
        track = self.get_track(gap)
        print('滑动轨迹:', track)
        slider = self.get_slider()
        self.move_gap(slider, track)
        try:
            self.wait.until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'span.geetest_success_radar_tip_content'), '验证成功'))
            time.sleep(3)
        except TimeoutException:
            self.browser.refresh()
            self.get_geetest_button().click()
            self.crack()

    def __del__(self):
        self.browser.close()

    def run(self):
        self.open()
        self.get_geetest_button().click()
        self.crack()


if __name__ == '__main__':
    crack = CrackGeetest('https://www.zhipin.com/wapi/zpAntispam/verify/sliderNew?u=IA%7E%7E&callbackUrl=http%3A%2F%2Fwww.zhipin.com%2Fc101220200%2F%3Fquery%3Dpython%26page%3D9%26ka%3Dpage-9&p=I_NY7maoR3YDW3c0Og%7E%7E')
    crack.run()


