from selenium import webdriver
from utils.geeTest import CrackGeetest


class GetCookie(object):
    def __init__(self):
        home_url = "https://www.zhipin.com/shanghai/?ka=header-site"
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
        self.browser.get(home_url)

    def get_cookie(self):
        self.browser.get("https://www.zhipin.com/c100010000/?page=1&ka=page-2")
        self.browser.refresh()
        if self.browser.current_url != 'https://www.zhipin.com/c100010000/?page=1&ka=page-2':
            CrackGeetest(
                'https://www.zhipin.com/wapi/zpAntispam/verify/sliderNew?u=IA%7E%7E&callbackUrl=http%3A%2F%2Fwww.zhipin.com%2Fc101220200%2F%3Fquery%3Dpython%26page%3D9%26ka%3Dpage-9&p=I_NY7maoR3YDW3c0Og%7E%7E',
            ).run()
            self.browser.refresh()
        cookie_str = self.browser.get_cookie('__zp_stoken__').get('value')
        if cookie_str:
            print(cookie_str)
            return cookie_str


if __name__ == "__main__":
    c = GetCookie()
    cookie = c.get_cookie()
    print(cookie)

