import requests
import re
from lxml import etree
# from multiprocessing.dummy import Pool as ThreadPool
from spider.getCookie import GetCookie
from db.MysqlSave import Save2Mysql
from settings import KEYWORD


class JobSpider(object):
    def __init__(self):
        self.mysql = Save2Mysql()
        self.mysql.add_table()
        self.session = requests.Session()
        self.get_cookie = GetCookie()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'cookie': f'__zp_stoken__={self.get_cookie.get_cookie()}'
        })

    def start_requests(self):
        cities = self.get_city_urls().keys()
        print(cities)
        params = "?query={}&page=1&ka=page-1".format(KEYWORD)
        num = ''
        try:
            with open('spider/break_point.ini', 'r', encoding='utf-8') as f:
                num = f.read()
        except FileNotFoundError:
            num = 0
        finally:
            print(num)
            cities = list(cities)[int(num):]
            print(cities)
            for index, city in enumerate(cities):
                url = 'https://www.zhipin.com/c{}/{}'.format(city, params)
                print(url)
                try:
                    self.parse(url)
                except Exception as e:
                    print(e.args)
                    with open('spider/break_point.ini', 'w', encoding='utf-8') as f:
                        f.write(str(index))

    @staticmethod
    def get_city_urls():
        resp = requests.get('https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json')
        a = resp.json()
        city_group = a.get('zpData').get('cityGroup')
        data = {}
        for char in city_group:
            for city in char.get('cityList'):
                code = city.get('code')
                name = city.get('name')
                data[str(code)] = name
        return data

    def parse(self, url):
        resp = self.session.get(url).content.decode('utf-8')
        # with open('001.html', 'w', encoding='utf-8') as f:
        #     f.write(resp)
        response = etree.HTML(resp)
        num = int(re.findall('page=(\d+)', url)[0])
        try:
            response.xpath('//title/text()')[0]
        except IndexError:
            self.parse(url)
        else:
            if response.xpath('//title/text()')[0] != '请稍后':
                try:
                    response.xpath('//div[@class="job-primary"]')[0]
                except IndexError as e:
                    self.session.headers.update({
                        'cookie': f'__zp_stoken__={self.get_cookie.get_cookie()}'
                    })
                    return
                else:
                    item = {}
                    job_info_divs = response.xpath('//div[@class="job-primary"]')
                    for div in job_info_divs:
                        item['city_id'] = url.split('/')[-2].replace('c', '')
                        item['job_id'] = div.xpath('div[@class="i'
                                             'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                             'ry-box"]/div[@class="job-title"]/span[@class="job-name"]/a/@data-jobid')[0]
                        item['job_name'] = div.xpath('div[@class="i'
                                             'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                             'ry-box"]/div[@class="job-title"]/span[@class="job-name"]/a/text()')[0]
                        item['job_area'] = div.xpath('div[@class="i'
                                             'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                             'ry-box"]/div[@class="job-title"]/span[@class="job-area-wrapper"]/'
                                                     'span[@class="job-area"]/text()')[0]
                        item['job_salary'] = div.xpath('div[@class="i'
                                             'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                             'ry-box"]/div[@class="job-limit clearfix"]/span[@class="red"]/'
                                                     'text()')[0]
                        try:
                            item['job_exe'], item['job_edu'] = div.xpath('div[@class="i'
                                                 'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                                 'ry-box"]/div[@class="job-limit clearfix"]/p/text()')
                        except ValueError:
                            item['job_exe'] = ' | '.join(div.xpath('div[@class="i'
                                                 'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                                 'ry-box"]/div[@class="job-limit clearfix"]/p/text()')[:-1])
                            item['job_edu'] = div.xpath('div[@class="i'
                                                 'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                                 'ry-box"]/div[@class="job-limit clearfix"]/p/text()')[-1]
                        item['job_tags'] = ' | '.join(div.xpath('div[@class="info-append clearfix"]/div[@class="tags"]/span[@class="tag-item"]/text()'))
                        item['job_welfare'] = ''.join(div.xpath('div[@class="info-append clearfix"]/div[@class="info-desc"]/text()'))
                        try:
                            item['contact'], item['position'] = div.xpath('div[@class="i'
                                             'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                             'ry-box"]/div[@class="job-limit clearfix"]/div[@class="info-publis"]/h3[@class="name"]/text()')
                        except ValueError:
                            item['contact'] = div.xpath('div[@class="i'
                                             'nfo-primary"]/div[@class="primary-wrapper"]/div[@class="prima'
                                             'ry-box"]/div[@class="job-limit clearfix"]/div[@class="info-publis"]/h3[@class="name"]/text()')[0]
                            item['position'] = ''
                        item['company_name'] = div.xpath('div[@class="info-primary"]/div[@class="info-company"]/div[@class="company-text"]/h3[@class="name"]/a/text()')[0]
                        item['company_industry'] = div.xpath('div[@class="info-primary"]/div[@class="info-company"]/div[@class="company-text"]/p/a/text()')[0]
                        try:
                            item['company_natural'], item['company_size'] = div.xpath('div[@class="info-primary"]/div[@class="info-company"]/div[@class="company-text"]/p/text()')
                        except ValueError as e:
                            print(e)
                            item['company_natural'] = ''
                            item['company_size'] = div.xpath('div[@class="info-primary"]/div[@class="info-company"]/div[@class="company-text"]/p/text()')[0]
                        self.mysql.insert(item)
                        print('插入成功', item)
                    num += 1
                    host, params = url.split('?')
                    params = re.sub('(\d+)', str(num), params)
                    next_url = host + '?' + params
                    self.parse(next_url)
            else:
                print('加载cookie重新下载')
                self.session.headers.update({
                    'cookie': f'__zp_stoken__={self.get_cookie.get_cookie()}'
                })
                self.parse(url)

    def run(self):
        self.start_requests()


if __name__ == '__main__':
    job_spider = JobSpider()
    job_spider.run()